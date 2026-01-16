from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

from model_bakery import baker

from example.apps.userplayground.views import add_row
from userdefinedtables.models import BinaryColumn, BinaryColumnEntry, Row


class AddRowViewBinaryColumnTestCase(TestCase):
    """Test the add_row view behavior with binary columns."""
    
    def setUp(self):
        self.factory = RequestFactory()
        
    def test__empty_optional_binary_field_does_not_create_entry(self):
        """Test that submitting an empty value for an optional binary field does not create an entry."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=False,
        )
        
        # Create a POST request with empty binary field value
        post_data = {
            f'column_{binary_column.pk}': '',  # Empty string
        }
        request = self.factory.post(f'/playground/{list_1.pk}/add_row/', post_data)
        
        # Add messages middleware (required for the view)
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # ACT
        response = add_row(request, list_pk=list_1.pk)
        
        # ASSERT
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # A row should be created
        rows = Row.objects.filter(list=list_1)
        self.assertEqual(rows.count(), 1)
        row = rows.first()
        
        # But NO entry should be created for the empty optional binary field
        entries = BinaryColumnEntry.objects.filter(row=row, column=binary_column)
        self.assertEqual(entries.count(), 0, "No entry should be created for empty optional binary field")
    
    def test__false_value_for_optional_binary_field_creates_entry(self):
        """Test that explicitly submitting 'false' for an optional binary field creates an entry with value=False."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=False,
        )
        
        # Create a POST request with explicit 'false' value
        # (In HTML forms, unchecked checkboxes typically don't send any value,
        # but we're testing the case where 'false' is explicitly sent)
        post_data = {
            f'column_{binary_column.pk}': 'false',
        }
        request = self.factory.post(f'/playground/{list_1.pk}/add_row/', post_data)
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # ACT
        response = add_row(request, list_pk=list_1.pk)
        
        # ASSERT
        self.assertEqual(response.status_code, 302)
        
        rows = Row.objects.filter(list=list_1)
        self.assertEqual(rows.count(), 1)
        row = rows.first()
        
        # An entry SHOULD be created with value=False
        entries = BinaryColumnEntry.objects.filter(row=row, column=binary_column)
        self.assertEqual(entries.count(), 1)
        entry = entries.first()
        self.assertFalse(entry.value, "Entry value should be False")
    
    def test__true_value_for_optional_binary_field_creates_entry(self):
        """Test that submitting 'true' for an optional binary field creates an entry with value=True."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=False,
        )
        
        # Create a POST request with 'true' value
        post_data = {
            f'column_{binary_column.pk}': 'true',
        }
        request = self.factory.post(f'/playground/{list_1.pk}/add_row/', post_data)
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # ACT
        response = add_row(request, list_pk=list_1.pk)
        
        # ASSERT
        self.assertEqual(response.status_code, 302)
        
        rows = Row.objects.filter(list=list_1)
        self.assertEqual(rows.count(), 1)
        row = rows.first()
        
        # An entry SHOULD be created with value=True
        entries = BinaryColumnEntry.objects.filter(row=row, column=binary_column)
        self.assertEqual(entries.count(), 1)
        entry = entries.first()
        self.assertTrue(entry.value, "Entry value should be True")
    
    def test__empty_required_binary_field_shows_error(self):
        """Test that an empty required binary field shows an error message."""
        # ARRANGE
        list_1 = baker.make("userdefinedtables.list")
        binary_column = baker.make(
            "userdefinedtables.binarycolumn",
            list=list_1,
            required=True,
        )
        
        # Create a POST request with empty binary field value
        post_data = {
            f'column_{binary_column.pk}': '',
        }
        request = self.factory.post(f'/playground/{list_1.pk}/add_row/', post_data)
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # ACT
        response = add_row(request, list_pk=list_1.pk)
        
        # ASSERT
        # Should still redirect (row is created but with error message)
        self.assertEqual(response.status_code, 302)
        
        # Check that an error message was added
        message_list = list(messages)
        error_messages = [m for m in message_list if 'required' in str(m).lower()]
        self.assertGreater(len(error_messages), 0, "Should have an error message about required field")
