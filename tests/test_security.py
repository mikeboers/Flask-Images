from . import *


class TestSecurity(TestCase):

    def test_path_normalization(self):
        self.assertRaises(ValueError, url_for, 'images', filename='/etc//passwd')
        self.assertRaises(ValueError, url_for, 'images', filename='/./etc/passwd')
        self.assertRaises(ValueError, url_for, 'images', filename='/etc/./passwd')
        self.assertRaises(ValueError, url_for, 'images', filename='/something/../etc/passwd')
        self.assertRaises(ValueError, url_for, 'images', filename='../etc/passwd')
        self.assertRaises(ValueError, url_for, 'images', filename='http://example.com/../photo.jpg')

    def test_invalid_scheme(self):
        self.assertRaises(ValueError, url_for, 'images', filename='file:///etc/passwd')

    def test_invalid_scheme_with_netloc(self):
        self.assertRaises(ValueError, url_for, 'images', filename='file://../etc/passwd')

    def test_valid_paths(self):
        url_for('images', filename='http://example.com/photo.jpg')
        url_for('images', filename='relative/path.jpg')
        url_for('images', filename='/absolute/path.jpg')

