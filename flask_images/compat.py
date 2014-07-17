# -*- coding: utf-8 -*-
""" pythoncompat """

import sys

_ver = sys.version_info

#: Python 2.x
is_py2 = (_ver[0] == 2)

#: Python 3.x
is_py3 = (_ver[0] == 3)

if is_py2:
    from urllib import urlencode, quote
    from urllib2 import urlopen
    from urlparse import urlparse

    def iteritems(d):
        return d.iteritems()

    def itervalues(d):
        return d.itervalues()

    xrange = xrange

elif is_py3:
    from urllib.parse import urlencode, quote, urlparse
    from urllib.request import urlopen

    def iteritems(d):
        return iter(d.items())

    def itervalues(d):
        return iter(d.values())


