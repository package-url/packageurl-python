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

# Visit https://github.com/package-url/purl-python for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from urllib import quote
from urlparse import unquote


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


class PackageURL(namedtuple('PackageURL',
    ['type', 'namespace', 'name', 'version', 'qualifiers', 'subpath'])):
    """
    A purl is a package URL as defined at
    https://github.com/package-url/purl-spec.
    """
    def __new__(self, type=None, namespace=None, name=None,
                version=None, qualifiers=None, subpath=None):

        required = dict(type=type, namespace=namespace, name=name)
        for key, value in required.items():
            if value:
                continue
            raise ValueError('Invalid purl: {} is a required argument.'
                             .format(key))

        strings = dict(type=type, namespace=namespace, name=name,
                       version=version, subpath=subpath)
        for key, value in strings.items():
            if not value or isinstance(value, basestring):
                continue
            raise ValueError('Invalid purl: {} argument must be a string: {}'
                             .format(key, repr(value)))

        if qualifiers and not isinstance(qualifiers, dict):
            raise ValueError('Invalid purl: {} argument must be a dict: {}'
                             .format('qualifiers', repr(qualifiers)))

        return super(PackageURL, self).__new__(PackageURL, type=type,
            namespace=namespace or None, name=name, version=version or None,
            qualifiers=qualifiers or None, subpath=subpath or None)

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
        purl = []
        if self.type:
            purl.append(self.type.strip().lower())
            purl.append(':')

        if self.namespace:
            namespace = self.namespace.strip().strip('/')
            if self.type and self.type in ('bitbucket', 'github',):
                namespace = namespace.lower()
            segments = namespace.split('/')
            segments = [seg for seg in segments if seg and seg.strip()]
            if segments:
                subpaths = map(quote, segments)
                purl.append('/'.join(segments))
                purl.append('/')

        name = self.name.strip().strip('/')
        if self.type and self.type in ('bitbucket', 'github', 'pypi',):
            name = name.lower()
        if self.type and self.type in ('pypi',):
            name = name.replace('_', '-')
        name = quote(name)
        purl.append(name)

        if self.version:
            purl.append('@')
            purl.append(quote(self.version.strip()))

        if self.qualifiers:
            quals = {
                k.strip().lower(): quote(v) for k, v in self.qualifiers.items()
                if k and k.strip() and v and v.strip()
            }
            quals = sorted(quals.items())
            quals = ['{}={}'.format(k, v) for k, v in quals]
            quals = '&'.join(quals)
            if quals:
                purl.append('?')
                purl.append(quals)

        if self.subpath:
            purl.append('#')
            subpaths = self.subpath.split('/')
            subpaths = [sp for sp in subpaths if sp and sp.strip()
                        and sp not in ('.', '..')]
            if subpaths:
                subpaths = map(quote, subpaths)
                purl.append('/'.join(subpaths))

        return ''.join(purl)

    @classmethod
    def from_string(cls, purl, require_version=False):
        """
        Return a PackageURL object parsed from a string.
        Raise ValueError on errors.
        Optionally raise ValuError if require_version is True and no version
        is provided.
        """
        if (not purl or not isinstance(purl, basestring)
            or not purl.strip()):
            raise ValueError('A purl string argument is required.')

        purl = purl.strip().strip('/')

        head, sep, subpath = purl.rpartition('#')
        if sep:
            if subpath:
                subpaths = subpath.split('/')
                subpaths = [
                    sp for sp in subpaths
                    if sp and sp.strip() and sp not in ('.', '..')
                ]
                if subpaths:
                    subpaths = map(unquote, subpaths)
                    subpath = '/'.join(subpaths)
            subpath = subpath or None
        else:
            head = subpath
            subpath = None

        head, sep, qualifiers = head.rpartition('?')
        if sep:
            if qualifiers:
                qualifiers = qualifiers.split('&')
                qualifiers = [kv.partition('=') for kv in qualifiers]
                qualifiers = {
                    k.strip().lower(): unquote(v)
                    for k, _, v in qualifiers
                    if k and k.strip() and v and v.strip()
                }
            qualifiers = qualifiers or None
        else:
            head = qualifiers
            qualifiers = None

        head, sep, version = head.rpartition('@')
        if sep:
            if version and version.strip():
                version = unquote(version).strip()
            version = version or None
        else:
            head = version
            version = None

        if require_version and not version:
            raise ValueError(
                'purl is missing the required '
                'version component: {}'.format(repr(purl)))

        typ, sep, ns_name = head.partition(':')
        typ = typ.strip().lower()
        if not typ or not sep:
            raise ValueError(
                'purl is missing the required '
                'type component: {}'.format(repr(purl)))

        ns_name = ns_name.strip().strip('/')
        ns_name = ns_name.split('/')
        ns_name = [unquote(seg).strip() for seg in ns_name
                   if seg and seg.strip()]
        namespace = ''
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

        namespace = namespace or None


        return PackageURL(typ, namespace, name, version, qualifiers, subpath)
