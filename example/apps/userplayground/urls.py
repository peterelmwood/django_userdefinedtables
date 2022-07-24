from django.urls import path

from example.apps.userplayground.views import add_column, user_playground_home


urlpatterns = [
    path("", user_playground_home, name="playground"),
    path("add_column/", add_column, name="add_column"),
]
