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

import json
import os
import re
import unittest

from packageurl import PackageURL
from packageurl import normalize
from packageurl import normalize_qualifiers


def create_test_function(
    description,
    purl,
    canonical_purl,
    is_invalid,
    type,
    name,
    namespace,
    version,
    qualifiers,
    subpath,  # NOQA
    test_func_prefix="test_purl_pkg_",
    **kwargs
):
    """
    Return a new (test function, test_name) where the test_function closed on
    test arguments. If is_error is True the tests are expected to raise an
    Exception.
    """
    if is_invalid:

        def test_purl(self):
            try:
                PackageURL.from_string(purl)
                self.fail("Should raise a ValueError")
            except ValueError:
                pass

            try:
                PackageURL.from_string(canonical_purl)
                self.fail("Should raise a ValueError")
            except ValueError:
                pass

            try:
                PackageURL(type, namespace, name, version, qualifiers, subpath)
            except ValueError:
                pass

    else:

        def test_purl(self):
            # parsing the test canonical `purl` then re-building a `purl` from these
            # parsed components should return the test canonical `purl`
            cano = PackageURL.from_string(purl)
            assert canonical_purl == cano.to_string()

            # parsing the test `purl` should return the components parsed from the
            # test canonical `purl`
            parsed = PackageURL.from_string(canonical_purl)
            assert cano.to_dict() == parsed.to_dict()

            # parsing the test `purl` then re-building a `purl` from these parsed
            # components should return the test canonical `purl`
            assert canonical_purl == parsed.to_string()

            # building a `purl` from the test components should return the test
            # canonical `purl`
            built = PackageURL(type, namespace, name, version, qualifiers, subpath)
            assert canonical_purl == built.to_string()

    # create a good function name for use in test discovery
    if not description:
        description = purl
    if is_invalid:
        test_func_prefix += "is_invalid_"
    test_name = python_safe_name(test_func_prefix + description)
    test_purl.__name__ = test_name
    test_purl.funcname = test_name
    return test_purl, test_name


def python_safe_name(s):
    """
    Return a name derived from string `s` safe to use as a Python function name.

    For example:
    >>> s = "not `\\a /`good` -safe name ??"
    >>> assert python_safe_name(s) == 'not_good_safe_name'
    """
    no_punctuation = re.compile(r"[\W_]", re.MULTILINE).sub
    s = s.lower()
    s = no_punctuation(" ", s)
    s = "_".join(s.split())
    return s


class PurlTest(unittest.TestCase):
    pass


