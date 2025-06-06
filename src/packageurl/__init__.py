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

from __future__ import annotations

import string
from collections import namedtuple
from typing import TYPE_CHECKING
from typing import Any
from typing import Union
from typing import overload
from urllib.parse import quote as _percent_quote
from urllib.parse import unquote as _percent_unquote
from urllib.parse import urlsplit as _urlsplit

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable
    from typing import ClassVar

    from typing_extensions import Literal
    from typing_extensions import Self

    AnyStr = Union[str, bytes]

# Python 3
basestring = (bytes, str)

"""
A purl (aka. Package URL) implementation as specified at:
https://github.com/package-url/purl-spec
"""


def quote(s: AnyStr) -> str:
    """
    Return a percent-encoded unicode string, except for colon :, given an `s`
    byte or unicode string.
    """
    s_bytes = s.encode("utf-8") if isinstance(s, str) else s
    quoted = _percent_quote(s_bytes)
    if not isinstance(quoted, str):
        quoted = quoted.decode("utf-8")
    quoted = quoted.replace("%3A", ":")
    return quoted


def unquote(s: AnyStr) -> str:
    """
    Return a percent-decoded unicode string, given an `s` byte or unicode
    string.
    """
    unquoted = _percent_unquote(s)  # type:ignore[arg-type]  # typeshed is incorrect here
    if not isinstance(unquoted, str):
        unquoted = unquoted.decode("utf-8")
    return unquoted


@overload
def get_quoter(encode: bool = True) -> Callable[[AnyStr], str]: ...


@overload
def get_quoter(encode: None) -> Callable[[str], str]: ...


def get_quoter(encode: bool | None = True) -> Callable[[AnyStr], str] | Callable[[str], str]:
    """
    Return quoting callable given an `encode` tri-boolean (True, False or None)
    """
    if encode is True:
        return quote
    elif encode is False:
        return unquote
    elif encode is None:
        return lambda x: x


def normalize_type(type: AnyStr | None, encode: bool | None = True) -> str | None:
    if not type:
        return None

    type_str = type if isinstance(type, str) else type.decode("utf-8")
    quoter = get_quoter(encode)
    type_str = quoter(type_str)
    return type_str.strip().lower() or None


def normalize_namespace(
    namespace: AnyStr | None, ptype: str | None, encode: bool | None = True
) -> str | None:
    if not namespace:
        return None

    namespace_str = namespace if isinstance(namespace, str) else namespace.decode("utf-8")
    namespace_str = namespace_str.strip().strip("/")
    if ptype in ("bitbucket", "github", "pypi", "gitlab"):
        namespace_str = namespace_str.lower()
    segments = [seg for seg in namespace_str.split("/") if seg.strip()]
    segments_quoted = map(get_quoter(encode), segments)
    return "/".join(segments_quoted) or None


def normalize_name(
    name: AnyStr | None, ptype: str | None, encode: bool | None = True
) -> str | None:
    if not name:
        return None

    name_str = name if isinstance(name, str) else name.decode("utf-8")
    quoter = get_quoter(encode)
    name_str = quoter(name_str)
    name_str = name_str.strip().strip("/")
    if ptype in ("bitbucket", "github", "pypi", "gitlab"):
        name_str = name_str.lower()
    if ptype == "pypi":
        name_str = name_str.replace("_", "-")
    return name_str or None


def normalize_version(version: AnyStr | None, encode: bool | None = True) -> str | None:
    if not version:
        return None

    version_str = version if isinstance(version, str) else version.decode("utf-8")
    quoter = get_quoter(encode)
    version_str = quoter(version_str.strip())
    return version_str or None


@overload
def normalize_qualifiers(
    qualifiers: AnyStr | dict[str, str] | None, encode: Literal[True] = ...
) -> str | None: ...


@overload
def normalize_qualifiers(
    qualifiers: AnyStr | dict[str, str] | None, encode: Literal[False] | None
) -> dict[str, str]: ...


@overload
def normalize_qualifiers(
    qualifiers: AnyStr | dict[str, str] | None, encode: bool | None = ...
) -> str | dict[str, str] | None: ...


