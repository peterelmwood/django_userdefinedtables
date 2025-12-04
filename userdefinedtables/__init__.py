"""
django_userdefinedtables

A Django application for user-defined tables with EAV-style flexibility.
"""

__version__ = "0.0.14"

VERSION = __version__

default_app_config = "userdefinedtables.apps.UserdefinedtablesConfig"

# Public API
__all__ = [
    "__version__",
    "VERSION",
]
