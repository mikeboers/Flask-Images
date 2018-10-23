from PIL import Image
from six import moves, string_types


TRANSFORM_AXIS = {
    Image.EXTENT: (0, 1, 0, 1),
    Image.AFFINE: (None, None, 0, None, None, 1),
    Image.QUAD: (0, 1, 0, 1, 0, 1, 0, 1),
    Image.PERSPECTIVE: (None, None, None, None, None, None, None, None),
    # Image.MESH: ???
}


class Transform(list):

    def __init__(self, spec, image_size=None):

        super(Transform, self).__init__(spec)

        self.flag = getattr(Image, self[0].upper())
        try:
            axis = (None, 0, 1) + TRANSFORM_AXIS[self.flag]
        except KeyError:
            raise ValueError('unknown transform %r' % self[0])

        if len(self) != len(axis):
            raise ValueError('expected %d transform values; got %d' % (len(axis), len(self)))

        for i in moves.range(1, len(self)):
            v = self[i]
            if isinstance(v, string_types):
                if v[-1:] in ('%', 'p'): # Percentages.
                    if axis[i] is None:
                        raise ValueError('unknown dimension for %s value %d' % (self[0], i))
                    if image_size is None:
                        raise ValueError('no image size with relative transform')
                    self[i] = image_size[axis[i]] * float(v[:-1]) / 100
                else:
                    self[i] = float(v)

        # Finalize the size.
        if not self[1] or not self[2]:
            if not image_size:
                ValueError('no image size or transform size')
        self[1] = int(self[1] or image_size[0])
        self[2] = int(self[2] or image_size[1])

    @property
    def size(self):
        return self[1], self[2]

    def apply(self, image):
        return image.transform(
            (int(self[1] or image.size[0]), int(self[2] or image.size[1])),
            self.flag,
            self[3:],
            Image.BILINEAR,
        )
