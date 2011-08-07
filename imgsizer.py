
from __future__ import division

import math
import os
import logging
import Image as image
from cStringIO import StringIO
import datetime
import hashlib
import sys
import base64
import struct

from .uri.query import Query
from .request import Request, Response
from . import status


log = logging.getLogger(__name__)

# TODO:
# - take max_age from config

def encode_int(value):
    return base64.urlsafe_b64encode(struct.pack('>I', int(value))).rstrip('=').lstrip('A')
    
class ImgSizer(object):
    
    MODE_FIT = 'fit'
    MODE_CROP = 'crop'
    MODE_PAD = 'pad'
    MODES = (MODE_FIT, MODE_CROP, MODE_PAD)
    
    def __init__(self, path, cache_root, sig_key, maxage):
        self.path = [os.path.abspath(x) for x in path]
        self.cache_root = cache_root
        self.sig_key = sig_key
        self.maxage = maxage
    
    def build_url(self, local_path, **kwargs):
        for key in 'background mode width height quality format padding'.split():
            if key in kwargs:
                kwargs[key[0]] = kwargs[key]
                del kwargs[key]
        query = Query(kwargs)
        
        
        abs_path = self.find_img(local_path)
        if abs_path:
            query['v'] = encode_int(int(os.path.getmtime(abs_path)))
        
        query.sort()
        
        query['path'] = local_path
        query.sign(self.sig_key, add_time=False, add_nonce=False)
        del query['path']
        
        return local_path + ('?' + str(query) if kwargs else '')
        
    def find_img(self, local_path):
        local_path = local_path.lstrip('/')
        for path_base in self.path:
            path = os.path.join(path_base, local_path)
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
            
            else:
                img = img.resize((width, height), image.ANTIALIAS)
        
        elif width:
            height = orig_height * width // orig_width
            img = img.resize((width, height), image.ANTIALIAS)

        elif height:
            width = orig_width * height // orig_height
            img = img.resize((width, height), image.ANTIALIAS)
        
        return img
    
    @Request.application
    def __call__(self, request):
        
        path = self.find_img(request.path_info)
        if not path:
            return status.NotFound()
        
        query = Query(request.query)
        query['path'] = request.path_info
        if not query.verify(self.sig_key):
            log.warning('signature not accepted')
            return status.NotFound()
        
        raw_mtime = os.path.getmtime(path)
        mtime = datetime.datetime.utcfromtimestamp(raw_mtime)
        # log.debug('last_modified: %r' % mtime)
        # log.debug('if_modified_since: %r' % request.if_modified_since)
        if request.if_modified_since and request.if_modified_since >= mtime:
            return status.NotModified()
        
        
        mode = request.query.get('m')
        background = request.query.get('b')
        width = request.query.get('w')
        width = int(width) if width else None
        height = request.query.get('h')
        height = int(height) if height else None
        quality = request.query.get('q')
        quality = int(quality) if quality else 75
        format = request.query.get('f', '').lower() or os.path.splitext(path)[1][1:] or 'jpeg'
        format = {'jpg' : 'jpeg'}.get(format, format)
        has_version = 'v' in request.query
                
        cache_key = hashlib.md5(repr((
            path, mode, width, height, quality, format, background
        ))).hexdigest()
        cache_path = os.path.join(self.cache_root, cache_key + '.' + format)
        cache_mtime = os.path.getmtime(cache_path) if os.path.exists(cache_path) else None
        
        if not cache_mtime or cache_mtime < raw_mtime:
            
            log.info('resizing %r for %s' % (request.path_info, request.query))
            
            img = image.open(path)
            img = self.resize(img, width=width, height=height, mode=mode, background=background)
            
            try:
                cache_file = open(cache_path, 'wb')
                img.save(cache_file, format, quality=quality)
                cache_file.close()
            except Exception as e:
                log.exception('error while saving image to cache')
        
        return Response().send_file(cache_path,
            mimetype='image/%s' % format,
            cache_max_age=31536000 if has_version else self.max_age,
        )



class ImgSizerAppMixin(object):
    
    def setup_config(self):
        super(ImgSizerAppMixin, self).setup_config()
        self.config.setdefaults(
            imgsizer_path=[],
            imgsizer_maxage=3600,
            imgsizer_cache_dir='/tmp',
            imgsizer_url_base='__img',
        )
    
    def __init__(self, *args, **kwargs):
        super(ImgSizerAppMixin, self).__init__(*args, **kwargs)
        
        self.imgsizer = ImgSizer(
            self.config.imgsizer_path,
            self.config.imgsizer_cache_dir,
            self.config.private_key or os.urandom(32),
            self.config.imgsizer_maxage,
        )
        self.route('/' + self.config.imgsizer_url_base, self.imgsizer)
        self.view_globals['auto_img_src'] = self.auto_img_src
    
    def auto_img_src(self, *args, **kwargs):
        return '/' + self.config.imgsizer_url_base + self.imgsizer.build_url(*args, **kwargs)


if __name__ == '__main__':
    #
    __app__ = ImgSizer(
        path=[],
        sig_key='awesome'
    )
    print __app__.build_url('/mock/photos/2459172663_35af8640ff.jpg', width=200)