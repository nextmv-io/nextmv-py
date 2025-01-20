# Nextmv Python SDK

This is the Python SDK for the Nextmv Platform.

## Installation

Requires Python `>=3.9`. Install using `pip`:

```bash
pip install nextmv
```

Install all optional dependencies:

```bash
pip install "nextmv[all]"
```

## Usage

The Nextmv Python SDK is used to interact with various parts of the Nextmv
Platform:

- [Working with a Decision Model][working-with-a-decision-model]: Get to know
      the functionality for running decision models. These API functions work
      the same way in any machine (local or hosted).
- [Cloud][cloud]: Interact with the Nextmv Cloud API.

### Working with a Decision Model

To run a model, you can use the various helper functionality provided by the
SDK. Note that when you create an app that runs locally in your machine, it
will run in the same way in a Nextmv Cloud-hosted machine.

#### Options

Use options to capture parameters (i.e.: configurations) for the run:

```python
import nextmv

options = nextmv.Options(
    nextmv.Parameter("str_option", str, "default value", "A string option", required=True),
    nextmv.Parameter("int_option", int, 1, "An int option", required=False),
    nextmv.Parameter("float_option", float, 1.0, "A float option", required=False),
    nextmv.Parameter("bool_option", bool, True, "A bool option", required=True),
)

print(options.str_option)
print(options.int_option)
print(options.float_option)
print(options.bool_option)
print(options.to_dict())
```

By using options, you are able to pass in the values of the parameters with CLI
arguments or environment variables.

<!-- markdownlint-disable -->

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or environment variables.

optiTo exclude the `markdownlint` rule start and end block, you can use the
following syntax in your markdown file:STR_OPTION
        [env var: STR_OPTION] (required) (default: default value) (type: str): A string option
  -int_optRemember to replace `Your markdown content here` with your actual markdown
content.(type: int): An int option
  -float_option FLOAT_OPTION, --float_option FLOAT_OPTION
        [env var: FLOAT_OPTION] (default: 1.0) (type: float): A float option
  -bool_option BOOL_OPTION, --bool_option BOOL_OPTION
        [env var: BOOL_OPTION] (required) (default: True) (type: bool): A bool option
```

<!-- markdownlint-enable -->

#### Input

Capture the input data for the run.

- Work with `JSON`inputs.

    ```python
    import nextmv

    # Read JSON from stdin.
    json_input_1 = nextmv.load_local()
    print(json_input_1.data)

    # Can also specify JSON format directly, and read from a file.
    json_input_2 = nextmv.load_local(input_format=nextmv.InputFormat.JSON, path="input.json")
    print(json_input_2.data)
    ```

- Work with plain, `utf-8` encoded, text inputs.

    ```python
    import nextmv

    # Read text from stdin.
    text_input_1 = nextmv.load_local(input_format=nextmv.InputFormat.TEXT)
    print(text_input_1.data)

    # Can also read from a file.
    text_input_2 = nextmv.load_local(input_format=nextmv.InputFormat.TEXT, path="input.txt")
    print(text_input_2.data)
    ```

<!-- markdownlint-disable -->

- Work with multiple `CSV` files.

    ```python
    import nextmv

    # Read multiple CSV files from a dir named "input".
    csv_archive_input_1 = nextmv.load_local(input_format=nextmv.InputFormat.CSV_ARCHIVE)
    print(csv_archive_input_1.data)

    # Read multiple CSV files from a custom dir.
    csv_archive_input_2 = nextmv.load_local(input_format=nextmv.InputFormat.CSV_ARCHIVE, path="custom_dir")
    print(csv_archive_input_2.data)
    ```

<!-- markdownlint-enable -->

#### Logging

The Nextmv platform captures logs via `stderr`. Use the provided functionality
to record logs.

```python
import sys

import nextmv

print("0. I do nothing")

nextmv.redirect_stdout()

nextmv.log("1. I log a message to stderr")

print("2. I print a message to stdout")

nextmv.reset_stdout()

print("3. I print another message to stdout")

print("4. I print yet another message to stderr without the logger", file=sys.stderr)

nextmv.log("5. I log a message to stderr using the nextmv module directly")

