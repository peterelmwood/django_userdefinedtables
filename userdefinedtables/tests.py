from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from model_bakery import baker


class ColumnTestCase(TestCase):
    def test__list_cannot_have_two_identically_named_columns(self):
        # ASSIGN
        list_1 = baker.make("userdefinedtables.list")
        column_1 = baker.make(
            "userdefinedtables.column",
            list=list_1,
            name="duplicate",
        )

        # ACT
        # ASSERT
        with self.assertRaises(IntegrityError):
            baker.make("userdefinedtables.column", list=list_1, name=column_1.name)


class SingleLineOfTextColumnTestCase(TestCase):
    def test__singlelineoftextcolumn_maximum_length_cannot_exceed_max_length_of_255(self):
        # ASSIGN
        # ACT
        # ASSERT
        with self.assertRaises(IntegrityError):
            baker.make("userdefinedtables.singlelineoftextcolumn", maximum_length=256)

    def test__singlelineoftextcolumn_maximum_length_cannot_be_decreased_below_longest_entry(self):
        # ASSIGN
        column = baker.make("userdefinedtables.singlelineoftextcolumn", maximum_length=255)
        entry = baker.make("userdefinedtables.singlelineoftextcolumnentry", column=column, value="1" * 255)

        # ACT
        # ASSERT
        with self.assertRaises(ValueError):
            column.maximum_length = len(entry.value) - 1
            column.save()

    def test__singlelineoftextcolumnentry_cannot_be_exceed_singlelineoftextcolumn_maximum_length(self):
        # ASSIGN
        column = baker.make("userdefinedtables.singlelineoftextcolumn", maximum_length=255)

        # ACT
        # ASSERT
        with self.assertRaises(ValueError):
            entry = baker.make("userdefinedtables.singlelineoftextcolumnentry", column=column, value="1" * 256)


class ChoiceColumnTestCase(TestCase):
    def test__choice_cannot_be_deleted_after_foreign_keyed_by_choiceentry(self):
        # ASSIGN
        choice = baker.make("userdefinedtables.choice")
        choice_entry = baker.make("userdefinedtables.choiceentry", value=choice)

        # ACT
        # ASSERT
        with self.assertRaises(ProtectedError):
            choice.delete()


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
