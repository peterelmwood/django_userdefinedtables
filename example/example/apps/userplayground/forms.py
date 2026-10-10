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

    def __init__(self, *args, list=None, **kwargs):
        """
        ``list`` is the ``List`` the new column will belong to. It is excluded from the form's
        fields, so the model's per-list name uniqueness constraint is not checked by the ModelForm
        machinery; passing it in lets ``clean`` enforce that constraint before anything is saved.
        """
        super().__init__(*args, **kwargs)
        self.list = list

    def clean_column(self):
        # Only runs once the ChoiceField has validated the submitted value, so a missing or
        # out-of-range selection keeps its field error instead of raising here.
        column_type_index = int(self.cleaned_data["column"])
        try:
            return COLUMN_TYPES[column_type_index]
        except IndexError:
            raise forms.ValidationError(
                _("Cannot select a column that doesn't exist."),
                params={"column": column_type_index},
            ) from None

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        if name and self.list is not None and self.list.columns.filter(name=name).exists():
            self.add_error(
                "name",
                forms.ValidationError(
                    _("A column named '%(name)s' already exists in this list."),
                    code="duplicate_name",
                    params={"name": name},
                ),
            )
        return cleaned_data
