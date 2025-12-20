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

from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query_utils import DeferredAttribute

from packageurl import PackageURL


def to_purl(value: Optional[str | PackageURL]) -> Optional[PackageURL]:
    if value is None or value == "":
        # in case of PURL being blank we return None as well in order
        # to avoid type confusion, as blank is not a valid PURL
        return None

    if isinstance(value, PackageURL):
        return value

    try:
        return PackageURL.from_string(value)
    except ValueError as e:
        raise ValidationError(f"Invalid PURL: {e}")


class PURLDescriptor(DeferredAttribute):
    def __get__(
        self, instance: Optional[models.Model], cls: Optional[type[models.Model]] = None
    ) -> Optional[PackageURL]:
        return super().__get__(instance, cls)

    def __set__(
        self, instance: Optional[models.Model], value: Optional[str | PackageURL]
    ) -> None:
        if instance:
            instance.__dict__[self.field.name] = to_purl(value)


class PURLField(models.CharField):
    """
    Custom field for Package URLs (PURLs) that automatically handles
    conversion between string representation and PackageURL objects.

    This field:
    - Stores PURLs as strings in the database (using to_string())
    - Returns PackageURL objects when accessed through the ORM
    - Validates PURLs using PackageURL.from_string()
    - Handles None/empty values appropriately
    """

    description = "A field for storing Package URLs (PURLs)"
    descriptor_class = PURLDescriptor

    def __init__(self, *args, **kwargs):
        kwargs["blank"] = True
        kwargs["null"] = False
        super().__init__(*args, **kwargs)

    def to_python(self, value: Optional[str | PackageURL]) -> Optional[PackageURL]:
        return to_purl(value)

    def get_prep_value(self, value: Optional[str | PackageURL]) -> str:
        if value is None or value == "":
            return ""

        if isinstance(value, PackageURL):
            return value.to_string()

        try:
            # here we ensure that before querying / saving to the database
            # we normalize the string so that the order of e.g. qualifiers
            # is consistent
            return PackageURL.from_string(value).to_string()
        except ValueError as e:
            raise ValidationError(f"Invalid PURL: {e}")

    def from_db_value(
        self, value: Optional[str], expression, connection
    ) -> Optional[PackageURL]:
        return to_purl(value)
