# Contributing to django_userdefinedtables

Thank you for your interest in contributing to django_userdefinedtables! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/django_userdefinedtables.git
   cd django_userdefinedtables
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   pip install -r requirements/dev.txt
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Running Tests

Run the package's test suite using Django's test runner from the repository root:

```bash
DJANGO_SETTINGS_MODULE=test_settings python manage.py test userdefinedtables
```

The `userdefinedtables` label matters: an unscoped run also discovers the example project's tests,
which cannot run under the root `test_settings.py`.

The example project has its own tests and settings. Run them from the `example/` directory:

```bash
cd example
PYTHONPATH=.. python manage.py test example.apps.userplayground --settings=test_settings
```

See [example/README.md](example/README.md#running-the-tests) for details. CI runs both commands.

## Code Style

This project uses:
- **Black** for code formatting (line length: 120)
- **isort** for import sorting
- **flake8** for linting

These are enforced via pre-commit hooks. To manually format your code:

```bash
black . --line-length 120
isort . --profile black
```

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, ensuring:
   - All tests pass
   - Code is properly formatted
   - New features include tests
   - Documentation is updated if needed

3. Commit your changes with a clear commit message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

4. Push to your fork and create a pull request

## Pull Request Guidelines

- Include a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update CHANGELOG.md under the [Unreleased] section (it becomes the release notes; see Releasing)
- Do not change `__version__`; the release workflow bumps it on merge
- Keep changes focused - one feature/fix per PR when possible

## Dependency Updates

Dependency bumps are raised automatically by [Dependabot](https://docs.github.com/en/code-security/dependabot)
according to `.github/dependabot.yml`. It watches the GitHub Actions workflows, the Python requirements for the
library and the example project, and the example project's Docker base image, and opens at most five pull requests
per ecosystem at a time.

Please review and merge those pull requests rather than opening manual version bumps. The one exception is
`.pre-commit-config.yaml`, which Dependabot does not manage; refresh it with:

```bash
pre-commit autoupdate
```

## Releasing

Every pull request merged into `main` is released automatically by the
`Release on merge to main` workflow (`.github/workflows/release.yml`). On merge it:

1. Works out the bump level from the `release:*` labels of every pull request
   merged since the last release, as they were when each was merged (the
   highest wins):
   - `release:major` → `X.0.0`
   - `release:minor` → `X.Y.0`
   - `release:patch` (or no label) → `X.Y.Z`
   - `release:skip` on the merged PR → its merge does not start a release; the
     changes ship with the next one
2. Bumps `__version__` in `userdefinedtables/__init__.py` and moves the
   `[Unreleased]` section of `CHANGELOG.md` under the new version.
3. Commits that to `main` and tags it `vX.Y.Z`.
4. Builds the package, publishes it to PyPI, and creates a GitHub release using
   the changelog section as the release notes.

The workflow is safe to re-run: it first completes any release whose earlier run
failed after the version commit landed on `main`, then cuts a new release only if
something has merged since. The logic lives in `scripts/release.sh`.

So: do not edit `__version__` in a pull request, keep your changes listed under
`[Unreleased]` in `CHANGELOG.md`, and add a `release:*` label if the default
patch bump is not right. The workflow can be exercised locally without
publishing:

```bash
python scripts/release.py bump patch      # edits __init__.py and CHANGELOG.md
python scripts/release.py notes 0.0.15    # prints the release notes for a version
python -m unittest discover -s scripts -p 'test_*.py'
```

## Reporting Issues

When reporting issues, please include:
- Django version
- Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Any relevant error messages or stack traces

## Questions?

Feel free to open an issue for questions or discussions about the project.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
