from django.contrib import admin
from django.urls import include, path

from example.apps.userplayground.views import user_playground_home
from example.views import home


urlpatterns = [
    path("admin/", admin.site.urls),
    path("playground/", include("example.apps.userplayground.urls")),
    path("", home, name="home"),
]
