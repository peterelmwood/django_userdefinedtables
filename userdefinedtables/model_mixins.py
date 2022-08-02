#!/usr/bin/env python

"""
Defines mixins for common model behaviors.
"""

# stdlib

# django

# local django
from django.db import models, transaction

# thirdparty


class OrderableMixin:
    def insert_at(self, index):
        assert not self._state.adding, "Insertions on new items are done implicitly. This method is the approach to use"
        " when an item already exists and is meant to be inserted in another location."

        # in the trivial case, we do not actually need to move things around, so we return
        if self.index == index:
            return

        with transaction.atomic():
            # in either of the other cases, we need to move things around, and so wrap either move in a transaction
            if self.index < index:
                self.__class__.objects.filter(index__gt=self.index, index__lte=index).update(
                    index=models.F("index") - 1
                )
            else:
                self.__class__.objects.filter(index__lt=self.index, index__gte=index).update(
                    index=models.F("index") + 1
                )
            self.index = index
            self.save()

    def save(self):
        if self._state.adding:
            # if there are no items indexed above this one, this will perform no changes, but will still make a db query
            self.__class__.objects.filter(list=self.list, index__gte=self.index).update(index=models.F("index") + 1)
        # in a situation where we are not adding an item, we will need to handle the change directly using
        # `self.insert_at`
        super().save()

    def delete(self):
        index = self.index
        list = self.list
        super().delete()
        higher_rows = self.__class__.objects.filter(list=list, index__gte=index)
        if higher_rows.exists():
            higher_rows.update(index=models.F("index") - 1)
