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

from packageurl import PackageURL
from packageurl.contrib.route import Router
from packageurl.contrib.route import NoRouteAvailable


router = Router()


def purl2url(purl):
    """
    Return a URL inferred from the `purl` string
    """
    if purl:
        try:
            return router.process(purl)
        except NoRouteAvailable:
            return


@router.route("pkg:cargo/.*")
def build_cargo_download_url(purl):
    """
    Return a cargo download URL `url` from a the `purl` string
    """
    purl_data = PackageURL.from_string(purl)

    name = purl_data.name
    version = purl_data.version

    if not (name and version):
        return

    return "https://crates.io/api/v1/crates/{name}/{version}/download".format(
        name=name, version=version
    )


@router.route("pkg:bitbucket/.*")
def build_bitbucket_homepage_url(purl):
    """
    Return a bitbucket homepage URL `url` from a the `purl` string
    """
    purl_data = PackageURL.from_string(purl)

    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version
    subpath = purl_data.subpath

    if not (name and namespace):
        return

    url = "https://bitbucket.org/{namespace}/{name}".format(
        namespace=namespace, name=name
    )
    if version:
        url = "{url}/src/{version}".format(url=url, version=version)

    if subpath:
        url = "{url}/{subpath}".format(url=url, subpath=subpath)

    return url


@router.route("pkg:github/.*")
def build_github_homepage_url(purl):
    """
    Return a github homepage URL `url` from a the `purl` string
    """
    purl_data = PackageURL.from_string(purl)

    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version
    subpath = purl_data.subpath

    if not (name and namespace):
        return

    url = "https://github.com/{namespace}/{name}".format(namespace=namespace, name=name)

    if version:
        url = "{url}/tree/{version}".format(url=url, version=version)

    if subpath:
        url = "{url}/{subpath}".format(url=url, subpath=subpath)

    return url


@router.route("pkg:gitlab/.*")
def build_gitlab_homepage_url(purl):
    """
    Return a gitlab homepage URL `url` from a the `purl` string
    """
    purl_data = PackageURL.from_string(purl)

    namespace = purl_data.namespace
    name = purl_data.name
    version = purl_data.version
    subpath = purl_data.subpath

    if not (name and namespace):
        return

    url = "https://gitlab.com/{namespace}/{name}".format(namespace=namespace, name=name)

    if version:
        url = "{url}/-/tree/{version}".format(url=url, version=version)

    if subpath:
        url = "{url}/{subpath}".format(url=url, subpath=subpath)

    return url


@router.route("pkg:rubygems/.*")
def build_gem_download_url(purl):
    """
    Return a rubygems homepage URL `url` from a the `purl` string
    """
    purl_data = PackageURL.from_string(purl)

    name = purl_data.name
    version = purl_data.version

    if not (name and version):
        return

    return "https://rubygems.org/downloads/{name}-{version}.gem".format(
        name=name, version=version
    )
