# Get started with an existing decision model

!!! tip

    ⌛️ Approximate time to complete: 15 min.

If you already have a Python decision model, this guide will help you get it
running locally using the `nextmv.local` package. On the other hand, if you
don't have a decision model and are exploring Nextmv, you can head to the
[tutorial on getting started with a new model][get-started-new-model] instead.

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
type: python
runtime: ghcr.io/nextmv-io/runtime/python:3.11
files:
  - main.py
python:
  pip-requirements: requirements.txt
configuration:
  content:
    format: json
  options:
    items:
      - name: duration
        description: Duration for the solver, in seconds.
        required: false
        option_type: float
        default: 1
        additional_attributes:
          min: 0
          max: 10
          step: 1
        ui:
          control_type: slider
      - name: input
        description: Path to input file. Default is stdin.
        required: false
        option_type: string
        default: ""
      - name: output
        description: Path to output file. Default is stdout.
        required: false
        option_type: string
        default: ""
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
"""Capacited Vehicles Routing Problem (CVRP)."""

import json

import nextmv
import plotly.graph_objects as go
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def print_solution(
    data, manager, routing, solution, options: nextmv.Options
) -> nextmv.Output:
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")

    total_distance = 0
    total_load = 0
    routes = []
    for vehicle_id in range(data["num_vehicles"]):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            continue
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        route_load = 0
        plan = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data["demands"][node_index]
            plan_output += f" {node_index} Load({route_load}) -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
            stop = {
                "node": node_index,
                "load": route_load,
            }
            plan.append(stop)
        plan_output += f" {manager.IndexToNode(index)} Load({route_load})\n"
        stop = {
            "node": manager.IndexToNode(index),
            "load": route_load,
        }
        plan.append(stop)
        plan_output += f"Distance of the route: {route_distance}m\n"
        plan_output += f"Load of the route: {route_load}\n"
        route = {
            "vehicle_id": vehicle_id,
            "distance": route_distance,
            "load": route_load,
            "plan": plan,
        }
        routes.append(route)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print(f"Total distance of all routes: {total_distance}m")
    print(f"Total load of all routes: {total_load}")

    statistics = nextmv.Statistics(
        result=nextmv.ResultStatistics(
            duration=routing.solver().WallTime() / 1000.0,
            value=solution.ObjectiveValue(),
            custom={
                "total_distance": total_distance,
                "total_load": total_load,
            },
        )
    )

    # Create visualization assets
    assets = create_route_visualization(data, routes)

    output = nextmv.Output(
        options=options,
        solution={"routes": routes},
        statistics=statistics,
        assets=assets,
    )

    return output


