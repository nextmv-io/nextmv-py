# Output

!!! tip "Reference"

    Find the reference for the `output` module [here](../reference/output.md).

Write the output data after a run is completed.

## `JSON` outputs

Work with `JSON`output.

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

The `solution` property of the output is a dictionary that represents the
output data. The `statistics` property can be a `nextmv.Statistics` object, or
a dictionary.

## `CSV` output

Work with one, or multiple, `CSV` files. In the `solution` property of the
output, the keys are the filenames and the values are the dataframes,
represented as a list of dictionaries.

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

Similarly to the `JSON` output, the `statistics` property can be a
`nextmv.Statistics` object, or a dictionary.

## Assets

A run in Nextmv Cloud can include [custom assets][custom-assets], such as those
used in [custom visualization][custom-visualization].

You can use the `assets` property of the output to include these assets.

### Example

You can create a simple plot, which consists of a Plotly bar chart with radius
and distance for a planet. Consider the following `visuals.py` file:

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

The `assets` can be a list of `nextmv.Asset` objects, or a list of dictionaries
that comply with the [custom assets][custom-assets] and [custom
visualization][custom-visualization] schemas, whichever the case may be.

[custom-assets]: https://docs.nextmv.io/docs/using-nextmv/run/custom-assets
[custom-visualization]: https://docs.nextmv.io/docs/using-nextmv/run/custom-visualization/overview
