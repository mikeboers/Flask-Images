import sys
import os

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'


project = u'Flask-Images'
copyright = u'2014, Mike Boers'

version = '2.1'
release = '2.1.1'


exclude_patterns = ['_build']

pygments_style = 'sphinx'


sys.path.append(os.path.abspath('_themes'))
html_theme_path = ['_themes']
html_theme = 'flask_small'
html_theme_options = {
    'index_logo': '',
    'github_fork': 'mikeboers/Flask-Images',
}

html_static_path = ['_static']
