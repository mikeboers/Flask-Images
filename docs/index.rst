Flask-Images
============

Flask-Images is a Flask extension that provides dynamic image resizing for your application.

This extension adds a :func:`resized_img_src` function (and :ref:`others <api>`) to the template context, which creates a URL to dynamically resize an image. This function takes either a path to a local image (either absolute, or relative to the :data:`IMAGES_PATH`) or an URL to a remote image, and returns a URL that will serve a resized version on demand.

Alternatively, this responds to ``url_for('images', filename='...', **kw)`` to ease transition from Flask's static files.

Try `the demo app`_ (`demo source`_), and see `with an example image`_.

.. _the demo app: https://flask-images.herokuapp.com
.. _demo source: https://github.com/mikeboers/Flask-Images/blob/master/demo
.. _with an example image: https://flask-images.herokuapp.com/demo?url=https%3A%2F%2Ffarm4.staticflickr.com%2F3540%2F5753968652_a28184e5fb.jpg


Usage
=====

For example, within a Jinja template:

::

    <img src="{{resized_img_src('logo.png', width=100)}}" />
    <img src="{{resized_img_src('photo.jpeg', width=400, height=300, mode='crop', quality=95)}}" />
    OR
    <img src="{{url_for('images', filename='logo.png', width=100)}}" />
    <img src="{{url_for('images.crop', filename='photo.jpeg', width=400, height=300, quality=95)}}" />


Behaviour is specified with keyword arguments:

- ``mode``: one of ``'fit'``, ``'crop'``, ``'pad'``, or ``None``:

    - ``'fit'``: as large as possible while fitting within the given dimensions;

    - ``'crop'``: as large as possible while fitting into the given aspect ratio,
      e.g.: |crop-example|

    - ``'pad'``: as large as possible while fitting within the given dimensions,
      and padding to thegiven dimensions with a background colour;

    - ``None``: resize to the specific dimensions without preserving aspect ratio.

- ``width`` and ``height``: pixel dimensions; at least one is required, but
  both are required for most modes.

- ``format``: The file extension to use (as accepted by PIL); defaults to the
  input image's extension.

- ``quality``: JPEG quality; defaults to `75`.

- ``background``: Background colour for padding; currently only accepts
  `'white'` and defaults to black.

- ``enlarge``: TBD.

- ``transform``: TBD.

- ``hidpi`` and ``hidpi_quality``: TBD.


.. |crop-example| image:: https://flask-images.herokuapp.com/imgsizer/_?h=50&m=crop&u=https%3A%2F%2Ffarm4.staticflickr.com%2F3540%2F5753968652_a28184e5fb.jpg&w=400&x=&s=jXZSUvAWKkXotNOUi0Ap1ceWcdE

Installation
------------

From PyPI::

    pip install Flask-Images

From GitHub::

    git clone git@github.com:mikeboers/Flask-Images
    pip install -e Flask-Images


Usage
-----

All you must do is make sure your app has a secret key, then create the
:class:`Images` object::

    app = Flask(__name__)
    app.secret_key = 'monkey'
    images = Images(app)


Now, use either the :func:`resized_img_src` function in your templates, or the
``images.<mode>`` routes in ``url_for``.

Can be used within Python after import::

    from flask.ext.images import resized_img_src



Configuration
-------------

Configure Flask-Images via the following keys in the Flask config:

- .. data:: IMAGES_URL

    The url to mount Flask-Images to; defaults to ``'/imgsizer'``.

- .. data:: IMAGES_NME

    The name of the registered endpoint used in url_for.

- .. data:: IMAGES_PATH

    A list of paths to search for images (relative to ``app.root_path``); e.g. ``['static/uploads']``

- .. data:: IMAGES_CACHE

    Where to store resized images; defaults to ``'/tmp/flask-images'``.

- .. data:: IMAGES_MAX_AGE

    How long to tell the browser to cache missing results; defaults to ``3600``. Usually, we will set a max age of one year, and cache bust via the modification time of the source image.




..
    Contents:
    .. toctree::
       :maxdepth: 2
    Indices and tables
    ==================
    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

