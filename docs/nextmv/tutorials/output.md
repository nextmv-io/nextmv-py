# Output

!!! tip "Reference"

    Find the reference for the `output` module [here](../reference/output.md).

Write the output data after a run is completed. The [`Output`][output] class is
the main holding place for the decisions made by the decision model. An output
is built through [options][options], a solution, statistics, and other assets.
An output is written to a destination, through the
[`OutputWriter`][output-writer] class. You may use the [`write`][write]
function to write an output to a destination, or call the `.write` method on
the `OutputWriter` class.

The most common destination, and the one used by Nextmv Cloud, is either
`stdout` or the local filesystem. The
[`LocalOutputWriter`][local-output-writer] class is provided for this reason
and it is the default output writer used by the `write` function. When writing
locally, the output is written, by default, to this locations:

* File or `stdout` for `JSON` outputs.
* `output` directory for `CSV_ARCHIVE` outputs.
* `outputs` directory for `MULTI_FILE` outputs.

## `JSON` outputs

Work with `JSON` outputs. This is the default output format for Nextmv.

```python
import nextmv

output = nextmv.Output(
    solution={"foo": "bar"},
    statistics=nextmv.Statistics(
        result=nextmv.ResultStatistics(
            duration=1.0,
            value=2.0,
            custom={"custom": "result_value"},
        ),
        run=nextmv.RunStatistics(
            duration=3.0,
            iterations=4,
            custom={"custom": "run_value"},
        ),
    ),
)

# Write to stdout.
nextmv.write(output)

# Write to a file.
nextmv.write(output, path="output.json")
```

The `.solution` property of the output is a dictionary that represents the
output data. The `.statistics` property can be a [`Statistics`][statistics]
object, or a dictionary.

By default, `Output` serializes `JSON` using pretty printing. If you want
to change the serialization behavior, you can pass the `json_configurations`
parameter. The provided values are passed to the underlying `json.dumps`
method. For example, to get compressed output, you can set:

```python
output = nextmv.Output(
    # ...
    json_configurations={
        "indent": None,  # No indentation for compact output
        "separators": (",", ":")  # Use compact separators
    },
    # ...
)
```

## `CSV_ARCHIVE` outputs

Work with one, or multiple, `CSV` files. In the `.solution` property of the
output, the keys are the filenames and the values are the dataframes,
represented as a list of dictionaries. Each `CSV` file must be `utf-8`
encoded.

By default, the output is written to a directory named `output`, and the
filenames are derived from the keys of the `.solution` dictionary. If you want
to change the output directory, you can pass the `path` parameter to the
[`write`][write] function.

```python
import nextmv

output = nextmv.Output(
    output_format=nextmv.OutputFormat.CSV_ARCHIVE,
    solution={
        "output": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 40},
        ],
    },
    statistics=nextmv.Statistics(
        result=nextmv.ResultStatistics(
            duration=1.0,
            value=2.0,
            custom={"custom": "result_value"},
        ),
        run=nextmv.RunStatistics(
            duration=3.0,
            iterations=4,
            custom={"custom": "run_value"},
        ),
    ),
)

# Write multiple CSV fiules to a dir named "output".
nextmv.write(output)

# Write multiple CSV files to a custom dir.
nextmv.write(output, "custom_dir")
```

Similarly to the `JSON` output, the `.statistics` property can be a
[`Statistics`][statistics] object, or a dictionary.

By default, `Output` serializes `CSV` using `,` as the separator. If you
want to change the serialization behavior, you can pass the `csv_configurations`
parameter. The provided values are passed to the underlying `csv.DictWriter`
method. For example, to use `;` as the separator, you can set:

```python
output = nextmv.Output(
    # ...
    csv_configurations={
        "delimiter": ";",  # Use semicolon as the separator
    },
    # ...
)
```

## `MULTI_FILE` outputs

When you need to work with a diverse set of files, use the `MULTI_FILE` output
format. Multi-file supports the following file formats:

* `.json`
* Text (utf-8 encoded text)
* `.csv` (which must be utf-8 encoded)
* `.xlsx` (Excel files)

To work with multi-file outputs, you need to define one or more
[`SolutionFile`][solution-file] classes, each of which is associated with a
file. You can use the following convenience functions to create these classes:

* [`json_solution_file`][json-solution-file]: write a `.json` file.
* [`csv_solution_file`][csv-solution-file]: write a `.csv` file.
* [`text_solution_file`][text-solution-file]: write a text file. Any file
  with `utf-8` encoded text can be used, like `.mip`, or `.lp` files.

By default, the output is written to a directory named `outputs`, and the
filenames are derived from the `.name` parameter of the
[`SolutionFile`][solution-file] classes. If you want to change the output
directory, you can pass the `path` parameter to the [`write`][write] function.

In the `output` directory, the following sub-directories are used:

* `outputs/solutions`: for the solution files.
* `outputs/statistics`: for the statistics file. If `MULTI_FILE` is used, the statistics
  are written to a file named `statistics.json`.
* `outputs/assets`: for the assets files. If `MULTI_FILE` is used, the assets
  are written to a file named `assets.json`.

```python
import nextmv

# Define a solution file for a JSON file.
json_file = nextmv.json_solution_file("output.json", {"foo": "bar"})

# Define a solution file for a CSV file.
csv_file = nextmv.csv_solution_file("output.csv", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 40}])

# Define a solution file for a text file.
text_file = nextmv.text_solution_file("output.txt", "Hello, World!")

output = nextmv.Output(
    output_format=nextmv.OutputFormat.MULTI_FILE,
    solution_files=[json_file, csv_file, text_file],
    statistics=nextmv.Statistics(
        result=nextmv.ResultStatistics(
            duration=1.0,
            value=2.0,
            custom={"custom": "result_value"},
        ),
        run=nextmv.RunStatistics(
            duration=3.0,
            iterations=4,
            custom={"custom": "run_value"},
        ),
    ),
)

# Write multiple files to a dir named "outputs".
nextmv.write(output)

# Write multiple files to a custom dir.
nextmv.write(output, "custom_dir")
```

