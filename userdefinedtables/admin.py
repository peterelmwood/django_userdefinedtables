from django.contrib import admin

from userdefinedtables.models import *


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    pass


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(ChoiceColumn)
class ChoiceColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(BinaryColumn)
class BinaryColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(LookupColumn)
class LookupColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(NumberColumn)
class NumberColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(PictureColumn)
class PictureColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(CurrencyColumn)
class CurrencyColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(DateTimeColumn)
class DateTimeColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(MultipleLineTextColumn)
class MultipleLineTextColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(SingleLineOfTextColumn)
class SingleLineOfTextColumnAdmin(admin.ModelAdmin):
    pass


@admin.register(URLColumn)
class URLColumnAdmin(admin.ModelAdmin):
    pass