def create_route_visualization(data, routes) -> list[nextmv.Asset]:
    """Create a Plotly visualization of the vehicle routes."""
    coordinates = data.get("coordinates", [])
    if not coordinates:
        return []

    fig = go.Figure()

    # Define colors for different vehicles
    colors = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]

    # Plot each route
    for route in routes:
        vehicle_id = route["vehicle_id"]
        plan = route["plan"]
        color = colors[vehicle_id % len(colors)]

        # Extract coordinates for this route
        route_x = []
        route_y = []
        for stop in plan:
            node = stop["node"]
            if node < len(coordinates):
                route_x.append(coordinates[node][0])
                route_y.append(coordinates[node][1])

        # Plot the route as a line
        fig.add_trace(
            go.Scatter(
                x=route_x,
                y=route_y,
                mode="lines+markers",
                name=f"Vehicle {vehicle_id}",
                line=dict(color=color, width=2),
                marker=dict(size=8),
            )
        )

    # Highlight the depot
    if coordinates:
        depot_x, depot_y = coordinates[0]
        fig.add_trace(
            go.Scatter(
                x=[depot_x],
                y=[depot_y],
                mode="markers",
                name="Depot",
                marker=dict(size=15, color="black", symbol="star"),
            )
        )

    # Update layout
    fig.update_layout(
        title="CVRP Routes Visualization",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        showlegend=True,
        hovermode="closest",
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    # Convert figure to JSON
    fig_json = fig.to_json()

    # Create asset
    assets = [
        nextmv.Asset(
            name="Route Visualization",
            content_type="json",
            visual=nextmv.Visual(
                visual_schema=nextmv.VisualSchema.PLOTLY,
                visual_type="custom-tab",
                label="Routes",
            ),
            content=[json.loads(fig_json)],
        )
    ]

    return assets


def main():
    """Solve the CVRP problem."""
    nextmv.redirect_stdout()
    manifest = nextmv.Manifest.from_yaml(".")
    options = manifest.extract_options()
    input = nextmv.load(path=options.input)

    # Instantiate the data problem.
    data = input.data

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
    search_parameters.time_limit.FromSeconds(options.duration)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        output = print_solution(data, manager, routing, solution, options)
        nextmv.write(output, path=options.output)


if __name__ == "__main__":
    main()
```

This is a short summary of the changes introduced to the example:

* Load the app manifest from the `app.yaml` file.
* Extract options (configurations) from the manifest.
* The input data is no longer in the Python file itself. We will move it to a
  file under `inputs/input.json`. In a single `json` file we will define
  the complete input. Given that we are working with the `json` content
  format, we use the Python SDK to load the input data from `stdin`.
* Modify the definition of data to use the loaded input data.
* Store the solution to the problem, and solver metrics (statistics), in an
  output.
* Write the output to `stdout`, given that we are working with the `json`
  content format.

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

Let's use the mechanisms provided by the `local` package to run the app
systematically by submitting a couple of runs to the local app, using the
[`local.Application.new_run`][local-app-new-run] method.

Create a script named `app1.py`, or use a cell of a Jupyter notebook. Copy and
paste the following code into it, making sure you use the correct app `src`
(for this example, the current working directory, `"."`).:

```python title="app1.py"
import os

import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src=".")

# Provide any input you want for the app. This input can come from a file, for
# example.
input = nextmv.load(path=os.path.join("inputs", "input.json"))

# Execute some local runs with the provided input.
run_1 = local_app.new_run(input=input)
print("run_1:", run_1)

run_2 = local_app.new_run(input=input)
print("run_2:", run_2)
```

When you instantiate a [`local.Application`][local-app], the `src` argument
must point to a directory where the [`app.yaml` manifest][app-manifest] file is
located.

This will print the IDs of the runs created. The app runs start in the
background. Run the script, or notebook cell, to get an output similar to this:

```bash
$ python app1.py

run_1: local-lyxnxlsl
run_2: local-ykfq7nej
```

## 6. Get a run result

You can get a run result using the run ID with the
[`local.Application.run_result`][local-app-run-result] method.

Create another script, which you can name `app2.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct run ID (one of the identifiers that were printed in step 5) and
app `src`:

```python title="app2.py"
import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src=".")

# Get the result of a specific run by its ID.
result_1 = local_app.run_result(run_id="<RUN_ID_1_PRINTED_IN_STEP_5>")
nextmv.write(result_1)
```

Run the script, or notebook cell, and you should see an output similar to this
one:

