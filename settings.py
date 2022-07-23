from django.conf import settings

DECIMAL_FIELD_KWARGS = getattr(settings, "USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS", {})

DECIMAL_FIELD_KWARGS.setdefault("decimal_places", 4)
DECIMAL_FIELD_KWARGS.setdefault("max_places", 16)
