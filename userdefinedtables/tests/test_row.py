#!/usr/bin/env python

"""
Tests the Row model of the django_userdefinedtables app.
"""

# stdlib

# django
from django.db import IntegrityError
from django.test.testcases import TestCase

# local django

# thirdparty
from model_bakery import baker


class RowTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test__two_rows_cannot_be_first_row_in_list(self):
        # ASSIGN
        list = baker.make("userdefinedtables.list")
        row_1 = baker.make("userdefinedtables.row", list=list, previous_row=None)

        # ACT
        # ASSERT
        with self.assertRaises(IntegrityError):
            baker.make("userdefinedtables.row", list=list, previous_row=None)

    def test__two_rows_cannot_be_last_row_in_list(self):
        # ASSIGN
        list = baker.make("userdefinedtables.list")
        row_1 = baker.make("userdefinedtables.row", list=list, next_row=None)

        # ACT
        # ASSERT
        with self.assertRaises(IntegrityError):
            baker.make("userdefinedtables.row", list=list, next_row=None)

    def test__list_with_row_must_have_first_row(self):
        # ASSIGN
        list = baker.make("userdefinedtables.list")
        row_1 = baker.make("userdefinedtables.row", list=list)
        row_2 = baker.make("userdefinedtables.row", list=list, previous_row=row_1)

        # ACT

        # ASSERT
        with self.assertRaises(IntegrityError):
            row_1.previous_row = row_2
            row_1.save()
