#!/usr/bin/env python

"""
Tests the Row model of the django_userdefinedtables app.
"""

# stdlib

# django
from django.test import TestCase

# local django

# thirdparty
from model_bakery import baker


class RowTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test__adding_a_new_row_at_existing_index_moves_the_occupying_row(self):
        # ASSIGN
        list = baker.make("userdefinedtables.list")
        row_1 = baker.make("userdefinedtables.row", list=list, index=1)

        # ACT
        row_2 = baker.make("userdefinedtables.row", list=list, index=1)
        row_1.refresh_from_db()

        # ASSERT
        self.assertEqual(2, row_1.index)
        self.assertEqual(1, row_2.index)

    def test__inserting_an_existing_row_into_lower_index_moves_other_rows_up(self):
        # ASSIGN
        my_list = baker.make("userdefinedtables.list")
        row_1 = baker.make("userdefinedtables.row", list=my_list, index=1)
        row_2 = baker.make("userdefinedtables.row", list=my_list, index=2)

        # ACT
        row_2.insert_at(1)
        row_1.refresh_from_db()

        # ASSERT
        self.assertEqual(2, row_1.index)
        self.assertEqual(1, row_2.index)

    def test__inserting_an_existing_row_into_higher_index_moves_other_rows_down(self):
        # ASSIGN
        my_list = baker.make("userdefinedtables.list")
        row_1 = baker.make("userdefinedtables.row", list=my_list, index=1)
        row_2 = baker.make("userdefinedtables.row", list=my_list, index=2)

        # ACT
        row_1.insert_at(2)
        row_2.refresh_from_db()

        # ASSERT
        self.assertEqual(2, row_1.index)
        self.assertEqual(1, row_2.index)

    def test__deleting_row_lower_than_others_moves_them_down(self):
        # ASSIGN
        my_list = baker.make("userdefinedtables.list")
        row_1 = baker.make("userdefinedtables.row", list=my_list, index=1)
        row_2 = baker.make("userdefinedtables.row", list=my_list, index=2)

        # ACT
        row_1.delete()
        row_2.refresh_from_db()

        # ASSERT
        self.assertEqual(1, row_2.index)
