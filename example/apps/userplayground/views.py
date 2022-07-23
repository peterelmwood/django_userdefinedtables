from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from example.apps.userplayground.forms import AddFieldForm


def user_playground_home(request):
    return render(request, "user_playground_home.html")


@csrf_protect
def make_table(request):
    if request.method == "GET":
        form = AddFieldForm()
    else:
        print("request.POST: ", request.POST)
        form = AddFieldForm(request.POST)
    return render(request, "make_table.html", context={"form": form})
