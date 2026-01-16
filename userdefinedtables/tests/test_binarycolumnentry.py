from django.test import TestCase

from model_bakery import baker

from userdefinedtables.models import BinaryColumn, BinaryColumnEntry, Row


class BinaryColumnEntryTestCase(TestCase):
    def test__optional_binary_column_can_be_left_unset(self):
        """Test that an optional binary column does not require an entry."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=False,
        )
        row = baker.make("userdefinedtables.row", list=list_1)
        
        # ACT - Don't create an entry for the binary column
        # No entry created means the value is "unset" (not False or True)
        
        # ASSERT
        # There should be no entry for this row/column combination
        entries = BinaryColumnEntry.objects.filter(row=row, column=binary_column)
        self.assertEqual(entries.count(), 0)

    def test__optional_binary_column_can_be_set_to_false(self):
        """Test that an optional binary column can explicitly be set to False."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=False,
        )
        row = baker.make("userdefinedtables.row", list=list_1)
        
        # ACT - Explicitly create an entry with value=False
        entry = BinaryColumnEntry.objects.create(
            row=row,
            column=binary_column,
            value=False
        )
        
        # ASSERT
        # Entry should exist with value False
        self.assertIsNotNone(entry)
        self.assertFalse(entry.value)
        entries = BinaryColumnEntry.objects.filter(row=row, column=binary_column)
        self.assertEqual(entries.count(), 1)

    def test__optional_binary_column_can_be_set_to_true(self):
        """Test that an optional binary column can be set to True."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=False,
        )
        row = baker.make("userdefinedtables.row", list=list_1)
        
        # ACT - Create an entry with value=True
        entry = BinaryColumnEntry.objects.create(
            row=row,
            column=binary_column,
            value=True
        )
        
        # ASSERT
        self.assertIsNotNone(entry)
        self.assertTrue(entry.value)

    def test__required_binary_column_must_have_entry(self):
        """Test that a required binary column should have an entry."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=True,
        )
        row = baker.make("userdefinedtables.row", list=list_1)
        
        # ACT - Create an entry (required)
        entry = BinaryColumnEntry.objects.create(
            row=row,
            column=binary_column,
            value=False
        )
        
        # ASSERT
        self.assertIsNotNone(entry)
        entries = BinaryColumnEntry.objects.filter(row=row, column=binary_column)
        self.assertEqual(entries.count(), 1)
