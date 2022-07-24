from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from example.apps.userplayground.forms import AddFieldForm


def user_playground_home(request):
    return render(request, "user_playground_home.html")


@csrf_protect
def add_column(request):
    if request.method == "GET":
        form = AddFieldForm()
    else:
        form = AddFieldForm(request.POST)
    return render(request, "add_column.html", context={"form": form})
