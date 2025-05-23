# Run an Application

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

To run an `Application`, you can use of the following methods:

* `new_run`: creates (submits) a new run and returns the ID (`run_id`) of the
  run. With the `run_id`, you can perform other operations, such as getting the
  run’s metadata, logs, and result.
* `new_run_with_result`: does the same as `new_run`, but it also polls for the
  result of the run. This method returns the result of the run, and it is
  useful for submitting and getting the result in a single call. Using this
  method is recommended because we have a built-in polling mechanism that
  handles retries, exponential backoff, jitter, and timeouts.

The following example shows how to make a new run.

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

run_id = app.new_run(
    input={"foo": "bar"},
)

print(run_id)
```

```bash
$ python main.py
devint-9KzmD41Hg
```

As mentioned before, you may use the recommended `new_run_with_result` method
and get the results immediately after submitting the run and they become
available.

```python
import json
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

result = app.new_run_with_result(
    input={...},
)

print(json.dumps(result.to_dict(), indent=2))

```

```bash
$ python main.py
{
  "description": "",
  "id": "devint-srVCH41NR",
  "metadata": {
    "application_id": "...",
    "application_instance_id": "devint",
    "application_version_id": "",
    "created_at": "2025-04-18T03:56:30Z",
    "duration": 14302.0,
    "error": "",
    "input_size": 502.0,
    "output_size": 1075.0,
    "status": "succeeded",
    "status_v2": "succeeded"
  },
  "name": "",
  "user_email": "sebastian@nextmv.io",
  "output": {
    "options": {
      "input": "",
      "output": "",
      "duration": 30,
      "provider": "SCIP"
    },
    "solution": {...},
    "statistics": {
      "run": {
        "duration": 0.004137277603149414
      },
      "result": {
        "duration": 0.002,
        "value": 444.0,
        "custom": {
          "status": "optimal",
          "variables": 11,
          "constraints": 1
        }
      },
      "schema": "v1"
    },
    "assets": []
  }
}
```
