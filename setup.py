#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


setup(
    name='purl-python',
    version='0.1.0',
    license='MIT',
    description='A "purl" aka. package URL parser and builder.',
    long_description='Python library to parse and build "purl" aka. package URLs.',
    author='the purl authors',
    url='https://github.com/package-url/purl-python',
    packages=find_packages('src'),
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    platforms='any',
    keywords='package, url, package manager, package url',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
