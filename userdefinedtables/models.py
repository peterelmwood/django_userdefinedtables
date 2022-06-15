from typing import List as TypedList

from django.db import models


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
    value = models.CharField(max_length=255, blank=True, null=False)
    maximum_length = models.PositiveSmallIntegerField(default=255)

    class Meta(Column.Meta):
        constraints = Column.Meta.constraints + [
            models.CheckConstraint(check=models.Q(maximum_length__lte=255), name="maximum_length cannot exceed 255"),
            models.UniqueConstraint(
                fields=["value", "list"],
                condition=models.Q(unique=True),
                name="value cannot occur twice in list, if unique == True",
            ),
        ]
