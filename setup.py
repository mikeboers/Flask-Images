try:
    import multiprocessing
except ImportError:
    pass


from setuptools import setup

setup(
    name='Flask-Images',
    version='1.1.5',
    description='Dynamic image resizing for Flask.',
    url='http://github.com/mikeboers/Flask-Images',
        
    author='Mike Boers',
    author_email='flask_images@mikeboers.com',
    license='BSD-3',

    py_modules=['flask_images'],

    install_requires=[
        'Flask',

        # We need either PIL, or the newer Pillow. Since this may induce some
        # dependency madness, I have created a module that should flatten that
        # out. See: https://github.com/mikeboers/Flask-Images/pull/10 for more.
        'PillowCase',
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    tests_require=[
        'Flask-Testing',
        'nose>=1.0',
    ],
    test_suite='nose.collector',

    zip_safe=False,
)
