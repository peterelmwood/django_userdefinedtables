# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Removed `django-bootstrap-v5` from package dependencies (it's only used in the example app)
- Replaced wildcard import in `admin.py` with explicit imports for better code clarity
- Updated Python version support: dropped Python 3.6 and 3.7 (EOL), added Python 3.11 and 3.12
- Updated Django version support: minimum version is now Django 3.2 LTS, added support for Django 4.1 and 4.2
- Improved code quality with consistent formatting
- Updated GitHub Actions workflows to test on Python 3.12 and use proper test settings

### Added
- CHANGELOG.md to track project changes
- CONTRIBUTING.md with development guidelines and contribution instructions
- Proper test settings configuration for easier development
- Improved README with better value proposition, key features, and clearer installation instructions
- Enhanced example README with comprehensive setup instructions

## [0.0.14] - 2022

### Added
- Initial release with core functionality
- Support for multiple column types (Text, Number, Currency, DateTime, Binary, Picture, Lookup, URL, Choice)
- Admin interface registration for all models
- Multi-table inheritance for simplified querying
- Comprehensive test suite

[Unreleased]: https://github.com/peterelmwood/django_userdefinedtables/compare/v0.0.14...HEAD
[0.0.14]: https://github.com/peterelmwood/django_userdefinedtables/releases/tag/v0.0.14
