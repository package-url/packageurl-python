# -*- coding: utf-8 -*-
#
# Copyright (c) the purl authors
# SPDX-License-Identifier: MIT
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

import os
import re

try:
    from urlparse import urlparse  # Python 2
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import urlparse  # Python 3
    from urllib.parse import unquote_plus

from packageurl import PackageURL
from packageurl.contrib.route import Router
from packageurl.contrib.route import NoRouteAvailable


"""
This module helps build a PackageURL from an arbitrary URL.
This uses the a routing mechanism available in the route.py module.

In order to make it easy to use, it contains all the conversion functions
in this single Python script.
"""


purl_router = Router()


def url2purl(url):
    """
    Return a PackageURL inferred from the `url` string or None.
    """
    if url:
        try:
            return purl_router.process(url)
        except NoRouteAvailable:
            return


get_purl = url2purl


def purl_from_pattern(type_, pattern, url):
    url = unquote_plus(url)
    compiled_pattern = re.compile(pattern, re.VERBOSE)
    match = compiled_pattern.match(url)

    if match:
        purl_data = {
            field: value for field, value in match.groupdict().items()
            if field in PackageURL._fields
        }
        return PackageURL(type_, **purl_data)


def register_pattern(type_, pattern, router=purl_router):
    """
    Register a pattern with its type.
    """
    def endpoint(url):
        return purl_from_pattern(type_, pattern, url)
    router.append(pattern, endpoint)


def get_path_segments(url):
    """
    Return a list of path segments from a `url` string. This list may be empty.
    """
    path = unquote_plus(urlparse(url).path)
    segments = [seg for seg in path.split("/") if seg]

    if len(segments) <= 1:
        segments = []

    return segments


@purl_router.route('https?://registry.npmjs.*/.*',
                   'https?://registry.yarnpkg.com/.*',
                   'https?://(www\\.)?npmjs.*/package/.*',
                   'https?://(www\\.)?yarnpkg.com/package/.*')
def build_npm_purl(uri):
    # npm URLs are difficult to disambiguate with regex
    if '/package/' in uri:
        return build_npm_web_purl(uri)
    elif '/-/' in uri:
        return build_npm_download_purl(uri)
    else:
        return build_npm_api_purl(uri)


def build_npm_api_purl(uri):
    path = unquote_plus(urlparse(uri).path)
    segments = [seg for seg in path.split('/') if seg]

    if len(segments) != 2:
        return

    # /@invisionag/eslint-config-ivx
    if segments[0].startswith('@'):
        namespace = segments[0]
        name = segments[1]
        return PackageURL('npm', namespace, name)

    # /angular/1.6.6
    else:
        name = segments[0]
        version = segments[1]
        return PackageURL('npm', name=name, version=version)


def build_npm_download_purl(uri):
    path = unquote_plus(urlparse(uri).path)
    segments = [seg for seg in path.split('/') if seg and seg != '-']
    len_segments = len(segments)

    # /@invisionag/eslint-config-ivx/-/eslint-config-ivx-0.0.2.tgz
    if len_segments == 3:
        namespace, name, filename = segments

    # /automatta/-/automatta-0.0.1.tgz
    elif len_segments == 2:
        namespace = None
        name, filename = segments

    else:
        return

    base_filename, ext = os.path.splitext(filename)
    version = base_filename.split('-')[-1]

    return PackageURL('npm', namespace, name, version)


def build_npm_web_purl(uri):
    path = unquote_plus(urlparse(uri).path)
    if path.startswith('/package/'):
        path = path[9:]

    segments = [seg for seg in path.split('/') if seg]
    len_segments = len(segments)
    namespace = version = None

    # @angular/cli/v/10.1.2
    if len_segments == 4:
        namespace = segments[0]
        name = segments[1]
        version = segments[3]

    # express/v/4.17.1
    elif len_segments == 3:
        namespace = None
        name = segments[0]
        version = segments[2]

    # @angular/cli
    elif len_segments == 2:
        namespace = segments[0]
        name = segments[1]

    # express
    elif len_segments == 1 and len(segments) > 0 and segments[0][0] != '@':
        name = segments[0]

    else:
        return

    return PackageURL('npm', namespace, name, version)