print("6. I print a message to stdout, again")
```

After executing it, here are the messages printed to the different streams.

- `stdout`

    ```txt
    1. I do nothing
    2. I print another message to stdout
    3. I print a message to stdout, again
    ```

- `stderr`

    ```txt
    1. I log a message to stderr
    2. I print a message to stdout
    3. I print yet another message to stderr without the logger
    4. I log a message to stderr using the nextmv module directly
    ```

#### Output

Write the output data after a run is completed.

- Work with `JSON` outputs.

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
    nextmv.write_local(output)

    # Write to a file.
    nextmv.write_local(output, path="output.json")
    ```

- Work with multple `CSV` files.

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
    nextmv.write_local(output)

    # Write multiple CSV files to a custom dir.
    nextmv.write_local(output, "custom_dir")
    ```

#### Model

A decision model is a program that makes decisions, i.e.: solves decision
problems. The model takes in an input (representing the problem data and
options) and returns an output, which is the solution to the decision problem.
The `nextmv.Model` class is the base class for all models. It holds the
necessary logic to handle all decisions.

When creating your own decision model, you must create a class that inherits
from `nextmv.Model` and implement the `solve` method.

```python
import nextmv

class YourCustomModel(nextmv.Model):
    def solve(self, input: nextmv.Input) -> nextmv.Output:
        """Implement the logic to solve the decision problem here."""
        pass
```

Here is an example of a simple knapsack problem, using `highspy` (HiGHS
open-source solver).

Consider the following input and options to configure the solver:

```python
import nextmv


sample_input = {
  "items": [
    {"id": "cat","value": 100,"weight": 20},
    {"id": "dog","value": 20,"weight": 45},
    {"id": "water","value": 40,"weight": 2},
    {"id": "phone","value": 6,"weight": 1},
    {"id": "book","value": 63,"weight": 10},
    {"id": "rx","value": 81,"weight": 1},
    {"id": "tablet","value": 28,"weight": 8},
    {"id": "coat","value": 44,"weight": 9},
    {"id": "laptop","value": 51,"weight": 13},
    {"id": "keys","value": 92,"weight": 1},
    {"id": "nuts","value": 18,"weight": 4}
  ],
  "weight_capacity": 50
}
options = nextmv.Options(
    nextmv.Parameter("duration", int, 30, "Max runtime duration (in seconds).", False),
)
```

You can define a `DecisionModel` that packs the knapsack with the most valuable
items without exceeding the weight capacity.

```python
import time
from importlib.metadata import version

import highspy
import nextmv

class DecisionModel(nextmv.Model):
    def solve(self, input: nextmv.Input) -> nextmv.Output:
        """Solves the given problem and returns the solution."""

        start_time = time.time()

        # Creates the solver.
        solver = highspy.Highs()
        solver.silent()  # Solver output ignores stdout redirect, silence it.
        solver.setOptionValue("time_limit", input.options.duration)

        # Initializes the linear sums.
        weights = 0.0
        values = 0.0

        # Creates the decision variables and adds them to the linear sums.
        items = []
        for item in input.data["items"]:
            item_variable = solver.addVariable(0.0, 1.0, item["value"])
            items.append({"item": item, "variable": item_variable})
            weights += item_variable * item["weight"]
            values += item_variable * item["value"]

        # This constraint ensures the weight capacity of the knapsack will not be
        # exceeded.
        solver.addConstr(weights <= input.data["weight_capacity"])

        # Sets the objective function: maximize the value of the chosen items.
        status = solver.maximize(values)

        # Determines which items were chosen.
        chosen_items = [
            item["item"] for item in items if solver.val(item["variable"]) > 0.9
        ]

        input.options.version = version("highspy")

        statistics = nextmv.Statistics(
            run=nextmv.RunStatistics(duration=time.time() - start_time),
            result=nextmv.ResultStatistics(
                value=sum(item["value"] for item in chosen_items),
                custom={
                    "status": str(status),
                    "variables": solver.numVariables,
                    "constraints": solver.numConstrs,
                },
            ),
        )

        return nextmv.Output(
            options=input.options,
            solution={"items": chosen_items},
            statistics=statistics,
        )
```

To solve the problem, you can run the model with the input and options:

```python
import json

import nextmv


model = DecisionModel()
input = nextmv.Input(data=sample_input, options=options)
output = model.solve(input)
print(json.dumps(output.solution, indent=2))
```

If you want to run the model as a Nextmv Cloud app, you need two components:

- A model configuration. This configuration tells Nextmv Cloud how to _load_
  the model.
- An app manifest. Every Nextmv Cloud app must have a manifest that establishes
  how to _run_ the app. It holds information such as the runtime, and files
  that the app needs.

Continuing with the knapsack problem, you can define the model configuration
for it. From the config, there is a convenience function to create the manifest.

```python
import nextmv
import nextmv.cloud