def normalize_qualifiers(
    qualifiers: AnyStr | dict[str, str] | None, encode: bool | None = True
) -> str | dict[str, str] | None:
    """
    Return normalized `qualifiers` as a mapping (or as a string if `encode` is
    True). The `qualifiers` arg is either a mapping or a string.
    Always return a mapping if decode is True (and never None).
    Raise ValueError on errors.
    """
    if not qualifiers:
        return None if encode else {}

    if isinstance(qualifiers, basestring):
        qualifiers_str = qualifiers if isinstance(qualifiers, str) else qualifiers.decode("utf-8")

        # decode string to list of tuples
        qualifiers_list = qualifiers_str.split("&")
        if any("=" not in kv for kv in qualifiers_list):
            raise ValueError(
                f"Invalid qualifier. Must be a string of key=value pairs:{qualifiers_list!r}"
            )
        qualifiers_parts = [kv.partition("=") for kv in qualifiers_list]
        qualifiers_pairs: Iterable[tuple[str, str]] = [(k, v) for k, _, v in qualifiers_parts]
    elif isinstance(qualifiers, dict):
        qualifiers_pairs = qualifiers.items()
    else:
        raise ValueError(f"Invalid qualifier. Must be a string or dict:{qualifiers!r}")

    quoter = get_quoter(encode)
    qualifiers_map = {
        k.strip().lower(): quoter(v)
        for k, v in qualifiers_pairs
        if k and k.strip() and v and v.strip()
    }

    valid_chars = string.ascii_letters + string.digits + ".-_"
    for key in qualifiers_map:
        if not key:
            raise ValueError("A qualifier key cannot be empty")

        if "%" in key:
            raise ValueError(f"A qualifier key cannot be percent encoded: {key!r}")

        if " " in key:
            raise ValueError(f"A qualifier key cannot contain spaces: {key!r}")

        if any(c not in valid_chars for c in key):
            raise ValueError(
                f"A qualifier key must be composed only of ASCII letters and numbers"
                f"period, dash and underscore: {key!r}"
            )

        if key[0] in string.digits:
            raise ValueError(f"A qualifier key cannot start with a number: {key!r}")

    qualifiers_map = dict(sorted(qualifiers_map.items()))

    if not encode:
        return qualifiers_map

    qualifiers_list = [f"{key}={value}" for key, value in qualifiers_map.items()]
    return "&".join(qualifiers_list) or None


def normalize_subpath(subpath: AnyStr | None, encode: bool | None = True) -> str | None:
    if not subpath:
        return None

    subpath_str = subpath if isinstance(subpath, str) else subpath.decode("utf-8")
    quoter = get_quoter(encode)
    segments = subpath_str.split("/")
    segments = [quoter(s) for s in segments if s.strip() and s not in (".", "..")]
    subpath_str = "/".join(segments)
    return subpath_str or None


@overload
def normalize(
    type: AnyStr | None,
    namespace: AnyStr | None,
    name: AnyStr | None,
    version: AnyStr | None,
    qualifiers: AnyStr | dict[str, str] | None,
    subpath: AnyStr | None,
    encode: Literal[True] = ...,
) -> tuple[str, str | None, str, str | None, str | None, str | None]: ...


@overload
def normalize(
    type: AnyStr | None,
    namespace: AnyStr | None,
    name: AnyStr | None,
    version: AnyStr | None,
    qualifiers: AnyStr | dict[str, str] | None,
    subpath: AnyStr | None,
    encode: Literal[False] | None,
) -> tuple[str, str | None, str, str | None, dict[str, str], str | None]: ...


@overload
def normalize(
    type: AnyStr | None,
    namespace: AnyStr | None,
    name: AnyStr | None,
    version: AnyStr | None,
    qualifiers: AnyStr | dict[str, str] | None,
    subpath: AnyStr | None,
    encode: bool | None = ...,
) -> tuple[str, str | None, str, str | None, str | dict[str, str] | None, str | None]: ...


def normalize(
    type: AnyStr | None,
    namespace: AnyStr | None,
    name: AnyStr | None,
    version: AnyStr | None,
    qualifiers: AnyStr | dict[str, str] | None,
    subpath: AnyStr | None,
    encode: bool | None = True,
) -> tuple[
    str | None,
    str | None,
    str | None,
    str | None,
    str | dict[str, str] | None,
    str | None,
]:
    """
    Return normalized purl components
    """
    type_norm = normalize_type(type, encode)
    namespace_norm = normalize_namespace(namespace, type_norm, encode)
    name_norm = normalize_name(name, type_norm, encode)
    version_norm = normalize_version(version, encode)
    qualifiers_norm = normalize_qualifiers(qualifiers, encode)
    subpath_norm = normalize_subpath(subpath, encode)
    return type_norm, namespace_norm, name_norm, version_norm, qualifiers_norm, subpath_norm


