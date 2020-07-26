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

import pytest

from packageurl.contrib.purl2url import build_bitbucket_homepage_url
from packageurl.contrib.purl2url import build_cargo_download_url
from packageurl.contrib.purl2url import build_github_homepage_url
from packageurl.contrib.purl2url import build_gitlab_homepage_url
from packageurl.contrib.purl2url import build_gem_download_url
from packageurl.contrib.purl2url import purl2url


def test_purl2url_with_valid_purls():
    purls_url = {
        "pkg:github/tg1999/fetchcode": "https://github.com/tg1999/fetchcode",
        "pkg:github/tg1999/fetchcode@master": "https://github.com/tg1999/fetchcode/tree/master",
        "pkg:github/tg1999/fetchcode@master#tests": "https://github.com/tg1999/fetchcode/tree/master/tests",
        "pkg:github/tg1999": None,
        "pkg:cargo/clap@2.3.3": "https://crates.io/api/v1/crates/clap/2.3.3/download",
        "pkg:cargo/rand@0.7.2": "https://crates.io/api/v1/crates/rand/0.7.2/download",
        "pkg:cargo/structopt@0.3.11": "https://crates.io/api/v1/crates/structopt/0.3.11/download",
        "pkg:cargo/abc": None,
        "pkg:rubygems/unf@0.1.3": "https://rubygems.org/downloads/unf-0.1.3.gem",
        "pkg:rubygems/yajl-ruby@1.2.0": "https://rubygems.org/downloads/yajl-ruby-1.2.0.gem",
        "pkg:gem/package-name": None,
        "pkg:bitbucket/birkenfeld/pygments-main": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld/pygments-main@244fd47e07d1014f0aed9c": "https://bitbucket.org/birkenfeld/pygments-main/src/244fd47e07d1014f0aed9c",
        "pkg:bitbucket/birkenfeld/pygments-main@master#views": "https://bitbucket.org/birkenfeld/pygments-main/src/master/views",
        "pkg:bitbucket/birkenfeld": None,
        "pkg:gitlab/tg1999/firebase@master": "https://gitlab.com/tg1999/firebase/-/tree/master",
        "pkg:gitlab/tg1999/firebase@1a122122#views": "https://gitlab.com/tg1999/firebase/-/tree/1a122122/views",
        "pkg:gitlab/tg1999/firebase": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999": None,
    }

    for purl, url in purls_url.items():
        assert url == purl2url(purl)


def test_convert_with_invalid_purls():
    purls = ["pkg:github", "pkg:cargo", "pkg:gem", "pkg:bitbucket", "pkg:gitlab", None]
    with pytest.raises(Exception) as e_info:
        for purl in purls:
            url = purl2url(purl)
            assert "Invalid PURL" == e_info
