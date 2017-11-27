# Copyright (c) the purl authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Visit https://github.com/package-url/packageurl-python for support and
# download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

# Python 2 and 3 support
try:
    # Python 2
    from urlparse import urlsplit
    from urllib import quote as percent_quote
    from urllib import unquote as percent_unquote
except ImportError:
    # Python 3
    from urllib.parse import urlsplit
    from urllib.parse import quote as percent_quote
    from urllib.parse import unquote as percent_unquote

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str = unicode
    basestring = basestring
except NameError:
    # Python 3
    unicode = str
    basestring = (bytes, str,)


"""
A purl (aka. Package URL) implementation as specified at:
https://github.com/package-url/purl-spec
"""


def quote(s):
    """
    Percent-encode a string, except for colon :
    """
    quoted = percent_quote(s)
    return quoted.replace('%3A', ':')


def normalize(type, namespace, name, version, qualifiers, subpath, encode=True):
    """
    Return normalized purl components.
    """
    if encode is True:
        quoting = quote
    elif encode is False:
        quoting = percent_unquote
    elif encode is None:
        quoting = lambda x: x

    if type:
        type = type.strip().lower()

    if namespace:
        namespace = namespace.strip().strip('/')
        if type and type in ('bitbucket', 'github', 'pypi'):
            namespace = namespace.lower()
        segments = namespace.split('/')
        segments = [seg for seg in segments if seg and seg.strip()]
        segments = map(quoting, segments)
        namespace = '/'.join(segments)

    if name:
        name = name.strip().strip('/')
        if type in ('bitbucket', 'github', 'pypi',):
            name = name.lower()
        if type in ('pypi',):
            name = name.replace('_', '-')
        name = quoting(name)

    name = name or None

    if version:
        version = quoting(version.strip())

    if qualifiers:
        if isinstance(qualifiers, basestring):
            # decode string to dict
            qualifiers = qualifiers.split('&')
            qualifiers = [kv.partition('=') for kv in qualifiers]
            if qualifiers:
                qualifiers = [(k, v) for k, _, v in qualifiers]
            else:
                qualifiers = []
        elif isinstance(qualifiers, dict):
            qualifiers = qualifiers.items()
        else:
            raise ValueError(
                'Invalid qualifier. '
                'Must be a string or dict:{}'.format(repr(qualifiers)))

        if qualifiers:
            qualifiers = {
                k.strip().lower(): quoting(v)
                for k, v in qualifiers
                if k and k.strip() and v and v.strip()
            }

            if qualifiers and encode is True:
                # encode dict as a string
                qualifiers = sorted(qualifiers.items())
                qualifiers = ['{}={}'.format(k, v) for k, v in qualifiers]
                qualifiers = '&'.join(qualifiers)

    if subpath:
        segments = subpath.split('/')
        segments = [quoting(s) for s in segments if s and s.strip()
                    and s not in ('.', '..')]
        subpath = '/'.join(segments)

    return (type or None, namespace or None, name or None, version or None,
            qualifiers or None, subpath or None)


_components = ['type', 'namespace', 'name', 'version', 'qualifiers', 'subpath']
class PackageURL(namedtuple('PackageURL', _components)):
    """
    A purl is a package URL as defined at
    https://github.com/package-url/purl-spec
    """

    def __new__(self, type=None, namespace=None, name=None,
                version=None, qualifiers=None, subpath=None):

        required = dict(type=type, name=name)
        for key, value in required.items():
            if value:
                continue
            raise ValueError('Invalid purl: {} is a required argument.'
                             .format(key))

        strings = dict(type=type, namespace=namespace, name=name,
                       version=version, subpath=subpath)
        for key, value in strings.items():
            if value and isinstance(value, basestring) or not value:
                continue
            raise ValueError('Invalid purl: {} argument must be a string: {}.'
                             .format(key, repr(value)))

        if qualifiers and not isinstance(qualifiers, dict):
            raise ValueError('Invalid purl: {} argument must be a dict: {}.'
                             .format('qualifiers', repr(qualifiers)))

        type, namespace, name, version, qualifiers, subpath = normalize(
            type, namespace, name, version, qualifiers, subpath, encode=None)

        return super(PackageURL, self).__new__(PackageURL, type=type,
            namespace=namespace, name=name, version=version,
            qualifiers=qualifiers, subpath=subpath)

    def __str__(self, *args, **kwargs):
        return self.to_string()

    def to_dict(self):
        """
        Return a dict of purl components.
        """
        return self._asdict()

    def to_string(self):
        """
        Return a purl string built from components.
        """
        type, namespace, name, version, qualifiers, subpath = normalize(
            self.type, self.namespace, self.name, self.version,
            self.qualifiers, self.subpath,
            encode=True
        )

        purl = [type, ':']

        if namespace:
            purl.append(namespace)
            purl.append('/')

        purl.append(name)

        if version:
            purl.append('@')
            purl.append(version)

        if qualifiers:
            purl.append('?')
            purl.append(qualifiers)

        if subpath:
            purl.append('#')
            purl.append(subpath)

        return ''.join(purl)

    @classmethod
    def from_string(cls, purl):
        """
        Return a PackageURL object parsed from a string.
        Raise ValueError on errors.
        """
        if (not purl or not isinstance(purl, basestring)
            or not purl.strip()):
            raise ValueError('A purl string argument is required.')

        type, sep, remainder = purl.partition(':')
        if not type or not sep:
            raise ValueError(
                'purl is missing the required '
                'type component: {}.'.format(repr(purl)))

        # this strip '/, // and /// as possible in :// or :///
        remainder = remainder.strip().strip('/')
        cleaned = '{}:{}'.format(type, remainder)

        type, authority, path, qualifiers, subpath = urlsplit(
            url=cleaned, scheme=type, allow_fragments=True)

        if authority:
            raise ValueError(
                'Invalid purl {} cannot contain a "user:pass@host:port" URL Authority '
                'component: {}.'.format(repr(purl)), repr(netloc))

        remainder, sep, version = path.rpartition('@')
        if not sep:
            remainder = version
            version = None

        ns_name = remainder.strip().strip('/')
        ns_name = ns_name.split('/')
        ns_name = [seg for seg in ns_name if seg and seg.strip()]
        namespace = ''
        name = ''
        if len(ns_name) > 1:
            name = ns_name[-1]
            ns = ns_name[0:-1]
            namespace = '/'.join(ns)
        elif len(ns_name) == 1:
            name = ns_name[0]

        if not name:
            raise ValueError(
                'purl is missing the required '
                'name component: {}'.format(repr(purl)))

        type, namespace, name, version, qualifiers, subpath = normalize(
            type, namespace, name, version, qualifiers, subpath,
            encode=False
        )

        return PackageURL(type, namespace, name, version, qualifiers, subpath)