```bash
$ python app2.py

{
  "description": "Local run created at 2025-11-15T04:25:24.898982Z",
  "id": "local-odl83e4j",
  "metadata": {
    "application_id": ".",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-11-15T04:25:24.898982Z",
    "duration": 1801.5,
    "error": "",
    "input_size": 3649.0,
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
  "name": "local run local-odl83e4j",
  "user_email": "",
  "console_url": "",
  "output": {
    "options": {
      "duration": 1,
      "input": "",
      "output": ""
    },
    "solution": {
      "routes": [
        {
          "vehicle_id": 0,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 7,
              "load": 8
            },
            {
              "node": 3,
              "load": 10
            },
            {
              "node": 4,
              "load": 14
            },
            {
              "node": 1,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 1,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 14,
              "load": 4
            },
            {
              "node": 16,
              "load": 12
            },
            {
              "node": 10,
              "load": 14
            },
            {
              "node": 9,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 2,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 12,
              "load": 2
            },
            {
              "node": 11,
              "load": 3
            },
            {
              "node": 15,
              "load": 11
            },
            {
              "node": 13,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 3,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 8,
              "load": 8
            },
            {
              "node": 2,
              "load": 9
            },
            {
              "node": 6,
              "load": 13
            },
            {
              "node": 5,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        }
      ]
    },
    "statistics": {
      "result": {
        "duration": 1.001,
        "value": 6208.0,
        "custom": {
          "total_distance": 6208,
          "total_load": 60
        }
      },
      "schema": "v1"
    },
    "assets": []
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

## 7. Get run information

Runs may take a while to complete. We recommend you poll for the run status
until it is completed. Once the run is completed, you can get the run result as
shown above. To get the run information, use the run ID and the
[`local.Application.run_metadata`][local-app-run-metadata] method.

Create another script, which you can name `app3.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct run ID (one of the identifiers that were printed in step 5) and
app `src`:

You can get the run information using the run ID.

```python title="app3.py"
import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src=".")

# Get the information of a specific run by its ID.
result_info_2 = local_app.run_metadata(run_id="<RUN_ID_2_PRINTED_IN_STEP_5>")
nextmv.write(result_info_2)
```

Run the script, or notebook cell, and you should see an output similar to this
one:

```bash
$ python app3.py

{
  "description": "Local run created at 2025-11-15T04:25:24.898982Z",
  "id": "local-odl83e4j",
  "metadata": {
    "application_id": ".",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-11-15T04:25:24.898982Z",
    "duration": 1801.5,
    "error": "",
    "input_size": 3649.0,
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
  "name": "local run local-odl83e4j",
  "user_email": "",
  "console_url": ""
}
```

As you can see, the run information contains metadata about the run, such as its
status, creation time, and more.

## 8. All in one

Since runs are started in the background, you should poll until the run
succeeds (or fails) to get the results. You can use the
[`local.Application.new_run_with_result`][local-app-new-run-with-result] method
to do everything:

1. Start a run
2. Poll for results
3. Return them

Create another script, which you can name `app4.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct app `src`:

```python title="app4.py"
import os

import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src=".")

# Provide any input you want for the app. This input can come from a file, for
# example.
input = nextmv.load(path=os.path.join("inputs", "input.json"))

# Start a new run and get its result immediately.
result_3 = local_app.new_run_with_result(input=input)
nextmv.write(result_3)
```

Run the script, or notebook cell, and you should see an output similar to the
one shown in the [getting a run result section][get-run-result].

```bash
$ python app4.py

