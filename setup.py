#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

from setuptools import find_packages
from setuptools import setup


setup(
    name='purl-python',
    version='0.1.3',
    license='MIT',
    description='A "purl" aka. package URL parser and builder.',
    long_description='Python library to parse and build "purl" aka. package URLs.',
    author='the purl authors',
    url='https://github.com/package-url/purl-python',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
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
