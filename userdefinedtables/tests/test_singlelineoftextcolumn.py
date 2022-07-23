from django.db import IntegrityError
from django.test import TestCase

from model_bakery import baker


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
