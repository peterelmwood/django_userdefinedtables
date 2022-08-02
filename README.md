![Tests passing](https://github.com/peterelmwood/django_userdefinedtables/actions/workflows/publish-to-test-pypi.yml/badge.svg)
![Latest is on pypi](https://github.com/peterelmwood/django_userdefinedtables/actions/workflows/publish-to-pypi.yml/badge.svg)

# django_userdefinedtables
This application is intended to be used as a way for an end user to define their own database tables.

It is loosely inspired by the way SharePoint lists work.

## Installation

To install django_userdefinedtables, use the following command:
``pip install django_userdefinedtables``

`userdefinedtables` should then added to the `APPS` list in the Django settings.

## Use

### Models
The models which are available for use are:
- *List*: Akin to a table in a relational database.
- *Column*: Akin to a column/attribute in a relational database. The naked _Column_ model should not be used, as it is the parent in a [multi-table inheritance](https://docs.djangoproject.com/en/4.0/topics/db/models/#multi-table-inheritance) scheme used among the various column models.
- *Row*: Akin to a row in a relational database. Manages order and membership of data entries.

## Active Development & Contribution

This project is still in a nascent stage, and is volatile, to a degree. Contribution by other members of the community is welcome, whether in the form of pull requests or ideas.
