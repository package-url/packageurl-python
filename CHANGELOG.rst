Changelog
=========

0.9.9 (2022-02-15)
------------------

- Update version to be semver compliant. No changes to the code have been made.

0.9.8.1 (2022-02-11)
--------------------

- Fix generic sourceforge PackageURL generation #79

0.9.8 (2022-02-11)
------------------

- Do not create a generic PackageURL for URLs without a path in url2purl #72
- Use project name as the Package name when creating generic sourceforge PackageURLs #74
- Update PyPI route pattern in url2purl to handle different file name formats #76
- Create generic PackageURL for code.google.com archive URLs #78
- Capture more download types for bitbucket URLs

0.9.7 (2022-02-07)
------------------

- Create a generic PackageURL for URLs that do not fit existing routes in url2purl #68

0.9.6 (2021-10-05)
------------------

- Drop support for Python 2 #61
- Add support for new github URLs in url2purl #47

0.9.5 (2021-10-04)
------------------

- Add support for "archive/refs/tags/" github URLs in url2purl #47

0.9.4 (2021-02-02)
------------------

- Fix Python 2 compatibility issue #57

0.9.3 (2020-10-06)
------------------

- Add QuerySet utils to lookup and filter along the PackageURLMixin Django class #48
- Add a PackageURLFilter class for Django FilterSet implementations #48
- Move the django_models module to django.models #48
  Replace `packageurl.contrib.django_models` imports with `packageurl.contrib.django.models`.

0.9.2 (2020-09-15)
------------------

- Document usage in README
- Adopt SPDX license identifier
- Add support for GitHub "raw" URLs in url2purl #43
- Improve GitHub support for "v" prefixed version in url2purl #43


0.9.1 (2020-08-05)
------------------

- Add and improve URL <-> Package URL conversion for gitlab, github, cargo,
  bitbucket and hackage URL conversions
- Add new purl2url conversion utility
- Remove the null=True on Django CharField fields of the PackageURLMixin
- PackageURL.to_dict() now takes an optional "empty" argument with the value
  that empty values to have. It defaults to None which was the current behaviour.
  For some use cases, having an empty string may be a better option and this
  enables this.


0.9.0 (2020-05-21)
------------------

- Make PackageURL hashable.
- Add cargo type or url2purl
- Increase the size of the Django model contrib version to 100 chars.
- Remove Python 3 idioms (f strings)

0.8.7 (2019-08-15)
------------------

- Add max length validation to the Django model contrib.