{
  "description": "Local run created at 2025-11-15T04:37:31.074413Z",
  "id": "local-cufver73",
  "metadata": {
    "application_id": ".",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-11-15T04:37:31.074413Z",
    "duration": 1763.5,
    "error": "",
    "input_size": 3649.0,
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
  "name": "local run local-cufver73",
  "user_email": "",
  "console_url": "",
  "output": {
    "options": {
      "duration": 1,
      "input": "",
      "output": ""
    },
    "solution": {
      "routes": [
        {
          "vehicle_id": 0,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 7,
              "load": 8
            },
            {
              "node": 3,
              "load": 10
            },
            {
              "node": 4,
              "load": 14
            },
            {
              "node": 1,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 1,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 14,
              "load": 4
            },
            {
              "node": 16,
              "load": 12
            },
            {
              "node": 10,
              "load": 14
            },
            {
              "node": 9,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 2,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 12,
              "load": 2
            },
            {
              "node": 11,
              "load": 3
            },
            {
              "node": 15,
              "load": 11
            },
            {
              "node": 13,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 3,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 8,
              "load": 8
            },
            {
              "node": 2,
              "load": 9
            },
            {
              "node": 6,
              "load": 13
            },
            {
              "node": 5,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        }
      ]
    },
    "statistics": {
      "result": {
        "duration": 1.001,
        "value": 6208.0,
        "custom": {
          "total_distance": 6208,
          "total_load": 60
        }
      },
      "schema": "v1"
    },
    "assets": []
  }
}
```

The complete methodology for running is discussed in detail in the [runs
tutorial][runs-tutorial].

## 9. Visualize run assets

The Nextmv-ified `main.py` script contains a method called
`create_route_visualization`, which was created by us. This method uses
`plotly` to create a visualization for the given example: the routes assigned
to the vehicles, departing and returning to the depot. We are going to use the
[location coordinates][location-coordinates] provided by the OR-Tools example
to visualize the routes.

Create a new `input_with_coordinates.json` file in the `inputs` directory which
includes the coordinates:

```json title="input_with_coordinates.json"
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
  "depot" : 0,
  "coordinates": [
    [456, 320],
    [228, 0],
    [912, 0],
    [0, 80],
    [114, 80],
    [570, 160],
    [798, 160],
    [342, 240],
    [684, 240],
    [570, 400],
    [912, 400],
    [114, 480],
    [228, 480],
    [342, 560],
    [684, 560],
    [0, 640],
    [798, 640]
  ]
}
```

Up until now, the `main.py` script has not created any run assets given that no
`coordinates` were given. Now, we can run the app again using this new input
file to generate the visualization assets. You can use the
[`local.Application.run_visuals`][local-app-run-visuals] method
to visualize the assets of a run.

Create another script, which you can name `app5.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct app `src`:

```python title="app5.py"
import os

import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src=".")

# Provide any input you want for the app. This input can come from a file, for
# example.
input = nextmv.load(path=os.path.join("inputs", "input_with_coordinates.json"))

# Start a new run and get its result immediately.
result_4 = local_app.new_run_with_result(input=input)
nextmv.write(result_4)

# Visualize the assets of the run.
local_app.run_visuals(run_id=result_4.id)
```

Run the script, or notebool cell, and you should see an output similar to this
one:

```bash
$ python app5.py

{
  "description": "Local run created at 2025-11-15T04:37:31.074413Z",
  "id": "local-cufver73",
  "metadata": {
    "application_id": ".",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-11-15T04:37:31.074413Z",
    "duration": 1763.5,
    "error": "",
    "input_size": 3649.0,
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
  "name": "local run local-cufver73",
  "user_email": "",
  "console_url": "",
  "output": {
    "options": {
      "duration": 1,
      "input": "",
      "output": ""
    },
    "solution": {
      "routes": [
        {
          "vehicle_id": 0,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 7,
              "load": 8
            },
            {
              "node": 3,
              "load": 10
            },
            {
              "node": 4,
              "load": 14
            },
            {
              "node": 1,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 1,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 14,
              "load": 4
            },
            {
              "node": 16,
              "load": 12
            },
            {
              "node": 10,
              "load": 14
            },
            {
              "node": 9,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 2,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 12,
              "load": 2
            },
            {
              "node": 11,
              "load": 3
            },
            {
              "node": 15,
              "load": 11
            },
            {
              "node": 13,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        },
        {
          "vehicle_id": 3,
          "distance": 1552,
          "load": 15,
          "plan": [
            {
              "node": 0,
              "load": 0
            },
            {
              "node": 8,
              "load": 8
            },
            {
              "node": 2,
              "load": 9
            },
            {
              "node": 6,
              "load": 13
            },
            {
              "node": 5,
              "load": 15
            },
            {
              "node": 0,
              "load": 15
            }
          ]
        }
      ]
    },
    "statistics": {
      "result": {
        "duration": 1.001,
        "value": 6208.0,
        "custom": {
          "total_distance": 6208,
          "total_load": 60
        }
      },
      "schema": "v1"
    },
    "assets": [...] # <==== Assets will now be present here.
  }
}
```

The `.output.solution.assets` field will now contain the visualization assets
produced by the `create_route_visualization` method in the `main.py` script.
The following libraries are supported for visualizing assets with the
`run_visuals` method:

* `plotly`
* `folium`

