# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.17] - 2026-09-16

### Changed
- Modernized Python tooling (#22):
  - Packaging metadata moved from `setup.py`/`setup.cfg` into a PEP 621 `pyproject.toml`; the version is read statically so isolated builds no longer import the package (fixes #20)
  - Dependencies are managed with [uv](https://docs.astral.sh/uv/) via `pyproject.toml` dependency groups and a committed `uv.lock`; the `requirements/` directory has been removed
  - black, isort and flake8 have been replaced by [ruff](https://docs.astral.sh/ruff/) for linting and formatting
  - pre-commit hooks updated (`pre-commit-hooks` v5.0.0 -> v6.0.0) and now include ruff, `uv lock` and django-upgrade
  - CI now uses uv, fails on lint findings, and tests an explicit Python x Django matrix
  - TestPyPI publishing only runs on `main` and is gated on the test workflow
  - Dependabot watches `pyproject.toml`/`uv.lock` (uv ecosystem) instead of `setup.py`/`requirements/*.txt`
- Dropped support for Python 3.8 and 3.9 (EOL); added Python 3.13 and 3.14
- Dropped support for Django 3.2, 4.0, 4.1 and 4.2 (EOL); minimum is now Django 5.2 LTS, added support for Django 6.0 and 6.1
- `CheckConstraint` definitions now use `condition=` instead of the `check=` argument removed in Django 6.0
- Example project switched from the unmaintained `django-bootstrap-v5` (which pins Django <5.0) to its successor `django-bootstrap5`; templates load `django_bootstrap5` instead of `bootstrap5`

## [0.0.16] - 2026-09-16

- Maintenance release with no user-facing changes.

## [0.0.15] - 2026-09-16

### Changed
- Removed `django-bootstrap-v5` from package dependencies (it's only used in the example app)
- Replaced wildcard import in `admin.py` with explicit imports for better code clarity
- Updated Python version support: dropped Python 3.6 and 3.7 (EOL), added Python 3.11 and 3.12
- Updated Django version support: minimum version is now Django 3.2 LTS, added support for Django 4.1 and 4.2
- Improved code quality with consistent formatting
- Bumped `pre-commit/pre-commit-hooks` from v3.4.0 to v5.0.0
- Brought the tree into compliance with the pre-commit hooks (trailing whitespace, end-of-file newlines, requirements ordering) and relaxed the hooks' Python pin from 3.9 to any Python 3
- Updated GitHub Actions workflows to test on Python 3.12 and use proper test settings
- Enhanced package metadata with project URLs and better configuration
- Improved package initialization with docstring and better exports
- Added verbose name to AppConfig for better admin display

### Removed
- Deprecated `default_app_config` attribute (removed in Django 5.0, no longer needed with Django 3.2+)

### Added
- Automatic releases: every merge to `main` bumps the version (level chosen by a `release:*` PR label, patch by default), tags it, publishes to PyPI, and creates a GitHub release
- Dependabot configuration for GitHub Actions, Python (library and example), and Docker dependencies, capped at 5 open PRs per ecosystem
- CHANGELOG.md to track project changes
- CONTRIBUTING.md with development guidelines and contribution instructions
- Proper test settings configuration for easier development
- Improved README with better value proposition, key features, and clearer installation instructions
- Enhanced example README with comprehensive setup instructions
- Flake8 configuration in setup.cfg
- Build system configuration in pyproject.toml
- isort configuration with first-party package recognition

## [0.0.14] - 2022

### Added
- Initial release with core functionality
- Support for multiple column types (Text, Number, Currency, DateTime, Binary, Picture, Lookup, URL, Choice)
- Admin interface registration for all models
- Multi-table inheritance for simplified querying
- Comprehensive test suite

[Unreleased]: https://github.com/peterelmwood/django_userdefinedtables/compare/v0.0.17...HEAD
[0.0.17]: https://github.com/peterelmwood/django_userdefinedtables/compare/v0.0.16...v0.0.17
[0.0.16]: https://github.com/peterelmwood/django_userdefinedtables/compare/v0.0.15...v0.0.16
[0.0.15]: https://github.com/peterelmwood/django_userdefinedtables/compare/v0.0.14...v0.0.15
[0.0.14]: https://github.com/peterelmwood/django_userdefinedtables/releases/tag/v0.0.14