@purl_router.route('https?://repo1.maven.org/maven2/.*',
                   'https?://central.maven.org/maven2/.*',
                   'maven-index://repo1.maven.org/.*')
def build_maven_purl(uri):
    path = unquote_plus(urlparse(uri).path)
    segments = [seg for seg in path.split('/') if seg and seg != 'maven2']

    if len(segments) < 3:
        return

    before_last_segment, last_segment = segments[-2:]
    has_filename = before_last_segment in last_segment

    filename = None
    if has_filename:
        filename = segments.pop()

    version = segments[-1]
    name = segments[-2]
    namespace = '.'.join(segments[:-2])
    qualifiers = {}

    if filename:
        name_version = '{}-{}'.format(name, version)
        _, _, classifier_ext = filename.rpartition(name_version)
        classifier, _, extension = classifier_ext.partition('.')
        if not extension:
            return

        qualifiers['classifier'] = classifier.strip('-')

        valid_types = ('aar', 'ear', 'mar', 'pom', 'rar', 'rpm',
                       'sar', 'tar.gz', 'war', 'zip')
        if extension in valid_types:
            qualifiers['type'] = extension

    return PackageURL('maven', namespace, name, version, qualifiers)


# https://rubygems.org/downloads/jwt-0.1.8.gem
rubygems_pattern = (
    r"^https?://rubygems.org/downloads/"
    r"(?P<name>.+)-(?P<version>.+)"
    r"(\.gem)$"
)

register_pattern('rubygems', rubygems_pattern)


# https://pypi.python.org/packages/source/a/anyjson/anyjson-0.3.3.tar.gz
pypi_pattern = (
    r"(?P<name>.+)-(?P<version>.+)"
    r"\.(zip|tar.gz|tar.bz2|.tgz)$"
)

# This pattern can be found in the following locations:
# - wheel.wheelfile.WHEEL_INFO_RE
# - distlib.wheel.FILENAME_RE
# - setuptools.wheel.WHEEL_NAME
# - pip._internal.wheel.Wheel.wheel_file_re
wheel_file_re = re.compile(
    r"^(?P<namever>(?P<name>.+?)-(?P<version>.*?))"
    r"((-(?P<build>\d[^-]*?))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)"
    r"\.whl)$",
    re.VERBOSE
)


@purl_router.route('https?://.+python.+org/packages/.*')
def build_pypi_purl(uri):
    path = unquote_plus(urlparse(uri).path)
    last_segment = path.split('/')[-1]

    # /wheel-0.29.0-py2.py3-none-any.whl
    if last_segment.endswith('.whl'):
        match = wheel_file_re.match(last_segment)
        if match:
            return PackageURL(
                'pypi',
                name=match.group('name'),
                version=match.group('version'),
            )

    return purl_from_pattern('pypi', pypi_pattern, last_segment)


# http://nuget.org/packages/EntityFramework/4.2.0.0
# https://www.nuget.org/api/v2/package/Newtonsoft.Json/11.0.1
nuget_www_pattern = (
    r"^https?://.*nuget.org/(api/v2/)?packages?/"
    r"(?P<name>.+)/"
    r"(?P<version>.+)$"
)

register_pattern('nuget', nuget_www_pattern)


# https://api.nuget.org/v3-flatcontainer/newtonsoft.json/10.0.1/newtonsoft.json.10.0.1.nupkg
nuget_api_pattern = (
    r"^https?://api.nuget.org/v3-flatcontainer/"
    r"(?P<name>.+)/"
    r"(?P<version>.+)/"
    r".*(nupkg)$"  # ends with "nupkg"
)

register_pattern('nuget', nuget_api_pattern)


