
from distutils.core import setup

setup(
    name='Flask-Images',
    version='0.1.1',
    description='Dynamic image resizing for Flask.',
    url='http://github.com/mikeboers/Flask-Images',
        
    author='Mike Boers',
    author_email='flask_imgsizer@mikeboers.com',
    license='BSD-3',
    
    install_requires='''
        PIL
    ''',
    
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
    
)