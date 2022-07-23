#!/usr/bin/env python

"""
Tests the CurrencyColumn model of the userdefinedtables app.
"""

# stdlib

# django
from django.db import IntegrityError
from django.test import TestCase

# local django


# thirdparty
from model_bakery import baker


class CurrencyColumnTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.currency_column = baker.make("userdefinedtables.currencycolumn", maximum=10, minimum=1)

    def test__currencycolumn_minimum_cannot_be_more_than_maximum(self):
        # ASSIGN
        # ACT
        # ASSERT
        with self.assertRaises(IntegrityError):
            baker.make("userdefinedtables.currencycolumn", minimum=10, maximum=1)

    def test__set_no_maximum__works_as_expected(self):
        # ASSIGN
        # ACT
        self.currency_column.set_no_maximum()

        # ASSERT
        self.assertTrue(self.currency_column.lte_maximum(10**6))

    def test__set_no_minimum__works_as_expected(self):
        # ASSIGN
        # ACT
        self.currency_column.set_no_minimum()

        # ASSERT
        self.assertTrue(self.currency_column.gte_minimum(-100))

    def test__gte_minimum__works_as_expected_with_numerical_minimum(self):
        # ASSIGN
        # ACT
        # ASSERT
        self.assertEqual(1, self.currency_column.minimum)
        self.assertGreater(5, self.currency_column.minimum)
        self.assertTrue(self.currency_column.gte_minimum(20))

    def test__gte_minimum__works_as_expected_with_null_minimum(self):
        # ASSIGN
        # ACT
        self.currency_column.set_no_minimum()

        # ASSERT
        self.assertIsNone(self.currency_column.minimum)

        # essentially this tests that there is no minimum, but we can't truly do that
        self.assertTrue(self.currency_column.gte_minimum(-(2**32)))

    def test__lte_maximum__works_as_expected_with_numerical_maximum(self):
        # ASSIGN
        # ACT
        # ASSERT
        self.assertEqual(10, self.currency_column.maximum)
        self.assertLess(5, self.currency_column.maximum)
        self.assertTrue(self.currency_column.lte_maximum(5))

    def test__lte_maximum__works_as_expected_with_null_maximum(self):
        # ASSIGN
        # ACT
        self.currency_column.set_no_maximum()

        # ASSERT
        self.assertIsNone(self.currency_column.maximum)

        # essentially this tests that there is no maximum, but we can't truly do that
        self.assertTrue(self.currency_column.lte_maximum(2**32))