model_configuration = nextmv.ModelConfiguration(
    name="highs_model",
    requirements=[ # Acts as a requirements.txt file.
        "highspy==1.8.1", # Works like a line in a requirements.txt file.
        "nextmv==0.14.0"
    ],
    options=options,
)
manifest = nextmv.cloud.Manifest.from_model_configuration(model_configuration)
```

Once the model, options, model configuration, and manifest are defined, you can
[push the app to Nextmv Cloud][push-an-application] and [run
it][run-an-application].

### Cloud

Before starting:

1. [Sign up][signup] for a Nextmv account.
2. Get your API key. Go to [Team > API Key][api-key].

Visit the [docs][docs] for more information. Make sure that you have your API
key set as an environment variable:

```bash
export NEXTMV_API_KEY="<YOUR-API-KEY>"
```

Additionally, you must have a valid app in Nextmv Cloud.

#### Push an application

There are two strategies to push an application to the Nextmv Cloud:

1. Specifying `app_dir`, which is the path to an app’s root directory. This
   acts as an external strategy, where the app is composed of files in a
   directory and those apps are packaged and pushed to Nextmv Cloud. This is
   language-agnostic and can work for an app written in any language.

    Place the following script in the root of your app directory and run it to
    push your app to the Nextmv Cloud. This is equivalent to using the Nextmv
    CLI and running `nextmv app push`.

    ```python
    import os

    from nextmv import cloud

    client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
    app = cloud.Application(client=client, id="<YOUR-APP-ID>")
    app.push()  # Use verbose=True for step-by-step output.
    ```

2. Specifying a `model` and `model_configuration`. This acts as an internal (or
   Python-native) strategy called "Apps from Models", where an app is created
   from a [`nextmv.Model`][model]. The model is encoded, some dependencies and
   accompanying files are packaged, and the app is pushed to Nextmv Cloud.

   To push a `nextmv.Model` to Nextmv Cloud, you need optional dependencies.
   You can install them by running:

    ```bash
    pip install "nextmv[all]"
    ```

    Once all the optional dependencies are installed, you can push the app to
    Nextmv Cloud.

    ```python
    import os

    from nextmv import cloud

    class CustomDecisionModel(nextmv.Model):
        def solve(self, input: nextmv.Input) -> nextmv.Output:
            """Implement the logic to solve the decision problem here."""
            pass

    client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
    app = cloud.Application(client=client, id="<YOUR-APP-ID>")

    model = CustomDecisionModel()
    options = nextmv.Options() # Define the options here.
    model_configuration = nextmv.ModelConfiguration(
        name="custom_decision_model",
        requirements=[ # Acts as a requirements.txt file.
            "nextmv==0.14.0",
            # Add any other dependencies here.
        ],
        options=options,
    )
    manifest = nextmv.cloud.Manifest.from_model_configuration(model_configuration)

    app.push( # Use verbose=True for step-by-step output.
        manifest=manifest,
        model=model,
        model_configuration=model_configuration,
    )
    ```

#### Run an application

Make a run and get the results.

```python
import os

from nextmv import cloud

input = {
    "defaults": {"vehicles": {"speed": 20}},
    "stops": [
        {
            "id": "Nijō Castle",
            "location": {"lon": 135.748134, "lat": 35.014239},
            "quantity": -1,
        },
        {
            "id": "Kyoto Imperial Palace",
            "location": {"lon": 135.762057, "lat": 35.025431},
            "quantity": -1,
        },
    ],
    "vehicles": [
        {
            "id": "v2",
            "capacity": 2,
            "start_location": {"lon": 135.728898, "lat": 35.039705},
        },
    ],
}

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR-APP-ID>")
result = app.new_run_with_result(
    input=input,
    instance_id="latest",
    run_options={"solve.duration": "1s"},
    polling_options=cloud.PollingOptions(),  # Customize the polling options.
)
print(result.to_dict())
```

[signup]: https://cloud.nextmv.io
[docs]: https://nextmv.io/docs
[api-key]: https://cloud.nextmv.io/team/api-keys
[cloud]: #cloud
[working-with-a-decision-model]: #working-with-a-decision-model
[push-an-application]: #push-an-application
[run-an-application]: #run-an-application
[model]: #model
