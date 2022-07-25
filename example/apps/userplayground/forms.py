from django import forms

from userdefinedtables.models import COLUMN_TYPES, List


column_names = [col_type._meta.object_name for col_type in COLUMN_TYPES]


class AddTableForm(forms.ModelForm):
    class Meta:
        model = List
        exclude = []


class AddColumnForm(forms.Form):
    options = forms.ChoiceField(widget=forms.RadioSelect, choices=enumerate(column_names))
