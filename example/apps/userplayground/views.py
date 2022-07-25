from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.views.decorators.csrf import csrf_protect

from example.apps.userplayground.forms import AddColumnForm, AddTableForm
from userdefinedtables.models import List


class ListsView(generic.ListView):
    template_name = "user_playground_home.html"
    context_object_name = "lists"

    def get_queryset(self):
        """Return the last five published questions."""
        return List.objects.all()


def add_table(request):
    if request.method == "GET":
        form = AddTableForm()
    else:
        form = AddTableForm(request.POST)
        form.save()
    return render(request, "add_table.html", context={"form": form})


@csrf_protect
def add_column(request, list_pk=None):
    my_list = get_object_or_404(List, pk=list_pk)

    columns = my_list.column_columns.all()

    if request.method == "GET":
        form = AddColumnForm()
    else:
        form = AddColumnForm(request.POST)
    return render(request, "add_column.html", context={"form": form, "columns": columns})
