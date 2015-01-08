from . import *


class TestURLEscaping(TestCase):

    def test_url_with_query(self):
        url = url_for('images', filename='http://example.com/?a=1&b=2')
        self.assertTrue(
            url.startswith('/imgsizer/_?u=http%3A%2F%2Fexample.com%2F%3Fa%3D1%26b%3D2&'),
            url
        )
