Changelog
=========

0.16.0 (unreleased)
-------------------

0.15.2 (2024-07-04)
-------------------

- Update GitHub generated Download URL for maximum compatibility.
  https://github.com/package-url/packageurl-python/issues/157

0.15.1 (2024-06-13)
-------------------

- Add support for Composer in ``purl2url`` and ``url2purl``.
  https://github.com/package-url/packageurl-python/pull/144

- Add an option for ``exact_match`` purl QuerySet lookups in the
  ``PackageURLQuerySetMixin.for_package_url``method.
  https://github.com/package-url/packageurl-python/issues/118

0.15.0 (2024-03-12)
-------------------

- Add support to get PackageURL from ``go_package`` or 
  go module ``name version`` string as seen in a go.mod file.
  https://github.com/package-url/packageurl-python/pull/148

- Add cran ecosystem support for url2purl
  https://github.com/package-url/packageurl-python/pull/149

0.14.0 (2024-02-29)
-------------------

- Add support for getting golang purl from go import.
  https://github.com/nexB/purldb/issues/259

- Fix the "gem" type in the README docs.
  https://github.com/package-url/packageurl-python/pull/114

0.13.4 (2024-01-08)
-------------------

- Improve support for SourceForge URLs in `url2purl`.
  https://github.com/package-url/packageurl-python/issues/139

0.13.3 (2024-01-04)
-------------------

- Improve support for SourceForge URLs in `url2purl`.
  https://github.com/package-url/packageurl-python/issues/139

0.13.2 (2024-01-04)
-------------------

- Improve support for SourceForge URLs in `url2purl`.
  https://github.com/package-url/packageurl-python/issues/139

0.13.1 (2023-12-11)
-------------------

- Add support for Python 3.12
  https://github.com/package-url/packageurl-python/pull/135

0.13.0 (2023-12-08)
-------------------

- Revert changes from 
  https://github.com/package-url/packageurl-python/pull/115/ 
  In above PR we dropped namespaces for a golang purl and stored 
  whole namespace and name in name itself, which was further discussed 
  again and decided we will like to keep namespace back. 

0.12.0 (2023-12-08)
-------------------

- Modified `PackageURL.from_string` to properly handle golang purls.
  https://github.com/package-url/packageurl-python/pull/115/

- Improve support for PyPI URLs in `url2purl`.
  https://github.com/package-url/packageurl-python/pull/128

- Return the "gem" type instead of "rubygems" for "https://rubygems.org/" URLs in
  `url2purl`. The `pkg:rubygems/` purls are backward-compatible in `purl2url`.
  https://github.com/package-url/packageurl-python/pull/114/

0.11.3 (2023-12-08)
--------------------

- Add support for GitLab "/archive/" URLs in `url2purl`.
  https://github.com/package-url/packageurl-python/issues/133

0.11.2 (2022-07-25)
--------------------

- Remove deprecated `purl_to_lookups` and `without_empty_values` import compatibility
  from `packageurl.contrib.django.models`.
  Replace those functions import using `packageurl.contrib.django.utils`.
- Add download purl2url support for bitbucket and gitlab.

0.11.1 (2022-03-24)
-------------------

- Add support for the golang type in `purl2url.get_repo_url()` #107

0.11.0rc1 (2022-12-29)
----------------------

- Apply typing
- Add support for Python 3.11
- Fix minor typos
- Drop Python 3.6


0.10.5rc1 (2022-12-28)
----------------------

- Fixed `PackageURL.from_string` to properly handle npm purls with namespace.


0.10.4 (2022-10-17)
-------------------

- Refactor the purl2url functions and utilities #42

  - Split purl2url into `get_repo_url()` and `get_download_url()` returning
    accordingly a "Repository URL" and a "Download URL".
  - A new `get_inferred_urls` function is available to get return all
    inferred URLs (repository and download) values.
  - Add support in purl2url for npm, pypi, hackage, and nuget.
  - Package URL qualifiers can now be provided to `purl_from_pattern()`.
  - The `download_url` qualifier is returned in `get_download_url()` when available.

- Usage of `purl2url.purl2url` and `purl2url.get_url` is still available for
  backward compatibility but should be migrated to `purl2url.get_repo_url`.

- Include the `version_prefix` ("v" or "V") as a qualifier in build_github_purl #42
  This allow to infer valid URLs in the context of purl2url.


0.10.3 (2022-09-15)
-------------------

- Fix named arguments in purl_to_lookups.


0.10.2 (2022-09-15)
-------------------

- Add encode option in purl_lookups #94 
  (`purl_to_lookups`, `without_empty_values` is moved from packageurl.contrib.django.models
  to packageurl.contrib.django.utils)


0.10.1 (2022-08-02)
-------------------

- Add ability to filter objects with EMPTY purls in PackageURLFilter #92


0.10.0 (2022-06-27)
-------------------

- Upgrade virtualenv.pyz to latest version #85
- Replace Travis CI by GitHub Actions #84
- Add black to the CI and apply formatting on whole codebase #91
- Improve url2purl support for nom URLs
- Improve url2purl support for rubygems.org URLs #89


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
