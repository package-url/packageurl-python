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

import io
import json
import os
from dataclasses import asdict
from unittest import TestCase

from packageurl.contrib.url2fix import url2fix


def get_fix(url):
    fix = url2fix(url)
    return fix and asdict(fix)


def get_url2fix_test_method(test_url, expected_purl):
    def test_method(self):
        self.assertEqual(expected_purl, get_fix(test_url), msg=test_url)

    return test_method


def build_tests(clazz, test_file="url2fix.json"):
    """
    Dynamically build test methods for CodeFix inference from a JSON test file.
    The JSON test file is a key-sorted mapping of {test url: expected fix}.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")
    test_file = os.path.join(test_data_dir, test_file)

    with io.open(test_file, encoding="utf-8") as tests:
        tests_data = json.load(tests)

    for test_url, expected_fix in sorted(tests_data.items()):
        test_name = f"test_url2fix_{test_url}"
        test_method = get_url2fix_test_method(test_url, expected_fix)
        test_method.funcname = test_name
        # attach that method to our test class
        setattr(clazz, test_name, test_method)


class TestURL2FIXDataDriven(TestCase):
    pass


build_tests(clazz=TestURL2FIXDataDriven)