class PackageURL(
    namedtuple("PackageURL", ("type", "namespace", "name", "version", "qualifiers", "subpath"))
):
    """
    A purl is a package URL as defined at
    https://github.com/package-url/purl-spec
    """

    SCHEME: ClassVar[str] = "pkg"

    type: str
    namespace: str | None
    name: str
    version: str | None
    qualifiers: dict[str, str]
    subpath: str | None

    def __new__(
        cls,
        type: AnyStr | None = None,
        namespace: AnyStr | None = None,
        name: AnyStr | None = None,
        version: AnyStr | None = None,
        qualifiers: AnyStr | dict[str, str] | None = None,
        subpath: AnyStr | None = None,
    ) -> Self:
        required = dict(type=type, name=name)
        for key, value in required.items():
            if value:
                continue
            raise ValueError(f"Invalid purl: {key} is a required argument.")

        strings = dict(
            type=type,
            namespace=namespace,
            name=name,
            version=version,
            subpath=subpath,
        )

        for key, value in strings.items():
            if value and isinstance(value, basestring) or not value:
                continue
            raise ValueError(f"Invalid purl: {key} argument must be a string: {value!r}.")

        if qualifiers and not isinstance(qualifiers, (basestring, dict)):
            raise ValueError(
                f"Invalid purl: qualifiers argument must be a dict or a string: {qualifiers!r}."
            )

        (
            type_norm,
            namespace_norm,
            name_norm,
            version_norm,
            qualifiers_norm,
            subpath_norm,
        ) = normalize(type, namespace, name, version, qualifiers, subpath, encode=None)

        return super().__new__(
            cls,
            type=type_norm,
            namespace=namespace_norm,
            name=name_norm,
            version=version_norm,
            qualifiers=qualifiers_norm,
            subpath=subpath_norm,
        )

    def __str__(self, *args: Any, **kwargs: Any) -> str:
        return self.to_string()

    def __hash__(self) -> int:
        return hash(self.to_string())

    def to_dict(self, encode: bool | None = False, empty: Any = None) -> dict[str, Any]:
        """
        Return an ordered dict of purl components as {key: value}.
        If `encode` is True, then "qualifiers" are encoded as a normalized
        string. Otherwise, qualifiers is a mapping.
        You can provide a value for `empty` to be used in place of default None.
        """
        data = self._asdict()
        if encode:
            data["qualifiers"] = normalize_qualifiers(self.qualifiers, encode=encode)

        for field, value in data.items():
            data[field] = value or empty

        return data

    def to_string(self) -> str:
        """
        Return a purl string built from components.
        """
        type, namespace, name, version, qualifiers, subpath = normalize(
            self.type,
            self.namespace,
            self.name,
            self.version,
            self.qualifiers,
            self.subpath,
            encode=True,
        )

        purl = [self.SCHEME, ":", type, "/"]

        if namespace:
            purl.extend((namespace, "/"))

        purl.append(name)

        if version:
            purl.append("@")
            purl.append(version)

        if qualifiers:
            purl.append("?")
            purl.append(qualifiers)

        if subpath:
            purl.append("#")
            purl.append(subpath)

        return "".join(purl)

    @classmethod
    def from_string(cls, purl: str) -> Self:
        """
        Return a PackageURL object parsed from a string.
        Raise ValueError on errors.
        """
        if not purl or not isinstance(purl, str) or not purl.strip():
            raise ValueError("A purl string argument is required.")

        scheme, sep, remainder = purl.partition(":")
        if not sep or scheme != cls.SCHEME:
            raise ValueError(
                f'purl is missing the required "{cls.SCHEME}" scheme component: {purl!r}.'
            )

        # this strip '/, // and /// as possible in :// or :///
        remainder = remainder.strip().lstrip("/")

        version: str | None  # this line is just for type hinting
        subpath: str | None  # this line is just for type hinting

        type_, sep, remainder = remainder.partition("/")
        if not type_ or not sep:
            raise ValueError(f"purl is missing the required type component: {purl!r}.")

        type_ = type_.lower()

        scheme, authority, path, qualifiers_str, subpath = _urlsplit(
            url=remainder, scheme="", allow_fragments=True
        )

        # The spec (seems) to allow colons in the name and namespace.
        # urllib.urlsplit splits on : considers them parts of scheme
        # and authority.
        # Other libraries do not care about this.
        # See https://github.com/package-url/packageurl-python/issues/152#issuecomment-2637692538
        # We do + ":" + to put the colon back that urlsplit removed.
        if authority:
            path = authority + ":" + path

        if scheme:
            path = scheme + ":" + path

        path = path.lstrip("/")

        namespace: str | None = ""
        # NPM purl have a namespace in the path
        # and the namespace in an npm purl is
        # different from others because it starts with `@`
        # so we need to handle this case separately
        if type_ == "npm" and path.startswith("@"):
            namespace, sep, path = path.partition("/")

        remainder, sep, version = path.rpartition("@")
        if not sep:
            remainder = version
            version = None

        ns_name = remainder.strip().strip("/")
        ns_name_parts = ns_name.split("/")
        ns_name_parts = [seg for seg in ns_name_parts if seg and seg.strip()]
        name = ""
        if not namespace and len(ns_name_parts) > 1:
            name = ns_name_parts[-1]
            ns = ns_name_parts[:-1]
            namespace = "/".join(ns)
        elif len(ns_name_parts) == 1:
            name = ns_name_parts[0]

        if not name:
            raise ValueError(f"purl is missing the required name component: {purl!r}")

        type_, namespace, name, version, qualifiers, subpath = normalize(
            type_,
            namespace,
            name,
            version,
            qualifiers_str,
            subpath,
            encode=False,
        )

        return cls(type_, namespace, name, version, qualifiers, subpath)
