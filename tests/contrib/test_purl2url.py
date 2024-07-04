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


def test_purl2url_get_repo_url():
    purls_url = {
        "pkg:github/tg1999/fetchcode": "https://github.com/tg1999/fetchcode",
        "pkg:github/tg1999/fetchcode@master": "https://github.com/tg1999/fetchcode/tree/master",
        "pkg:github/tg1999/fetchcode@master#tests": "https://github.com/tg1999/fetchcode/tree/master",
        "pkg:github/nexb/scancode-toolkit@3.1.1?version_prefix=v": "https://github.com/nexb/scancode-toolkit/tree/v3.1.1",
        "pkg:github/tg1999": None,
        "pkg:cargo/rand@0.7.2": "https://crates.io/crates/rand/0.7.2",
        "pkg:cargo/abc": "https://crates.io/crates/abc",
        "pkg:gem/bundler@2.3.23": "https://rubygems.org/gems/bundler/versions/2.3.23",
        "pkg:rubygems/bundler@2.3.23": "https://rubygems.org/gems/bundler/versions/2.3.23",
        "pkg:rubygems/package-name": "https://rubygems.org/gems/package-name",
        "pkg:bitbucket/birkenfeld/pygments-main": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld/pygments-main@244fd47e07d1014f0aed9c": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld/pygments-main@master#views": "https://bitbucket.org/birkenfeld/pygments-main",
        "pkg:bitbucket/birkenfeld": None,
        "pkg:gitlab/tg1999/firebase@master": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999/firebase@1a122122#views": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999/firebase": "https://gitlab.com/tg1999/firebase",
        "pkg:gitlab/tg1999": None,
        "pkg:gitlab/hoppr/hoppr@v1.11.1-dev.2": "https://gitlab.com/hoppr/hoppr",
        "pkg:pypi/sortedcontainers": "https://pypi.org/project/sortedcontainers/",
        "pkg:pypi/sortedcontainers@2.4.0": "https://pypi.org/project/sortedcontainers/2.4.0/",
        "pkg:pypi/packageurl_python": "https://pypi.org/project/packageurl-python/",
        "pkg:composer/psr/log": "https://packagist.org/packages/psr/log",
        "pkg:composer/psr/log@1.1.3": "https://packagist.org/packages/psr/log#1.1.3",
        "pkg:npm/is-npm": "https://www.npmjs.com/package/is-npm",
        "pkg:npm/is-npm@1.0.0": "https://www.npmjs.com/package/is-npm/v/1.0.0",
        "pkg:nuget/System.Text.Json": "https://www.nuget.org/packages/System.Text.Json",
        "pkg:nuget/System.Text.Json@6.0.6": "https://www.nuget.org/packages/System.Text.Json/6.0.6",
        "pkg:hackage/cli-extras": "https://hackage.haskell.org/package/cli-extras",
        "pkg:hackage/cli-extras@0.2.0.0": "https://hackage.haskell.org/package/cli-extras-0.2.0.0",
        "pkg:golang/xorm.io/xorm": "https://pkg.go.dev/xorm.io/xorm",
        "pkg:golang/xorm.io/xorm@v0.8.2": "https://pkg.go.dev/xorm.io/xorm@v0.8.2",
        "pkg:golang/gopkg.in/ldap.v3@v3.1.0": "https://pkg.go.dev/gopkg.in/ldap.v3@v3.1.0",
    }

    for purl, url in purls_url.items():
        assert url == purl2url.get_repo_url(purl)


