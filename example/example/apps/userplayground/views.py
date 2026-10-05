from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.views.decorators.csrf import csrf_protect

from example.apps.userplayground.forms import AddColumnForm, AddTableForm
from userdefinedtables.models import (
    COLUMN_TYPES,
    ENTRY_TYPES,
    Choice,
    ChoiceColumn,
    Column,
    Entry,
    List,
    LookupColumn,
    Row,
)

# The UniqueConstraint on Column that forbids two columns with the same name in one list
COLUMN_NAME_CONSTRAINT = next(
    constraint for constraint in Column._meta.constraints if tuple(constraint.fields) == ("name", "list")
)


def is_duplicate_column_name_error(exc):
    """
    Return True if the IntegrityError is a violation of the (name, list) uniqueness constraint on Column.

    PostgreSQL reports the violated constraint by name through the driver's diagnostics. SQLite has no
    constraint names and instead lists the columns of the failed UNIQUE index in the message.
    """
    diag = getattr(exc.__cause__, "diag", None)
    constraint_name = getattr(diag, "constraint_name", None)
    if constraint_name:
        return constraint_name == COLUMN_NAME_CONSTRAINT.name
    message = str(exc)
    return "UNIQUE constraint failed" in message and f"{Column._meta.db_table}.name" in message


def add_duplicate_column_name_error(form, column):
    form.add_error("name", f"A column named '{column.name}' already exists in this list.")


def get_column_type_instance(column):
    """Get the specific column type instance for a column."""
    for col_type in COLUMN_TYPES:
        try:
            return getattr(column, col_type._meta.model_name)
        except (AttributeError, ObjectDoesNotExist):
            continue
    return None


def get_entry_type_for_column_type(column_model_name):
    """Map a column model name to its matching entry type class."""
    for entry_type in ENTRY_TYPES:
        entry_model_name = entry_type._meta.model_name
        stem = entry_model_name.removesuffix("entry")
        if stem == column_model_name:
            return entry_type
        if not stem.endswith("column") and f"{stem}column" == column_model_name:
            return entry_type
    return None


def get_columns_with_types(columns):
    columns_with_types = []
    for column in columns:
        column_type = get_column_type_instance(column)
        type_name = column_type.__class__.__name__ if column_type else "Unknown"
        col_info = {
            "column": column,
            "type_name": type_name,
        }

        if isinstance(column_type, ChoiceColumn):
            col_info["choices"] = Choice.objects.all()
        elif isinstance(column_type, LookupColumn):
            lookup_entries = []
            lookup_column_type = get_column_type_instance(column_type.lookup_column)
            if lookup_column_type:
                lookup_entry_type = get_entry_type_for_column_type(lookup_column_type._meta.model_name)
                if lookup_entry_type:
                    lookup_entries = list(
                        lookup_entry_type.objects.filter(
                            column=lookup_column_type,
                            row__in=column_type.lookup_list.rows.all(),
                        ).select_related("row")
                    )
            col_info["lookup_entries"] = lookup_entries

        columns_with_types.append(col_info)

    return columns_with_types


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
        # The list is passed in so the form can reject column names that already exist in it
        form = AddColumnForm(request.POST, list=my_list)
        if form.is_valid():
            # Get the column type from cleaned data
            column_type_class = form.cleaned_data.get("column")

            # Create an instance of the specific column type
            column = column_type_class(
                name=form.cleaned_data.get("name"),
                description=form.cleaned_data.get("description", ""),
                required=form.cleaned_data.get("required", False),
                unique=form.cleaned_data.get("unique", False),
                list=my_list,
            )
            # The form already rejects names that exist in this list, but a concurrent request can insert
            # the same name between that check and the save. Lock the list row so column creation through
            # this view is serialised per list, then re-check under the lock. This relies on PostgreSQL,
            # which the example runs on; SQLite (used only by test_settings.py) ignores select_for_update()
            # and may raise OperationalError ("database is locked") under real write concurrency instead.
            with transaction.atomic():
                List.objects.select_for_update().get(pk=my_list.pk)
                if my_list.columns.filter(name=column.name).exists():
                    add_duplicate_column_name_error(form, column)
                else:
                    # A writer that does not take the list lock (the admin, the model API, or any caller
                    # on SQLite where select_for_update() is a no-op) can still slip a duplicate in after
                    # the re-check, so the model's unique constraint remains the final guard. Save in a
                    # savepoint so a failed insert does not poison the outer transaction, and translate
                    # only a confirmed (name, list) violation into a form error; any other integrity
                    # failure (for example a column type whose required fields this form does not
                    # collect) propagates untouched.
                    try:
                        with transaction.atomic():
                            column.save()
                    except IntegrityError as exc:
                        if not is_duplicate_column_name_error(exc):
                            raise
                        add_duplicate_column_name_error(form, column)
                    else:
                        messages.success(request, f"Column '{column.name}' added successfully!")
                        return redirect("add_column", list_pk=list_pk)
    else:
        # Pre-select the first column type (choices are indexed into COLUMN_TYPES)
        form = AddColumnForm(initial={"column": "0"}, list=my_list)
    # An invalid POST falls through and re-renders the bound form with its errors
    return render(request, "add_column.html", context={"form": form, "columns": columns, "list": my_list})


