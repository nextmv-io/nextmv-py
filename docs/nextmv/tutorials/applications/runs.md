# Run an Application

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

A run is a single execution of an app against an instance. It is the basic
functionality encompassed of receiving an input, running the app, and returning
an output. This tutorial will walk you through running an app remotely on
Nextmv Cloud. It works the same for both [subscription apps][subscription-apps]
and [custom apps][custom-apps].

There are two recommended methods for running an app:

1. Using [polling][polling-section].
2. Using [webhooks][webhooks]. Go that section for more information.

Here is an example of using the
[`Application.new_run_with_result`][app-new-run-with-result] method, which
takes care of all the nuances of polling for you. The Nextmv Python SDK
automatically handles polling, file size limits, retries, exponential backoff,
jitter, timeouts, and other Nextmv Cloud nuances for you.

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

run_id = app.new_run_with_result(
    input={"foo": "bar"},
    instance_id="<YOUR_INSTANCE_ID>",
    run_options={
        "solve.duration": "10s",
        "solve.iterations": "20",
    },
    polling_options=cloud.PollingOptions(),  # Customize polling options.
)

print(run_id)
```

Please find these other sections in this tutorial:

* [Running with non-JSON payloads][running-non-json-section]: how to run an
  app with non-JSON payloads, such as CSV or Excel files.
* [Cancel a run][cancel-run-section]: how to cancel a run that is no longer
  necessary.

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
    import os

    from nextmv import cloud

    client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
    app = cloud.Application(client=client, id="<YOUR_APP_ID>")

    run_id = app.new_run(
        input={"foo": "bar"},
        instance_id="<YOUR_INSTANCE_ID>",
        options={
            "solve.duration": "10s",
            "solve.iterations": "20",
        },
    )

    print(run_id)
    ```

    ```bash
    $ python main.py
    devint-9KzmD41Hg
    ```

