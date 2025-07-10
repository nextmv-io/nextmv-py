# Statistics

!!! tip "Reference"

    Find the reference for the `statistics` module [here](../reference/statistics.md).

`ModelStatistics` allows access to the statistics of a `gurobipy.Model`. It is
a convenience function that will collect a simple set of statistics.

Consider the same script shown in the [model section][model], which solves a
simple knapsack problem. You may use the `ModelStatistics` to obtain the
statistics of the model. This convenience functionality is provided out of the
box, but we recommend that you customize how the model is interpreted to
extract statistics.

```python
import nextmv

import nextmv_gurobipy as ngp

# Model code here.

statistics = ngp.ModelStatistics(model, start_time)
nextmv.write(statistics)
```

Run the script:

```bash
python main.py
{
  "run": {
    "duration": 0.004244089126586914
  },
  "result": {
    "duration": 0.00031304359436035156,
    "value": 444.0,
    "custom": {
      "status": "OPTIMAL",
      "variables": 11,
      "constraints": 1
    }
  },
  "series_data": {},
  "schema": "v1"
}
```

[model]: ./model.md
