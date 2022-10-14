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

import pytest

from packageurl.contrib import purl2url


def test_purl2url_get_repo_url_with_valid_purls():
    purls_url = {
        "pkg:github/tg1999/fetchcode": "https://github.com/tg1999/fetchcode",
        "pkg:github/tg1999/fetchcode@master": "https://github.com/tg1999/fetchcode",
        "pkg:github/tg1999/fetchcode@master#tests": "https://github.com/tg1999/fetchcode",
        "pkg:github/tg1999": None,

        "pkg:cargo/rand@0.7.2": "https://crates.io/crates/rand/0.7.2",
        "pkg:cargo/abc": "https://crates.io/crates/abc",

        "pkg:rubygems/bundler@2.3.23": "https://rubygems.org/gems/bundler/versions/2.3.23",
        "pkg:gem/package-name": None,

        "pkg:bitbucket/birkenfeld/pygments-main": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld/pygments-main@244fd47e07d1014f0aed9c": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld/pygments-main@master#views": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld": None,

        "pkg:gitlab/tg1999/firebase@master": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999/firebase@1a122122#views": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999/firebase": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999": None,

        "pkg:pypi/sortedcontainers": "https://pypi.org/project/sortedcontainers/",
        "pkg:pypi/sortedcontainers@2.4.0": "https://pypi.org/project/sortedcontainers/2.4.0/",
        "pkg:pypi/packageurl_python": "https://pypi.org/project/packageurl-python/",

        "pkg:npm/is-npm": "https://www.npmjs.com/package/is-npm",
        "pkg:npm/is-npm@1.0.0": "https://www.npmjs.com/package/is-npm/v/1.0.0",

        "pkg:nuget/System.Text.Json": "https://www.nuget.org/packages/System.Text.Json",
        "pkg:nuget/System.Text.Json@6.0.6": "https://www.nuget.org/packages/System.Text.Json/6.0.6",

        "pkg:hackage/cli-extras": "https://hackage.haskell.org/package/cli-extras",
        "pkg:hackage/cli-extras@0.2.0.0": "https://hackage.haskell.org/package/cli-extras-0.2.0.0",
    }

    for purl, url in purls_url.items():
        assert url == purl2url.get_repo_url(purl)


def test_purl2url_get_download_url_with_valid_purls():
    purls_url = {
        "pkg:cargo/rand@0.7.2": "https://crates.io/api/v1/crates/rand/0.7.2/download",
        "pkg:rubygems/bundler@2.3.23": "https://rubygems.org/downloads/bundler-2.3.23.gem",
        "pkg:npm/is-npm@1.0.0": "http://registry.npmjs.org/is-npm/-/is-npm-1.0.0.tgz",
        "pkg:hackage/cli-extras@0.2.0.0": "https://hackage.haskell.org/package/cli-extras-0.2.0.0/cli-extras-0.2.0.0.tar.gz",
        "pkg:nuget/System.Text.Json@6.0.6": "https://www.nuget.org/api/v2/package/System.Text.Json/6.0.6",

        "pkg:cargo/abc": None,
        "pkg:github/tg1999/fetchcode": None,
        "pkg:gem/package-name": None,
        "pkg:bitbucket/birkenfeld": None,
        "pkg:gitlab/tg1999/firebase@1a122122": None,
        "pkg:pypi/sortedcontainers@2.4.0": None,
    }

    for purl, url in purls_url.items():
        assert url == purl2url.get_download_url(purl)


def test_purl2url_get_repo_url_with_invalid_purls():
    purls = [
        "pkg:github",
        "pkg:cargo",
        "pkg:gem",
        "pkg:bitbucket",
        "pkg:gitlab",
        None,
    ]

    for purl in purls:
        with pytest.raises(Exception) as e_info:
            purl2url.get_repo_url(purl)
            assert "Invalid PURL" == e_info
