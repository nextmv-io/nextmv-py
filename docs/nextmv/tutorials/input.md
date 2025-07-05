# Input

!!! tip "Reference"

    Find the reference for the `input` module [here](../reference/input.md).

Capture the input data for the run. The [`Input`][input] class is the main
holding place for a decision model's input data. An input is built through
[options][options] and data. An input is loaded from a source, through the
[`InputLoader`][input-loader] class. You may use the [`load`][load] function to
build an input from a source, or call the `.load`method on the `InputLoader`
class.

The most common source, and the one used by Nextmv Cloud, is either `stdin` or
the local filesystem. The [`LocalInputLoader`][local-input-loader] class is
provided for this reason and it is the default input loader used by the `load`
function.

## `JSON` inputs

Work with `JSON` inputs. This is the default input format for Nextmv.

```python
import nextmv

# Read JSON from stdin.
json_input_1 = nextmv.load()
print(json_input_1.data)

# Can also specify JSON format directly, and read from a file.
json_input_2 = nextmv.load(input_format=nextmv.InputFormat.JSON, path="input.json")
print(json_input_2.data)
```

## `TEXT` inputs

Work with plain, `utf-8` encoded, text inputs. Note that the data is not
limited to exist as a `.txt` file, any file with `utf-8` encoded text can be
used as input, like `.mip`, or `.lp` files.

```python
import nextmv

# Read text from stdin.
text_input_1 = nextmv.load(input_format=nextmv.InputFormat.TEXT)
print(text_input_1.data)

# Can also read from a file.
text_input_2 = nextmv.load(input_format=nextmv.InputFormat.TEXT, path="input.txt")
print(text_input_2.data)
```

## `CSV_ARCHIVE` inputs

Work with one, or multiple, `CSV` files. In the resulting `.data` property of
the input, the keys are the filenames and the values are the dataframes,
represented as a list of dictionaries. Each `CSV` file must be `utf-8` encoded.

```python
import nextmv

# Read multiple CSV files from a dir named "input".
csv_archive_input_1 = nextmv.load(input_format=nextmv.InputFormat.CSV_ARCHIVE)
print(csv_archive_input_1.data)

# Read multiple CSV files from a custom dir.
csv_archive_input_2 = nextmv.load(input_format=nextmv.InputFormat.CSV_ARCHIVE, path="custom_dir")
print(csv_archive_input_2.data)
```

## `MULTI_FILE` inputs

When you need to work with a diverse set of files, use the `MULTI_FILE` input
format. Multi-file supports the following file formats:

* `.json`
* Text (utf-8 encoded text)
* `.csv` (which must be utf-8 encoded)
* `.xlsx` (Excel files)

To work with multi-file inputs, you need to define one or more
[`DataFile`][data-file] classes, each of which is associated with a file. You
can use the following convenience functions to create these classes:

* [`json_data_file`][json-data-file]: load a `.json` file.
* [`csv_data_file`][csv-data-file]: load a `.csv` file.
* [`text_data_file`][text-data-file]: load a text file. Any file with
  `utf-8` encoded text can be used, like `.mip`, or `.lp` files.

```python
import nextmv

# Define a data file for a JSON file.
json_file = nextmv.json_data_file("input.json")

# Define a data file for a CSV file.
csv_file = nextmv.csv_data_file("input.csv")

# Define a data file for a text file.
text_file = nextmv.text_data_file("input.txt")

# Load the multi-file input with the defined data files from a dir named "inputs".
multi_file_input_1 = nextmv.load(
    input_format=nextmv.InputFormat.MULTI_FILE,
    data_files=[json_file, csv_file, text_file],
)
print(multi_file_input_1.data)

# Load the multi-file input with the defined data files from a custom dir.
multi_file_input_2 = nextmv.load(
    input_format=nextmv.InputFormat.MULTI_FILE,
    path="custom_dir",
    data_files=[json_file, csv_file, text_file],
)
print(multi_file_input_2.data)
```

The resulting `.data` property of the `Input` object will contain a dictionary
where the keys are the names of the files, and the values are the data loaded
from those files.

When working with binary files, such as Excel files, you must define your own
`DataFile` class. The most important parameter of this class is the `.loader`,
which is a `Callable` (function) that you provide. The signature of this
function is as follows:

```python
def loader(file_path: str) -> Any:
    pass
```

The `file_path` establishes the location where this data is read from. The
`.name` defined in the class is going to be given to this function, with the
correct directory already joined. This `.loader` can receive additional
arguments and keyword arguments, which you can define in the `DataFile` class
through the `.loader_args` and `.loader_kwargs` parameters.

```python
from typing import Any

import nextmv


# Define a custom loader for an Excel file.
def excel_loader(file_path: str) -> Any:
    import pandas as pd

    return pd.read_excel(file_path, sheet_name=None)


# Define a data file for an Excel file.
excel_file = nextmv.DataFile(
    name="input.xlsx",
    loader=excel_loader,
    loader_args=[],  # Optional, you don't need to define this if no args are needed.
    loader_kwargs={},  # Optional, you don't need to define this if no kwargs are needed.
)

# Load the multi-file input with the defined data files from a dir named "inputs".
multi_file_input_3 = nextmv.load(
    input_format=nextmv.InputFormat.MULTI_FILE,
    data_files=[excel_file],
)
print(multi_file_input_3.data)

# Load the multi-file input with the defined data files from a custom dir.
multi_file_input_4 = nextmv.load(
    input_format=nextmv.InputFormat.MULTI_FILE,
    path="custom_dir",
    data_files=[excel_file],
)
print(multi_file_input_4.data)
```

As mentioned, the `.data` property of the `Input` object will contain a dictionary
where the keys are the names of the files, and the values are the data loaded
from those files. If you wish to customize the key names, you can use the
`.input_data_key` parameter in the `DataFile` class. The convenience functions
also support this argument, allowing you to specify a custom key name
for the data loaded from the file.

[data-file]: ../reference/input.md#nextmv.nextmv.input.DataFile
[json-data-file]: ../reference/input.md#nextmv.nextmv.input.json_data_file
[csv-data-file]: ../reference/input.md#nextmv.nextmv.input.csv_data_file
[text-data-file]: ../reference/input.md#nextmv.nextmv.input.text_data_file
[input]: ../reference/input.md#nextmv.nextmv.input.Input
[input-loader]: ../reference/input.md#nextmv.nextmv.input.InputLoader
[load]: ../reference/input.md#nextmv.nextmv.input.load
[local-input-loader]: ../reference/input.md#nextmv.nextmv.input.LocalInputLoader
[options]: ./options.md
