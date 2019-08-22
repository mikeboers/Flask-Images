from __future__ import division

from io import BytesIO as StringIO
from subprocess import call
import base64
import cgi
import datetime
import errno
import hashlib
import logging
import math
import os
import re
import struct
import sys

from six import iteritems, PY3, string_types, text_type
if PY3:
    from urllib.parse import urlparse, urlencode, quote as urlquote
    from urllib.request import urlopen
    from urllib.error import HTTPError
else:
    from urlparse import urlparse
    from urllib import urlencode, quote as urlquote
    from urllib2 import urlopen, HTTPError

from PIL import Image, ImageFilter
from flask import request, current_app, send_file, abort

try:
    from itsdangerous import Signer, constant_time_compare
except ImportError:
    from itsdangerous import Signer
    from itsdangerous._compat import constant_time_compare

from . import modes
from .size import ImageSize
from .transform import Transform


log = logging.getLogger(__name__)



def encode_str(value):
    if isinstance(value, text_type):
        return value.encode('utf-8')
    return value

def encode_int(value):
    return base64.urlsafe_b64encode(struct.pack('>I', int(value))).decode('utf-8').rstrip('=').lstrip('A')


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


# We must whitelist schemes which are permitted, otherwise craziness (such as
# allowing access to the filesystem) may ensue.
ALLOWED_SCHEMES = set(('http', 'https', 'ftp'))

# The options which we immediately recognize and shorten.
LONG_TO_SHORT = dict(
    background='b',
    cache='c',
    enlarge='e',
    format='f',
    height='h',
    mode='m',
    quality='q',
    transform='x',
    url='u',
    version='v',
    width='w',
    sharpen='usm',
    # signature -> 's', but should not be here.
)
SHORT_TO_LONG = dict((v, k) for k, v in iteritems(LONG_TO_SHORT))




