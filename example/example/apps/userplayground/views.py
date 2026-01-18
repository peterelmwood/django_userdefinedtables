from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from example.apps.userplayground.forms import AddColumnForm, AddTableForm
from userdefinedtables.models import (
    COLUMN_TYPES,
    ENTRY_TYPES,
    Choice,
    ChoiceColumn,
    List,
    LookupColumn,
    PictureColumn,
    Row,
)


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
    if request.method == "GET":
        form = AddTableForm()
        return render(request, "add_table.html", context={"form": form})
    else:
        form = AddTableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Table created successfully!")
            return redirect("playground")
        # If form is invalid, render with errors
        return render(request, "add_table.html", context={"form": form})


@csrf_protect
def add_column(request, list_pk=None):
    my_list = get_object_or_404(List, pk=list_pk)
    columns = my_list.columns.all()

    if request.method == "GET":
        form = AddColumnForm(initial={COLUMN_TYPES[0]._meta.object_name: "Yes"})
    else:
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
    columns = list(my_list.columns.all().order_by('index'))
    rows = list(my_list.rows.all().order_by('index'))

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
        row_data = {'row': row, 'entries': []}
        for column in columns:
            entry = entries_by_key.get((row.id, column.id))
            row_data['entries'].append(entry.value if entry else '')
        table_data.append(row_data)
    
    context = {
        'list': my_list,
        'columns': columns,
        'rows': rows,
        'table_data': table_data,
    }
    return render(request, "list_detail.html", context=context)


def add_row(request, list_pk):
    """View to add a new row with data entry."""
    my_list = get_object_or_404(List, pk=list_pk)
    columns = my_list.columns.all().order_by('index')
    
    if request.method == "POST":
        # Create a new row
        row = Row.objects.create(list=my_list)
        
        # Save entries for each column
        for column in columns:
            # Get the specific column type instance
            column_type = get_column_type_instance(column)
            
            if column_type:
                # Find corresponding entry type
                entry_type = None
                for et in ENTRY_TYPES:
                    if et._meta.model_name.replace('entry', 'column') == column_type._meta.model_name:
                        entry_type = et
                        break
                
                if entry_type:
                    field_name = f"column_{column.pk}"
                    
                    # Handle different entry types based on their specific requirements
                    try:
                        if entry_type._meta.model_name == 'binarycolumnentry':
                            value = request.POST.get(field_name, '')
                            normalized = value.strip().lower()
                            if not normalized and not column.required:
                                # Preserve "no selection" for optional fields
                                continue
                            elif normalized in ['true', '1', 'yes', 'on']:
                                value = True
                            elif normalized in ['false', '0', 'no', 'off']:
                                value = False
                            else:
                                # Fallback: anything not explicitly truthy is False
                                value = False
                            entry_type.objects.create(row=row, column=column_type, value=value)
                        elif entry_type._meta.model_name == 'choiceentry':
                            # For ChoiceColumn, get the Choice instance by ID
                            choice_id = request.POST.get(field_name, '')
                            if choice_id:
                                choice = Choice.objects.get(pk=choice_id)
                                entry_type.objects.create(row=row, column=column_type, value=choice)
                            elif column.required:
                                messages.error(request, f"Choice is required for {column.name}")
                        elif entry_type._meta.model_name == 'picturecolumnentry':
                            # For PictureColumn, get the uploaded file
                            uploaded_file = request.FILES.get(field_name)
                            if uploaded_file:
                                entry_type.objects.create(row=row, column=column_type, value=uploaded_file)
                            elif column.required:
                                messages.error(request, f"Picture is required for {column.name}")
                        elif entry_type._meta.model_name == 'lookupcolumnentry':
                            # For LookupColumn, get the Entry instance by ID
                            entry_id = request.POST.get(field_name, '')
                            if entry_id:
                                from userdefinedtables.models import Entry
                                lookup_entry = Entry.objects.get(pk=entry_id)
                                entry_type.objects.create(row=row, column=column_type, value=lookup_entry)
                            elif column.required:
                                messages.error(request, f"Lookup value is required for {column.name}")
                        else:
                            # Handle all other column types (text, number, date, url, etc.)
                            value = request.POST.get(field_name, '')
                            if value or not column.required:
                                entry_type.objects.create(row=row, column=column_type, value=value)
                    except Exception as e:
                        messages.error(request, f"Error saving {column.name}: {str(e)}")
        
        messages.success(request, "Row added successfully!")
        return redirect("list_detail", list_pk=list_pk)
    
    # Prepare columns with their type information for the template
    columns_with_types = []
    for column in columns:
        column_type = get_column_type_instance(column)
        type_name = column_type.__class__.__name__ if column_type else "Unknown"
        col_info = {
            'column': column,
            'type_name': type_name,
        }
        
        # Add special data for certain column types
        if isinstance(column_type, ChoiceColumn):
            # Get all available choices for ChoiceColumn
            col_info['choices'] = Choice.objects.all()
        elif isinstance(column_type, LookupColumn):
            # Get entries from the lookup list/column for LookupColumn
            lookup_list = column_type.lookup_list
            lookup_column = column_type.lookup_column
            # Get all rows from the lookup list and their entries for the lookup column
            lookup_rows = lookup_list.rows.all()
            lookup_entries = []
            lookup_column_type = get_column_type_instance(lookup_column)
            if lookup_column_type:
                for entry_type in ENTRY_TYPES:
                    if entry_type._meta.model_name.removesuffix('entry') == lookup_column_type._meta.model_name:
                        # Get all entries for this column
                        entries = entry_type.objects.filter(
                            column=lookup_column_type,
                            row__in=lookup_rows
                        ).select_related('row')
                        lookup_entries.extend(entries)
                        break
            col_info['lookup_entries'] = lookup_entries
        
        columns_with_types.append(col_info)
    
    context = {
        'list': my_list,
        'columns_with_types': columns_with_types,
    }
    return render(request, "add_row.html", context=context)


def delete_row(request, list_pk, row_pk):
    """Delete a row."""
    my_list = get_object_or_404(List, pk=list_pk)
    row = get_object_or_404(my_list.rows, pk=row_pk)
    row.delete()
    messages.success(request, "Row deleted successfully!")
    return redirect("list_detail", list_pk=list_pk)
