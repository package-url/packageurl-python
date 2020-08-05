# -*- coding: utf-8 -*-
#
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
from collections import OrderedDict
import string

# Python 2 and 3 support
try:
    # Python 2
    from urlparse import urlsplit as _urlsplit
    from urllib import quote as _percent_quote
    from urllib import unquote as _percent_unquote
except ImportError:
    # Python 3
    from urllib.parse import urlsplit as _urlsplit
    from urllib.parse import quote as _percent_quote
    from urllib.parse import unquote as _percent_unquote

# Python 2 and 3 support
try:
    # Python 2
    unicode
    basestring = basestring  # NOQA
    bytes = str  # NOQA
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA
    basestring = (bytes, str,)  # NOQA

"""
A purl (aka. Package URL) implementation as specified at:
https://github.com/package-url/purl-spec
"""


def quote(s):
    """
    Return a percent-encoded unicode string, except for colon :, given an `s`
    byte or unicode string.
    """
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    quoted = _percent_quote(s)
    if not isinstance(quoted, unicode):
        quoted = quoted.decode('utf-8')
    quoted = quoted.replace('%3A', ':')
    return quoted


def unquote(s):
    """
    Return a percent-decoded unicode string, given an `s` byte or unicode
    string.
    """
    unquoted = _percent_unquote(s)
    if not isinstance(unquoted, unicode):
        unquoted = unquoted .decode('utf-8')
    return unquoted


def get_quoter(encode=True):
    """
    Return quoting callable given an `encode` tri-boolean (True, False or None)
    """
    if encode is True:
        return quote
    elif encode is False:
        return unquote
    elif encode is None:
        return lambda x: x


def normalize_type(type, encode=True):  # NOQA
    if not type:
        return
    if not isinstance(type, unicode):
        type = type.decode('utf-8')  # NOQA

    quoter = get_quoter(encode)
    type = quoter(type)  # NOQA
    return type.strip().lower() or None


def normalize_namespace(namespace, ptype, encode=True):  # NOQA
    if not namespace:
        return
    if not isinstance(namespace, unicode):
        namespace = namespace.decode('utf-8')

    namespace = namespace.strip().strip('/')
    if ptype in ('bitbucket', 'github', 'pypi', 'gitlab'):
        namespace = namespace.lower()
    segments = [seg for seg in namespace.split('/') if seg.strip()]
    segments = map(get_quoter(encode), segments)
    return '/'.join(segments) or None


def normalize_name(name, ptype, encode=True):  # NOQA
    if not name:
        return
    if not isinstance(name, unicode):
        name = name.decode('utf-8')

    quoter = get_quoter(encode)
    name = quoter(name)
    name = name.strip().strip('/')
    if ptype in ('bitbucket', 'github', 'pypi', 'gitlab'):
        name = name.lower()
    if ptype in ('pypi',):
        name = name.replace('_', '-')
    return name or None


def normalize_version(version, encode=True):  # NOQA
    if not version:
        return
    if not isinstance(version, unicode):
        version = version.decode('utf-8')

    quoter = get_quoter(encode)
    version = quoter(version.strip())
    return version or None


def normalize_qualifiers(qualifiers, encode=True):  # NOQA
    """
    Return normalized `qualifiers` as a mapping (or as a string if `encode` is
    True). The `qualifiers` arg is either a mapping or a string.
    Always return a mapping if decode is True (and never None).
    Raise ValueError on errors.
    """
    if not qualifiers:
        return None if encode else OrderedDict()

    if isinstance(qualifiers, basestring):
        if not isinstance(qualifiers, unicode):
            qualifiers = qualifiers.decode('utf-8')
        # decode string to list of tuples
        qualifiers = qualifiers.split('&')
        if not all('=' in kv for kv in qualifiers):
            raise ValueError(
                'Invalid qualifier. '
                'Must be a string of key=value pairs:{}'.format(repr(qualifiers)))
        qualifiers = [kv.partition('=') for kv in qualifiers]
        qualifiers = [(k, v) for k, _, v in qualifiers]
    elif isinstance(qualifiers, dict):
        qualifiers = qualifiers.items()
    else:
        raise ValueError(
            'Invalid qualifier. '
            'Must be a string or dict:{}'.format(repr(qualifiers)))

    quoter = get_quoter(encode)
    qualifiers = {k.strip().lower(): quoter(v)
        for k, v in qualifiers if k and k.strip() and v and v.strip()}

    valid_chars = string.ascii_letters + string.digits + '.-_'
    for key in qualifiers:
        if not key:
            raise ValueError('A qualifier key cannot be empty')

        if '%' in key:
            raise ValueError(
                "A qualifier key cannot be percent encoded: {}".format(repr(key)))

        if ' ' in key:
            raise ValueError(
                "A qualifier key cannot contain spaces: {}".format(repr(key)))

        if not all(c in valid_chars for c in key):
            raise ValueError(
                "A qualifier key must be composed only of ASCII letters and numbers"
                "period, dash and underscore: {}".format(repr(key)))

        if key[0] in string.digits:
            raise ValueError(
                "A qualifier key cannot start with a number: {}".format(repr(key)))

    qualifiers = sorted(qualifiers.items())
    qualifiers = OrderedDict(qualifiers)
    if encode:
        qualifiers = ['{}={}'.format(k, v) for k, v in qualifiers.items()]
        qualifiers = '&'.join(qualifiers)
        return qualifiers or None
    else:
        return qualifiers or {}


