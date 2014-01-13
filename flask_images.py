from __future__ import division

from cStringIO import StringIO
from subprocess import call
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlparse
import base64
import datetime
import errno
import hashlib
import logging
import math
import os
import re
import struct
import sys

from PIL import Image as image
from flask import request, current_app, send_file, abort
from itsdangerous import Signer, constant_time_compare


log = logging.getLogger(__name__)


def encode_int(value):
    return base64.urlsafe_b64encode(struct.pack('>I', int(value))).rstrip('=').lstrip('A')


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class Images(object):
    
    MODE_FIT = 'fit'
    MODE_CROP = 'crop'
    MODE_PAD = 'pad'
    MODE_RESHAPE = 'reshape'
    MODES = (MODE_FIT, MODE_CROP, MODE_PAD, MODE_RESHAPE)
    
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['images'] = self

        app.config.setdefault('IMAGES_URL', '/imgsizer') # This is historical.
        app.config.setdefault('IMAGES_NAME', 'images')
        app.config.setdefault('IMAGES_PATH', ['static'])
        app.config.setdefault('IMAGES_CACHE', '/tmp/flask-images')
        app.config.setdefault('IMAGES_MAX_AGE', 3600)

        app.add_url_rule(app.config['IMAGES_URL'] + '/<path:path>', app.config['IMAGES_NAME'], self.handle_request)
        app.context_processor(self._context_processor)
        app.url_build_error_handlers.append(self.build_error_handler)

    def build_error_handler(self, error, endpoint, values):

        # See if we were asked for "images" or "images.<mode>".
        m = re.match(r'^%s(?:\.(%s))?$' % (
            re.escape(current_app.config['IMAGES_NAME']),
            '|'.join(re.escape(mode) for mode in self.MODES)
        ), endpoint)
        if m:
            
            filename = values.pop('filename')
            mode = m.group(1)

            # This is slightly awkward, but I want to trigger the built-in
            # TypeError if you use the "images.<mode>" method AND provide
            # a "mode" kwarg.
            if mode:
                return self.build_url(filename, mode=mode, **values)
            return self.build_url(filename, **values)

        return None

    def _context_processor(self):
        return dict(
            resized_img_src=resized_img_src,
        )

    def build_url(self, local_path, **kwargs):

        local_path = local_path.strip('/')

        for key in 'background mode width height quality format padding'.split():
            if key in kwargs:
                kwargs[key[0]] = kwargs.pop(key)
        
        # Remote URLs are encoded into the query.
        parsed = urlparse(local_path)
        if parsed.netloc:
            kwargs['u'] = local_path
            local_path = 'remote'

        # Local ones are not.
        else:
            abs_path = self.find_img(local_path)
            if abs_path:
                kwargs['v'] = encode_int(int(os.path.getmtime(abs_path)))
        
        # Sign the query.
        public_kwargs = ((k, v) for k, v in kwargs.iteritems() if not k.startswith('_'))
        query = urlencode(sorted(public_kwargs), True)
        signer = Signer(current_app.secret_key)
        sig = signer.get_signature('%s?%s' % (local_path, query))

        return '%s/%s?%s&s=%s' % (
            current_app.config['IMAGES_URL'],
            local_path,
            query,
            sig,
        )
        
    def find_img(self, local_path):
        for path_base in current_app.config['IMAGES_PATH']:
            path = os.path.join(current_app.root_path, path_base, local_path)
            if os.path.exists(path):
                return path
    
    def resize(self, img, width=None, height=None, mode=None, background=None):
        
        orig_width, orig_height = img.size

        width = min(width, orig_width) if width else None
        height = min(height, orig_height) if height else None
        
        if not img.mode.lower().startswith('rgb'):
            img = img.convert('RGBA')
        
        if width and height:
    
            fit, crop = sorted([
                (width, orig_height * width // orig_width),
                (orig_width * height // orig_height, height)
            ])
    
            if mode == self.MODE_FIT or mode == self.MODE_PAD:
                img = img.resize(fit, image.ANTIALIAS)
                
                if mode == self.MODE_PAD:
                    pad_color = {'white': (255, 255, 255)}.get(str(background).lower(), 0)
                    back = image.new('RGBA', (width, height), pad_color)
                    back.paste(img, (
                        (width  - fit[0]) // 2,
                        (height - fit[1]) // 2
                    ))
                    img = back
            
            elif mode == self.MODE_CROP:
                dx = (crop[0] - width) // 2
                dy = (crop[1] - height) // 2
                img = img.resize(crop, image.ANTIALIAS).crop(
                    (dx, dy, dx + width, dy + height)
                )
            
            elif mode == self.MODE_RESHAPE or mode is None:
                img = img.resize((width, height), image.ANTIALIAS)

            else:
                raise ValueError('unsupported mode %r' % mode)
        
        elif width:
            height = orig_height * width // orig_width
            img = img.resize((width, height), image.ANTIALIAS)

        elif height:
            width = orig_width * height // orig_height
            img = img.resize((width, height), image.ANTIALIAS)
        
        return img
    

    def handle_request(self, path):

        # Verify the signature.
        query = dict(request.args.iteritems())
        old_sig = str(query.pop('s', None))
        if not old_sig:
            abort(404)
        signer = Signer(current_app.secret_key)
        new_sig = signer.get_signature('%s?%s' % (path, urlencode(sorted(query.iteritems()), True)))
        if not constant_time_compare(old_sig, new_sig):
            abort(404)
        
        remote_url = query.get('u')
        if remote_url:

            # Download the remote file.
            makedirs(current_app.config['IMAGES_CACHE'])
            path = os.path.join(
                current_app.config['IMAGES_CACHE'],
                hashlib.md5(remote_url).hexdigest() + os.path.splitext(remote_url)[1]
            )

            if not os.path.exists(path):
                log.info('downloading %s' % remote_url)
                tmp_path = path + '.tmp-' + str(os.getpid())
                fh = open(tmp_path, 'wb')
                fh.write(urlopen(remote_url).read())
                fh.close()
                call(['mv', tmp_path, path])
        else:
            path = self.find_img(path)
            if not path:
                abort(404) # Not found.

        raw_mtime = os.path.getmtime(path)
        mtime = datetime.datetime.utcfromtimestamp(raw_mtime)
        # log.debug('last_modified: %r' % mtime)
        # log.debug('if_modified_since: %r' % request.if_modified_since)
        if request.if_modified_since and request.if_modified_since >= mtime:
            return '', 304
        
        
        mode = query.get('m')
        background = query.get('b')
        width = query.get('w')
        width = int(width) if width else None
        height = query.get('h')
        height = int(height) if height else None
        quality = query.get('q')
        quality = int(quality) if quality else 75
        format = query.get('f', '').lower() or os.path.splitext(path)[1][1:] or 'jpeg'
        format = {'jpg' : 'jpeg'}.get(format, format)
        has_version = 'v' in query
                
        cache_key = hashlib.md5(repr((
            path, mode, width, height, quality, format, background
        ))).hexdigest()

        cache_dir = os.path.join(current_app.config['IMAGES_CACHE'], cache_key[:2])
        cache_path = os.path.join(cache_dir, cache_key + '.' + format)

        cache_mtime = os.path.getmtime(cache_path) if os.path.exists(cache_path) else None
        
        if not cache_mtime or cache_mtime < raw_mtime:
            
            log.info('resizing %r for %s' % (path, query))
            
            img = image.open(path)
            img = self.resize(img, width=width, height=height, mode=mode, background=background)
            
            makedirs(cache_dir)
            cache_file = open(cache_path, 'wb')
            img.save(cache_file, format, quality=quality)
            cache_file.close()
        
        return send_file(cache_path,
            mimetype='image/%s' % format,
            cache_timeout=31536000 if has_version else current_app.config['IMAGES_MAX_AGE'],
        )


def resized_img_src(path, **kw):
    return current_app.extensions['images'].build_url(path, **kw)


