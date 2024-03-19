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

from packageurl.contrib.django.utils import purl_to_lookups
from packageurl.utils import get_golang_purl


def test_purl_to_lookups_without_encode():
    assert purl_to_lookups(
        purl_str="pkg:alpine/openssl@0?arch=aarch64&distroversion=edge&reponame=main",
        encode=False,
    ) == {
        "type": "alpine",
        "name": "openssl",
        "version": "0",
        "qualifiers": {
            "arch": "aarch64",
            "distroversion": "edge",
            "reponame": "main",
        },
    }


def test_purl_to_lookups_with_encode():
    assert purl_to_lookups(
        purl_str="pkg:alpine/openssl@0?arch=aarch64&distroversion=edge&reponame=main",
        encode=True,
    ) == {
        "type": "alpine",
        "name": "openssl",
        "version": "0",
        "qualifiers": "arch=aarch64&distroversion=edge&reponame=main",
    }


def test_get_golang_purl():
    assert None == get_golang_purl(None)
    golang_purl_1 = get_golang_purl(
        "github.com/envoyproxy/go-control-plane/envoy/config/listener/v3"
    )
    assert "pkg:golang/github.com/envoyproxy/go-control-plane/envoy/config/listener/v3" == str(
        golang_purl_1
    )
    assert golang_purl_1.name == "v3"
    assert golang_purl_1.namespace == "github.com/envoyproxy/go-control-plane/envoy/config/listener"
    golang_purl_2 = get_golang_purl(
        go_package="github.com/grpc-ecosystem/go-grpc-middleware v1.3.0"
    )
    assert "pkg:golang/github.com/grpc-ecosystem/go-grpc-middleware@v1.3.0" == str(golang_purl_2)
    with pytest.raises(Exception):
        get_golang_purl("github.com/envoyproxy/go-control-plane/envoy/config/listener@v3.1")