def test_purl2url_get_download_url():
    purls_url = {
        # Generated
        "pkg:cargo/rand@0.7.2": "https://crates.io/api/v1/crates/rand/0.7.2/download",
        "pkg:gem/bundler@2.3.23": "https://rubygems.org/downloads/bundler-2.3.23.gem",
        "pkg:npm/is-npm@1.0.0": "http://registry.npmjs.org/is-npm/-/is-npm-1.0.0.tgz",
        "pkg:hackage/cli-extras@0.2.0.0": "https://hackage.haskell.org/package/cli-extras-0.2.0.0/cli-extras-0.2.0.0.tar.gz",
        "pkg:nuget/System.Text.Json@6.0.6": "https://www.nuget.org/api/v2/package/System.Text.Json/6.0.6",
        "pkg:github/nexb/scancode-toolkit@3.1.1?version_prefix=v": "https://github.com/nexb/scancode-toolkit/archive/v3.1.1.tar.gz",
        "pkg:github/StonyShi/reactor-netty-jersey@ac525d91ff1724395640531df08e3e4eabef207d": "https://github.com/stonyshi/reactor-netty-jersey/archive/ac525d91ff1724395640531df08e3e4eabef207d.tar.gz",
        "pkg:bitbucket/robeden/trove@3.0.3": "https://bitbucket.org/robeden/trove/get/3.0.3.tar.gz",
        "pkg:bitbucket/robeden/trove@3.0.3?version_prefix=v": "https://bitbucket.org/robeden/trove/get/v3.0.3.tar.gz",
        "pkg:gitlab/tg1999/firebase@1a122122": "https://gitlab.com/tg1999/firebase/-/archive/1a122122/firebase-1a122122.tar.gz",
        "pkg:gitlab/tg1999/firebase@1a122122?version_prefix=v": "https://gitlab.com/tg1999/firebase/-/archive/v1a122122/firebase-v1a122122.tar.gz",
        "pkg:gitlab/hoppr/hoppr@v1.11.1-dev.2": "https://gitlab.com/hoppr/hoppr/-/archive/v1.11.1-dev.2/hoppr-v1.11.1-dev.2.tar.gz",
        # From `download_url` qualifier
        "pkg:github/yarnpkg/yarn@1.3.2?download_url=https://github.com/yarnpkg/yarn/releases/download/v1.3.2/yarn-v1.3.2.tar.gz&version_prefix=v": "https://github.com/yarnpkg/yarn/releases/download/v1.3.2/yarn-v1.3.2.tar.gz",
        "pkg:generic/lxc-master.tar.gz?download_url=https://salsa.debian.org/lxc-team/lxc/-/archive/master/lxc-master.tar.gz": "https://salsa.debian.org/lxc-team/lxc/-/archive/master/lxc-master.tar.gz",
        "pkg:generic/code.google.com/android-notifier?download_url=https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/android-notifier/android-notifier-desktop-0.5.1-1.i386.rpm": "https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/android-notifier/android-notifier-desktop-0.5.1-1.i386.rpm",
        "pkg:bitbucket/robeden/trove?download_url=https://bitbucket.org/robeden/trove/downloads/trove-3.0.3.zip": "https://bitbucket.org/robeden/trove/downloads/trove-3.0.3.zip",
        "pkg:sourceforge/zclasspath?download_url=http://master.dl.sourceforge.net/project/zclasspath/maven2/org/zclasspath/zclasspath/1.5/zclasspath-1.5.jar": "http://master.dl.sourceforge.net/project/zclasspath/maven2/org/zclasspath/zclasspath/1.5/zclasspath-1.5.jar",
        "pkg:pypi/aboutcode-toolkit@3.4.0rc1?download_url=https://files.pythonhosted.org/packages/87/44/0fa8e9d0cccb8eb86fc1b5170208229dc6d6e9fd6e57ea1fe19cbeea68f5/aboutcode_toolkit-3.4.0rc1-py2.py3-none-any.whl": "https://files.pythonhosted.org/packages/87/44/0fa8e9d0cccb8eb86fc1b5170208229dc6d6e9fd6e57ea1fe19cbeea68f5/aboutcode_toolkit-3.4.0rc1-py2.py3-none-any.whl",
        # Not-supported
        "pkg:github/tg1999/fetchcode": None,
        "pkg:cargo/abc": None,
        "pkg:rubygems/package-name": None,
        "pkg:bitbucket/birkenfeld": None,
        "pkg:pypi/sortedcontainers@2.4.0": None,
        "pkg:composer/psr/log@1.1.3": None,
        "pkg:golang/xorm.io/xorm@v0.8.2": None,
        "pkg:golang/gopkg.in/ldap.v3@v3.1.0": None,
    }

    for purl, url in purls_url.items():
        assert url == purl2url.get_download_url(purl)


def test_purl2url_get_inferred_urls():
    purls_url = {
        "pkg:cargo/rand@0.7.2": [
            "https://crates.io/crates/rand/0.7.2",
            "https://crates.io/api/v1/crates/rand/0.7.2/download",
        ],
        "pkg:gem/bundler@2.3.23": [
            "https://rubygems.org/gems/bundler/versions/2.3.23",
            "https://rubygems.org/downloads/bundler-2.3.23.gem",
        ],
        "pkg:npm/is-npm@1.0.0": [
            "https://www.npmjs.com/package/is-npm/v/1.0.0",
            "http://registry.npmjs.org/is-npm/-/is-npm-1.0.0.tgz",
        ],
        "pkg:hackage/cli-extras@0.2.0.0": [
            "https://hackage.haskell.org/package/cli-extras-0.2.0.0",
            "https://hackage.haskell.org/package/cli-extras-0.2.0.0/cli-extras-0.2.0.0.tar.gz",
        ],
        "pkg:nuget/System.Text.Json@6.0.6": [
            "https://www.nuget.org/packages/System.Text.Json/6.0.6",
            "https://www.nuget.org/api/v2/package/System.Text.Json/6.0.6",
        ],
        "pkg:cargo/abc": ["https://crates.io/crates/abc"],
        "pkg:github/tg1999/fetchcode": ["https://github.com/tg1999/fetchcode"],
        "pkg:gitlab/tg1999/firebase@1a122122": [
            "https://gitlab.com/tg1999/firebase",
            "https://gitlab.com/tg1999/firebase/-/archive/1a122122/firebase-1a122122.tar.gz",
        ],
        "pkg:pypi/sortedcontainers@2.4.0": ["https://pypi.org/project/sortedcontainers/2.4.0/"],
        "pkg:composer/psr/log@1.1.3": ["https://packagist.org/packages/psr/log#1.1.3"],
        "pkg:rubygems/package-name": ["https://rubygems.org/gems/package-name"],
        "pkg:bitbucket/birkenfeld": [],
    }

    for purl, url in purls_url.items():
        assert url == purl2url.get_inferred_urls(purl)


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