When working with binary files, such as Excel files, you must define your own
`SolutionFile` class. The most important parameter of this class is the
`.writer`, which is a `Callable` (function) that you provide. The signature of
this function is as follows:

```python
def writer(file_path: str, data: Any) -> None:
    pass
```

The `file_path` establishes the location where this data is written to. The
`.name` defined in the class is going to be given to this function, with the
correct directory already joined. This `.writer` can receive additional
arguments and keyword arguments, which you can define in the `SolutionFile`
class through the `.writer_args` and `.writer_kwargs` parameters.

```python
from typing import Any

import nextmv

# Define a custom writer for an Excel file.
def excel_writer(file_path: str, data: Any) -> None:
    import pandas as pd

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

# Define a solution file for an Excel file.
excel_file = nextmv.SolutionFile(
    name="output.xlsx",
    writer=excel_writer,
    writer_args=[],  # Optional, you don't need to define this if no args are needed
    writer_kwargs={},  # Optional, you don't need to define this if no kwargs are needed
)

# Load the multi-file output with the defined solution files.
multi_file_output = nextmv.Output(
    output_format=nextmv.OutputFormat.MULTI_FILE,
    solution_files=[excel_file],
    statistics=nextmv.Statistics(
        result=nextmv.ResultStatistics(
            duration=1.0,
            value=2.0,
            custom={"custom": "result_value"},
        ),
        run=nextmv.RunStatistics(
            duration=3.0,
            iterations=4,
            custom={"custom": "run_value"},
        ),
    ),
)

# Write multiple files to a dir named "outputs".
nextmv.write(multi_file_output)

# Write multiple files to a custom dir.
nextmv.write(multi_file_output, "custom_dir")
```

## Assets

A run in Nextmv Cloud can include [custom assets][custom-assets], such as those
used in [custom visualization][custom-visualization].

You can use the `.assets` property of the output to include these assets.

For example, you can create a simple plot, which consists of a Plotly bar chart
with radius and distance for a planet. Consider the following `visuals.py`
file:

```python
import json

import nextmv
import plotly.graph_objects as go


def create_visuals(name: str, radius: float, distance: float) -> list[nextmv.Asset]:
    """Create a Plotly bar chart with radius and distance for a planet."""

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=[name], y=[radius], name="Radius (km)", marker_color="red", opacity=0.5),
    )
    fig.add_trace(
        go.Bar(x=[name], y=[distance], name="Distance (Millions km)", marker_color="blue", opacity=0.5),
    )
    fig.update_layout(
        title="Radius and Distance by Planet", xaxis_title="Planet", yaxis_title="Values", barmode="group"
    )
    fig = fig.to_json()

    assets = [
        nextmv.Asset(
            name="Plotly example",
            content_type="json",
            visual=nextmv.Visual(
                visual_schema=nextmv.VisualSchema.PLOTLY,
                visual_type="custom-tab",
                label="Charts",
            ),
            content=[json.loads(fig)],
        )
    ]

    return assets
```

This list of assets can be included in the output.

```python
import nextmv
from visuals import create_visuals

# Read the input from stdin.
input = nextmv.load()
name = input.data["name"]

options = nextmv.Options(
    nextmv.Option("details", bool, True, "Print details to logs. Default true.", False),
)

##### Insert model here

# Print logs that render in the run view in Nextmv Console.
message = f"Hello, {name}"
nextmv.log(message)

if options.details:
    detail = "You are", {input.data["distance"]}, " million km from the sun"
    nextmv.log(detail)

assets = create_visuals(name, input.data["radius"], input.data["distance"])

# Write output and statistics.
output = nextmv.Output(
    options=options,
    solution=None,
    statistics=nextmv.Statistics(
        result=nextmv.ResultStatistics(
            value=1.23,
            custom={"message": message},
        ),
    ),
    assets=assets,
)
nextmv.write(output)
```

The `.assets` can be a list of [`Asset`][assets] objects, or a list of
dictionaries that comply with the [custom assets][custom-assets] and [custom
visualization][custom-visualization] schemas, whichever the case may be.

[custom-assets]: https://docs.nextmv.io/docs/using-nextmv/run/custom-assets
[custom-visualization]: https://docs.nextmv.io/docs/using-nextmv/run/custom-visualization/overview
[output]: ../reference/output.md#nextmv.nextmv.output.Output
[output-writer]: ../reference/output.md#nextmv.nextmv.output.OutputWriter
[write]: ../reference/output.md#nextmv.nextmv.output.write
[local-output-writer]: ../reference/output.md#nextmv.nextmv.output.LocalOutputWriter
[options]: ./options.md
[statistics]: ../reference/output.md#nextmv.nextmv.output.Statistics
[assets]: ../reference/output.md#nextmv.nextmv.output.Asset
[solution-file]: ../reference/output.md#nextmv.nextmv.output.SolutionFile
[json-solution-file]: ../reference/output.md#nextmv.nextmv.output.json_solution_file
[csv-solution-file]: ../reference/output.md#nextmv.nextmv.output.csv_solution_file
[text-solution-file]: ../reference/output.md#nextmv.nextmv.output.text_solution_file
