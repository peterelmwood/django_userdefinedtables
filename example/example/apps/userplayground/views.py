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
    columns = my_list.columns.all().order_by('index')
    rows = my_list.rows.all().order_by('index')
    
    # Build table data
    table_data = []
    for row in rows:
        row_data = {'row': row, 'entries': []}
        for column in columns:
            # Get the specific column type instance
            column_type = get_column_type_instance(column)
            entry = None
            
            # Get the entry for this row and column
            if column_type:
                # Find corresponding entry type
                for entry_type in ENTRY_TYPES:
                    if entry_type._meta.model_name.replace('entry', 'column') == column_type._meta.model_name:
                        try:
                            entry = entry_type.objects.filter(row=row, column=column_type).first()
                        except (AttributeError, ObjectDoesNotExist):
                            pass
                        break
            
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
                    value = request.POST.get(field_name, '')
                    
                    # Special handling for binary columns to distinguish "unset" from "False"
                    if entry_type._meta.model_name == 'binarycolumnentry':
                        if not value:
                            # Empty value: skip entry creation for optional, error for required
                            if column.required:
                                messages.error(request, f"Error saving {column.name}: This field is required.")
                            continue
                        # Non-empty value: convert to boolean
                        value = value.lower() in ['true', '1', 'yes', 'on']
                        # Always create entry for binary columns with non-empty values
                        try:
                            entry_type.objects.create(row=row, column=column_type, value=value)
                        except Exception as e:
                            messages.error(request, f"Error saving {column.name}: {str(e)}")
                    else:
                        # For non-binary columns, create entry if value exists or column is optional
                        if value or not column.required:
                            try:
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
        columns_with_types.append({
            'column': column,
            'type_name': type_name,
        })
    
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
