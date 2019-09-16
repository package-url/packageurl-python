# packageurl-python

A parser and builder for purl Package URLs for Python 2 and 3.

See https://github.com/package-url/purl-spec for details.

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

Install
=======
::

    pip install packageurl-python



Running tests
=============

install::

    virtualenv .
    bin/pip install -r requirements_tests.txt

run tests::

    bin/py.test -vvs
