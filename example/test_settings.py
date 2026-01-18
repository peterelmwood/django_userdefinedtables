"""
Django test settings for django_userdefinedtables example project.
"""

from settings import *  # noqa

# Override database to use SQLite for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
