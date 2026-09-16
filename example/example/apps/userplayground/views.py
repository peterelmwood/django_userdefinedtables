from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from example.apps.userplayground.forms import AddColumnForm, AddTableForm
from userdefinedtables.models import COLUMN_TYPES, ENTRY_TYPES, List, Row


def get_column_type_instance(column):
    """Get the specific column type instance for a column."""
    for col_type in COLUMN_TYPES:
        try:
            return getattr(column, col_type._meta.model_name)
        except (AttributeError, ObjectDoesNotExist):
            continue
    return None


class ListsView(generic.ListView):
    template_name = "user_playground_home.html"
    context_object_name = "lists"

    def get_queryset(self):
        """Return all lists."""
        return List.objects.all()


def add_table(request):
    if request.method == "POST":
        form = AddTableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Table created successfully!")
            return redirect("playground")
    else:
        form = AddTableForm()
    # An invalid POST falls through and re-renders the bound form with its errors
    return render(request, "add_table.html", context={"form": form})


@csrf_protect
def add_column(request, list_pk=None):
    my_list = get_object_or_404(List, pk=list_pk)
    columns = my_list.columns.all()

    if request.method == "POST":
        form = AddColumnForm(request.POST)
        if form.is_valid():
            # Get the column type from cleaned data
            column_type_class = form.cleaned_data.get("column")
            
            # Create an instance of the specific column type
            column = column_type_class(
                name=form.cleaned_data.get("name"),
                description=form.cleaned_data.get("description", ""),
                required=form.cleaned_data.get("required", False),
                unique=form.cleaned_data.get("unique", False),
                list=my_list
            )
            column.save()
            messages.success(request, f"Column '{column.name}' added successfully!")
            return redirect("add_column", list_pk=list_pk)
    else:
        form = AddColumnForm(initial={COLUMN_TYPES[0]._meta.object_name: "Yes"})
    return render(request, "add_column.html", context={"form": form, "columns": columns, "list": my_list})
