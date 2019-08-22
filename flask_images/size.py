from __future__ import division

from PIL import Image

from . import modes
from .transform import Transform


class ImageSize(object):

    @property
    def image(self):
        if not self._image and self.path:
            self._image = Image.open(self.path)
        return self._image

    def __init__(self, path=None, image=None, width=None, height=None,
        enlarge=True, mode=None, transform=None, sharpen=None, _shortcut=False, **kw
    ):

        # Inputs.
        self.__dict__.update(kw)
        self.path = path
        self._image = image
        self.req_width = width
        self.req_height = height
        self.enlarge = bool(enlarge)
        self.mode = mode
        self.transform = transform
        self.sharpen = sharpen

        self.image_width = self.image_height = None
        
        # Results to be updated as appropriate.
        self.needs_enlarge = None
        self.width = width
        self.height = height
        self.op_width = None
        self.op_height = None

        if _shortcut and width and height and enlarge and mode in (modes.RESHAPE, modes.CROP, None):
            return

        # Source the original image dimensions.
        if self.transform:
            self.image_width, self.image_height = Transform(self.transform,
                self.image.size if self.image else (width, height)
            ).size
        else:
            self.image_width, self.image_height = self.image.size

        # It is possible that no dimensions are even given, so pass it through.
        if not (self.width or self.height):
            self.width = self.image_width
            self.height = self.image_height
            return

        # Maintain aspect ratio and scale width.
        if not self.height:
            self.needs_enlarge = self.width > self.image_width
            if not self.enlarge:
                self.width = min(self.width, self.image_width)
            self.height = self.image_height * self.width // self.image_width
            return

        # Maintain aspect ratio and scale height.
        if not self.width:
            self.needs_enlarge = self.height > self.image_height
            if not self.enlarge:
                self.height = min(self.height, self.image_height)
            self.width = self.image_width * self.height // self.image_height
            return

        # Don't maintain aspect ratio; enlarging is sloppy here.
        if self.mode in (modes.RESHAPE, None):
            self.needs_enlarge = self.width > self.image_width or self.height > self.image_height
            if not self.enlarge:
                self.width = min(self.width, self.image_width)
                self.height = min(self.height, self.image_height)
            return

        if self.mode not in (modes.FIT, modes.CROP, modes.PAD):
            raise ValueError('unknown mode %r' % self.mode)

        # This effectively gives us the dimensions of scaling to fit within or
        # around the requested size. These are always scaled to fit.
        fit, pre_crop = sorted([
            (self.req_width, self.image_height * self.req_width // self.image_width),
            (self.image_width * self.req_height // self.image_height, self.req_height)
        ])

        self.op_width, self.op_height = fit if self.mode in (modes.FIT, modes.PAD) else pre_crop
        self.needs_enlarge = self.op_width > self.image_width or self.op_height > self.image_height

        if self.needs_enlarge and not self.enlarge:
            self.op_width = min(self.op_width, self.image_width)
            self.op_height = min(self.op_height, self.image_height)
            if self.mode != modes.PAD:
                self.width = min(self.width, self.image_width)
                self.height = min(self.height, self.image_height)
            return

        if self.mode != modes.PAD:
            self.width = min(self.op_width, self.width)
            self.height = min(self.op_height, self.height)



