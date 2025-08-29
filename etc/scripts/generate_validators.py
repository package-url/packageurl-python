# Generate a simple script based on provided list for package types

"""
{
  "$schema": "https://packageurl.org/schemas/purl-type-definition.schema-1.0.json",
  "$id": "https://packageurl.org/types/pypi-definition.json",
  "type": "pypi",
  "type_name": "PyPI",
  "description": "Python packages",
  "repository": {
    "use_repository": true,
    "default_repository_url": "https://pypi.org",
    "note": "Previously https://pypi.python.org"
  },
  "namespace_definition": {
    "requirement": "prohibited",
    "note": "there is no namespace"
  },
  "name_definition": {
    "native_name": "name",
    "case_sensitive": false,
    "normalization_rules": [
      "Replace underscore _ with dash -",
      "Replace dot . with underscore _ when used in distribution (sdist, wheel) names"
    ],
    "note": "PyPI treats - and _ as the same character and is not case sensitive. Therefore a PyPI package name must be lowercased and underscore _ replaced with a dash -. Note that PyPI itself is preserving the case of package names. When used in distribution and wheel names, the dot . is replaced with an underscore _"
  },
  "version_definition": {
    "case_sensitive": false,
    "native_name": "version"
  },
  "qualifiers_definition": [
    {
      "key": "file_name",
      "requirement": "optional",
      "description": "The file_name qualifier selects a particular distribution file (case-sensitive). For naming convention, see the Python Packaging User Guide on source distributions https://packaging.python.org/en/latest/specifications/source-distribution-format/#source-distribution-file-name and on binary distributions https://packaging.python.org/en/latest/specifications/binary-distribution-format/#file-name-convention and the rules for platform compatibility tags https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/"
    }
  ],
  "examples": [
    "pkg:pypi/django@1.11.1",
    "pkg:pypi/django@1.11.1?filename=Django-1.11.1.tar.gz",
    "pkg:pypi/django@1.11.1?filename=Django-1.11.1-py2.py3-none-any.whl",
    "pkg:pypi/django-allauth@12.23"
  ]
}
"""
from packageurl import PackageURL
from pathlib import Path
import json

HEADER = '''# Copyright (c) the purl authors
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

from packageurl.contrib.route import Router

"""
Validate each type according to the PURL spec type definitions
"""

class TypeValidator:
    @classmethod
    def validate(cls, purl, strict=False):
        if not strict:
            purl = cls.normalize(purl)

        if cls.namespace_requirement == "prohibited" and purl.namespace:
            yield f"Namespace is prohibited for purl type: {cls.type!r}"

        elif cls.namespace_requirement == "required" and not purl.namespace:
            yield f"Namespace is required for purl type: {cls.type!r}"

        if (
            not cls.namespace_case_sensitive
            and purl.namespace
            and purl.namespace.lower() != purl.namespace
        ):
            yield f"Namespace is not lowercased for purl type: {cls.type!r}"

        if not cls.name_case_sensitive and purl.name and purl.name.lower() != purl.name:
            yield f"Name is not lowercased for purl type: {cls.type!r}"

        if not cls.version_case_sensitive and purl.version and purl.version.lower() != purl.version:
            yield f"Version is not lowercased for purl type: {cls.type!r}"

        yield from cls.validate_type(purl, strict=strict)

    @classmethod
    def normalize(cls, purl):
        from packageurl import PackageURL
        from packageurl import normalize

        type_norm, namespace_norm, name_norm, version_norm, qualifiers_norm, subpath_norm = (
            normalize(
                purl.type,
                purl.namespace,
                purl.name,
                purl.version,
                purl.qualifiers,
                purl.subpath,
                encode=False,
            )
        )

        return PackageURL(
            type=type_norm,
            namespace=namespace_norm,
            name=name_norm,
            version=version_norm,
            qualifiers=qualifiers_norm,
            subpath=subpath_norm,
        )

    @classmethod
    def validate_type(cls, purl, strict=False):
        if strict:
            yield from cls.validate_qualifiers(purl=purl)

    @classmethod
    def validate_qualifiers(cls, purl):
        if not purl.qualifiers:
            return

        purl_qualifiers_keys = set(purl.qualifiers.keys())
        allowed_qualifiers_set = cls.allowed_qualifiers

        disallowed = purl_qualifiers_keys - allowed_qualifiers_set

        if disallowed:
            yield (
                f"Invalid qualifiers found: {', '.join(sorted(disallowed))}. "
                f"Allowed qualifiers are: {', '.join(sorted(allowed_qualifiers_set))}"
            )
'''