class Images(object):
    
    
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
        app.url_build_error_handlers.append(self.build_error_handler)

        if hasattr(app, 'add_template_global'): # Flask >= 0.10
            app.add_template_global(resized_img_src)
            app.add_template_global(resized_img_size)
            app.add_template_global(resized_img_attrs)
            app.add_template_global(resized_img_tag)
        else:
            ctx = {
                'resized_img_src': resized_img_src,
                'resized_img_size': resized_img_size,
                'resized_img_attrs': resized_img_attrs,
                'resized_img_tag': resized_img_tag,
            }
            app.context_processor(lambda: ctx)


    def build_error_handler(self, error, endpoint, values):

        # See if we were asked for "images" or "images.<mode>".
        m = re.match(r'^%s(?:\.(%s))?$' % (
            re.escape(current_app.config['IMAGES_NAME']),
            '|'.join(re.escape(mode) for mode in modes.ALL)
        ), endpoint)
        if m:
            
            filename = values.pop('filename')

            mode = m.group(1)
            if mode:
                # There used to be a TypeError here that werkzeug would generate,
                # if there was already a "mode" but it seems that has changed in
                # newer versions, so lets just take care of it ourselves.
                if 'mode' in values:
                    raise ValueError("`mode` is specified in endpoint and kwargs.")
                values['mode'] = mode

            return self.build_url(filename, **values)

        return None

    def build_url(self, local_path, **kwargs):

        # Make the path relative.
        local_path = local_path.strip('/')

        # We complain when we see non-normalized paths, as it is a good
        # indicator that unsanitized data may be getting through.
        # Mutating the scheme syntax to match is a little gross, but it works
        # for today.
        norm_path = os.path.normpath(local_path)
        if local_path.replace('://', ':/') != norm_path or norm_path.startswith('../'):
            raise ValueError('path is not normalized')

        external = kwargs.pop('external', None) or kwargs.pop('_external', None)
        scheme = kwargs.pop('scheme', None)
        if scheme and not external:
            raise ValueError('cannot specify scheme without external=True')
        if kwargs.get('_anchor'):
            raise ValueError('images have no _anchor')
        if kwargs.get('_method'):
            raise ValueError('images have no _method')
        
        # Remote URLs are encoded into the query.
        parsed = urlparse(local_path)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme not in ALLOWED_SCHEMES:
                raise ValueError('scheme %r is not allowed' % parsed.scheme)
            kwargs['url'] = local_path
            local_path = '_' # Must be something.

        # Local ones are not.
        else:
            abs_path = self.find_img(local_path)
            if abs_path:
                kwargs['version'] = encode_int(int(os.path.getmtime(abs_path)))
        
        # Prep the cache flag, which defaults to True.
        cache = kwargs.pop('cache', True)
        if not cache:
            kwargs['cache'] = ''

        # Prep the enlarge flag, which defaults to False.
        enlarge = kwargs.pop('enlarge', False)
        if enlarge:
            kwargs['enlarge'] = '1'

        # Prep the transform, which is a set of delimited strings.
        transform = kwargs.get('transform')
        if transform:
            if isinstance(transform, string_types):
                transform = re.split(r'[,;:_ ]', transform)
            # We replace delimiters with underscores, and percent with p, since
            # these won't need escaping.
            kwargs['transform'] = '_'.join(str(x).replace('%', 'p') for x in transform)

        # Sign the query.
        # Collapse to a dict first so that if we accidentally have two of the
        # same kwarg (e.g. used `hidpi_sharpen` and `usm` which both turn into `usm`).
        public_kwargs = {
            LONG_TO_SHORT.get(k, k): v
            for k, v in iteritems(kwargs)
            if v is not None and not k.startswith('_')
        }
        query = urlencode(sorted(iteritems(public_kwargs)), True)
        signer = Signer(current_app.secret_key)
        sig = signer.get_signature('%s?%s' % (local_path, query))

        url = '%s/%s?%s&s=%s' % (
            current_app.config['IMAGES_URL'],
            urlquote(local_path, "/$-_.+!*'(),"),
            query,
            sig,
        )

        if external:
            url = '%s://%s%s/%s' % (
                scheme or request.scheme,
                request.host,
                request.script_root,
                url.lstrip('/')
            )

        return url
        
    def find_img(self, local_path):
        local_path = os.path.normpath(local_path.lstrip('/'))
        for path_base in current_app.config['IMAGES_PATH']:
            path = os.path.join(current_app.root_path, path_base, local_path)
            if os.path.exists(path):
                return path
    
    def calculate_size(self, path, **kw):
        path = self.find_img(path)
        if not path:
            abort(404)
        return ImageSize(path=path, **kw)

    def resize(self, image, background=None, **kw):
        
        size = ImageSize(image=image, **kw)

        # Get into the right colour space.
        if not image.mode.upper().startswith('RGB'):
            image = image.convert('RGBA')

        # Apply any requested transform.
        if size.transform:
            image = Transform(size.transform, image.size).apply(image)
        
        # Handle the easy cases.
        if size.mode in (modes.RESHAPE, None) or size.req_width is None or size.req_height is None:
            return image.resize((size.width, size.height), Image.ANTIALIAS)

        if size.mode not in (modes.FIT, modes.PAD, modes.CROP):
            raise ValueError('unknown mode %r' % size.mode)

        if image.size != (size.op_width, size.op_height):
            image = image.resize((size.op_width, size.op_height), Image.ANTIALIAS)
        
        if size.mode == modes.FIT:
            return image

        elif size.mode == modes.PAD:
            pad_color = str(background or 'black')
            padded = Image.new('RGBA', (size.width, size.height), pad_color)
            padded.paste(image, (
                (size.width  - size.op_width ) // 2,
                (size.height - size.op_height) // 2
            ))
            return padded
            
        elif size.mode == modes.CROP:

            dx = (size.op_width  - size.width ) // 2
            dy = (size.op_height - size.height) // 2
            return image.crop(
                (dx, dy, dx + size.width, dy + size.height)
            )
            
        else:
            raise RuntimeError('unhandled mode %r' % size.mode)
    
    def post_process(self, image, sharpen=None):

        if sharpen:
            assert len(sharpen) == 3, 'unsharp-mask has 3 parameters'
            image = image.filter(ImageFilter.UnsharpMask(
                float(sharpen[0]),
                int(sharpen[1]),
                int(sharpen[2]),
            ))

        return image

    def handle_request(self, path):

        # Verify the signature.
        query = dict(iteritems(request.args))
        old_sig = str(query.pop('s', None))
        if not old_sig:
            abort(404)
        signer = Signer(current_app.secret_key)
        new_sig = signer.get_signature('%s?%s' % (path, urlencode(sorted(iteritems(query)), True)))
        if not constant_time_compare(str(old_sig), str(new_sig)):
            log.warning("Signature mismatch: url's {} != expected {}".format(old_sig, new_sig))
            abort(404)
        
        # Expand kwargs.

        query = dict((SHORT_TO_LONG.get(k, k), v) for k, v in iteritems(query))
        remote_url = query.get('url')
        if remote_url:

            # This is redundant for newly built URLs, but not for those which
            # have already been generated and cached.
            parsed = urlparse(remote_url)
            if parsed.scheme not in ALLOWED_SCHEMES:
                abort(404)

            # Download the remote file.
            makedirs(current_app.config['IMAGES_CACHE'])
            path = os.path.join(
                current_app.config['IMAGES_CACHE'],
                hashlib.md5(encode_str(remote_url)).hexdigest() + os.path.splitext(parsed.path)[1]
            )

            if not os.path.exists(path):
                log.info('downloading %s' % remote_url)
                tmp_path = path + '.tmp-' + str(os.getpid())
                try:
                    remote_file = urlopen(remote_url).read()
                except HTTPError as e:
                    # abort with remote error code (403 or 404 most times)
                    # log.debug('HTTP Error: %r' % e)
                    abort(e.code)
                else:
                    fh = open(tmp_path, 'wb')
                    fh.write(remote_file)
                    fh.close()
                call(['mv', tmp_path, path])
        else:
            path = self.find_img(path)
            if not path:
                abort(404) # Not found.

        raw_mtime = os.path.getmtime(path)
        mtime = datetime.datetime.utcfromtimestamp(raw_mtime).replace(microsecond=0)
        # log.debug('last_modified: %r' % mtime)
        # log.debug('if_modified_since: %r' % request.if_modified_since)
        if request.if_modified_since and request.if_modified_since >= mtime:
            return '', 304
        
        mode = query.get('mode')

        transform = query.get('transform')
        transform = re.split(r'[;,_/ ]', transform) if transform else None

        background = query.get('background')
        width = query.get('width')
        width = int(width) if width else None
        height = query.get('height')
        height = int(height) if height else None
        quality = query.get('quality')
        quality = int(quality) if quality else 75
        format = (query.get('format', '') or os.path.splitext(path)[1][1:] or 'jpeg').lower()
        format = {'jpg' : 'jpeg'}.get(format, format)
        has_version = 'version' in query
        use_cache = query.get('cache', True)
        enlarge = query.get('enlarge', False)

        sharpen = query.get('sharpen')
        sharpen = re.split(r'[+:;,_/ ]', sharpen) if sharpen else None

        if use_cache:

            # The parts in this initial list were parameters cached in version 1.
            # In order to avoid regenerating all images when a new feature is
            # added, we append (feature_name, value) tuples to the end.
            cache_key_parts = [path, mode, width, height, quality, format, background]
            if transform:
                cache_key_parts.append(('transform', transform))
            if sharpen:
                cache_key_parts.append(('sharpen', sharpen))
            if enlarge:
                cache_key_parts.append(('enlarge', enlarge))


            cache_key = hashlib.md5(repr(tuple(cache_key_parts)).encode('utf-8')).hexdigest()
            cache_dir = os.path.join(current_app.config['IMAGES_CACHE'], cache_key[:2])
            cache_path = os.path.join(cache_dir, cache_key + '.' + format)
            cache_mtime = os.path.getmtime(cache_path) if os.path.exists(cache_path) else None
        
        mimetype = 'image/%s' % format
        cache_timeout = 31536000 if has_version else current_app.config['IMAGES_MAX_AGE']

        if not use_cache or not cache_mtime or cache_mtime < raw_mtime:
            
            log.info('resizing %r for %s' % (path, query))
            image = Image.open(path)
            image = self.resize(image,
                background=background,
                enlarge=enlarge,
                height=height,
                mode=mode,
                transform=transform,
                width=width,
            )
            image = self.post_process(image,
                sharpen=sharpen,
            )

            if not use_cache:
                fh = StringIO()
                image.save(fh, format, quality=quality)
                return fh.getvalue(), 200, [
                    ('Content-Type', mimetype),
                    ('Cache-Control', str(cache_timeout)),
                ]
            
            makedirs(cache_dir)
            cache_file = open(cache_path, 'wb')
            image.save(cache_file, format, quality=quality)
            cache_file.close()
        
        return send_file(cache_path, mimetype=mimetype, cache_timeout=cache_timeout)