1. Sleep for an appropriate amount of time.
1. Get the `status_v2` in the metadata using the `run_id`. The following
   states indicate that you should stop polling:

      * `succeeded`: the run completed and you can retrieve the run results.
      * `failed`: the run did not complete and you can retrieve the run error.
      * [`canceled`][cancel-a-run]: the run was canceled.

    On the other hand, the following states indicate that you should continue
    polling:

      * `running`: the run is still in progress.
      * [`queued`][queued-runs]: the run is waiting to be executed.

    Each time you check for the run status (poll), you should increase the time
    between polls. This is called exponential backoff. In addition, you should
    set a maximum number of retries and a timeout.

    The following example shows how to get the status of the run using the
    [`Application.run_metadata`][app-run-metadata] method.

    ```python
    import os

    import nextmv
    from nextmv import cloud

    client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
    app = cloud.Application(client=client, id="<YOUR_APP_ID>")
    run_information = app.run_metadata(run_id="<YOUR_RUN_ID>")
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
    [`Application.run_result`][app-run-metadata] method.

    ```python
    import os

    import nextmv
    from nextmv import cloud

    client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
    app = cloud.Application(client=client, id="<YOUR_APP_ID>")
    run_result = app.run_result(run_id="<YOUR_RUN_ID>")
    nextmv.write(run_result)  # Get the full result of the run.

    ```

    ```bash
    $ python main.py
    {
      "description": "",
      "id": "devint-s-prp41Hg",
      "metadata": {
        "application_id": "1504",
        "application_instance_id": "devint",
        "application_version_id": "",
        "created_at": "2025-04-18T05:23:27Z",
        "duration": 4818.0,
        "error": "",
        "input_size": 502.0,
        "output_size": 1074.0,
        "status": "succeeded",
        "status_v2": "succeeded"
      },
      "name": "",
      "user_email": "sebastian@nextmv.io",
      "console_url": "https://cloud.nextmv.io/app/1504/run/devint-s-prp41Hg?view=details",
      "output": {
        "options": {
          "input": "",
          "output": "",
          "duration": 2,
          "provider": "SCIP"
        },
        "solution": {...},
        "statistics": {
          "run": {
            "duration": 0.004414081573486328
          },
          "result": {
            "duration": 0.003,
            "value": 444.0,
            "custom": {...}
          },
          "schema": "v1"
        },
        "assets": []
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
* [`Application.run_metadata_with_polling`][app-run-metadata-with-polling]:
  does the same as `run_metadata`, but it also polls for the metadata of the
  run. This method returns the metadata of the run, and it is useful for
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

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

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

You can use the `dir_path` argument to read inputs from the local filesystem.
The following input format are supported:

* [`InputFormat.CSV_ARCHIVE`][inputformat]: one, or more, CSV files.
* [`InputFormat.MULTI_FILE`][inputformat]: one, or more, files. This is the
      most flexible input format, as it supports all the file formats that have
      been mentioned previously (JSON, `utf-8` encoded text, CSV). In addition,
      Excel files are supported as well.

Please note the following:

* The `dir_path` is the path to a directory containing input files. If
  specified, the function will package the files in the directory into a tar
  file and upload it as a large input.
* If both `input` and `dir_path` are specified, `input` is ignored, and the
  files in the directory are used instead.
* When `dir_path` is specified, the `configuration` argument _must_ be
  provided. More specifically, the [`.input_type`][input-type-param] parameter
  dictates what kind of input is being submitted to the Nextmv Cloud.

  * [`InputFormat.CSV_ARCHIVE`][inputformat]: the input format will be set to
        `csv-archive`.
  * [`InputFormat.MULTI_FILE`][inputformat]: the input format will be set to
        `multi-file`.

  In both cases, the input files are read from the directory specified by
  `dir_path`, tarred, and uploaded to Nextmv Cloud.
* The output format is also specified in the configuration. It can be set to
  either `csv-archive` or `multi-file` (see
  [`.output_type`][output-type-param]), depending on the input format.

Here is an example of how to run an app with a directory of input files:

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="1504")


# Run with CSV_ARCHIVE input.
csv_run_id = app.new_run(
    configuration=cloud.RunConfiguration(
        format=cloud.Format(
            format_input=cloud.FormatInput(
                input_type=nextmv.InputFormat.CSV_ARCHIVE,
            ),
            format_output=cloud.FormatOutput(
                output_type=nextmv.OutputFormat.CSV_ARCHIVE,
            ),
        )
    ),
    dir_path="input", # Files are in the "input" directory.
)
print(f"CSV run ID: {csv_run_id}")

# Run with MULTI_FILE input.
multi_file_run_id = app.new_run(
    configuration=cloud.RunConfiguration(
        format=cloud.Format(
            format_input=cloud.FormatInput(
                input_type=nextmv.InputFormat.MULTI_FILE,
            ),
            format_output=cloud.FormatOutput(
                output_type=nextmv.OutputFormat.MULTI_FILE,
            ),
        )
    ),
    dir_path="inputs", # Files are in the "inputs" directory.
)
print(f"MULTI_FILE run ID: {multi_file_run_id}")
```

## Cancel a run

You can cancel a run when it is no longer necessary. To cancel a run, you need
the `run_id`. Runs that are in the following states (given by `run_status_v2`
in the metadata) can be canceled:

* `running`: the run is in progress.
* [`queued`][queued-runs]: the run is waiting to be executed.

You can cancel a run using the [`Application.cancel_run`][app-cancel-run] method.

```python
import os

from nextmv.cloud import Application, Client

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR_APP_ID>")
app.cancel_run(run_id="<YOUR_RUN_ID>")
```

[subscription-apps]: /platform/deploy-app/subscription-apps
[custom-apps]: /platform/deploy-app/custom-apps
[polling-section]: #polling
[cancel-run-section]: #cancel-a-run
[running-non-json-section]: #running-with-non-json-payloads
[webhooks]: https://docs.nextmv.io/docs/using-nextmv/setup/webhooks
[app-new-run]: ../../reference/cloud/application.md#nextmv.nextmv.cloud.application.Application.new_run
[app-run-metadata]: ../../reference/cloud/application.md#nextmv.nextmv.cloud.application.Application.run_metadata
[app-run-metadata-with-polling]: ../../reference/cloud/application.md#nextmv.nextmv.cloud.application.Application.run_metadata_with_polling
[app-new-run-with-result]: ../../reference/cloud/application.md#nextmv.nextmv.cloud.application.Application.new_run_with_result
[app-cancel-run]: ../../reference/cloud/application.md#nextmv.nextmv.cloud.application.Application.cancel_run
[cancel-a-run]: #cancel-a-run
[input]: ../../reference/input.md#nextmv.nextmv.input.Input
[inputformat]: ../../reference/input.md#nextmv.nextmv.input.InputFormat
[input-type-param]: ../../reference/cloud/run/#nextmv.nextmv.cloud.run.FormatInput
[output-type-param]: ../../reference/cloud/run/#nextmv.nextmv.cloud.run.FormatOutput
[queued-runs]: ./queuing.md
