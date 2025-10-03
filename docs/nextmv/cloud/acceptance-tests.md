# Acceptance tests

!!! tip

    Find more information about acceptance tests in this [section of the Nextmv docs](https://docs.nextmv.io/docs/using-nextmv/experiments/acceptance).

Define the desired acceptance test ID and name. As mentioned above, an
acceptance test is based on a [batch experiment][batch-experiments].

* If you already started a batch experiment, you don't need to provide the
  `input_set_id` parameter. In that case, the ID and name of the acceptance
  test and the underlying batch experiment **must be the same**.
* If you didn't start a batch experiment, you need to provide the
  `input_set_id` and a new batch experiment will be created for you, with the
  same ID and name as the acceptance test.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")
acceptance_test = app.new_acceptance_test(
    candidate_instance_id="latest-2",
    control_instance_id="latest",
    id="<YOUR_ACCEPTANCE_TEST_ID>",
    name="<YOUR_ACCEPTANCE_TEST_ID>",
    metrics=[
        cloud.Metric(
            field="result.value",
            metric_type=cloud.MetricType.direct_comparison,
            params=cloud.MetricParams(operator=cloud.Comparison.less_than),
            statistic="mean",
        ),
        cloud.Metric(
            field="result.custom.activated_vehicles",
            metric_type=cloud.MetricType.direct_comparison,
            params=cloud.MetricParams(operator=cloud.Comparison.greater_than),
            statistic="mean",
        ),
    ],
    # input_set_id=os.getenv("INPUT_SET_ID"), # Defining this would create a new batch experiment.
    description="An optional description",
)
nextmv.write(acceptance_test)
```  

```bash
$ python main.py
{
  "id": "experiment-1",
  "name": "experiment-1",
  "description": "An optional description",
  "app_id": "routing",
  "experiment_id": "experiment-1",
  "control": {
    "instance_id": "latest",
    "version_id": "v1.0.4"
  },
  "candidate": {
    "instance_id": "latest-2",
    "version_id": "v1.1.0"
  },
  "metrics": [
    {
      "field": "result.value",
      "metric_type": "direct-comparison",
      "params": {
        "operator": "lt"
      },
      "statistic": "mean"
    },
    {
      "field": "result.custom.activated_vehicles",
      "metric_type": "direct-comparison",
      "params": {
        "operator": "gt"
      },
      "statistic": "mean"
    }
  ],
  "created_at": "2024-01-12T19:30:29.677473Z",
  "updated_at": "2024-01-12T19:30:29.677473Z"
}
```

## Delete an acceptance test

Deleting an acceptance test will also delete all of the associated information.
Note that deleting it will _not delete the underlying [batch
experiment][batch-experiments] and its runs_.

!!! warning

    This action is permanent and cannot be undone.

You can delete an acceptance test with the `Application.delete_acceptance_test`
method.

```python
import os

from nextmv.cloud import Application, Client

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR_APP_ID>")
app.delete_acceptance_test(acceptance_test_id="<YOUR_ACCEPTANCE_TEST_ID>")
```  

You will _not_ be prompted to confirm the deletion.

[batch-experiments]: ./batch-experiments.md