def delete_column(request, list_pk, column_pk):
    my_list = get_object_or_404(List, pk=list_pk)
    column = get_object_or_404(my_list.columns, pk=column_pk)
    column_name = column.name
    column.delete()
    messages.success(request, f"Column '{column_name}' deleted successfully!")
    return redirect("add_column", list_pk=list_pk)


def list_detail(request, list_pk):
    """View to display list with all rows and data."""
    my_list = get_object_or_404(List, pk=list_pk)
    columns = list(my_list.columns.all().order_by("index"))
    rows = list(my_list.rows.all().order_by("index"))

    # Prefetch all entries for the displayed rows and columns to avoid
    # per-cell queries (rows * columns * entry_types).
    row_ids = [row.id for row in rows]
    column_ids = [column.id for column in columns]

    entries_by_key = {}
    if row_ids and column_ids:
        for entry_type in ENTRY_TYPES:
            for entry in entry_type.objects.filter(row_id__in=row_ids, column_id__in=column_ids):
                # There should be at most one entry per (row, column) pair.
                entries_by_key[(entry.row_id, entry.column_id)] = entry

    # Build table data
    table_data = []
    for row in rows:
        row_data = {"row": row, "entries": []}
        for column in columns:
            entry = entries_by_key.get((row.id, column.id))
            row_data["entries"].append(entry.value if entry else "")
        table_data.append(row_data)

    context = {
        "list": my_list,
        "columns": columns,
        "rows": rows,
        "table_data": table_data,
    }
    return render(request, "list_detail.html", context=context)


def add_row(request, list_pk):
    """View to add a new row with data entry."""
    my_list = get_object_or_404(List, pk=list_pk)
    columns = list(my_list.columns.all().order_by("index"))

    if request.method == "POST":
        has_errors = False
        try:
            with transaction.atomic():
                row = Row.objects.create(list=my_list)

                for column in columns:
                    column_type = get_column_type_instance(column)
                    if not column_type:
                        continue

                    entry_type = get_entry_type_for_column_type(column_type._meta.model_name)
                    if not entry_type:
                        continue

                    field_name = f"column_{column.pk}"
                    entry_model_name = entry_type._meta.model_name

                    if entry_model_name == "binarycolumnentry":
                        normalized = request.POST.get(field_name, "").strip().lower()
                        if not normalized:
                            if column.required:
                                messages.error(request, f"Value is required for {column.name}")
                                has_errors = True
                            continue
                        if normalized in ["true", "1", "yes", "on"]:
                            value = True
                        elif normalized in ["false", "0", "no", "off"]:
                            value = False
                        else:
                            value = False
                        entry_type.objects.create(row=row, column=column_type, value=value)
                    elif entry_model_name == "choiceentry":
                        choice_id = request.POST.get(field_name, "").strip()
                        if not choice_id:
                            if column.required:
                                messages.error(request, f"Choice is required for {column.name}")
                                has_errors = True
                            continue
                        choice = Choice.objects.filter(pk=choice_id).first()
                        if not choice:
                            messages.error(request, f"Invalid choice selected for {column.name}")
                            has_errors = True
                            continue
                        entry_type.objects.create(row=row, column=column_type, value=choice)
                    elif entry_model_name == "picturecolumnentry":
                        uploaded_file = request.FILES.get(field_name)
                        if not uploaded_file:
                            if column.required:
                                messages.error(request, f"Picture is required for {column.name}")
                                has_errors = True
                            continue
                        entry_type.objects.create(row=row, column=column_type, value=uploaded_file)
                    elif entry_model_name == "lookupcolumnentry":
                        lookup_entry_id = request.POST.get(field_name, "").strip()
                        if not lookup_entry_id:
                            if column.required:
                                messages.error(request, f"Lookup value is required for {column.name}")
                                has_errors = True
                            continue
                        lookup_entry = Entry.objects.filter(pk=lookup_entry_id).first()
                        if not lookup_entry:
                            messages.error(request, f"Invalid lookup value selected for {column.name}")
                            has_errors = True
                            continue
                        entry_type.objects.create(row=row, column=column_type, value=lookup_entry)
                    else:
                        value = request.POST.get(field_name, "")
                        if not value:
                            if column.required:
                                messages.error(request, f"Value is required for {column.name}")
                                has_errors = True
                            continue
                        entry_type.objects.create(row=row, column=column_type, value=value)

                if has_errors:
                    raise ValueError("row_validation_failed")
        except ValueError as exc:
            if str(exc) != "row_validation_failed":
                raise
        else:
            messages.success(request, "Row added successfully!")
            return redirect("list_detail", list_pk=list_pk)

    context = {
        "list": my_list,
        "columns_with_types": get_columns_with_types(columns),
    }
    return render(request, "add_row.html", context=context)


def delete_row(request, list_pk, row_pk):
    """Delete a row."""
    my_list = get_object_or_404(List, pk=list_pk)
    row = get_object_or_404(my_list.rows, pk=row_pk)
    row.delete()
    messages.success(request, "Row deleted successfully!")
    return redirect("list_detail", list_pk=list_pk)
