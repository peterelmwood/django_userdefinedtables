from django.urls import path

from example.apps.userplayground.views import add_column, add_table, ListsView


urlpatterns = [
    path("", ListsView.as_view(), name="playground"),
    path("add_table/", add_table, name="add_table"),
    path("tables/<list_pk>/add_column/", add_column, name="add_column"),
]
