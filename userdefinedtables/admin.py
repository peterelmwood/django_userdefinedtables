from django.contrib import admin

from userdefinedtables.models import Column, List


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    pass


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    pass
