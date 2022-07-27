from django import forms
from django.utils.translation import gettext_lazy as _

from userdefinedtables.models import COLUMN_TYPES, Column, List

column_names = [col_type._meta.object_name for col_type in COLUMN_TYPES]


class AddTableForm(forms.ModelForm):
    class Meta:
        model = List
        exclude = []


class AddColumnForm(forms.ModelForm):
    column = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=enumerate(column_names),
        required=True,
        help_text="Determine which column type matches your needs.",
        error_messages={"required": _("Column selection is required.")},
    )

    class Meta:
        model = Column
        fields = ["column", "name", "description", "required", "unique"]

    def clean(self):
        super().clean()
        column_type_index = int(self.cleaned_data["column"])
        if not column_type_index >= 0 and not column_type_index < len(column_names):
            raise forms.ValidationError(
                "Cannot select a column that doesn't exist.",
                params={"column": column_type_index},
            )
        column_type = COLUMN_TYPES[column_type_index]
        self.cleaned_data["column"] = column_type

        return self.cleaned_data
