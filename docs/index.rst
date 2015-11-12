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

    - ``'crop'``: as large as possible while fitting into the given aspect ratio;

    - ``'pad'``: as large as possible while fitting within the given dimensions,
      and padding to thegiven dimensions with a background colour;

    - ``None``: resize to the specific dimensions without preserving aspect ratio.

- ``width`` and ``height``: pixel dimensions; at least one is required, but
  both are required for most modes.

- ``format``: The file extension to use (`as accepted by PIL <http://effbot.org/imagingbook/formats.htm>`_ (or `Pillow <https://pillow.readthedocs.org/>`_)); defaults to the
  input image's extension.

- ``quality``: JPEG quality (no effect on non-JPEG images); defaults to `75`.

- ``background``: Background colour for ``pad`` mode. Expressed via via
  CSS names (e.g. ``"black"``), hexadecimal (e.g. ``"#ff8800"``), or
  `anything else accepted by PIL <http://effbot.org/imagingbook/imagecolor.htm>`_.
  Defaults to ``"black"``.

- ``enlarge``: Should the image be enlarged to satisfy requested dimensions? E.g.
  If you specify ``mode="crop", width=400, height=400, enlarge=True``, but the
  image is smaller than 400x400, it will be enlarged to fill that requested size. 
  Defaults to ``False``.

- ``transform``: A space-or-comma separated list of a transform method and its values,
  `as understood by PIL <http://effbot.org/imagingbook/image.htm#tag-Image.Image.transform>`_:
  E.g. ``"name,width,height,v0,...,vn"``. Width and height of zero will use the image's
  native dimensions. Percent values are interpreted as relative to the real size of the appropriate axis.
  E.g.: ``transform="EXTENT,50%,50%,25%,25%,75%,75%"`` will crop the center out of the image.

- ``sharpen``: Space-or-comma separated parameters for an `unsharp mask <https://en.wikipedia.org/wiki/Unsharp_masking>`_,
  `as understood by Pillow <http://pillow.readthedocs.org/en/latest/reference/ImageFilter.html#PIL.ImageFilter.UnsharpMask>`_.
  E.g. ``sharpen="0.3,250,2"``.

- ``hidpi`` and ``hidpi_quality``: A resolution scale for HiDPI or "retina" displays.
  Requested dimensions will be multiplied by ``hidpi`` if the image can support it
  without enlargement. Any other kwargs matching ``hi_dpi_*`` will also take effect,
  e.g. for reducing JPEG quality of HiDPI images, e.g.: ``hi_dpi=2, quality=90, hidpi_quality=60``.
  This is only useful with :func:`resized_img_attrs` or :func:`resized_img_tag`.



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

- .. data:: IMAGES_NAME

    The name of the registered endpoint used in url_for.

- .. data:: IMAGES_PATH

    A list of paths to search for images (relative to ``app.root_path``); e.g. ``['static/uploads']``

- .. data:: IMAGES_CACHE

    Where to store resized images; defaults to ``'/tmp/flask-images'``.

- .. data:: IMAGES_MAX_AGE

    How long to tell the browser to cache missing results; defaults to ``3600``. Usually, we will set a max age of one year, and cache bust via the modification time of the source image.


.. _api:

Template Functions
------------------

.. function:: resized_img_src(filename, **kw)

    Get the URL that will render into a resized image.

.. function:: resized_img_size(filename, **kw)

    Get a :class:`flask.ext.images.size.Size` object for the given parameters.

.. function:: resized_img_attrs(filename, **kw)

    Get a ``dict`` of attributes for an HTML ``<img />`` tag.

.. function:: resized_img_tag(filename, **kw)

    Get a ``str`` HTML ``<img />`` tag.

..
    Contents:
    .. toctree::
       :maxdepth: 2
    Indices and tables
    ==================
    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

