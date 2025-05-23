# Track external runs

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

You can track runs that happened externally from the Nextmv Platform. This is
useful for onboarding to Nextmv quickly without having to run your decision
models in the Platform. Once a run has been tracked, you may use all the
features supported by Nextmv, such as testing, and experimentation. An external
run behaves just like a [standard run][application-runs], but it is not
executed on the Nextmv Platform.

You can read more about external runs [here][external-runs].

Generally speaking, a run can have two final states:

* `succeeded`: the run was successful.
* `failed`: the run failed.

To track a run with either of these states, you can use one of the following
methods:

* `track_run`: tracks the run as an external run and returns the ID (`run_id`)
  of the run. It is analogous to the [`new_run`][application-runs] method, but
  it does not execute the decision model on the Platform.
* `track_run_with_result`: does the same as `track_run`, but it also polls for
  the result of the run, which should be available not long after the run is
  submitted. This method is useful for submitting the run and getting the
  result in a single call. It is analogous to the
  [`new_run_with_result`][application-runs] method, but it does not execute the
  decision model on the Platform.

## Successful run

You can use the `track_run_with_result` method to track, and get the result, of
a run with a status of `succeeded`:

```python
import json
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

successful_result = app.track_run_with_result(
    tracked_run=cloud.TrackedRun(
        input=nextmv.Input(data={"sample": "input"}),
        output=nextmv.Output(solution={"sample": "output"}),
        status=cloud.TrackedRunStatus.SUCCEEDED,
        duration=42,
    )
)

print(json.dumps(successful_result.to_dict(), indent=2))
```

The run is tracked by the Nextmv Platform and run results are polled, just as
if you had [executed a normal run][application-runs]. The main difference is
that no decision model is executed on the Platform. Instead, the input and
output are recorded.

Please note the following:

* The `input` can be a `nextmv.Input`, a simple `dict[str, any]` or a plain
  `str`.
* The `output` can be a `nextmv.Output`, a simple `dict[str, any]` or a plain
  `str`. Using all the attributes of `nextmv.Output` is recommended, as it
  allows you to record statistics, useful for recording metrics, and assets,
  useful for visualizing charts.
* The `status`, as mentioned previously, can be `succeeded` or `failed`.
* The `duration` is the time it took to run the decision model, in seconds.
  This is optional, but recommended.

Alternatively, you may use the `track_run` method, which will just track the
run and return the `run_id`.

Running the code snippet above (using `track_run_with_result`) will track the
run and poll for the results:

```bash
$ python main.py
{
  "description": "",
  "id": "devint-94jwBZJHR",
  "metadata": {
    "application_id": "...",
    "application_instance_id": "devint",
    "application_version_id": "",
    "created_at": "2025-04-17T03:26:41Z",
    "duration": 42.0,
    "error": "",
    "input_size": 70.0,
    "output_size": 140.0,
    "status": "succeeded",
    "status_v2": "succeeded"
  },
  "name": "",
  "user_email": "sebastian@nextmv.io",
  "output": {
    "options": null,
    "output_format": "JSON",
    "solution": {
      "sample": "output"
    },
    "statistics": null,
    "assets": null
  }
}
```

## Failed run

Using the same `track_run_with_result` method, you can track a run with a
status of `failed`:

```python
import json
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

failed_result = app.track_run_with_result(
    tracked_run=cloud.TrackedRun(
        input=nextmv.Input(data={"sample": "input"}),
        output=nextmv.Output(solution={"sample": "output"}),
        status=cloud.TrackedRunStatus.FAILED,
        duration=42,
        error="You can record the error message here!",
        logs=["A super interesting log", "Another interesting log"],
    )
)

print(json.dumps(failed_result.to_dict(), indent=2))
```

Three main differences stand out when comparing against the `succeeded`
example:

* The `status` is set to `failed`.
* The `error` is a string that describes the error that occurred.
* The `logs` are a list of strings that describe the logs that were generated
  during the run. Each list item is a line in the log stream.

Similarly to before, you may just use the `track_run` method to track the run
and get back the `run_id`.

Running the code will track the run and poll for the results:

```bash
$ python main.py
{
  "description": "",
  "id": "devint-bONBLZJHg",
  "metadata": {
    "application_id": "...",
    "application_instance_id": "devint",
    "application_version_id": "",
    "created_at": "2025-04-17T03:41:05Z",
    "duration": 244.0,
    "error": "You can record the error message here!",
    "input_size": 70.0,
    "output_size": 112.0,
    "status": "failed",
    "status_v2": "failed"
  },
  "name": "",
  "user_email": "sebastian@nextmv.io",
  "error_log": {
    "error": "You can record the error message here!",
    "stdout": "{\"options\": null, \"output_format\": \"JSON\", \"solution\": {\"sample\": \"output\"}, \"statistics\": null, \"assets\": null}",
    "stderr": "A super interesting log\nAnother interesting log\nYou can record the error message here!\n"
  }
}
```

[external-runs]: https://docs.nextmv.io/docs/using-nextmv/run/track-runs
[application-runs]: ./runs.md
