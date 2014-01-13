Flask-Images
============

[![Build Status](https://travis-ci.org/mikeboers/Flask-Images.png?branch=master)](https://travis-ci.org/mikeboers/Flask-Images)

Dynamic image resizing for Flask.

This extension adds a `resized_img_src` function to the template context, which creates a URL to dynamically resize an image. This function takes either a path to a local image (either absolute, or relative to the `IMAGES_PATH`) or an URL to a remote image, and returns a URL that will serve a resized version on demand.

Alternatively, this responds to `url_for('images', filename='...', **kw)` to ease transition from Flask's static files.

Try [the demo app][demo_root] ([source][demo_src]), and see [with an example image][demo_demo].

[demo_root]: https://flask-images.herokuapp.com
[demo_demo]: https://flask-images.herokuapp.com/demo?url=https%3A%2F%2Ffarm4.staticflickr.com%2F3540%2F5753968652_a28184e5fb.jpg
[demo_src]: https://github.com/mikeboers/Flask-Images/blob/master/demo


For example:

~~~
<img src="{{resized_img_src('logo.png', width=100)}}" />
<img src="{{resized_img_src('photo.jpeg', width=400, height=300, mode='crop', quality=95)}}" />
OR
<img src="{{url_for('images', filename='logo.png', width=100)}}" />
<img src="{{url_for('images.crop', filename='photo.jpeg', width=400, height=300, quality=95)}}" />
~~~

Specify behaviour with keyword arguments:

- `mode`: one of `'fit'`, `'crop'`, `'pad'`, or `None`:
    - `'fit'`: as large as possible while fitting within the given dimensions;
    - `'crop'`: as large as possible while fitting into the given aspect ratio;
    - `'pad'`: as large as possible while fitting within the given dimensions, and padding to the given dimensions with a background colour;
    - `None`: resize to the specific dimensions without preserving aspect ratio.
- `width` and `height`: pixel dimensions; at least one is required.
- `format`: The file extension to use (as accepted by PIL); defaults to the input image's extension.
- `quality`: JPEG quality; defaults to `75`.
- `background`: Background colour for padding; currently only accepts `'white'` and defaults to black.


Installation
------------

From PyPI:

~~~bash
pip install Flask-Images
~~~

From GitHub:

~~~bash
git clone git@github.com:mikeboers/Flask-Images
pip install -e Flask-Images
~~~


Usage
-----

All you must do is make sure your app has a secret key, then create the `Images` object:

~~~python
app = Flask(__name__)
app.secret_key = 'monkey'
images = Images(app)
~~~

Now, use either the `resized_img_src` function in your templates, or the `images.<mode>` routes in `url_for`.


Configuration
-------------

Configure Flask-Images via the following keys in the Flask config:

- `IMAGES_URL`: The url to mount Flask-Images to; defaults to `'/imgsizer'`.
- `IMAGES_NAME`: The name of the registered endpoint.
- `IMAGES_PATH`: The paths to search relative to `app.root_path` for images.
- `IMAGES_CACHE`: Where to store resized images; defaults to `'/tmp/flask-images'`.
- `IMAGES_MAX_AGE`: How long to tell the browser to cache missing results; defaults to `3600`. Usually, we will set a max age of one year, and cache bust via the modification time of the source image.

