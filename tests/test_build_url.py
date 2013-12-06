from urlparse import urlsplit, parse_qs

from flask import Flask, url_for
from flask.ext.testing import TestCase
from flask.ext.images import Images


class TestUrlBuild(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'secret secret'
        app.config['IMAGES_PATH'] = ['assets']
        self.images = Images(app)
        return app

    def setUp(self):
        self.url = url_for('images', filename='cc.png', width=5, mode='crop')
        self.parsed_url = urlsplit(self.url)
        self.qs = parse_qs(self.parsed_url.query)

    def test_url_path(self):
        self.assertEqual('/imgsizer/cc.png', self.parsed_url.path)

    def test_qs_mode(self):
        self.assertEqual(['crop'], self.qs['m'])

    def test_qs_width(self):
        self.assertEqual(['5'], self.qs['w'])

    def test_qs_contains_secret(self):
        self.assertIn('s', self.qs)

    def test_response(self):
        response = self.client.get(self.url)
        self.assert200(response)
