from django.urls import path

from example.apps.userplayground.views import (
    add_column,
    add_row,
    add_table,
    delete_column,
    delete_row,
    list_detail,
    ListsView,
)


urlpatterns = [
    path("", ListsView.as_view(), name="playground"),
    path("add_table/", add_table, name="add_table"),
    path("tables/<int:list_pk>/", list_detail, name="list_detail"),
    path("tables/<int:list_pk>/add_column/", add_column, name="add_column"),
    path("tables/<int:list_pk>/columns/<int:column_pk>/delete/", delete_column, name="delete_column"),
    path("tables/<int:list_pk>/add_row/", add_row, name="add_row"),
    path("tables/<int:list_pk>/rows/<int:row_pk>/delete/", delete_row, name="delete_row"),
]
