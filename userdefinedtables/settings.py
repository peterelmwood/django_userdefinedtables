from django.conf import settings

USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS = getattr(settings, "USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS", {})

USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS.setdefault("decimal_places", 4)
USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS.setdefault("max_digits", 16)