def build_tests(clazz=PurlTest, test_file="test-suite-data.json"):
    """
    Dynamically build test methods for each purl test found in the `test_file`
    JSON file and attach a test method to the `clazz` class.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")
    test_file = os.path.join(test_data_dir, test_file)

    with open(test_file) as tf:
        tests_data = json.load(tf)
    for items in tests_data:
        test_func, test_name = create_test_function(**items)
        # attach that method to the class
        setattr(clazz, test_name, test_func)


build_tests()


class NormalizePurlTest(unittest.TestCase):
    def test_normalize_qualifiers_as_string(self):
        qualifiers_as_dict = {"classifier": "sources", "repository_url": "repo.spring.io/release"}
        qualifiers_as_string = "classifier=sources&repository_url=repo.spring.io/release"
        assert qualifiers_as_string == normalize_qualifiers(qualifiers_as_dict, encode=True)

    def test_normalize_qualifiers_as_dict(self):
        qualifiers_as_dict = {"classifier": "sources", "repository_url": "repo.spring.io/release"}
        qualifiers_as_string = "classifier=sources&repository_url=repo.spring.io/release"
        assert qualifiers_as_dict == normalize_qualifiers(qualifiers_as_string, encode=False)

    def test_create_PackageURL_from_qualifiers_string(self):
        canonical_purl = "pkg:maven/org.apache.xmlgraphics/batik-anim@1.9.1?classifier=sources&repository_url=repo.spring.io/release"
        type = "maven"  # NOQA
        namespace = "org.apache.xmlgraphics"
        name = "batik-anim"
        version = "1.9.1"
        qualifiers_as_string = "classifier=sources&repository_url=repo.spring.io/release"
        subpath = None

        purl = PackageURL(type, namespace, name, version, qualifiers_as_string, subpath)
        assert canonical_purl == purl.to_string()

    def test_create_PackageURL_from_qualifiers_dict(self):
        canonical_purl = "pkg:maven/org.apache.xmlgraphics/batik-anim@1.9.1?classifier=sources&repository_url=repo.spring.io/release"
        type = "maven"  # NOQA
        namespace = "org.apache.xmlgraphics"
        name = "batik-anim"
        version = "1.9.1"
        qualifiers_as_dict = {"classifier": "sources", "repository_url": "repo.spring.io/release"}
        subpath = None

        purl = PackageURL(type, namespace, name, version, qualifiers_as_dict, subpath)
        assert canonical_purl == purl.to_string()

    def test_normalize_encode_can_take_unicode_with_non_ascii_with_slash(self):
        uncd = "núcleo/núcleo"
        normal = normalize(
            type=uncd,
            namespace=uncd,
            name=uncd,
            version=uncd,
            qualifiers="a=" + uncd,
            subpath=uncd,
            encode=True,
        )
        expected = (
            "n%c3%bacleo/n%c3%bacleo",
            "n%C3%BAcleo/n%C3%BAcleo",
            "n%C3%BAcleo/n%C3%BAcleo",
            "n%C3%BAcleo/n%C3%BAcleo",
            "a=n%C3%BAcleo/n%C3%BAcleo",
            "n%C3%BAcleo/n%C3%BAcleo",
        )
        assert expected == normal

    def test_normalize_decode_can_take_unicode_with_non_ascii_with_slash(self):
        uncd = "núcleo/núcleo"
        normal = normalize(
            type=uncd,
            namespace=uncd,
            name=uncd,
            version=uncd,
            qualifiers="a=" + uncd,
            subpath=uncd,
            encode=False,
        )
        expected = (
            "núcleo/núcleo",
            "núcleo/núcleo",
            "núcleo/núcleo",
            "núcleo/núcleo",
            {"a": "núcleo/núcleo"},
            "núcleo/núcleo",
        )
        assert expected == normal

    def test_normalize_encode_always_reencodes(self):
        uncd = "n%c3%bacleo/n%c3%bacleo"
        normal = normalize(
            type=uncd,
            namespace=uncd,
            name=uncd,
            version=uncd,
            qualifiers="a=" + uncd,
            subpath=uncd,
            encode=True,
        )
        expected = (
            "n%25c3%25bacleo/n%25c3%25bacleo",
            "n%25c3%25bacleo/n%25c3%25bacleo",
            "n%25c3%25bacleo/n%25c3%25bacleo",
            "n%25c3%25bacleo/n%25c3%25bacleo",
            "a=n%25c3%25bacleo/n%25c3%25bacleo",
            "n%25c3%25bacleo/n%25c3%25bacleo",
        )
        assert expected == normal

    def test_qualifiers_must_be_key_value_pairs(self):
        purl = "pkg:maven/org.apache.xmlgraphics/batik-anim@1.9.1?this+is+not+a+key_value"
        try:
            PackageURL.from_string(purl)
            self.fail("Failed to raise exception for invalid qualifiers")
        except ValueError as ve:
            assert "Invalid qualifier. Must be a string of key=value pairs" in str(ve)

    def test_to_dict_optionally_returns_qualifiers_as_string(self):
        purl = PackageURL(
            type="maven",
            namespace="org.apache",
            name="commons-logging",
            version="12.3",
            qualifiers="this=12&that=13",
            subpath="this/is/a/path",
        )

        expected = dict(
            [
                ("type", "maven"),
                ("namespace", "org.apache"),
                ("name", "commons-logging"),
                ("version", "12.3"),
                (
                    "qualifiers",
                    dict(
                        [
                            ("that", "13"),
                            ("this", "12"),
                        ]
                    ),
                ),
                ("subpath", "this/is/a/path"),
            ]
        )
        assert expected == purl.to_dict()

        expected = dict(
            [
                ("type", "maven"),
                ("namespace", "org.apache"),
                ("name", "commons-logging"),
                ("version", "12.3"),
                ("qualifiers", "that=13&this=12"),
                ("subpath", "this/is/a/path"),
            ]
        )
        assert expected == purl.to_dict(encode=True)

    def test_to_dict_custom_empty_value(self):
        purl = PackageURL(
            type="maven",
            namespace="",
            name="commons-logging",
            version="12.3",
            qualifiers=None,
        )

        expected = dict(
            [
                ("type", "maven"),
                ("namespace", None),
                ("name", "commons-logging"),
                ("version", "12.3"),
                ("qualifiers", None),
                ("subpath", None),
            ]
        )
        assert expected == purl.to_dict()
        assert expected == purl.to_dict(empty=None)

        expected = dict(
            [
                ("type", "maven"),
                ("namespace", ""),
                ("name", "commons-logging"),
                ("version", "12.3"),
                ("qualifiers", ""),
                ("subpath", ""),
            ]
        )
        assert expected == purl.to_dict(empty="")


def test_purl_is_hashable():
    s = {PackageURL(name="hashable", type="pypi")}
    assert len(s) == 1