# http://master.dl.sourceforge.net/project/libpng/zlib/1.2.3/zlib-1.2.3.tar.bz2
sourceforge_pattern = (
    r"^https?://.*sourceforge.net/project/"
    r"(?P<namespace>([^/]+))/"  # do not allow more "/" segments
    r"(?P<name>.+)/"
    r"(?P<version>[0-9\.]+)/"  # version restricted to digits and dots
    r"(?P=name)-(?P=version).*"  # {name}-{version} repeated in the filename
    r"[^/]$"  # not ending with "/"
)

register_pattern('sourceforge', sourceforge_pattern)


# https://crates.io/api/v1/crates/rand/0.7.2/download
cargo_pattern = (
    r"^https?://crates.io/api/v1/crates/"
    r"(?P<name>.+)/(?P<version>.+)"
    r"(\/download)$"
)

register_pattern('cargo', cargo_pattern)


# https://raw.githubusercontent.com/volatilityfoundation/dwarf2json/master/LICENSE.txt
github_raw_content_pattern = (
    r"https?://raw.githubusercontent.com/(?P<namespace>[^/]+)/(?P<name>[^/]+)/"
    r"(?P<version>[^/]+)/(?P<subpath>.*)$"
)

register_pattern('github', github_raw_content_pattern)


@purl_router.route("https?://api.github\\.com/repos/.*")
def build_github_api_purl(url):
    """
    Return a PackageURL object from GitHub API `url`.
    For example:
    https://api.github.com/repos/nexB/scancode-toolkit/commits/40593af0df6c8378d2b180324b97cb439fa11d66
    https://api.github.com/repos/nexB/scancode-toolkit/
    and returns a `PackageURL` object
    """
    segments = get_path_segments(url)

    if not(len(segments) >= 3):
        return
    namespace = segments[1]
    name = segments[2]
    version = None

    # https://api.github.com/repos/nexB/scancode-toolkit/
    if len(segments) == 4 and segments[3] != 'commits':
        version = segments[3]

    # https://api.github.com/repos/nexB/scancode-toolkit/commits/40593af0df6c8378d2b180324b97cb439fa11d66
    if len(segments) == 5 and segments[3] == "commits":
        version = segments[4]

    return PackageURL(
        type='github', namespace=namespace, name=name, version=version
    )


# https://codeload.github.com/nexB/scancode-toolkit/tar.gz/v3.1.1
github_codeload_pattern = (
    r"https?://codeload.github.com/"
    r"(?P<namespace>.+)/(?P<name>.+)/(zip|tar.gz|tar.bz2|tgz)/v?(?P<version>.+)$"
)

register_pattern('github', github_codeload_pattern)


@purl_router.route("https?://github\\.com/.*")
def build_github_purl(url):
    """
    Return a PackageURL object from GitHub `url`.
    For example:
    https://github.com/package-url/packageurl-js/tree/master/test/data or
    https://github.com/package-url/packageurl-js/tree/master or
    https://github.com/package-url/packageurl-js or
    https://github.com/nexB/scancode-toolkit/archive/v3.1.1.zip
    """
    # https://github.com/nexB/scancode-toolkit/archive/v3.1.1.zip
    archive_pattern = (
        r"https?://github.com/(?P<namespace>.+)/(?P<name>.+)"
        r"/archive/v?(?P<version>.+).(zip|tar.gz|tar.bz2|.tgz)"
    )

    # https://github.com/pypa/get-virtualenv/raw/20.0.31/public/virtualenv.pyz
    raw_pattern = (
        r"https?://github.com/(?P<namespace>.+)/(?P<name>.+)"
        r"/raw/v?(?P<version>[^/]+)/(?P<subpath>.*)$"
    )

    blob_pattern = (
        r"https?://github.com/"
        r"(?P<namespace>.+)/(?P<name>.+)/blob/(?P<version>[^/]+)/(?P<subpath>.*)$"
    )

    releases_download_pattern= (
        r"https?://github.com/(?P<namespace>.+)/(?P<name>.+)"
        r"/releases/download/(?P<version>[^/]+)/.*$"
    )

    for pattern in [archive_pattern, raw_pattern, blob_pattern, releases_download_pattern]:
        matches = re.search(pattern, url)
        qualifiers = {}
        if matches:
            if pattern != releases_download_pattern:
                return purl_from_pattern(type_='github', pattern=pattern, url=url)
            qualifiers['download_url'] = url
            purl = purl_from_pattern(type_='github', pattern=pattern, url=url)
            return PackageURL(
                type=purl.type,
                name=purl.name,
                namespace=purl.namespace,
                version=purl.version,
                qualifiers=qualifiers
            )

    segments = get_path_segments(url)
    if not segments:
        return

    namespace = segments[0]
    name = segments[1]
    version = None
    subpath = None

    # https://github.com/TG1999/fetchcode/master
    if len(segments) >= 3 and segments[2] != 'tree':
        version = segments[2]
        subpath = '/'.join(segments[3:])

    # https://github.com/TG1999/fetchcode/tree/master
    if len(segments) >= 4 and segments[2] == 'tree':
        version = segments[3]
        subpath = '/'.join(segments[4:])

    return PackageURL(
        type='github',
        namespace=namespace,
        name=name,
        version=version,
        subpath=subpath,
    )