TEMPLATE = """
class {class_name}({validator_class}):
    type = "{type}"
    type_name = "{type_name}"
    description = '''{description}'''
    use_repository = {use_repository}
    default_repository_url = "{default_repository_url}"
    namespace_requirement = "{namespace_requirement}"
    allowed_qualifiers = {allowed_qualifiers}
    namespace_case_sensitive = {namespace_case_sensitive}
    name_case_sensitive = {name_case_sensitive}
    version_case_sensitive = {version_case_sensitive}
    purl_pattern = "{purl_pattern}"
"""


def generate_validators():
    """
    Generate validators for all package types defined in the packageurl specification.
    """

    base_dir = Path(__file__).parent.parent.parent

    types_dir = base_dir / "spec" / "types"

    script_parts = [HEADER]

    validators_by_type = {}

    for type in sorted(types_dir.glob("*.json")):
        type_def = json.loads(type.read_text())

        _type = type_def["type"]
        standard_validator_class = "TypeValidator"

        class_prefix = _type.capitalize()
        class_name = f"{class_prefix}{standard_validator_class}"
        validators_by_type[_type] = class_name
        name_normalization_rules=type_def["name_definition"].get("normalization_rules") or []
        allowed_qualifiers = [defintion.get("key") for defintion in type_def.get("qualifiers_definition") or []]
        namespace_case_sensitive = type_def["namespace_definition"].get("case_sensitive") or False
        name_case_sensitive = type_def["name_definition"].get("case_sensitive") or False
        version_definition = type_def.get("version_definition") or {}
        version_case_sensitive = version_definition.get("case_sensitive") or True
        repository = type_def.get("repository")
        use_repository_url = repository.get("use_repository") or False 

        if use_repository_url and "repsitory_url" not in allowed_qualifiers:
            allowed_qualifiers.append("repository_url")

        allowed_qualifiers = set(allowed_qualifiers)

        type_validator = TEMPLATE.format(**dict(
            class_name=class_name,
            validator_class=standard_validator_class,
            type=_type,
            type_name=type_def["type_name"],
            description=type_def["description"],
            use_repository=type_def["repository"]["use_repository"],
            default_repository_url=type_def["repository"].get("default_repository_url") or "",
            namespace_requirement=type_def["namespace_definition"]["requirement"],
            name_normalization_rules=name_normalization_rules,
            allowed_qualifiers=allowed_qualifiers or [],
            namespace_case_sensitive=namespace_case_sensitive,
            name_case_sensitive=name_case_sensitive,
            version_case_sensitive=version_case_sensitive,
            purl_pattern=f"pkg:{_type}/.*"
        ))

        script_parts.append(type_validator)
    
    script_parts.append(generate_validators_by_type(validators_by_type=validators_by_type))
    # script_parts.append(attach_router(validators_by_type.values()))

    validate_script = base_dir / "src" / "packageurl" / "validate.py"

    validate_script.write_text("\n".join(script_parts))


def generate_validators_by_type(validators_by_type):
    """
    Return a python snippet that maps a type to it's TypeValidator class
    """
    snippets = []
    for type, class_name in validators_by_type.items():
        snippet = f"    {type!r} : {class_name},"
        snippets.append(snippet)

    snippets = "\n".join(snippets)
    start = "VALIDATORS_BY_TYPE = {"
    end = "}"
    return f"{start}\n{snippets}\n{end}"

def attach_router(classes):
    snippets = []
    for class_name in classes:
        snippet = f"    {class_name},"
        snippets.append(snippet)
    snippets = "\n".join(snippets)
    start = "PACKAGE_REGISTRY = [ \n"
    end = "\n   ]"
    classes = f"{start}{snippets}{end}"
    router_code = '''
validate_router = Router()

for pkg_class in PACKAGE_REGISTRY:
    validate_router.append(pattern=pkg_class.purl_pattern, endpoint=pkg_class.validate)
    '''
    return f"{classes}{router_code}"


if __name__ == "__main__":
    generate_validators()