# Fixing Entry Type Mapping in PR #6

This document explains how to use the new mapping utilities to fix the entry type lookup issue in PR #6.

## Problem

The code in PR #6's `example/example/apps/userplayground/views.py` uses:
```python
if entry_type._meta.model_name.replace('entry', 'column') == column_type._meta.model_name:
```

This approach breaks for models that already have "column" in their name:
- `singlelineoftextcolumnentry`.replace('entry', 'column') → `singlelineoftextcolumncolumn` ❌
- Expected: `singlelineoftextcolumn` ✓

Affected column types:
- SingleLineOfTextColumnEntry
- MultipleLineTextColumnEntry
- DateTimeColumnEntry
- BinaryColumnEntry
- PictureColumnEntry
- LookupColumnEntry
- URLColumnEntry

## Solution

Use the new mapping utilities added in `userdefinedtables/models.py`:

### Available utilities:
- `COLUMN_TO_ENTRY` - Dictionary mapping column types to entry types
- `ENTRY_TO_COLUMN` - Dictionary mapping entry types to column types
- `get_entry_type_for_column(column_type)` - Function to get entry type for a column type
- `get_column_type_for_entry(entry_type)` - Function to get column type for an entry type

### How to fix `list_detail` view (line 105):

**Before:**
```python
for entry_type in ENTRY_TYPES:
    if entry_type._meta.model_name.replace('entry', 'column') == column_type._meta.model_name:
        try:
            entry = entry_type.objects.filter(row=row, column=column_type).first()
        except (AttributeError, ObjectDoesNotExist):
            pass
        break
```

**After:**
```python
from userdefinedtables.models import get_entry_type_for_column

# ... in list_detail function ...
if column_type:
    # Get the corresponding entry type
    entry_type = get_entry_type_for_column(type(column_type))
    if entry_type:
        try:
            entry = entry_type.objects.filter(row=row, column=column_type).first()
        except (AttributeError, ObjectDoesNotExist):
            pass
```

### How to fix `add_row` view (line 145):

**Before:**
```python
# Find corresponding entry type
entry_type = None
for et in ENTRY_TYPES:
    if et._meta.model_name.replace('entry', 'column') == column_type._meta.model_name:
        entry_type = et
        break
```

**After:**
```python
from userdefinedtables.models import get_entry_type_for_column

# ... in add_row function ...
# Find corresponding entry type
entry_type = get_entry_type_for_column(type(column_type))
```

## Alternative: Using the dictionary directly

If you prefer to use the dictionaries directly:

```python
from userdefinedtables.models import COLUMN_TO_ENTRY, ENTRY_TO_COLUMN

# Get entry type from column type
entry_type = COLUMN_TO_ENTRY.get(type(column_type))

# Get column type from entry type
column_type = ENTRY_TO_COLUMN.get(entry_type)
```

## Benefits

1. **Works for all column types** - No string manipulation issues
2. **Maintainable** - Uses the existing index-aligned COLUMN_TYPES and ENTRY_TYPES lists
3. **Efficient** - O(1) dictionary lookups instead of O(n) loops
4. **Type-safe** - No risk of typos or naming convention changes breaking the code
5. **Tested** - Comprehensive test suite with 16 tests covering all column/entry types
