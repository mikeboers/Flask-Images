import unittest
from urlparse import urlsplit, parse_qsl

import werkzeug as wz

from flask import Flask, url_for, render_template_string
from flask.ext.images import Images, ImageSize, resized_img_src
import flask

flask_version = tuple(map(int, flask.__version__.split('.')))


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = self.create_app()
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        self.req_ctx = self.app.test_request_context('http://localhost:8000/')
        self.req_ctx.push()
        self.client = self.app.test_client()

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'secret secret'
        app.config['IMAGES_PATH'] = ['assets']
        self.images = Images(app)
        return app

    def assert200(self, res):
        self.assertEqual(res.status_code, 200)

