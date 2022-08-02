#!/usr/bin/env python

"""
Defines the boilerplate tests for models that inherit the OrderableMixin.
"""

# stdlib
from typing import Union

# django
from django.test import TestCase

# local django

# thirdparty
from model_bakery import baker


class OrderableMixinTestSuite:
    class OrderableMixinTestCase(TestCase):
        orderable_model: Union[str, None] = None

        def test__adding_a_new_row_at_existing_index_moves_the_occupying_row(self):
            # ASSIGN
            list = baker.make("userdefinedtables.list")
            orderable_item_1 = baker.make(self.orderable_model, list=list, index=1)

            # ACT
            orderable_item_2 = baker.make(self.orderable_model, list=list, index=1)
            orderable_item_1.refresh_from_db()

            # ASSERT
            self.assertEqual(2, orderable_item_1.index)
            self.assertEqual(1, orderable_item_2.index)

        def test__inserting_an_existing_row_into_lower_index_moves_other_rows_up(self):
            # ASSIGN
            my_list = baker.make("userdefinedtables.list")
            orderable_item_1 = baker.make(self.orderable_model, list=my_list, index=1)
            orderable_item_2 = baker.make(self.orderable_model, list=my_list, index=2)

            # ACT
            orderable_item_2.insert_at(1)
            orderable_item_1.refresh_from_db()

            # ASSERT
            self.assertEqual(2, orderable_item_1.index)
            self.assertEqual(1, orderable_item_2.index)

        def test__inserting_an_existing_row_into_higher_index_moves_other_rows_down(self):
            # ASSIGN
            my_list = baker.make("userdefinedtables.list")
            orderable_item_1 = baker.make(self.orderable_model, list=my_list, index=1)
            orderable_item_2 = baker.make(self.orderable_model, list=my_list, index=2)

            # ACT
            orderable_item_1.insert_at(2)
            orderable_item_2.refresh_from_db()

            # ASSERT
            self.assertEqual(2, orderable_item_1.index)
            self.assertEqual(1, orderable_item_2.index)

        def test__deleting_row_lower_than_others_moves_them_down(self):
            # ASSIGN
            my_list = baker.make("userdefinedtables.list")
            orderable_item_1 = baker.make(self.orderable_model, list=my_list, index=1)
            orderable_item_2 = baker.make(self.orderable_model, list=my_list, index=2)

            # ACT
            orderable_item_1.delete()
            orderable_item_2.refresh_from_db()

            # ASSERT
            self.assertEqual(1, orderable_item_2.index)
