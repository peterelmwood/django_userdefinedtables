from datetime import datetime
from decimal import Decimal
from typing import List as TypedList

from django.db import models
from django.db.models.functions import Length


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
                name="name cannot occur twice in list",
            ),
        ]


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


class SingleLineOfTextColumnEntry(models.Model):
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


class MultipleLineTextColumnEntry(models.Model):
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


class ChoiceEntry(models.Model):
    value = models.ForeignKey(
        "userdefinedtables.choice",
        null=False,
        related_name="choices",
        on_delete=models.CASCADE,
    )
    column = models.ForeignKey(
        "userdefinedtables.choicecolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )


class NumberColumn(Column):
    minimum = models.DecimalField(default="-Infinity")
    maximum = models.DecimalField(default="Infinity")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(maximum__gte=models.F("minimum")),
                name="NumberColumn.minimum cannot exceed NumberColumn.maximum.",
            )
        ]

    def set_no_minimum(self):
        self.minimum = Decimal("-Infinity")
        self.save()

    def set_no_maximum(self):
        self.maximum = Decimal("Infinity")
        self.save()


class NumberEntry(models.Model):
    value = models.DecimalField()
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


class CurrencyColumn(NumberColumn):
    pass


class CurrencyEntry(models.Model):
    column = models.ForeignKey(
        "userdefinedtables.currencycolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )


class DateTimeColumn(Column):
    earliest_date = models.DateTimeField(default=datetime.fromtimestamp(0))
    latest_date = models.DateTimeField(default=None)


class DateTimeColumnEntry(models.Model):
    column = models.ForeignKey(
        "userdefinedtables.datetimecolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )

    datetime = models.DateTimeField()


class BinaryColumn(Column):
    pass


class BinaryColumnEntry(models.Model):
    column = models.ForeignKey(
        "userdefinedtables.binarycolumn",
        null=False,
        related_name="entries",
        on_delete=models.CASCADE,
    )
