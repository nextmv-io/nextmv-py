# Get started with an existing decision model

If you already have a Python decision model, this guide will help you get it
running locally using the `nextmv.local` package. On the other hand, if you are
new to Nextmv, you can head to the [tutorial on getting started with a new
model][get-started-new-model] instead.

To complete this tutorial, we will use an external example, working under the
principle that it is not a Nextmv-created decision model. You can, and should,
use your own decision model, or follow along with the example provided:

* [Vehicle routing problem with capacity constraints by
  OR-Tools][or-tools-example].

Let's dive right in 🤿.

## 1. Prepare the executable code

!!! tip

    If you are working with your own decision model and already know that it
    executes, feel free to skip this step.

The decision model is composed of executable code that solves an optimization
problem. Copy the desired example code to a script named `main.py`.

```python title="main.py"
"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp



def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = [
        # fmt: off
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
        # fmt: on
    ]
    data["demands"] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    data["vehicle_capacities"] = [15, 15, 15, 15]
    data["num_vehicles"] = 4
    data["depot"] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data["num_vehicles"]):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            continue
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data["demands"][node_index]
            plan_output += f" {node_index} Load({route_load}) -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        plan_output += f" {manager.IndexToNode(index)} Load({route_load})\n"
        plan_output += f"Distance of the route: {route_distance}m\n"
        plan_output += f"Load of the route: {route_load}\n"
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print(f"Total distance of all routes: {total_distance}m")
    print(f"Total load of all routes: {total_load}")


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data["vehicle_capacities"],  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)


if __name__ == "__main__":
    main()
```

## 2. Install requirements

!!! tip

    If you are working with your own decision model and already have all
    requirements ready for it, feel free to skip this step.

Make sure you have the appropriate requirements installed for your model. If
you don't have one already, create a `requirements.txt` file in the root of
your project with the Python package requirements needed.

```text title="requirements.txt"
ortools>=9.14.6206
```

Install the requirements by running the following command:

```bash
pip install -r requirements.txt
```

## 3. Run the executable code

!!! tip

    If you are working with your own decision model and already know that it
    executes, feel free to skip this step.

Make sure your decision model works by running the executable code.

```bash
$ python main.py
Objective: 6208
Route for vehicle 0:
 0 Load(0) ->  7 Load(8) ->  3 Load(10) ->  4 Load(14) ->  1 Load(15) ->  0 Load(15)
Distance of the route: 1552m
Load of the route: 15

Route for vehicle 1:
 0 Load(0) ->  14 Load(4) ->  16 Load(12) ->  10 Load(14) ->  9 Load(15) ->  0 Load(15)
Distance of the route: 1552m
Load of the route: 15

Route for vehicle 2:
 0 Load(0) ->  12 Load(2) ->  11 Load(3) ->  15 Load(11) ->  13 Load(15) ->  0 Load(15)
Distance of the route: 1552m
Load of the route: 15

Route for vehicle 3:
 0 Load(0) ->  8 Load(8) ->  2 Load(9) ->  6 Load(13) ->  5 Load(15) ->  0 Load(15)
Distance of the route: 1552m
Load of the route: 15

Total distance of all routes: 6208m
Total load of all routes: 60
```

## 4. Nextmv-ify the decision model

We are going to turn the executable decision model into a Nextmv Application.

!!! abstract "Application"

    So, what is a Nextmv Application? A Nextmv Application is an entity that
    contains a decision model as executable code. An Application can make a run
    by taking an input, executing the decision model, and producing an
    output. An Application is defined by its code, and a configuration file
    named `app.yaml`, known as the "app manifest".

    Think of the app as a shell that contains your decision model code, and
    provides the necessary structure to run it.

A run on a Nextmv Application follows this convention:

![App diagram][app-diagram]

* The app receives one, or more, inputs (problem data).
* The app run can be configured through options.
* The app processes the inputs, and executes the decision model.
* The app produces one, or more, outputs (solutions).
* The app optionally produces statistics (metrics) and assets (can be visual,
  like charts).

We are going to adapt the example so that it can follow these conventions.

Start by adding the `app.yaml` file, which is known as the [app
manifest][app-manifest], to the root of the project. This file contains the
configuration of the app.

```yaml title="app.yaml"
# This manifest holds the information the app needs to run on the Nextmv Cloud.
type: python
runtime: ghcr.io/nextmv-io/runtime/python:3.11
python:
  # All listed packages will get bundled with the app.
  pip-requirements: requirements.txt

# List all files/directories that should be included in the app.
files:
  - main.py
```

This tutorial is not meant to discuss the app manifest in-depth, for that you
can go to the [manifest docs][app-manifest]. However, these are the main
attributes shown in the manifest:

* `type`: it is a `python` application.
* `runtime`: when deployed to Nextmv Cloud, this application can be run on the
  standard `python:3.11` runtime.
* `files`: contains files that make up the executable code of the app. In this
  case, we only need the `main.py` file.
* `python.pip-requirements`: specifies the file with the Python packages that
  need to be installed for the application.

A dependency for `nextmv` is also added. This dependency is _optional_, and the
[modeling constructs][modeling-constructs] _are not needed_ to run a Nextmv
Application locally. However, using the SDK modeling features makes it easier
to work with Nextmv apps, as a lot of convenient functionality is already baked
in, like:

* Reading and interpreting the manifest.
* Easily reading and writing files based on the content format.
* Parsing and using options from the command line, or environment variables.
* Structuring inputs and outputs.

These are the new `requirements.txt` contents:

