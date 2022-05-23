from setuptools import setup

setup(

    name='Flask-Image-Resizer',
    version='3.0.3',
    description='Dynamic image resizing for Flask.',
    url='http://github.com/mikeboers/Flask-Images',
        
    author='Mike Boers',
    author_email='flask_images@mikeboers.com',
    license='BSD-3',

    packages=['flask_image_resizer'],

    install_requires=[

        'Flask>=0.9',
        'itsdangerous', # For Flask v0.9

        'Pillow',
        
        'six',

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
        'nose>=1.0',
    ],
    test_suite='nose.collector',

    zip_safe=False,
)
