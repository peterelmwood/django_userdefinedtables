from django.db import IntegrityError
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
