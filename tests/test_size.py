from . import *


class TestImageSize(TestCase):

    def test_reshape(self):

        s = ImageSize(transform=[0, 100, 100], width=50)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 50)
        self.assertEqual(s.height, 50)

        s = ImageSize(transform=[0, 100, 100], width=200, enlarge=True)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 200)
        self.assertEqual(s.height, 200)

        s = ImageSize(transform=[0, 100, 100], width=200, enlarge=False)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 100)
        self.assertEqual(s.height, 100)

        s = ImageSize(transform=[0, 100, 100], height=50)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 50)
        self.assertEqual(s.height, 50)

        s = ImageSize(transform=[0, 100, 100], height=200, enlarge=True)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 200)
        self.assertEqual(s.height, 200)

        s = ImageSize(transform=[0, 100, 100], height=200, enlarge=False)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 100)
        self.assertEqual(s.height, 100)


    def test_crop_enlarge(self):

        # Both need enlarging.
        s = ImageSize(transform=[0, 100, 100], width=150, height=200, mode='crop', enlarge=True)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 200)
        self.assertEqual(s.op_height, 200)

        # One needs enlarging.
        s = ImageSize(transform=[0, 200, 100], width=150, height=200, mode='crop', enlarge=True)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 400)
        self.assertEqual(s.op_height, 200)

        # Neither need enlarging.
        s = ImageSize(transform=[0, 400, 400], width=150, height=200, mode='crop', enlarge=True)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 200)
        self.assertEqual(s.op_height, 200)

    def test_crop_no_enlarge(self):

        # Both need enlarging.
        s = ImageSize(transform=[0, 100, 100], width=150, height=200, mode='crop', enlarge=False)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 100)
        self.assertEqual(s.height, 100)
        self.assertEqual(s.op_width, 100)
        self.assertEqual(s.op_height, 100)

        # One needs enlarging.
        s = ImageSize(transform=[0, 200, 100], width=150, height=200, mode='crop', enlarge=False)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 100) # <--
        self.assertEqual(s.op_width, 200)
        self.assertEqual(s.op_height, 100)

        # Neither need enlarging.
        s = ImageSize(transform=[0, 400, 400], width=150, height=200, mode='crop', enlarge=False)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 200)
        self.assertEqual(s.op_height, 200)

    def test_fit_enlarge(self):

        # Both need enlarging.
        s = ImageSize(transform=[0, 100, 100], width=150, height=200, mode='fit', enlarge=True)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 150)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 150)

        # One is big enough.
        s = ImageSize(transform=[0, 200, 100], width=150, height=200, mode='fit', enlarge=True)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 75)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 75)

        # Neither need enlarging.
        s = ImageSize(transform=[0, 400, 400], width=150, height=200, mode='fit', enlarge=True)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 150)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 150)

    def test_fit_no_enlarge(self):

        # Both need enlarging.
        s = ImageSize(transform=[0, 100, 100], width=150, height=200, mode='fit', enlarge=False)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 100)
        self.assertEqual(s.height, 100)
        self.assertEqual(s.op_width, 100)
        self.assertEqual(s.op_height, 100)

        # One is big enough.
        s = ImageSize(transform=[0, 200, 100], width=150, height=200, mode='fit', enlarge=False)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 75) # <--
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 75)

        # Neither need enlarging.
        s = ImageSize(transform=[0, 400, 400], width=150, height=200, mode='fit', enlarge=False)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 150)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 150)


    def test_pad_enlarge(self):

        # Both need enlarging.
        s = ImageSize(transform=[0, 100, 100], width=150, height=200, mode='pad', enlarge=True)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 150)

        # One is big enough.
        s = ImageSize(transform=[0, 200, 100], width=150, height=200, mode='pad', enlarge=True)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 75)

        # Neither need enlarging.
        s = ImageSize(transform=[0, 400, 400], width=150, height=200, mode='pad', enlarge=True)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 150)

    def test_pad_no_enlarge(self):

        # Both need enlarging.
        s = ImageSize(transform=[0, 100, 100], width=150, height=200, mode='pad', enlarge=False)
        self.assertTrue(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 100)
        self.assertEqual(s.op_height, 100)

        # One is big enough.
        s = ImageSize(transform=[0, 200, 100], width=150, height=200, mode='pad', enlarge=False)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200) # <--
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 75)

        # Neither need enlarging.
        s = ImageSize(transform=[0, 400, 400], width=150, height=200, mode='pad', enlarge=False)
        self.assertFalse(s.needs_enlarge)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 200)
        self.assertEqual(s.op_width, 150)
        self.assertEqual(s.op_height, 150)



