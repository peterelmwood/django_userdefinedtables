from datetime import datetime
from typing import List as TypedList

from django.db import models, transaction
from django.db.models.functions import Length

from userdefinedtables.settings import USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS


class List(models.Model):
    name = models.CharField(max_length=255, blank=True, null=False)

    def __str__(self):
        return self.name


class Column(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    list = models.ForeignKey(
        "userdefinedtables.list",
        null=False,
        on_delete=models.CASCADE,
        related_name="columns",
    )

    class Meta:
        constraints: TypedList = [
            models.UniqueConstraint(
                fields=["name", "list"],
                name="Column name cannot occur twice in one list",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def type(self):
        for column_typ in COLUMN_TYPES:
            if getattr(self, column_typ._meta.model_name, None):
                return column_typ.__name__
        return None


class Row(models.Model):
    list = models.ForeignKey(
        "userdefinedtables.list",
        on_delete=models.CASCADE,
        related_name="rows",
        null=False,
        blank=False,
    )
    index = models.PositiveBigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["list", "index"],
                name="A list can only have a single row at an index.",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]

    def insert_at(self, index):
        assert not self._state.adding, "Insertions on new items are done implicitly. This method is the approach to use"
        " when an item already exists and is meant to be inserted in another location."

        # in the trivial case, we do not actually need to move things around, so we return
        if self.index == index:
            return

        with transaction.atomic():
            # in either of the other cases, we need to move things around, and so wrap either move in a transaction
            if self.index < index:
                Row.objects.filter(index__gt=self.index, index__lte=index).update(index=models.F("index") - 1)
            else:
                Row.objects.filter(index__lt=self.index, index__gte=index).update(index=models.F("index") + 1)
            self.index = index
            self.save()

    def save(self):
        if self._state.adding:
            # if there are no rows indexed above this one, this will perform no changes, but will still make a db query
            Row.objects.filter(list=self.list, index__gte=self.index).update(index=models.F("index") + 1)
        # in a situation where we are not adding a row, we will need to handle the change directly using
        # `self.insert_at`
        super().save()

    def delete(self):
        index = self.index
        list = self.list
        super().delete()
        higher_rows = Row.objects.filter(list=list, index__gte=index)
        if higher_rows.exists():
            higher_rows.update(index=models.F("index") - 1)


class Entry(models.Model):
    row = models.ForeignKey(
        "userdefinedtables.row",
        on_delete=models.CASCADE,
        related_name="row_entries",
        null=False,
        blank=False,
    )


class SingleLineOfTextColumn(Column):
    maximum_length = models.PositiveSmallIntegerField(default=255)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(maximum_length__lte=255), name="maximum_length cannot exceed 255"),
        ]

    def save(self, *args, **kwargs) -> None:
        if not self._state.adding:
            entries_with_value_length = self.entries.annotate(length=Length("value"))
            if entries_with_value_length.exists():
                longest_entry = max(entries_with_value_length.values_list("length", flat=True))
                if longest_entry > self.maximum_length:
                    raise ValueError("Cannot reduce maximum_length property below the longest entry's length.")
        super().save(*args, **kwargs)


class SingleLineOfTextColumnEntry(Entry):
    value = models.CharField(max_length=255, blank=True, null=False)
    column = models.ForeignKey(
        "userdefinedtables.singlelineoftextcolumn", null=False, on_delete=models.CASCADE, related_name="entries"
    )

    def save(self, *args, **kwargs) -> None:
        if self.column.maximum_length < len(self.value):
            raise ValueError("Text entry length cannot exceed column maximum_length property.")
        super().save(*args, **kwargs)


class MultipleLineTextColumn(Column):
    pass


class MultipleLineTextColumnEntry(Entry):
    value = models.TextField(blank=True, null=False)
    column = models.ForeignKey(
        "userdefinedtables.multiplelinetextcolumn",
        blank=True,
        null=False,
        on_delete=models.CASCADE,
        related_name="entries",
    )


class ChoiceColumn(Column):
    pass


class Choice(models.Model):
    choice = models.CharField(max_length=255)


