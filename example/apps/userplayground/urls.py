from django.urls import path

from example.apps.userplayground.views import make_table, user_playground_home


urlpatterns = [
    path("", user_playground_home, name="playground"),
    path("make_table/", make_table, name="make_table"),
]
