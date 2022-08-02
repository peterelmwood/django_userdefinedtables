from django.db import IntegrityError
from django.test import TestCase

from model_bakery import baker

from userdefinedtables.tests.test_orderable_mixin import OrderableMixinTestSuite


class ColumnTestCase(OrderableMixinTestSuite.OrderableMixinTestCase):
    orderable_model = "userdefinedtables.column"

    def test__list_cannot_have_two_identically_named_columns(self):
        # ASSIGN
        list_1 = baker.make("userdefinedtables.list")
        column_1 = baker.make(
            self.orderable_model,
            list=list_1,
            name="duplicate",
        )

        # ACT
        # ASSERT
        with self.assertRaises(IntegrityError):
            baker.make(self.orderable_model, list=list_1, name=column_1.name)
