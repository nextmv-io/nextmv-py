# Input

!!! tip "Reference"

    Find the reference for the `input` module [here](../reference/input.md).

Capture the input data for the run.

## `JSON` input

Work with `JSON` inputs.

```python
import nextmv

# Read JSON from stdin.
json_input_1 = nextmv.load()
print(json_input_1.data)

# Can also specify JSON format directly, and read from a file.
json_input_2 = nextmv.load(input_format=nextmv.InputFormat.JSON, path="input.json")
print(json_input_2.data)
```

## `TEXT` input

Work with plain, `utf-8` encoded, text inputs.

```python
import nextmv

# Read text from stdin.
text_input_1 = nextmv.load(input_format=nextmv.InputFormat.TEXT)
print(text_input_1.data)

# Can also read from a file.
text_input_2 = nextmv.load(input_format=nextmv.InputFormat.TEXT, path="input.txt")
print(text_input_2.data)
```

## `CSV` input

Work with one, or multiple, `CSV` files. In the resulting `data` property of
the input, the keys are the filenames and the values are the dataframes,
represented as a list of dictionaries.

```python
import nextmv

# Read multiple CSV files from a dir named "input".
csv_archive_input_1 = nextmv.load(input_format=nextmv.InputFormat.CSV_ARCHIVE)
print(csv_archive_input_1.data)

# Read multiple CSV files from a custom dir.
csv_archive_input_2 = nextmv.load(input_format=nextmv.InputFormat.CSV_ARCHIVE, path="custom_dir")
print(csv_archive_input_2.data)
```
