# Run a local Application

!!! tip "Reference"

    Find the reference for the `Application` class [here](./reference/application.md).

A run is a single execution of an app's decision model. It is the basic
functionality encompassed of receiving an input, running the app, and returning
an output. This tutorial will walk you through running an app locally.

The recommended method for running an app is using [polling][polling-section].

Here is an example of using the
[`Application.new_run_with_result`][app-new-run-with-result] method, which
takes care of all the nuances of polling for you. The Nextmv Python SDK
automatically handles polling, file size limits, retries, exponential backoff,
jitter, timeouts, and other Nextmv nuances for you.

```python
import nextmv
from nextmv import local

app = local.Application(src="<YOUR_APP_SRC>") # Path to your local app, where the app.yaml manifest is located.

run_result = app.new_run_with_result(
    input={"name": "Patches", "radius": 6378, "distance": 147.6},
    run_options={
        "details": "true",
    },
    polling_options=nextmv.PollingOptions(),  # Customize polling options.
)

nextmv.write(run_result)
```

## Polling

The polling method is the most common way to check the status of a run. It
involves the following steps:

1. Submit a run request with the input (payload) and options (if desired). A
   `run_id` is returned.

    Use the [`Application.new_run`][app-new-run]: creates (submits) a new run and
    returns the ID (`run_id`) of the run. With the `run_id` you can perform
    other operations, such as getting the run’s metadata, logs, and result.

    The following example shows how to make a new run.

    ```python
    from nextmv import local

    app = local.Application(src="<YOUR_APP_SRC>") # Path to your local app, where the app.yaml manifest is located.

    run_id = app.new_run(
        input={"name": "Patches", "radius": 6378, "distance": 147.6},
        options={
            "details": "true",
        },
    )

    print(run_id)
    ```

    ```bash
    $ python main.py
    local-rq0pw6sy
    ```

1. Sleep for an appropriate amount of time.
1. Get the `status_v2` in the metadata using the `run_id`. The following
   states indicate that you should stop polling:

      * `succeeded`: the run completed and you can retrieve the run results.
      * `failed`: the run did not complete and you can retrieve the run error.

    On the other hand, the following states indicate that you should continue
    polling:

      * `running`: the run is still in progress.
      * `queued`: the run is waiting to be executed.

    Each time you check for the run status (poll), you should increase the time
    between polls. This is called exponential backoff. In addition, you should
    set a maximum number of retries and a timeout.

    The following example shows how to get the status of the run using the
    [`Application.run_metadata`][app-run-metadata] method.

    ```python
    import nextmv
    from nextmv import local

    app = local.Application(src="<YOUR_APP_SRC>")
    run_information = app.run_metadata(run_id="local-rq0pw6sy")
    nextmv.write({"result": run_information.metadata.status_v2})  # Get the status of the run
    ```

    ```bash
    $ python main.py
    {
      "result": "succeeded"
    }
    ```

1. Once you are done polling, retrieve the run results or error using the
   `run_id`.

    The following example shows how to get the run results using the
    [`Application.run_result`][app-run-result] method.

    ```python
    import nextmv
    from nextmv import local

    app = local.Application(src="<YOUR_APP_SRC>")
    run_result = app.run_result(run_id="local-rq0pw6sy")
    nextmv.write(run_result)  # Get the full result of the run.
    ```

    ```bash
    $ python main.py
    {
      "description": "Local run created at 2025-10-03T09:14:49.543398Z",
      "id": "local-au9xnvbj",
      "metadata": {
        "application_id": "/Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17",
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

If you are polling for a run, we _strongly_ encourage you to use the methods
provided by the SDK that handle polling, retries, exponential backoff, jitter,
and timeouts for you:

* [`Application.new_run_with_result`][app-new-run-with-result]: does the same
  as `new_run`, but it also polls for the result of the run. This method
  returns the result of the run, and it is useful for submitting and getting
  the result in a single call. Using this method is recommended because we have
  a built-in polling mechanism that handles retries, exponential backoff,
  jitter, and timeouts.
* [`Application.run_result_with_polling`][app-run-result-with-polling]:
  does the same as `run_result`, but it also polls for the metadata of the
  run. This method returns the result of the run, and it is useful for
  checking the status of the run in a single call.

## Running with non-JSON payloads

The [`Application.new_run`][app-new-run] and
[`Application.new_run_with_result`][app-new-run-with-result] methods take in an
input which can be:

* A `dict`: represents a JSON-serializable payload. This is the most common way
  to run an app.
* A `str`: represents a text payload, which must be `utf-8` encoded.
* An [`Input`][input]: represents a Nextmv input object. The `.data` property
  holds the input data. The `.input_format` property must be set to one of
  [`InputFormat.JSON`][inputformat] or
  [`InputFormat.TEXT`][inputformat]. This matches the above two data
  types, but it is a more structured way to pass the input data.

Here is a simple example showcasing how to run an app with JSON and text
inputs:

```python
import os

from nextmv import local

app = local.Application(src="<YOUR_APP_SRC>")

# Run with a JSON input.
json_run_id = app.new_run(
    input={"foo": "bar"},
)
print(f"JSON run ID: {json_run_id}")

