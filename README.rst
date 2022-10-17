=================
packageurl-python
=================

Python library to parse and build "purl" aka. Package URLs.
See https://github.com/package-url/purl-spec for details.

Join the discussion at https://gitter.im/package-url/Lobby or enter a ticket for support.

License: MIT

Tests and build status
======================

+----------------------+
| **Tests and build**  |
+======================+
| |ci-tests|           |
+----------------------+

Install
=======
::

    pip install packageurl-python

Usage
=====
::

    >>> from packageurl import PackageURL

    >>> purl = PackageURL.from_string("pkg:maven/org.apache.commons/io@1.3.4")
    >>> print(purl.to_dict())
    {'type': 'maven', 'namespace': 'org.apache.commons', 'name': 'io', 'version': '1.3.4', 'qualifiers': None, 'subpath': None}

    >>> print(purl.to_string())
    pkg:maven/org.apache.commons/io@1.3.4

    >>> print(str(purl))
    pkg:maven/org.apache.commons/io@1.3.4

    >>> print(repr(purl))
    PackageURL(type='maven', namespace='org.apache.commons', name='io', version='1.3.4', qualifiers={}, subpath=None)

Utilities
=========

Django models
^^^^^^^^^^^^^

`packageurl.contrib.django_models.PackageURLMixin` is a Django abstract model mixin to use Package URLs in Django.

URL to PURL
^^^^^^^^^^^

`packageurl.contrib.url2purl.get_purl(url)` returns a Package URL inferred from an URL.

::

    >>> from packageurl.contrib import url2purl
    >>> url2purl.get_purl("https://github.com/package-url/packageurl-python")
    PackageURL(type='github', namespace='package-url', name='packageurl-python', version=None, qualifiers={}, subpath=None)

PURL to URL
^^^^^^^^^^^

- `packageurl.contrib.purl2url.get_repo_url(purl)` returns a repository URL inferred from a Package URL.
- `packageurl.contrib.purl2url.get_download_url(purl)` returns a download URL inferred from a Package URL.
- `packageurl.contrib.purl2url.get_inferred_urls(purl)` return all inferred URLs (repository, download) from a Package URL.

::

    >>> from packageurl.contrib import purl2url

    >>> purl2url.get_repo_url("pkg:rubygems/bundler@2.3.23")
    "https://rubygems.org/gems/bundler/versions/2.3.23"

    >>> purl2url.get_download_url("pkg:rubygems/bundler@2.3.23")
    "https://rubygems.org/downloads/bundler-2.3.23.gem"

    >>> purl2url.get_inferred_urls("pkg:rubygems/bundler@2.3.23")
    ["https://rubygems.org/gems/bundler/versions/2.3.23", "https://rubygems.org/downloads/bundler-2.3.23.gem",]

Run tests
=========

Install test dependencies::

    python3 thirdparty/virtualenv.pyz --never-download --no-periodic-update .
    bin/pip install -e ."[test]"

Run tests::

    bin/py.test tests

Make a new release
==================

- start a new release branch
- update the CHANGELOG.rst and AUTHORS.rst
- update README.rst if needed
- bump version in setup.cfg
- run all tests
- install restview and validate that all .rst docs are correct
- commit and push this branch
- tag and push that tag
- make a PR to merge branch
- once merged, run::

    bin/pip install --upgrade pip wheel twine setuptools

- delete the "dist" and "build" directories::

    rm -rf dist/ build/

- create a source distribution and wheel with::

    bin/python setup.py sdist bdist_wheel

- finally, upload to PyPI::

    bin/twine upload dist/*


.. |ci-tests| image:: https://github.com/package-url/packageurl-python/actions/workflows/ci.yml/badge.svg?branch=main
    :target: https://github.com/package-url/packageurl-python/actions/workflows/ci.yml
    :alt: CI Tests and build status