@purl_router.route("https?://bitbucket\\.org/.*")
def build_bitbucket_purl(url):
    """
    Return a PackageURL object from BitBucket `url`.
    For example:
    https://bitbucket.org/TG1999/first_repo/src/master or
    https://bitbucket.org/TG1999/first_repo/src or
    https://bitbucket.org/TG1999/first_repo/src/master/new_folder
    """

    segments = get_path_segments(url)

    if not segments:
        return
    namespace = segments[0]
    name = segments[1]

    bitbucket_download_pattern = (
        r"https?://bitbucket.org/"
        r"(?P<namespace>.+)/(?P<name>.+)/downloads/(?P<version>.+).(zip|tar.gz|tar.bz2|.tgz)"
    )
    matches = re.search(bitbucket_download_pattern, url)

    qualifiers = {}
    if matches:
        qualifiers['download_url'] = url
        return PackageURL(
            type='bitbucket',
            namespace=namespace,
            name=name,
            qualifiers=qualifiers
        )

    version = None
    subpath = None

    # https://bitbucket.org/TG1999/first_repo/new_folder/
    if len(segments) >= 3 and segments[2] != 'src':
        version = segments[2]
        subpath = '/'.join(segments[3:])

    # https://bitbucket.org/TG1999/first_repo/src/master/new_folder/
    if len(segments) >= 4 and segments[2] == 'src':
        version = segments[3]
        subpath = '/'.join(segments[4:])

    return PackageURL(
        type='bitbucket',
        namespace=namespace,
        name=name,
        version=version,
        subpath=subpath,
    )


@purl_router.route("https?://gitlab\\.com/.*")
def build_gitlab_purl(url):
    """
    Return a PackageURL object from Gitlab `url`.
    For example:
    https://gitlab.com/TG1999/firebase/-/tree/1a122122/views
    https://gitlab.com/TG1999/firebase/-/tree
    https://gitlab.com/TG1999/firebase/-/master
    https://gitlab.com/tg1999/Firebase/-/tree/master
    """
    segments = get_path_segments(url)

    if not segments:
        return
    namespace = segments[0]
    name = segments[1]
    version = None
    subpath = None

    # https://gitlab.com/TG1999/firebase/master
    if (len(segments) >= 3) and segments[2] != '-' and segments[2] != 'tree':
        version = segments[2]
        subpath = '/'.join(segments[3:])

    # https://gitlab.com/TG1999/firebase/-/tree/master
    if len(segments) >= 5 and (segments[2] == '-' and segments[3] == 'tree'):
        version = segments[4]
        subpath = '/'.join(segments[5:])

    return PackageURL(
        type='gitlab',
        namespace=namespace,
        name=name,
        version=version,
        subpath=subpath,
    )


# https://hackage.haskell.org/package/a50-0.5/a50-0.5.tar.gz
hackage_pattern = (
    r"^https?://hackage.haskell.org/package/"
    r"(?P<name>.+)-(?P<version>.+)/"
    r"(?P=name)-(?P=version).*"
    r"[^/]$"
)

register_pattern('hackage', hackage_pattern)
