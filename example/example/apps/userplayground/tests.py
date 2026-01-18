from django.test import TestCase
from django.urls import reverse

from userdefinedtables.models import List


class AddTableViewTests(TestCase):
    def test_get_add_table_renders_form(self):
        """GET request should render form"""
        response = self.client.get(reverse("add_table"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_post_valid_data_creates_table_and_redirects(self):
        """POST with valid data should create table and redirect"""
        response = self.client.post(reverse("add_table"), {"name": "Test Table"})
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(List.objects.first().name, "Test Table")


class AddColumnViewTests(TestCase):
    def setUp(self):
        self.test_list = List.objects.create(name="Test List")
        self.url = reverse("add_column", kwargs={"list_pk": self.test_list.pk})

    def test_get_add_column_renders_form(self):
        """GET request should render form with existing columns"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        self.assertIn("columns", response.context)

    def test_post_valid_data_creates_column_and_redirects(self):
        """POST with valid data should create column and redirect"""
        response = self.client.post(
            self.url, {"column": "0", "name": "Test Column", "description": "", "required": False, "unique": False}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful save
        self.assertEqual(self.test_list.columns.count(), 1)

    def test_post_invalid_data_renders_form_with_errors(self):
        """POST with invalid data should re-render form with errors"""
        # Name is required, so posting without it should fail
        response = self.client.post(self.url, {"column": "0"})
        self.assertEqual(response.status_code, 200)  # Re-render form
        self.assertContains(response, "form")
        self.assertEqual(self.test_list.columns.count(), 0)  # No column created
        # Check that form errors are present
        self.assertTrue(response.context["form"].errors)
