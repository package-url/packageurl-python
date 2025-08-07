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
