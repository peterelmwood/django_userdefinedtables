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

Run the test suite using Django's test runner:

```bash
DJANGO_SETTINGS_MODULE=test_settings python manage.py test
```

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
- Update CHANGELOG.md under the [Unreleased] section
- Keep changes focused - one feature/fix per PR when possible

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
