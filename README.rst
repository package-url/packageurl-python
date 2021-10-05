# packageurl-python

Python library to parse and build "purl" aka. Package URLs.
See https://github.com/package-url/purl-spec for details.

Join the discussion at https://gitter.im/package-url/Lobby or enter a ticket for support.

License: MIT


Build and tests status
======================

+------------------------------------------------------------------------------------+
|                         **Linux (Travis) on Python 2 and 3**                       |
+====================================================================================+
|.. image:: https://api.travis-ci.com/package-url/packageurl-python.png?branch=master|
|   :target: https://travis-ci.com/package-url/packageurl-python                     |
|   :alt: Linux Master branch tests status                                           |
+------------------------------------------------------------------------------------+


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


Other utilities:

- packageurl.contrib.django_models.PackageURLMixin is a Django abstract model mixin to use Package URLs in Django.
- packageurl.contrib.purl2url.get_url(purl) returns the download URL inferred from a Package URL.
- packageurl.contrib.url2purl.get_purl(url) returns a Package URL inferred from URL.


Install
=======
::

    pip install packageurl-python

Run tests
=========

install::

    python3 thirdparty/virtualenv.pyz --never-download --no-periodic-update .
    bin/pip install -e ."[test]"

run tests::

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