def normalize_subpath(subpath, encode=True):  # NOQA
    if not subpath:
        return None
    if not isinstance(subpath, unicode):
        subpath = subpath.decode('utf-8')

    quoter = get_quoter(encode)
    segments = subpath.split('/')
    segments = [quoter(s) for s in segments if s.strip() and s not in ('.', '..')]
    subpath = '/'.join(segments)
    return subpath or None


def normalize(type, namespace, name, version, qualifiers, subpath, encode=True):  # NOQA
    """
    Return normalized purl components
    """
    type = normalize_type(type, encode)  # NOQA
    namespace = normalize_namespace(namespace, type, encode)
    name = normalize_name(name, type, encode)
    version = normalize_version(version, encode)
    qualifiers = normalize_qualifiers(qualifiers, encode)
    subpath = normalize_subpath(subpath, encode)
    return type, namespace, name, version, qualifiers, subpath


_components = ['type', 'namespace', 'name', 'version', 'qualifiers', 'subpath']


class PackageURL(namedtuple('PackageURL', _components)):
    """
    A purl is a package URL as defined at
    https://github.com/package-url/purl-spec
    """

    def __new__(self, type=None, namespace=None, name=None,  # NOQA
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

        if qualifiers and not isinstance(qualifiers, (basestring, dict,)):
            raise ValueError('Invalid purl: {} argument must be a dict or a string: {}.'
                             .format('qualifiers', repr(qualifiers)))

        type, namespace, name, version, qualifiers, subpath = normalize(# NOQA
            type, namespace, name, version, qualifiers, subpath, encode=None)

        return super(PackageURL, self).__new__(PackageURL, type=type,
            namespace=namespace, name=name, version=version,
            qualifiers=qualifiers, subpath=subpath)

    def __str__(self, *args, **kwargs):
        return self.to_string()

    def __hash__(self):
        return hash(self.to_string())

    def to_dict(self, encode=False, empty=None):
        """
        Return an ordered dict of purl components as {key: value}.
        If `encode` is True, then "qualifiers" are encoded as a normalized
        string. Otherwise, qualifiers is a mapping.
        You can provide a value for `empty` to be used in place of default None.
        """
        data = self._asdict()
        if encode:
            data['qualifiers'] = normalize_qualifiers(self.qualifiers, encode=encode)

        for field, value in data.items():
            data[field] = value or empty

        return data

    def to_string(self):
        """
        Return a purl string built from components.
        """
        type, namespace, name, version, qualifiers, subpath = normalize(# NOQA
            self.type, self.namespace, self.name, self.version,
            self.qualifiers, self.subpath,
            encode=True
        )

        purl = ['pkg:', type, '/']

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

        scheme, sep, remainder = purl.partition(':')
        if not sep or scheme != 'pkg':
            raise ValueError(
                'purl is missing the required '
                '"pkg" scheme component: {}.'.format(repr(purl)))

        # this strip '/, // and /// as possible in :// or :///
        remainder = remainder.strip().lstrip('/')

        type, sep, remainder = remainder.partition('/')  # NOQA
        if not type or not sep:
            raise ValueError(
                'purl is missing the required '
                'type component: {}.'.format(repr(purl)))

        scheme, authority, path, qualifiers, subpath = _urlsplit(
            url=remainder, scheme='', allow_fragments=True)

        if scheme or authority:
            msg = ('Invalid purl {} cannot contain a "user:pass@host:port" '
                   'URL Authority component: {}.')
            raise ValueError(msg.format(
                repr(purl), repr(authority)
                                        ))

        path = path.lstrip('/')
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

        type, namespace, name, version, qualifiers, subpath = normalize(# NOQA
            type, namespace, name, version, qualifiers, subpath,
            encode=False
        )

        return PackageURL(type, namespace, name, version, qualifiers, subpath)
