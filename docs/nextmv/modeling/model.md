# Model

!!! tip "Reference"

    Find the reference for the `model` module [here](./reference/model.md).

A decision model is a program that makes decisions, i.e.: solves decision
problems. The model takes in an input (representing the problem data and
options) and returns an output, which is the solution to the decision problem.
The `nextmv.Model` class is the base class for all models. It holds the
necessary logic to handle all decisions.

!!! note

    Your programs **DO NOT** need to use the `nextmv.Model` functionality to work
    with Nextmv Cloud.

As explained in the [Deploy App][deploy-app] section, a valid application in
Nextmv is that which:

1. Reads from `stdin` or a file.
2. Writes to `stdout` or a file.
3. Conforms to the statistics convention for registering statistics.
4. Contains an `app.yaml` manifest.

The `nextmv.Model` class is provided for two purposes:

1. As an opinionated way to structure your models.
2. As a feature to be able to push Python models to Nextmv Cloud directly, as
   they are converted to valid Nextmv applications.

With that clarified, let's see how to use the `nextmv.Model` class.

When creating your own decision model, you must create a class that inherits
from `nextmv.Model` and implement the `solve` method.

```python
import nextmv

class YourCustomModel(nextmv.Model):
    def solve(self, input: nextmv.Input) -> nextmv.Output:
        """Implement the logic to solve the decision problem here."""
        pass
```

## Example

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
    nextmv.Option("duration", int, 30, "Max runtime duration (in seconds).", False),
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
import nextmv


model = DecisionModel()
input = nextmv.Input(data=sample_input, options=options)
output = model.solve(input)
nextmv.write(output)
```

```bash
$ python main.py -duration 5
{
  "items": [
    {
      "id": "cat",
      "value": 100,
      "weight": 20
    },
    {
      "id": "water",
      "value": 40,
      "weight": 2
    },
    {
      "id": "phone",
      "value": 6,
      "weight": 1
    },
    {
      "id": "book",
      "value": 63,
      "weight": 10
    },
    {
      "id": "rx",
      "value": 81,
      "weight": 1
    },
    {
      "id": "coat",
      "value": 44,
      "weight": 9
    },
    {
      "id": "keys",
      "value": 92,
      "weight": 1
    },
    {
      "id": "nuts",
      "value": 18,
      "weight": 4
    }
  ]
}
```

## Push to Nextmv Cloud

If you want to run the model as a Nextmv Cloud app, you need two components:

* A model configuration. This configuration tells Nextmv Cloud how to _load_
  the model.
* An app manifest. Every Nextmv Cloud app must have a manifest that establishes
  how to _run_ the app. It holds information such as the runtime, and files
  that the app needs.

Continuing with the knapsack problem, you can define the model configuration
for it. From the config, there is a convenience function to create the
manifest.

```python
import nextmv
import nextmv.cloud


model_configuration = nextmv.ModelConfiguration(
    name="highs_model",
    requirements=[ # Acts as a requirements.txt file.
        "highspy==1.8.1", # Works like a line in a requirements.txt file.
        "nextmv==0.25.0"
    ],
    options=options,
)
manifest = nextmv.cloud.Manifest.from_model_configuration(model_configuration)
```

Once the model, options, model configuration, and manifest are defined, you can
push the app to Nextmv Cloud.

```python
import nextmv.cloud


client = nextmv.cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
application = nextmv.cloud.Application(client=client, id="<YOUR_APP_ID>")
application.push(
    model=model, # The implementation of the `nextmv.Model` class.
    model_configuration=model_configuration,
    manifest=manifest,
    verbose=True,
)
```

[deploy-app]: https://docs.nextmv.io/docs/using-nextmv/deploy/app/overview
