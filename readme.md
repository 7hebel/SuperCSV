# 📊 SuperCSV.

### Adds simple typing system to CSV.

---

### ✨ Available CSV types.

| NAME       | SHORT FORMS | PYTHON TYPE                                                      |
|:---------- |:----------- |:---------------------------------------------------------------- |
| `integer`  | `int`, `i`  | `int`                                                            |
| `float`    | `f`         | `float`                                                          |
| `string`   | `str`, `s`  | `str`                                                            |
| `boolean`  | `bool`, `b` | `bool`                                                           |
| `array`    | `arr`, `a`  | `list` (not nested, supports only `int`, `float`, `str`, `bool`) |
| `object`   | `obj`, `o`  | `dict`                                                           |
| `datetime` | `dt`, `d`   | `datetime.datetime`                                              |

### 📜 SuperCSV file syntax.

```csv
col1: TYPE1
col2: TYPE2

@@


col1, col2
...values
```

The `@@` separates annotation header from data section and is required.

Type names are not case sensitive.

### 🚀 Usage.

```csv
name: string
age: int
adult: bool

@@

name,age,adult
"John",27,1
"Robert",13,0
```

```python
import supercsv

csv: supercsv.parser.SCSVObject = supercsv.use_file("test.scsv")

# -- Reading.
csv[0] # -> Rturns first row.
csv.read(1) # -> Returns second row.
for row in csv.read_all():
  row # iterate over all rows.


# -- Writting.
new_row = {"name": "Alice", "age": 24, "adult": 1}

csv[0] = new_row # Override first row with new one.
csv.update_row(1, new_row) # Override second row with new one.
csv.update_field(0, "age", 28) # Update single field in the first row.

csv.insert_row(new_row) # Insert new row.

csv.remove_row(0) # Remove row at index 0.

```