# Run with a text input.
text_run_id = app.new_run(
    input="foo,bar\n1,2\n3,4",
)
print(f"Text run ID: {text_run_id}")
```

For these data types, the input is read from memory, as the data is passed to
the method directly.

---

You can use the `input_dir_path` argument to read inputs from the local
filesystem. The following input format are supported:

* [`InputFormat.CSV_ARCHIVE`][inputformat]: one, or more, CSV files.
* [`InputFormat.MULTI_FILE`][inputformat]: one, or more, files. This is the
      most flexible input format, as it supports all the file formats that have
      been mentioned previously (JSON, `utf-8` encoded text, CSV). In addition,
      Excel files are supported as well.

Please note the following:

* The `input_dir_path` is the path to a directory containing input files. If
  specified, the function will package the files in the directory into a tar
  file and upload it as a large input.
* If both `input` and `input_dir_path` are specified, `input` is ignored, and
  the files in the directory are used instead.
* When `input_dir_path` is specified, the `configuration` argument _must_ be
  provided. More specifically, the [`.input_type`][input-type-param] parameter
  dictates what kind of input is being submitted to the local runner. In both
  cases, the input files are read from the directory specified by
  `input_dir_path`, copied, and submitted to the runner.

      * [`InputFormat.CSV_ARCHIVE`][inputformat]: the input format will be set to `csv-archive`.
      * [`InputFormat.MULTI_FILE`][inputformat]: the input format will be set to `multi-file`.

* The output format is also specified in the configuration. It can be set to
  either `csv-archive` or `multi-file` (see
  [`.output_type`][output-type-param]), depending on the input format.

Here is an example of how to run an app with a directory of input files:

```python
import os

import nextmv
from nextmv import local

app = local.Application(src="<YOUR_APP_SRC>")


# Run with CSV_ARCHIVE input.
csv_run_id = app.new_run(
    configuration=nextmv.RunConfiguration(
        format=nextmv.Format(
            format_input=nextmv.FormatInput(
                input_type=nextmv.InputFormat.CSV_ARCHIVE,
            ),
            format_output=nextmv.FormatOutput(
                output_type=nextmv.OutputFormat.CSV_ARCHIVE,
            ),
        )
    ),
    input_dir_path="input", # Files are in the "input" directory.
)
print(f"CSV run ID: {csv_run_id}")

# Run with MULTI_FILE input.
multi_file_run_id = app.new_run(
    configuration=nextmv.RunConfiguration(
        format=nextmv.Format(
            format_input=nextmv.FormatInput(
                input_type=nextmv.InputFormat.MULTI_FILE,
            ),
            format_output=nextmv.FormatOutput(
                output_type=nextmv.OutputFormat.MULTI_FILE,
            ),
        )
    ),
    input_dir_path="inputs", # Files are in the "inputs" directory.
)
print(f"MULTI_FILE run ID: {multi_file_run_id}")
```

## List all runs

You can list all the runs created in your local app using the
[`Application.list_runs`][app-list-runs] method. This method returns a list of
runs, each containing metadata about the run, such as its ID, creation time,
duration, status, and more.

```python
from nextmv import local

app = local.Application(src="nextmv/default_app")

# List all runs
runs = app.list_runs()
for run in runs:
    print(f"Run ID: {run.id}, Status: {run.status_v2.value}")
```

You should see an output similar to this one:

```bash
Run ID: local-w2ze2sth, Status: succeeded
Run ID: local-80mxxuq8, Status: succeeded
Run ID: local-rq0pw6sy, Status: succeeded
```

## Run logs

You can retrieve the logs for a specific run using the
[`Application.run_logs`][app-run-logs] method. This method returns the logs as
a string, which can be printed directly to display them in the same format as
they are stored locally.

```python
from nextmv import local

app = local.Application(src="<YOUR_APP_SRC>")

# Get the logs for a specific run
logs = app.run_logs(run_id="local-rq0pw6sy")
print(logs)
```

The logs are retrieved from the `.nextmv/runs/{run_id}/logs/logs.log` file in
your local application directory. If the run does not have any logs or they are
empty, the method returns an empty string.

Example output:

```bash
$ python main.py

2025-10-03T09:14:49.543Z [INFO] Starting run local-rq0pw6sy
2025-10-03T09:14:49.612Z [INFO] Processing input data
2025-10-03T09:14:50.821Z [INFO] Run completed successfully
```

[polling-section]: #polling
[app-new-run]: ./reference/application.md#nextmv.nextmv.local.application.Application.new_run
[app-run-metadata]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_metadata
[app-run-result]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_result
[app-list-runs]: ./reference/application.md#nextmv.nextmv.local.application.Application.list_runs
[app-run-logs]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_logs
[app-run-result-with-polling]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_result_with_polling
[app-new-run-with-result]: ./reference/application.md#nextmv.nextmv.local.application.Application.new_run_with_result
[input]: ../modeling/reference/input.md#nextmv.nextmv.input.Input
[inputformat]: ../modeling/reference/input.md#nextmv.nextmv.input.InputFormat
[input-type-param]: ../modeling/reference/run.md#nextmv.nextmv.run.FormatInput
[output-type-param]: ../modeling/reference/run.md#nextmv.nextmv.run.FormatOutput
