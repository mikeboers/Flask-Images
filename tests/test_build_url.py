from . import *


class TestUrlBuild(TestCase):

    def test_default_mode(self):

        url = url_for('images', filename='cc.png', width=5, mode='crop')

        parsed_url = urlsplit(url)
        query_args = dict(parse_qsl(parsed_url.query))

        self.assertEqual('/imgsizer/cc.png', parsed_url.path)
        self.assertEqual('crop', query_args['m'])
        self.assertEqual('5', query_args['w'])
        self.assertIn('s', query_args)

        response = self.client.get(url)
        self.assert200(response)

    def test_explicit_modes(self):

        for mode in 'crop', 'fit', 'pad', 'reshape':

            url = url_for('images.%s' % mode, filename='cc.png', width=5)
            response = self.client.get(url)
            self.assert200(response)
            
            parsed_url = urlsplit(url)
            query_args = dict(parse_qsl(parsed_url.query))

            self.assertEqual('/imgsizer/cc.png', parsed_url.path)
            self.assertEqual(mode, query_args['m'])
            self.assertEqual('5', query_args['w'])
            self.assertIn('s', query_args)

    def test_too_many_modes(self):
        self.assertRaises(TypeError, url_for, 'images.crop', filename='cc.png', mode='reshape')

    def test_external(self):
        url = url_for('images', filename='cc.png', width=5, mode='crop', _external=True)
        parsed_url = urlsplit(url)

        self.assertEqual(parsed_url.scheme, 'http')
        self.assertEqual(parsed_url.netloc, 'localhost:8000')
