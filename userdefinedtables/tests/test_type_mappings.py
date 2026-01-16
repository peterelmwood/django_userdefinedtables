from django.test import TestCase

from userdefinedtables.models import (
    COLUMN_TO_ENTRY,
    COLUMN_TYPES,
    ENTRY_TO_COLUMN,
    ENTRY_TYPES,
    BinaryColumn,
    BinaryColumnEntry,
    ChoiceColumn,
    ChoiceEntry,
    CurrencyColumn,
    CurrencyEntry,
    DateTimeColumn,
    DateTimeColumnEntry,
    LookupColumn,
    LookupColumnEntry,
    MultipleLineTextColumn,
    MultipleLineTextColumnEntry,
    NumberColumn,
    NumberEntry,
    PictureColumn,
    PictureColumnEntry,
    SingleLineOfTextColumn,
    SingleLineOfTextColumnEntry,
    URLColumn,
    URLColumnEntry,
    get_column_type_for_entry,
    get_entry_type_for_column,
)


class TypeMappingTestCase(TestCase):
    """Test the bidirectional mappings between column types and entry types."""

    def test_column_types_and_entry_types_same_length(self):
        """COLUMN_TYPES and ENTRY_TYPES should have the same number of elements."""
        self.assertEqual(len(COLUMN_TYPES), len(ENTRY_TYPES))

    def test_column_to_entry_mapping_dict_created(self):
        """COLUMN_TO_ENTRY mapping dictionary should be created correctly."""
        self.assertEqual(len(COLUMN_TO_ENTRY), len(COLUMN_TYPES))
        # Verify all column types are keys
        for col_type in COLUMN_TYPES:
            self.assertIn(col_type, COLUMN_TO_ENTRY)

    def test_entry_to_column_mapping_dict_created(self):
        """ENTRY_TO_COLUMN mapping dictionary should be created correctly."""
        self.assertEqual(len(ENTRY_TO_COLUMN), len(ENTRY_TYPES))
        # Verify all entry types are keys
        for entry_type in ENTRY_TYPES:
            self.assertIn(entry_type, ENTRY_TO_COLUMN)

    def test_singlelineoftext_mapping(self):
        """Test mapping for SingleLineOfText types (has 'column' in name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(SingleLineOfTextColumn),
            SingleLineOfTextColumnEntry
        )
        self.assertEqual(
            COLUMN_TO_ENTRY[SingleLineOfTextColumn],
            SingleLineOfTextColumnEntry
        )
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(SingleLineOfTextColumnEntry),
            SingleLineOfTextColumn
        )
        self.assertEqual(
            ENTRY_TO_COLUMN[SingleLineOfTextColumnEntry],
            SingleLineOfTextColumn
        )

    def test_multiplelinetext_mapping(self):
        """Test mapping for MultipleLineText types (has 'column' in name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(MultipleLineTextColumn),
            MultipleLineTextColumnEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(MultipleLineTextColumnEntry),
            MultipleLineTextColumn
        )

    def test_datetime_mapping(self):
        """Test mapping for DateTime types (has 'column' in name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(DateTimeColumn),
            DateTimeColumnEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(DateTimeColumnEntry),
            DateTimeColumn
        )

    def test_binary_mapping(self):
        """Test mapping for Binary types (has 'column' in name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(BinaryColumn),
            BinaryColumnEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(BinaryColumnEntry),
            BinaryColumn
        )

    def test_picture_mapping(self):
        """Test mapping for Picture types (has 'column' in name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(PictureColumn),
            PictureColumnEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(PictureColumnEntry),
            PictureColumn
        )

    def test_lookup_mapping(self):
        """Test mapping for Lookup types (has 'column' in name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(LookupColumn),
            LookupColumnEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(LookupColumnEntry),
            LookupColumn
        )

    def test_url_mapping(self):
        """Test mapping for URL types (has 'column' in name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(URLColumn),
            URLColumnEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(URLColumnEntry),
            URLColumn
        )

    def test_choice_mapping(self):
        """Test mapping for Choice types (no 'column' in entry name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(ChoiceColumn),
            ChoiceEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(ChoiceEntry),
            ChoiceColumn
        )

    def test_number_mapping(self):
        """Test mapping for Number types (no 'column' in entry name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(NumberColumn),
            NumberEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(NumberEntry),
            NumberColumn
        )

    def test_currency_mapping(self):
        """Test mapping for Currency types (no 'column' in entry name)."""
        # Column to Entry
        self.assertEqual(
            get_entry_type_for_column(CurrencyColumn),
            CurrencyEntry
        )
        
        # Entry to Column
        self.assertEqual(
            get_column_type_for_entry(CurrencyEntry),
            CurrencyColumn
        )

    def test_get_entry_type_for_column_returns_none_for_invalid(self):
        """get_entry_type_for_column should return None for unknown column types."""
        self.assertIsNone(get_entry_type_for_column(None))
        self.assertIsNone(get_entry_type_for_column("InvalidType"))

    def test_get_column_type_for_entry_returns_none_for_invalid(self):
        """get_column_type_for_entry should return None for unknown entry types."""
        self.assertIsNone(get_column_type_for_entry(None))
        self.assertIsNone(get_column_type_for_entry("InvalidType"))

    def test_all_mappings_are_bidirectional(self):
        """Verify that all mappings work bidirectionally."""
        for col_type, entry_type in COLUMN_TO_ENTRY.items():
            # Forward mapping
            self.assertEqual(get_entry_type_for_column(col_type), entry_type)
            # Reverse mapping
            self.assertEqual(get_column_type_for_entry(entry_type), col_type)
            # Verify the reverse dict also has this mapping
            self.assertEqual(ENTRY_TO_COLUMN[entry_type], col_type)
