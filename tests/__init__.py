from urlparse import urlsplit, parse_qsl

from flask import Flask, url_for, render_template_string
from flask.ext.testing import TestCase as BaseTestCase
from flask.ext.images import Images


class TestCase(BaseTestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'secret secret'
        app.config['IMAGES_PATH'] = ['assets']
        self.images = Images(app)
        return app

