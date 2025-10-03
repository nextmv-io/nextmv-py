# Get started with an existing app

If you already have a Python decision model, this guide will help you get it
running locally using the `nextmv.local` package. On the other hand, if you are
new to Nextmv, you can head to the [tutorial on getting started with a new
app][get-started-new-app] instead.

Let's dive right in 🤿.

## Initialize

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

!!! abstract "Application"

    So, what is a Nextmv Application? A Nextmv Application is an entity that
    contains a decision model as executable code. An Application can make a run
    by taking an input, executing the decision model, and producing an
    output. An Application is defined by its code, and a configuration file
    named `app.yaml`, known as the "app manifest".

    Think of the app as a shell that contains your decision model code, and
    provides the necessary structure to run it.

## App structure and conventions

Your existing app must follow the Nextmv Application conventions:

1. Must read from either `Stdin` or a file.
2. Must write results either to `Stdout` or a file.
3. Should conform to the [Nextmv statistics convention][statistics-convention]
   to leverage experiments and tests.
4. Must contain an [app.yaml manifest][app-manifest] in the root of your app project.

A typical app structure looks like this:

```text
your-app/
├── app.yaml          # App manifest (required)
├── main.py           # Entry point for the app
├── README.md         # Description of the app
├── requirements.txt  # Python dependencies for the app
└── src/              # Source code for the app
```

The `app.yaml` manifest contains configuration about how to run your app. Here's a
basic example for a Python app:

```yaml
# This manifest holds the information the app needs to run on the Nextmv Cloud.
type: python
runtime: ghcr.io/nextmv-io/runtime/python:3.11
python:
  # All listed packages will get bundled with the app.
  pip-requirements: requirements.txt

# List all files/directories that should be included in the app.
files:
  - src/
  - main.py
```

## Make sure it works

Before using the local package, let's make sure your existing app runs correctly
by following the standard approach:

1. Navigate to your app directory.

    ```bash
    cd /path/to/your/existing/app
    ```

1. Install packages.

    ```bash
    pip3 install -r requirements.txt
    ```

1. Run the app. For example, if it takes a `.json` input from `stdin`:

    ```bash
    cat input.json | python3 main.py
    ```

You should get output similar to what your app normally produces. Once you've
confirmed it works manually, there's a better way...

## Start a run

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

[get-started-new-app]: ./get-started-new-app.md
[get-run-result]: #get-a-run-result
[statistics-convention]: https://docs.nextmv.io/docs/using-nextmv/reference/statistics
[app-manifest]: https://docs.nextmv.io/docs/using-nextmv/deploy/app/manifest
[cloud-index]: ../cloud/index.md
[runs-tutorial]: ./runs.md
