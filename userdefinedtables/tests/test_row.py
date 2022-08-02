#!/usr/bin/env python

"""
Tests the Row model of the django_userdefinedtables app.
"""

# stdlib

# django

# local django
from userdefinedtables.tests.test_orderable_mixin import OrderableMixinTestSuite

# thirdparty


class RowTestCase(OrderableMixinTestSuite.OrderableMixinTestCase):
    orderable_model = "userdefinedtables.row"
