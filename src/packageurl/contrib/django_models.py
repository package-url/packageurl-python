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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from packageurl import PackageURL


class PackageURLMixin(models.Model):
    """
    Abstract Model for Package URL "purl" fields support.
    """
    type = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        help_text=_(
            'A short code to identify the type of this package. '
            'For example: gem for a Rubygem, docker for a container, '
            'pypi for a Python Wheel or Egg, maven for a Maven Jar, '
            'deb for a Debian package, etc.'
        )
    )

    namespace = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_(
            'Package name prefix, such as Maven groupid, Docker image owner, '
            'GitHub user or organization, etc.'
        ),
    )

    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Name of the package.'),
    )

    version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Version of the package.'),
    )

    qualifiers = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text=_(
            'Extra qualifying data for a package such as the name of an OS, '
            'architecture, distro, etc.'
        ),
    )

    subpath = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_(
            'Extra subpath within a package, relative to the package root.'
        ),
    )

    class Meta:
        abstract = True

    @property
    def package_url(self):
        """
        Return a compact Package URL "purl" string.
        """
        try:
            purl = PackageURL(
                self.type, self.namespace, self.name,
                self.version, self.qualifiers, self.subpath
            )
        except ValueError:
            return ''
        return str(purl)

    def set_package_url(self, package_url):
        """
        Set values for each related field of the provided `package_url` string.
        Empty/Null values are normalized to `None` and are set as well
        to replace any existing values.
        This prevent mixing newly provided values with old ones.
        """
        purl = PackageURL.from_string(package_url)

        for field_name, value in purl.to_dict().items():
            setattr(self, field_name, value or None)