This will also open a browser window for each asset produced by the run. You
should see a simple plot like the following:

![OR-Tools visuals][ortools-visuals]

!!! warning

    The `run_visuals` method may not work as expected in a Jupyter notebook
    environment. We recommend running it from a script executed in a terminal.

## 10. Understanding what happened

If you inspect the application directory consolidated in step 4 again, you
will see a structure similar to the following:

```text
.
├── .nextmv
│   └── runs
│       ├── {RUN_1}
│       │   ├── inputs
│       │   │   └── input.json
│       │   ├── {RUN_1}.json
│       │   ├── logs
│       │   │   └── logs.log
│       │   ├── outputs
│       │   │   ├── assets
│       │   │   │   └── assets.json
│       │   │   ├── solutions
│       │   │   │   └── solution.json
│       │   │   └── statistics
│       │   │       └── statistics.json
│       │   └── visuals
│       ├── {RUN_2}
│       │   ├── inputs
│       │   │   └── input.json
│       │   ├── {RUN_2}.json
│       │   ├── logs
│       │   │   └── logs.log
│       │   ├── outputs
│       │   │   ├── assets
│       │   │   │   └── assets.json
│       │   │   ├── solutions
│       │   │   │   └── solution.json
│       │   │   └── statistics
│       │   │       └── statistics.json
│       │   └── visuals
│       ├── {RUN_3}
│       │   ├── inputs
│       │   │   └── input.json
│       │   ├── {RUN_3}.json
│       │   ├── logs
│       │   │   └── logs.log
│       │   ├── outputs
│       │   │   ├── assets
│       │   │   │   └── assets.json
│       │   │   ├── solutions
│       │   │   │   └── solution.json
│       │   │   └── statistics
│       │   │       └── statistics.json
│       │   └── visuals
│       └── {RUN_4}
│           ├── inputs
│           │   └── input.json
│           ├── {RUN_4}.json
│           ├── logs
│           │   └── logs.log
│           ├── outputs
│           │   ├── assets
│           │   │   └── assets.json
│           │   ├── solutions
│           │   │   └── solution.json
│           │   └── statistics
│           │       └── statistics.json
│           └── visuals
│               └── Routes_0.html
├── app.yaml
├── app1.py
├── app2.py
├── app3.py
├── app4.py
├── app5.py
├── inputs
│   ├── input_with_coordinates.json
│   └── input.json
├── main.py
├── README.md
└── requirements.txt
```

The `.nextmv` dir is used to store and manage the `local` applications runs in
a structured way. The `local` package is used to interact with these files,
with methods for starting runs, retrieving results, visualizing charts, and
more.

🎉🎉🎉 Congratulations, you have finished this tutorial!

## Next steps

You have successfully:

* Nextmv-ified a decision model.
* Ran it locally.
* Obtained run results.

After you complete exploring the `local` experience, you can unleash the full
potential of the Nextmv Platform with [Cloud][cloud-index].

[get-started-new-model]: ./get-started-new-model.md
[get-run-result]: #6-get-a-run-result
[app-manifest]: https://docs.nextmv.io/docs/using-nextmv/deploy/app/manifest
[cloud-index]: ../cloud/index.md
[runs-tutorial]: ./runs.md
[or-tools-example]: https://developers.google.com/optimization/routing/cvrp
[app-diagram]: ../../images/app-diagram.png
[modeling-constructs]: ../modeling/index.md
[local-app]: ./reference/application.md#nextmv.nextmv.local.application.Application
[local-app-new-run]: ./reference/application.md#nextmv.nextmv.local.application.Application.new_run
[local-app-run-result]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_result
[local-app-run-metadata]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_metadata
[local-app-new-run-with-result]: ./reference/application.md#nextmv.nextmv.local.application.Application.new_run_with_result
[local-app-run-visuals]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_visuals
[location-coordinates]: https://developers.google.com/optimization/routing/vrp#location_coordinates
[ortools-visuals]: ../../images/ortools-visuals.png
