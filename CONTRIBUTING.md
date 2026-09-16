# Contributing to django_userdefinedtables

Thank you for your interest in contributing to django_userdefinedtables! This document provides guidelines and instructions for contributing to this project.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for environment and dependency management and [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

1. Install uv (see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)).

2. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/django_userdefinedtables.git
   cd django_userdefinedtables
   ```

3. Create the virtual environment and install all dependencies (including the `dev` group):
   ```bash
   uv sync
   ```

   uv will install the Python version from `.python-version` if it isn't already available.

4. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Running Tests

Run the package's test suite using Django's test runner from the repository root:

```bash
DJANGO_SETTINGS_MODULE=test_settings uv run manage.py test userdefinedtables
```

The `userdefinedtables` label matters: an unscoped run also discovers the example project's tests,
which cannot run under the root `test_settings.py`.

The example project has its own tests and settings. Run them from the `example/` directory:

```bash
cd example
uv run --project .. manage.py test example.apps.userplayground --settings=test_settings
```

See [example/README.md](example/README.md#running-the-tests) for details. CI runs both commands.

To test against a specific Django version, install it into the environment first:

```bash
uv pip install "Django~=6.0.0"
DJANGO_SETTINGS_MODULE=test_settings uv run --no-sync manage.py test userdefinedtables
```

## Code Style

This project uses **ruff** for both linting and formatting (line length: 120). Configuration lives in `pyproject.toml`.

Formatting and linting are enforced via pre-commit hooks and in CI. To run them manually:

```bash
uv run ruff format .        # format
uv run ruff check --fix .   # lint and apply safe autofixes
```

Or without a project environment, via `uvx`:

```bash
uvx ruff format .
uvx ruff check .
```

## Managing Dependencies

Runtime dependencies live under `[project] dependencies` in `pyproject.toml`; development and test dependencies live under `[dependency-groups]`. After changing either, refresh the lockfile and commit `uv.lock`:

```bash
uv lock
```

The `uv-lock` pre-commit hook will fail if `uv.lock` is out of sync with `pyproject.toml`.

## Building the Package

```bash
uv build
```

This produces an sdist and a wheel in `dist/`. The version is read from `userdefinedtables/__init__.py`.

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
- Update CHANGELOG.md under the [Unreleased] section
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

## Dependency Updates

Dependency bumps are raised automatically by [Dependabot](https://docs.github.com/en/code-security/dependabot)
according to `.github/dependabot.yml`. It watches the GitHub Actions workflows, `pyproject.toml`/`uv.lock` for the
library and its development tooling, the example project's `requirements.txt`, and the example project's Docker base
image, and opens at most five pull requests per ecosystem at a time.

Please review and merge those pull requests rather than opening manual version bumps. The one exception is
`.pre-commit-config.yaml`, which Dependabot does not manage; refresh it with:

```bash
uv run pre-commit autoupdate
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