def resized_img_size(path, **kw):
    self = current_app.extensions['images']
    return self.calculate_size(path, **kw)

def resized_img_attrs(path, hidpi=None, width=None, height=None, enlarge=False, **kw):
    
    self = current_app.extensions['images']

    page = image = self.calculate_size(
        path,
        width=width,
        height=height,
        enlarge=enlarge,
        _shortcut=True,
        **kw
    )

    if hidpi:

        hidpi_size = self.calculate_size(
            path,
            width=hidpi * width if width else None,
            height=hidpi * height if height else None,
            enlarge=enlarge,
            _shortcut=True,
            **kw
        )

        # If the larger size works.
        if enlarge or not hidpi_size.needs_enlarge:
            image = hidpi_size

            for k, v in list(kw.items()):
                if k.startswith('hidpi_'):
                    kw.pop(k)
                    kw[k[6:]] = v

            kw.setdefault('quality', 60)
        
        else:
            hidpi = False

    return {

        'data-hidpi-scale': hidpi,
        'data-original-width': image.image_width,
        'data-original-height': image.image_height,

        'width': page.width,
        'height': page.height,
        'src': self.build_url(
            path,
            width=int(image.req_width) if image.req_width else image.req_width,
            height=int(image.req_height) if image.req_height else image.req_height,
            enlarge=enlarge,
            **kw
        ),
    
    }


def resized_img_tag(path, **kw):
    attrs = {}
    for attr, key in (('class', 'class_'), ):
        try:
            attrs[attr] = kw.pop(key)
        except KeyError:
            pass
    attrs.update(resized_img_attrs(path, **kw))
    return '<img %s/>' % ' '.join('%s="%s"' % (k, cgi.escape(str(v))) for k, v in sorted(iteritems(attrs)))


def resized_img_src(path, **kw):
    self = current_app.extensions['images']
    return self.build_url(path, **kw)


