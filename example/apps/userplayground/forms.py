from django import forms

from userdefinedtables.models import COLUMN_TYPES


column_names = [col_type._meta.object_name for col_type in COLUMN_TYPES]


class AddFieldForm(forms.Form):
    options = forms.ChoiceField(widget=forms.RadioSelect, choices=enumerate(column_names))
