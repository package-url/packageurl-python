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

from collections import OrderedDict
import io
import json
import os
import re
from unittest import TestCase

try:  # Python 2
    unicode
    str = unicode  # NOQA
except NameError:  # Python 3
    unicode = str  # NOQA


from packageurl.contrib.url2purl import get_purl as purl_getter


def get_purl(url):
    purl = purl_getter(url)
    return purl and unicode(purl.to_string())


class TestURL2PURL(TestCase):
    def test_get_purl_empty_string(self):
        self.assertEqual(None, get_purl(''))

    def test_get_purl_none(self):
        self.assertEqual(None, get_purl(None))

    def test_get_purl_unroutable_uri(self):
        self.assertEqual(None, get_purl('dsf.example'))


def python_safe(s):
    """
    Return a name safe to use as a python function name.
    """
    safe_chars = re.compile(r'[\W_]', re.MULTILINE)
    s = s.strip().lower()
    s = [x for x in safe_chars.split(s) if x]
    return '_'.join(s)


def get_url2purl_test_method(test_url, expected_purl):
    def test_method(self):
        self.assertEqual(expected_purl, get_purl(test_url))
    return test_method


def build_tests(clazz, test_file='url2purl.json', regen=False):
    """
    Dynamically build test methods for Package URL inference from a JSON test
    file.
    The JSON test file is a key-sorted mapping of {test url: expected purl}.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    test_file = os.path.join(test_data_dir, test_file)

    with io.open(test_file, encoding='utf-8') as tests:
        tests_data = json.load(tests)

    if regen:
        tests_data = {test_url: get_purl(test_url)
                      for test_url in tests_data.keys()}
        dumpable = json.dumps(OrderedDict(sorted(tests_data.items())), indent=2)
        with io.open(test_file, 'wb') as regened:
            regened.write(dumpable)

    for test_url, expected_purl in sorted(tests_data.items()):
        test_name = 'test_url2purl_{test_url}'.format(test_url=test_url)
        test_name = python_safe(test_name)
        test_method = get_url2purl_test_method(test_url, expected_purl)
        test_method.funcname = test_name
        # attach that method to our test class
        setattr(clazz, test_name, test_method)


class TestURL2PURLDataDriven(TestCase):
    pass


build_tests(clazz=TestURL2PURLDataDriven, regen=False)
