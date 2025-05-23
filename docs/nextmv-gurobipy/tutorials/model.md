# Model

!!! tip "Reference"

    Find the reference for the `model` module [here](../reference/model.md).

`Model` allows you to create a `gurobipy.Model` object from `nextmv.Options`.
This convenience function allows you to set up a Gurobi model using the
parameters that are customized through options. Notice that the return type is
a `gurobipy.Model`.

Consider the following script, which solves a simple knapsack problem.

```python
import time

import nextmv_gurobipy as ngp
from gurobipy import GRB

data = {
    "items": [
        {"id": "cat", "value": 100, "weight": 20},
        {"id": "dog", "value": 20, "weight": 45},
        {"id": "water", "value": 40, "weight": 2},
        {"id": "phone", "value": 6, "weight": 1},
        {"id": "book", "value": 63, "weight": 10},
        {"id": "rx", "value": 81, "weight": 1},
        {"id": "tablet", "value": 28, "weight": 8},
        {"id": "coat", "value": 44, "weight": 9},
        {"id": "laptop", "value": 51, "weight": 13},
        {"id": "keys", "value": 92, "weight": 1},
        {"id": "nuts", "value": 18, "weight": 4},
    ],
    "weight_capacity": 50,
}

options = ngp.ModelOptions().to_nextmv()
start_time = time.time()
model = ngp.Model(options)

# Initializes the linear sums.
weights = 0.0
values = 0.0

# Creates the decision variables and adds them to the linear sums.
items = []
for item in data["items"]:
    item_variable = model.addVar(vtype=GRB.BINARY, name=item["id"])
    items.append({"item": item, "variable": item_variable})
    weights += item_variable * item["weight"]
    values += item_variable * item["value"]

# This constraint ensures the weight capacity of the knapsack will not be
# exceeded.
model.addConstr(weights <= data["weight_capacity"])

# Sets the objective function: maximize the value of the chosen items.
model.setObjective(expr=values, sense=GRB.MAXIMIZE)

# Solves the problem.
model.optimize()
```

Run the script with custom options:

```bash
python main.py -TimeLimit 1 -MIPGap 0.4
...
...

Non-default parameters:
TimeLimit  1
MIPGap  0.4

Optimize a model with 1 rows, 11 columns and 11 nonzeros
Model fingerprint: 0x3fd9f770
Variable types: 0 continuous, 11 integer (11 binary)
Coefficient statistics:
  Matrix range     [1e+00, 4e+01]
  Objective range  [6e+00, 1e+02]
  Bounds range     [1e+00, 1e+00]
  RHS range        [5e+01, 5e+01]
Found heuristic solution: objective 428.0000000

Explored 0 nodes (0 simplex iterations) in 0.00 seconds (0.00 work units)
Thread count was 1 (of 10 available processors)

Solution count 1: 428 

Optimal solution found (tolerance 4.00e-01)
Best objective 4.280000000000e+02, best bound 5.430000000000e+02, gap 26.8692%
```

Notice how the solver output states which options were customized. Using the
`nextmv_gurobipy.Model` class has other added benefits, besides the convenience
of customizing solver options:

* It instantiates an empty environment.
* It redirects `stdout` to `stderr` for logging in Nextmv Cloud.
* It loads the license automatically if the `license_path` is given.