class ChoiceEntry(Entry):
    value = models.ForeignKey(
        "userdefinedtables.choice",
        null=False,
        related_name="choices",
        on_delete=models.PROTECT,
    )
    column = models.ForeignKey(
        "userdefinedtables.choicecolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )


class NumericalColumn(models.Model):
    minimum = models.DecimalField(null=True, default=None, **USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)
    maximum = models.DecimalField(null=True, default=None, **USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                check=models.Q(maximum__gte=models.F("minimum"), maximum__isnull=False, minimum__isnull=False)
                | models.Q(maximum__isnull=True)
                | models.Q(minimum__isnull=True),
                name="%(class)s.minimum cannot exceed %(class)s.maximum.",
            )
        ]

    def set_no_minimum(self):
        self.minimum = None
        self.save()

    def set_no_maximum(self):
        self.maximum = None
        self.save()

    def lte_maximum(self, value):
        return self.maximum is None or value <= self.maximum

    def gte_minimum(self, value):
        return self.minimum is None or value >= self.minimum


class NumberColumn(NumericalColumn, Column):
    pass


class NumberEntry(Entry):
    value = models.DecimalField(**USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)
    column = models.ForeignKey(
        "userdefinedtables.numbercolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.column.minimum > self.value or self.column.maximum < self.value:
            raise ValueError(f"NumberEntry.value must be between {self.column.minimum} and {self.column.maximum}")
        super().save(*args, **kwargs)


class CurrencyColumn(NumericalColumn, Column):
    pass


class CurrencyEntry(Entry):
    value = models.DecimalField(**USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)
    column = models.ForeignKey(
        "userdefinedtables.currencycolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.column.minimum > self.value or self.column.maximum < self.value:
            raise ValueError(f"NumberEntry.value must be between {self.column.minimum} and {self.column.maximum}")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"${self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class DateTimeColumn(Column):
    earliest_date = models.DateTimeField(default=datetime.fromtimestamp(0), null=True)
    latest_date = models.DateTimeField(default=None, null=True)


class DateTimeColumnEntry(Entry):
    value = models.DateTimeField()
    column = models.ForeignKey(
        "userdefinedtables.datetimecolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.value > self.column.latest_date or self.value < self.column.earliest_date:
            raise ValueError(f"Date value must be between {self.column.earliest_date} and {self.column.latest_date}.")
        super().save(*args, **kwargs)


class BinaryColumn(Column):
    pass


class BinaryColumnEntry(Entry):
    value = models.BooleanField()
    column = models.ForeignKey(
        "userdefinedtables.binarycolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )


class PictureColumn(Column):
    pass


class PictureColumnEntry(Entry):
    value = models.ImageField()
    column = models.ForeignKey(
        "userdefinedtables.picturecolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )


class LookupColumn(Column):
    lookup_list = models.ForeignKey(
        "userdefinedtables.list",
        null=False,
        related_name="lookups",
        on_delete=models.CASCADE,
    )
    lookup_column = models.ForeignKey(
        "userdefinedtables.column",
        null=False,
        related_name="lookup_columns",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.lookup_column.list != self.list:
            raise ValueError("Column must be a member of List.")
        self.save(*args, **kwargs)


class LookupColumnEntry(Entry):
    value = models.ForeignKey(
        "userdefinedtables.entry",
        null=False,
        on_delete=models.PROTECT,
        related_name="lookup_selections",
    )
    column = models.ForeignKey(
        "userdefinedtables.lookupcolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.value.value}"


class URLColumn(Column):
    pass


class URLColumnEntry(Entry):
    value = models.URLField()
    column = models.ForeignKey(
        "userdefinedtables.urlcolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )


COLUMN_TYPES = [
    SingleLineOfTextColumn,
    MultipleLineTextColumn,
    ChoiceColumn,
    NumberColumn,
    CurrencyColumn,
    DateTimeColumn,
    BinaryColumn,
    PictureColumn,
    LookupColumn,
    URLColumn,
]

ENTRY_TYPES = [
    SingleLineOfTextColumnEntry,
    MultipleLineTextColumnEntry,
    ChoiceEntry,
    NumberEntry,
    CurrencyEntry,
    DateTimeColumnEntry,
    BinaryColumnEntry,
    PictureColumnEntry,
    LookupColumnEntry,
    URLColumnEntry,
]
