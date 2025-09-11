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
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from packageurl import PackageURL


@dataclass
class PurlTestCase:
    description: str
    test_type: str
    input: Any
    expected_output: Optional[Any] = None
    expected_failure: bool = False
    test_group: Optional[str] = None


def load_test_case(case_dict: dict) -> PurlTestCase:
    return PurlTestCase(
        description=case_dict["description"],
        test_type=case_dict["test_type"],
        input=case_dict["input"],
        expected_output=case_dict.get("expected_output"),
        expected_failure=case_dict.get("expected_failure", False),
        test_group=case_dict.get("test_group"),
    )


def load_spec_files(spec_dir: str) -> Dict[str, List[PurlTestCase]]:
    """
    Load all JSON files from the given directory into a dictionary of test cases.
    Key = filename, Value = list of PurlTestCase objects
    """
    spec_data = {}
    for filename in os.listdir(spec_dir):
        if filename.endswith("-test.json"):
            filepath = os.path.join(spec_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    spec_data[filename] = [load_test_case(tc) for tc in data["tests"]]
                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
    return spec_data


current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
spec_file_path = os.path.join(root_dir, "spec", "tests", "spec", "specification-test.json")

with open(spec_file_path, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

all_tests = [load_test_case(tc) for tc in test_cases["tests"]]
parse_tests = [t for t in all_tests if t.test_type == "parse"]
build_tests = [t for t in all_tests if t.test_type == "build"]

SPEC_DIR = os.path.join(os.path.dirname(__file__), "..", "spec", "tests", "types")
spec_dict = load_spec_files(SPEC_DIR)

flattened_cases = []
for filename, cases in spec_dict.items():
    for case in cases:
        flattened_cases.append((filename, case.description, case))


@pytest.mark.parametrize(
    "case",
    parse_tests,
    ids=lambda c: c.description,
)
def test_parse(case: PurlTestCase):
    if case.expected_failure:
        with pytest.raises(Exception):
            PackageURL.from_string(case.input)
    else:
        result = PackageURL.from_string(case.input)
        assert result.to_string() == case.expected_output


@pytest.mark.parametrize(
    "case",
    build_tests,
    ids=lambda c: c.description,
)
def test_build(case: PurlTestCase):
    kwargs = {
        "type": case.input.get("type"),
        "namespace": case.input.get("namespace"),
        "name": case.input.get("name"),
        "version": case.input.get("version"),
        "qualifiers": case.input.get("qualifiers"),
        "subpath": case.input.get("subpath"),
    }

    if case.expected_failure:
        with pytest.raises(Exception):
            PackageURL(**kwargs).to_string()
    else:
        purl = PackageURL(**kwargs)
        assert purl.to_string() == case.expected_output


@pytest.mark.parametrize(
    "filename,description,case",
    flattened_cases,
    ids=lambda v: v[1] if isinstance(v, tuple) else str(v),
)
def test_package_type_case(filename, description, case: PurlTestCase):
    if case.expected_failure:
        with pytest.raises(Exception):
            run_test_case(case)
    else:
        run_test_case(case)


def run_test_case(case: PurlTestCase):
    if case.test_type == "parse":
        purl = PackageURL.from_string(case.input)
        expected = case.expected_output
        assert purl.type == expected["type"]
        assert purl.namespace == expected["namespace"]
        assert purl.name == expected["name"]
        assert purl.version == expected["version"]
        if expected["qualifiers"]:
            assert purl.qualifiers == expected["qualifiers"]
        else:
            assert not purl.qualifiers
        assert purl.subpath == expected["subpath"]

    elif case.test_type == "roundtrip":
        purl = PackageURL.from_string(case.input)
        assert purl.to_string() == case.expected_output

    elif case.test_type == "build":
        inp = case.input
        purl = PackageURL(
            type=inp["type"],
            namespace=inp["namespace"],
            name=inp["name"],
            version=inp["version"],
            qualifiers=inp.get("qualifiers"),
            subpath=inp.get("subpath"),
        )
        assert purl.to_string() == case.expected_output

    elif case.test_type == "validation":
        test_group = case.test_group
        if test_group not in ("base", "advanced"):
            raise Exception(test_group)
        strict = test_group == "base"
        messages = PackageURL.validate_string(purl=case.input, strict=strict)
        messages = [message.to_dict() for message in messages]
        if case.expected_output:
            assert messages == case.expected_output
        else:
            assert not messages
