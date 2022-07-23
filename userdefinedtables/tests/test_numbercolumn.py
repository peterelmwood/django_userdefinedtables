from django.db import IntegrityError
from django.test import TestCase

from model_bakery import baker


class NumberColumnTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.number_column = baker.make("userdefinedtables.numbercolumn", maximum=10, minimum=1)

    def test__numbercolumn_minimum_cannot_be_more_than_maximum(self):
        # ASSIGN
        # ACT
        # ASSERT
        with self.assertRaises(IntegrityError):
            baker.make("userdefinedtables.numbercolumn", minimum=10, maximum=1)

    def test__set_no_maximum__works_as_expected(self):
        # ASSIGN
        # ACT
        self.number_column.set_no_maximum()

        # ASSERT
        self.assertTrue(self.number_column.lte_maximum(10**6))

    def test__set_no_minimum__works_as_expected(self):
        # ASSIGN
        # ACT
        self.number_column.set_no_minimum()

        # ASSERT
        self.assertTrue(self.number_column.gte_minimum(-100))

    def test__gte_minimum__works_as_expected_with_numerical_minimum(self):
        # ASSIGN
        # ACT
        # ASSERT
        self.assertEqual(1, self.number_column.minimum)
        self.assertGreater(5, self.number_column.minimum)
        self.assertTrue(self.number_column.gte_minimum(20))

    def test__gte_minimum__works_as_expected_with_null_minimum(self):
        # ASSIGN
        # ACT
        self.number_column.set_no_minimum()

        # ASSERT
        self.assertIsNone(self.number_column.minimum)

        # essentially this tests that there is no minimum, but we can't truly do that
        self.assertTrue(self.number_column.gte_minimum(-(2**32)))

    def test__lte_maximum__works_as_expected_with_numerical_maximum(self):
        # ASSIGN
        # ACT
        # ASSERT
        self.assertEqual(10, self.number_column.maximum)
        self.assertLess(5, self.number_column.maximum)
        self.assertTrue(self.number_column.lte_maximum(5))

    def test__lte_maximum__works_as_expected_with_null_maximum(self):
        # ASSIGN
        # ACT
        self.number_column.set_no_maximum()

        # ASSERT
        self.assertIsNone(self.number_column.maximum)

        # essentially this tests that there is no maximum, but we can't truly do that
        self.assertTrue(self.number_column.lte_maximum(2**32))
