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

import pytest

from packageurl import PackageURL

current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
spec_file_path = os.path.join(root_dir, "spec", "tests", "spec", "specification-test.json")

valid_purl_types_file = os.path.join(root_dir, "spec", "purl-types-index.json")


with open(spec_file_path, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

with open(valid_purl_types_file, "r", encoding="utf-8") as f:
    valid_purl_types = json.load(f)

tests = test_cases["tests"]

parse_tests = [t for t in tests if t["test_type"] == "parse"]
build_tests = [t for t in tests if t["test_type"] == "build"]

@pytest.mark.parametrize("description, input_str, expected_output, expected_failure", [
    (t["description"], t["input"], t["expected_output"], t["expected_failure"])
    for t in parse_tests
])
def test_parse(description, input_str, expected_output, expected_failure):
    if expected_failure:
        with pytest.raises(Exception):
            PackageURL.from_string(input_str)
        # assert None ==PackageURL.from_string(input_str)
    else:
        result = PackageURL.from_string(input_str)
        assert result.to_string() == expected_output


@pytest.mark.parametrize("description, input_dict, expected_output, expected_failure", [
    (t["description"], t["input"], t["expected_output"], t["expected_failure"])
    for t in build_tests
])
def test_build(description, input_dict, expected_output, expected_failure):
    kwargs = {
        "type": input_dict.get("type"),
        "namespace": input_dict.get("namespace"),
        "name": input_dict.get("name"),
        "version": input_dict.get("version"),
        "qualifiers": input_dict.get("qualifiers"),
        "subpath": input_dict.get("subpath"),
    }

    if expected_failure:
        with pytest.raises(Exception):
            PackageURL(**kwargs).to_string()
    else:
        purl = PackageURL(**kwargs)
        assert purl.to_string() == expected_output


def load_spec_files(spec_dir):
    """
    Load all JSON files from the given directory into a dictionary.
    Key = filename, Value = parsed JSON content
    """
    spec_data = {}
    for filename in os.listdir(spec_dir):
        if filename.endswith("-test.json"):
            filepath = os.path.join(spec_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    spec_data[filename] = data["tests"]
                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
    return spec_data


SPEC_DIR = os.path.join(os.path.dirname(__file__), '..', 'spec', 'tests', 'types')
spec_dict = load_spec_files(SPEC_DIR)

flattened_cases = []
for filename, cases in spec_dict.items():
    for case in cases:
        flattened_cases.append((filename, case["description"], case))


@pytest.mark.parametrize("filename,description,test_case", flattened_cases)
def test_package_type_case(filename, description, test_case):
    test_type = test_case["test_type"]
    expected_failure = test_case.get("expected_failure", False)

    if expected_failure:
        with pytest.raises(Exception):
            run_test_case(test_case, test_type, description)
    else:
        run_test_case(test_case, test_type, description)


def run_test_case(case, test_type, desc):
    if test_type == "parse":
        purl = PackageURL.from_string(case["input"])
        expected = case["expected_output"]
        assert purl.type == expected["type"]
        assert purl.namespace == expected["namespace"]
        assert purl.name == expected["name"]
        assert purl.version == expected["version"]
        assert purl.qualifiers == expected["qualifiers"]
        assert purl.subpath == expected["subpath"]

    elif test_type == "roundtrip":
        purl = PackageURL.from_string(case["input"])
        assert purl.to_string() == case["expected_output"]

    elif test_type == "build":
        input_data = case["input"]
        purl = PackageURL(
            type=input_data["type"],
            namespace=input_data["namespace"],
            name=input_data["name"],
            version=input_data["version"],
            qualifiers=input_data.get("qualifiers"),
            subpath=input_data.get("subpath"),
        )
        assert purl.to_string() == case["expected_output"]
