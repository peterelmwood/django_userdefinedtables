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

#### Organizational
- *List*: Akin to a table in a relational database.
- *Column*: Akin to a column/attribute in a relational database. The naked _Column_ model should not be used, as it is the parent in a [multi-table inheritance](https://docs.djangoproject.com/en/4.0/topics/db/models/#multi-table-inheritance) scheme used to simplify querying for instances of the various column models.
- *Row*: Akin to a row in a relational database. Manages order and membership of data entries.
- *Entry*: Like, _Column_, utilizes multi-table inheritance for simplified querying.

#### Data Type
- *SingleLineOfTextColumn*: brief text field. Corresponding value utilizes Django _CharField_.
- *MultipleLineTextColumn*: longer length field. Corresponding value utilizes Django _TextField_.
- *ChoiceColumn*: option among several user-defined choices. Supported by the *Choice* model, which captures the actual choices available.
- *NumberColumn*: A column which allows for entry of a decimal number. Supported by _NumericalColumn_ abstract model, which Utilizes Django _DecimalField_.
- *CurrencyColumn*: defines a currency field. Set apart from the *NumberColumn* in order to support formatting, but is otherwise identical. **NOTE: This is possibly unnecessarily redundant to NumberColumn and may be removed in the future.**
- *DateTimeColumn*: defines a datetime field. Corresponding value utilizes Django _DateTimeField_.
- *BinaryColumnEntry*: defines a binary field. Corresponding value utilizes Django _BooleanField_.
- *PictureColumn*: defines a picture field. Corresponding value utilizes Django _ImageField_.
- *LookupColumn*: defines a way for end users to specify a reference to a value in another column. Utilizes several foreign key relationships.
- *URLColumn*: defines a url field. Corresponding value utilizes  Django _URLField_.

#### Instance/Entry
Generally, these entries are self-explanatory, given an understanding of the Data Type models.
- *SingleLineOfTextColumnEntry*
- *MultipleLineTextColumnEntry*
- *ChoiceEntry*
- *NumberEntry*
- *CurrencyEntry*
- *DateTimeColumnEntry*
- *BinaryColumnEntry*
- *LookupColumnEntry*
- *URLColumnEntry*

## Active Development & Contribution
This project is still in a nascent stage and is volatile to a degree. Contribution by other members of the community is welcome, whether in the form of pull requests or ideas.
