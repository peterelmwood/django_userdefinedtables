from unittest import mock

from django import forms
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from example.apps.userplayground.forms import AddColumnForm
from userdefinedtables.models import Column, List, SingleLineOfTextColumn


class AddTableViewTests(TestCase):
    def setUp(self):
        self.url = reverse("add_table")

    def test_get_add_table_renders_form(self):
        """GET request should render an unbound form"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertFalse(response.context["form"].is_bound)

    def test_post_valid_data_creates_table_and_redirects(self):
        """POST with valid data should create the table and redirect to the playground"""
        response = self.client.post(self.url, {"name": "Test Table"})
        # assertRedirects also fetches the destination and checks it responds with 200
        self.assertRedirects(response, reverse("playground"))
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(List.objects.get().name, "Test Table")

        # Following the redirect with a GET must not create anything else (POST-Redirect-GET)
        response = self.client.get(reverse("playground"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(List.objects.count(), 1)

    def test_post_invalid_data_renders_form_with_errors(self):
        """POST with invalid data should re-render the bound form with its errors and submitted input"""
        # List.name allows blank values, so an over-long name is the invalid case
        too_long_name = "x" * 256
        response = self.client.post(self.url, {"name": too_long_name})
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("name", form.errors)
        self.assertEqual(form["name"].value(), too_long_name)
        self.assertEqual(List.objects.count(), 0)


class AddColumnViewTests(TestCase):
    def setUp(self):
        self.test_list = List.objects.create(name="Test List")
        self.url = reverse("add_column", kwargs={"list_pk": self.test_list.pk})
        # Index 0 in COLUMN_TYPES is SingleLineOfTextColumn
        self.valid_data = {"column": "0", "name": "Test Column", "description": "", "required": False, "unique": False}

    def test_get_add_column_renders_form(self):
        """GET request should render an unbound form with existing columns and a default column type"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertIn("columns", response.context)

        form = response.context["form"]
        self.assertFalse(form.is_bound)
        # The first column type (SingleLineOfTextColumn) is pre-selected
        self.assertEqual(form["column"].value(), "0")

    def test_post_valid_data_creates_column_and_redirects(self):
        """POST with valid data should create the selected column subtype and redirect back to the page"""
        response = self.client.post(self.url, self.valid_data)
        # assertRedirects also fetches the destination and checks it responds with 200
        self.assertRedirects(response, self.url)

        self.assertEqual(self.test_list.columns.count(), 1)
        column = SingleLineOfTextColumn.objects.get(name="Test Column")
        self.assertEqual(column.list, self.test_list)
        self.assertEqual(column.type, "SingleLineOfTextColumn")
        # The base Column row must be the parent of the subtype, not a separate untyped column
        self.assertEqual(Column.objects.count(), 1)
        self.assertEqual(Column.objects.get().pk, column.pk)

        # Following the redirect with a GET shows the saved column in an unbound form
        # and must not create anything else (POST-Redirect-GET)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_bound)
        self.assertContains(response, "Test Column")
        self.assertEqual(self.test_list.columns.count(), 1)

    def test_post_invalid_data_renders_form_with_errors(self):
        """POST without the required name should re-render the bound form with errors"""
        response = self.client.post(self.url, {"column": "0"})
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("name", form.errors)
        self.assertEqual(self.test_list.columns.count(), 0)

    def test_post_missing_column_type_renders_form_with_errors(self):
        """POST without a column type should report the field error instead of crashing"""
        response = self.client.post(self.url, {"name": "Missing type"})
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("column", form.errors)
        self.assertEqual(form["name"].value(), "Missing type")
        self.assertEqual(self.test_list.columns.count(), 0)

    def test_post_invalid_column_type_renders_form_with_errors(self):
        """POST with a column type that is not a valid choice should report the field error"""
        response = self.client.post(self.url, {"name": "Invalid type", "column": "999"})
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("column", form.errors)
        self.assertEqual(self.test_list.columns.count(), 0)

    def test_post_duplicate_column_name_renders_form_with_errors(self):
        """POST with a name already used in the same list should show a form error, not crash"""
        SingleLineOfTextColumn.objects.create(name="Test Column", list=self.test_list)

        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("name", form.errors)
        self.assertEqual(self.test_list.columns.count(), 1)

    def test_post_duplicate_column_name_inserted_after_validation_renders_form_with_errors(self):
        """A same-named column inserted after the form validated should still become a form error"""
        original_clean = AddColumnForm.clean

        def clean_then_insert_duplicate(form):
            cleaned_data = original_clean(form)
            # Simulate a concurrent request winning the race between validation and save
            SingleLineOfTextColumn.objects.create(name="Test Column", list=self.test_list)
            return cleaned_data

        with mock.patch.object(AddColumnForm, "clean", clean_then_insert_duplicate):
            response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("name", form.errors)
        self.assertEqual(self.test_list.columns.count(), 1)

    def test_post_other_integrity_error_is_not_reported_as_duplicate_name(self):
        """An integrity failure that is not a name clash must propagate rather than show a false name error"""
        # Index 8 in COLUMN_TYPES is LookupColumn, whose required lookup_list and lookup_column
        # fields are not collected by AddColumnForm, so saving it violates a NOT NULL constraint.
        with self.assertRaises(IntegrityError):
            self.client.post(self.url, {**self.valid_data, "column": "8"})
        self.assertEqual(self.test_list.columns.count(), 0)

    def test_post_duplicate_name_is_reported_before_other_integrity_failures(self):
        """With a same-named column present, the duplicate is reported and no save is attempted"""
        SingleLineOfTextColumn.objects.create(name="Test Column", list=self.test_list)

        # Bypass the form's own check so only the view's locked re-check stands between the POST and a
        # LookupColumn save that would fail on NOT NULL; the duplicate must win, not be misreported.
        with mock.patch.object(AddColumnForm, "clean", forms.ModelForm.clean):
            response = self.client.post(self.url, {**self.valid_data, "column": "8"})
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("name", form.errors)
        self.assertEqual(self.test_list.columns.count(), 1)

    def test_post_duplicate_column_name_in_other_list_is_allowed(self):
        """The name uniqueness check is per list, so the same name may be used in another list"""
        other_list = List.objects.create(name="Other List")
        SingleLineOfTextColumn.objects.create(name="Test Column", list=other_list)

        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.url)
        self.assertEqual(self.test_list.columns.count(), 1)
        self.assertEqual(other_list.columns.count(), 1)
