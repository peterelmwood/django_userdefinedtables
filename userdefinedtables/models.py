from datetime import datetime
from typing import List as TypedList

from django.db import models
from django.db.models.functions import Length

import settings


class List(models.Model):
    name = models.CharField(max_length=255, blank=True, null=False)


class Column(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    list = models.ForeignKey(
        "userdefinedtables.list",
        null=False,
        on_delete=models.CASCADE,
        related_name="%(class)s_columns",
    )

    class Meta:
        constraints: TypedList = [
            models.UniqueConstraint(
                fields=["name", "list"],
                name="Column name cannot occur twice in one list",
            ),
        ]


class Row(models.Model):
    list = models.ForeignKey(
        "userdefinedtables.list",
        on_delete=models.CASCADE,
        related_name="rows",
        null=False,
        blank=False,
    )
    previous_row = models.OneToOneField(
        "userdefinedtables.row",
        on_delete=models.CASCADE,
        related_name="_nxt_row",
        null=True,
    )
    next_row = models.OneToOneField(
        "userdefinedtables.row",
        on_delete=models.CASCADE,
        related_name="_prv_row",
        null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["list", "previous_row"],
                name="For any list, a row can only follow one or zero rows. "
                "A null row can be followed by exactlly one row, per list.",
                condition=models.Q(previous_row__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["list", "next_row"],
                name="For any list, a row can only precede one or zero rows. "
                "A null row can be preceded by exactlly one row, per list.",
                condition=models.Q(next_row__isnull=True),
            ),
        ]


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
    minimum = models.DecimalField(null=True, default=None, **settings.USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)
    maximum = models.DecimalField(null=True, default=None, **settings.USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)

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
    value = models.DecimalField(**settings.USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)
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
    value = models.DecimalField(**settings.USER_DEFINED_TABLES_DECIMAL_FIELD_KWARGS)
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
