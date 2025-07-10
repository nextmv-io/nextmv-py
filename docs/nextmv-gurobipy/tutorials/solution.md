# Solution

!!! tip "Reference"

    Find the reference for the `solution` module [here](../reference/solution.md).

`ModelSolution` allows access to the solution of a `gurobipy.Model`. It is a
simple convenience function that will collect the decision variables and their
values.

Consider the same script shown in the [model section][model], which solves a
simple knapsack problem. You may use the `ModelSolution` to obtain the solution
of the model. This convenience functionality is provided out of the box, but we
recommend that you customize how the model is interpreted to parse the solution.

```python
import nextmv

import nextmv_gurobipy as ngp

# Model code here.

solution = ngp.ModelSolution(model)
nextmv.write(solution)
```

Run the script:

```bash
python main.py
{
  "cat": 1.0,
  "dog": 0.0,
  "water": 1.0,
  "phone": 1.0,
  "book": 1.0,
  "rx": 1.0,
  "tablet": 0.0,
  "coat": 1.0,
  "laptop": 0.0,
  "keys": 1.0,
  "nuts": 1.0
}
```

[model]: ./model.md