```text title="requirements.txt"
ortools>=9.14.6206
nextmv>=0.35.0
```

Now, you can overwrite the your `main.py` file with the Nextmv-ified version.

```python title="main.py"
MISSING CODE HERE!
```

This is a short summary of the changes introduced to the example:

* Change 1
* Change 2

Here is the data file that you need to place in an `inputs` directory:

```json title="input.json"
{
    "distance_matrix": [
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0]
    ],
    "demands" : [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8],
    "vehicle_capacities" : [15, 15, 15, 15],
    "num_vehicles" : 4,
    "depot" : 0
}
```

After you are done Nextmv-ifying, your Nextmv app should have the following
structure, for the example provided:

```text
.
├── app.yaml
├── inputs
│   └── input.json
├── main.py
└── requirements.txt
```

You are ready to run your existing Nextmv Application locally using the
`nextmv.local` package 🥳.

## 5. Start a run

You can initialize a local Application instance for your existing Nextmv
Application:

```python
from nextmv import local

local_app = local.Application(src="/path/to/your/existing/app")
```

This will create a local Application instance that points to your existing app
directory. The app directory must contain a valid `app.yaml` manifest file at
its root.

* You must specify the `src` argument with the path to your existing
  application directory.
* The directory must be structured according to Nextmv Application conventions.

Let's use the mechanisms provided by the `local` package to run the app
systematically by submitting a couple of runs to the local app.

```python
input = { # Provide any input appropriate for your app
  "name": "Patches",
  "radius": 6378,
  "distance": 147.6
}

run_1 = local_app.new_run(input=input)
print(run_1)

run_2 = local_app.new_run(input=input)
print(run_2)
```

This will print the IDs of the runs created. The app runs start in the
background.

## Get a run result

You can get a run result using the run ID.

```python
import nextmv


result_1 = local_app.run_result(run_id=run_1)
nextmv.write(result_1)
```

You should see an output similar to this one:

```json
{
  "description": "Local run created at 2025-10-03T09:14:49.543398Z",
  "id": "local-au9xnvbj",
  "metadata": {
    "application_id": "/path/to/your/existing/app",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-10-03T09:14:49.543398Z",
    "duration": 1311.6,
    "error": "",
    "input_size": 62.0,
    "output_size": 0.0,
    "format": {
      "input": {
        "type": "json"
      },
      "output": {
        "type": "json"
      }
    },
    "status_v2": "succeeded"
  },
  "name": "local run local-au9xnvbj",
  "user_email": "",
  "console_url": "",
  "synced_run_id": "devint-D6OCps3Ng",
  "synced_at": "2025-10-03T09:15:06.868320Z",
  "output": {
    "options": {
      "details": true
    },
    "solution": {
      "message": "Hello, Patches"
    },
    "statistics": {
      "result": {
        "value": 1.23,
        "custom": {
          "message": "Hello, Patches"
        }
      },
      "schema": "v1"
    },
    "assets": [...]
  }
}
```

You'll notice that the `.output` field contains the same output that is
produced by "manually" running the app. However, the run result also contains
information about the run, such as its ID, creation time, duration, status, and
more.

!!! note

    The Nextmv SDK keeps track of all the local runs you create inside your
    application.

## Get run information

Runs may take a while to complete. We recommend you poll for the run status
until it is completed. Once the run is completed, you can get the run result as
shown above.

You can get the run information using the run ID.

```python
result_info_2 = local_app.run_metadata(run_id=run_2)
nextmv.write(result_info_2)
```

You should see an output similar to this one:

```json
{
  "description": "Local run created at 2025-10-03T09:14:49.549581Z",
  "id": "local-9881aggf",
  "metadata": {
    "application_id": "/path/to/your/existing/app",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-10-03T09:14:49.549581Z",
    "duration": 0.0,
    "error": "",
    "input_size": 62.0,
    "output_size": 0.0,
    "format": {
      "input": {
        "type": "json"
      }
    },
    "status_v2": "queued"
  },
  "name": "local run local-9881aggf",
  "user_email": "",
  "console_url": ""
}
```

As you can see, the run information contains metadata about the run, such as its
status, creation time, and more.

## All in one

Since runs are started in the background, you should poll until the run
succeeds (or fails) to get the results. You can use the `new_run_with_result`
method to do everything:

1. Start a run
2. Poll for results
3. Return them

```python
result_3 = local_app.new_run_with_result(input=input)
nextmv.write(result_3)
```

You should see an output similar to the one shown in the [getting a run result
section][get-run-result].

The complete methodology for running is discussed in detail in the [runs
tutorial][runs-tutorial].

## Visualize assets

If your app produces visual assets, you can visualize them locally with the
following code:

```python
local_app.run_visuals(run_id=run_1)
```

This will open a browser window for each asset produced by the run. The visual
assets depend on what your specific application generates.

## Next steps

You have successfully:

* connected to your existing Nextmv Application,
* ran it locally using the `nextmv.local` package,
* obtained run results, and
* visualized assets (if your app produces them).

After you complete exploring the local experience, you can unleash the full
potential of the Nextmv Platform with [Cloud][cloud-index].

[get-started-new-model]: ./get-started-new-model.md
[get-run-result]: #get-a-run-result
[app-manifest]: https://docs.nextmv.io/docs/using-nextmv/deploy/app/manifest
[cloud-index]: ../cloud/index.md
[runs-tutorial]: ./runs.md
[or-tools-example]: https://developers.google.com/optimization/routing/cvrp
[app-diagram]: ../../images/app-diagram.png
[modeling-constructs]: ../modeling/index.md
