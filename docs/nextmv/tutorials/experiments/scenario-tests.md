# Scenario tests

!!! tip "Reference"

    Find the reference for the `scenario` module [here](../../reference/cloud/scenario.md).

!!! tip

    Find more information about scenario tests in this [section of the Nextmv docs](https://docs.nextmv.io/docs/using-nextmv/experiments/scenario).

Scenario tests are **offline** tests used to compare the output from one or
more scenarios. A scenario is composed of:

* An instance, to reference the underlying executable code.
* Input data, to provide the scenario with the necessary information to
  execute. Data can be obtained from input sets, managed inputs, or new data.
* Configurations, to define a variation of options/parameters to be used in the
  scenario.

You can use the `cloud.Scenario` class to set up a scenario. Consider the
following examples for setting up a scenario:

1. Input set

    ```python
    from nextmv import cloud

    scenario_1 = cloud.Scenario(
        scenario_input=cloud.ScenarioInput(
            scenario_input_type=cloud.ScenarioInputType.INPUT_SET,
            scenario_input_data="input-set-1",
        ),
        instance_id="v0.0.1",
        configuration=[
            cloud.ScenarioConfiguration(
                name="solve.duration",
                values=["1s", "2s"],
            ),
            cloud.ScenarioConfiguration(
                name="solve.iterations",
                values=["10", "20"],
            ),
        ],
    )
    ```

1. Managed inputs

    ```python
    from nextmv import cloud

    scenario_2 = cloud.Scenario(
        scenario_input=cloud.ScenarioInput(
            scenario_input_type=cloud.ScenarioInputType.INPUT,
            scenario_input_data=["input-1", "input-2"],
        ),
        instance_id="v0.0.2",
        configuration=[
            cloud.ScenarioConfiguration(
                name="solve.duration",
                values=["1s", "2s"],
            ),
            cloud.ScenarioConfiguration(
                name="solve.iterations",
                values=["10", "20"],
            ),
        ],
    )
    ```

1. New data

    ```python
    from nextmv import cloud

    sample_input = {
        "defaults": {
            "stops": {"duration": 120, "unplanned_penalty": 200000},
            "vehicles": {
                "end_location": {"lat": 33.122746, "lon": -96.659222},
                "end_time": "2021-10-17T11:00:00-06:00",
                "speed": 10,
                "start_location": {"lat": 33.122746, "lon": -96.659222},
                "start_time": "2021-10-17T09:00:00-06:00",
            },
        },
        "stops": [
            {"id": "location-1", "location": {"lat": 33.20580830033956, "lon": -96.75038245222623}, "quantity": -27},
            {"id": "location-2", "location": {"lat": 33.2259142720506, "lon": -96.54613745932127}, "quantity": -30},
            {"id": "location-3", "location": {"lat": 33.23528740544529, "lon": -96.61059803136642}, "quantity": -36},
            {"id": "location-4", "location": {"lat": 33.20379744909628, "lon": -96.61356543957307}, "quantity": -19},
            {"id": "location-5", "location": {"lat": 33.178801586789376, "lon": -96.64137458150537}, "quantity": -31},
        ],
        "vehicles": [{"capacity": 305, "id": "vehicle-1"}, {"capacity": 205, "id": "vehicle-2"}],
    }

    scenario_3 = cloud.Scenario(
        scenario_input=cloud.ScenarioInput(
            scenario_input_type=cloud.ScenarioInputType.NEW,
            scenario_input_data=[sample_input],
        ),
        instance_id="v0.0.3",
        configuration=[
            cloud.ScenarioConfiguration(
                name="solve.duration",
                values=["1s", "2s"],
            ),
            cloud.ScenarioConfiguration(
                name="solve.iterations",
                values=["10", "20"],
            ),
        ],
    )
    ```

* `scenario_1`. Demonstrates how to set up a scenario using an input set. The
  scenario input type is `INPUT_SET`, and the input set ID is `input-set-1`. An
  example instance with ID `v0.0.1` is used.
* `scenario_2`. Demonstrates how to set up a scenario using managed inputs. The
  scenario input type is `INPUT`, and the input IDs are `input-1` and
  `input-2`. An example instance with ID `v0.0.2` is used.
* `scenario_3`. Demonstrates how to set up a scenario using new data. The
  scenario input type is `NEW`, and the input data is a list of dictionaries
  containing the new data. An example instance with ID `v0.0.3` is used.

Note that for the three scenarios, the configuration is the same. The
configuration is a list of `ScenarioConfiguration` objects. A different set of
runs will be created from the cross-product of the configuration values. In the
examples, a total of 4 runs will be created for each scenario, with the
following options:

* `solve.duration="1s"` and `solve.iterations="10"`
* `solve.duration="1s"` and `solve.iterations="20"`
* `solve.duration="2s"` and `solve.iterations="10"`
* `solve.duration="2s"` and `solve.iterations="20"`

## Create a scenario test

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

You can create a scenario test using the `Application.create_scenario_test`
method.

```python
import os

from nextmv import cloud

sample_input = {
    "defaults": {
        "stops": {"duration": 120, "unplanned_penalty": 200000},
        "vehicles": {
            "end_location": {"lat": 33.122746, "lon": -96.659222},
            "end_time": "2021-10-17T11:00:00-06:00",
            "speed": 10,
            "start_location": {"lat": 33.122746, "lon": -96.659222},
            "start_time": "2021-10-17T09:00:00-06:00",
        },
    },
    "stops": [
        {"id": "location-1", "location": {"lat": 33.20580830033956, "lon": -96.75038245222623}, "quantity": -27},
        {"id": "location-2", "location": {"lat": 33.2259142720506, "lon": -96.54613745932127}, "quantity": -30},
        {"id": "location-3", "location": {"lat": 33.23528740544529, "lon": -96.61059803136642}, "quantity": -36},
        {"id": "location-4", "location": {"lat": 33.20379744909628, "lon": -96.61356543957307}, "quantity": -19},
        {"id": "location-5", "location": {"lat": 33.178801586789376, "lon": -96.64137458150537}, "quantity": -31},
    ],
    "vehicles": [{"capacity": 305, "id": "vehicle-1"}, {"capacity": 205, "id": "vehicle-2"}],
}

scenario_1 = cloud.Scenario(
    scenario_input=cloud.ScenarioInput(
        scenario_input_type=cloud.ScenarioInputType.INPUT_SET,
        scenario_input_data="input-set-1",
    ),
    instance_id="v0.0.1",
    configuration=[
        cloud.ScenarioConfiguration(
            name="solve.duration",
            values=["1s", "2s"],
        ),
        cloud.ScenarioConfiguration(
            name="solve.iterations",
            values=["10", "20"],
        ),
    ],
)

scenario_2 = cloud.Scenario(
    scenario_input=cloud.ScenarioInput(
        scenario_input_type=cloud.ScenarioInputType.INPUT,
        scenario_input_data=["input-1", "input-2"],
    ),
    instance_id="v0.0.2",
    configuration=[
        cloud.ScenarioConfiguration(
            name="solve.duration",
            values=["1s", "2s"],
        ),
        cloud.ScenarioConfiguration(
            name="solve.iterations",
            values=["10", "20"],
        ),
    ],
)

scenario_3 = cloud.Scenario(
    scenario_input=cloud.ScenarioInput(
        scenario_input_type=cloud.ScenarioInputType.NEW,
        scenario_input_data=[sample_input],
    ),
    instance_id="v0.0.3",
    configuration=[
        cloud.ScenarioConfiguration(
            name="solve.duration",
            values=["1s", "2s"],
        ),
        cloud.ScenarioConfiguration(
            name="solve.iterations",
            values=["10", "20"],
        ),
    ],
)

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

scenario_test_id = app.new_scenario_test(
    id="scenario_test_1",
    name="Scenario test 1",
    scenarios=[scenario_1, scenario_2, scenario_3],
    description="An optional description for your scenario test",
    repetitions=2,
)
print(scenario_test_id)
```

Please note the following from the example above:

* The `id`, `name` and `scenarios` parameters are required.
* The `description` is optional.
* The `repetitions` parameter is optional and defaults to 0. It defines how
  many times should the scenario test be repeated. A value of 0 means that the
  scenario test will not be repeated, thus, the scenario test will be executed
  once. A value of 1 means that the scenario test will be repeated once, thus,
  the scenario test will be executed twice. A value of 2 means that 3 scenario
  tests will be executed, and so on.
* You can define an optional `scenario_id` for each scenario. In the example,
  the ID is not defined for any of the scenarios, so the ID will be generated
  automatically by enumerating the scenarios (`scenario-1`, `scenario-2`,
  `scenario-3`). Note that every scenario must have a unique ID.

## Get a scenario test

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

Scenario tests are designed to be visualized from the [Console web
interface][console-web]. Go to the app, `Experiments` > `Scenario` tab.

![Scenario test][scenario-test-image]

We highly recommend using the Console for creating and managing scenario tests.
However, you can also use the Python SDK to get the results of a scenario test
with the `Application.scenario_test` method.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

scenario_test = app.scenario_test(scenario_test_id="<YOUR_SCENARIO_TEST_ID>")

nextmv.write(scenario_test)
```

To list all scenario tests in the application, you can use the
`Application.list_scenario_tests` method.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

scenario_tests = app.list_scenario_tests()

for st in scenario_tests:
    nextmv.write(st)
```

## Manage a scenario test

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

You can update a scenario test using the `Application.update_scenario_test`
method.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

scenario_test = app.update_scenario_test(
    scenario_test_id="<YOUR_SCENARIO_TEST_ID>",
    name="A new name",
    description="A new description",
)

nextmv.write(scenario_test)
```

You may also delete a scenario test using the `Application.delete_scenario_test`
method.

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

app.delete_scenario_test("<YOUR_SCENARIO_TEST_ID>")
```

[console-web]: https://cloud.nextmv.io
[scenario-test-image]: ../../../images/scenario-test.png
