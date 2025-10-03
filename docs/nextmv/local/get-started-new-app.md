# Get started with a new app

If you are new to Nextmv, and want to explore the local experience, this guide
is a great place to start. On the other hand, if you already have a Python
decision model, you can head to the [tutorial on getting started with an
existing app][get-started-existing-app] instead.

Let's dive right in 🤿.

## Initialize

You can initialize a sample Nextmv Application by running the following
command:

```python
from nextmv import local

local_app = local.Application.initialize()
```

This will create a new directory with your application in the current working
directory. The app created is a simple hello world example.

* You can specify the `src` argument to customize the name of the application
  (directory).
* You can specify the `destination` argument to customize the location where the
  application will be created. By default, it will be created in the current
  working directory.

!!! abstract "Application"

    So, what is a Nextmv Application? A Nextmv Application is an entity that
    contains a decision model as executable code. An Application can make a run
    by taking an input, executing the decision model, and producing an
    output. An Application is defined by its code, and a configuration file
    named `app.yaml`, known as the "app manifest".

    Think of the app as a shell that contains your decision model code, and
    provides the necessary structure to run it.

## Make sure it works

`cd` into the app directory and follow the `README.md` to make sure you can run
it.

1. Install packages.

    ```bash
    pip3 install -r requirements.txt
    ```

1. Run the app.

    ```bash
    cat input.json | python3 main.py
    ```

You should have obtained an output similar to the following:

```bash
Hello, Patches
You are 147.6 million km from the sun
{
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
```

🎉 The sample app works! But there is a better way...

## Start a run

Let's use the mechanisms provided by the `local` package to run the app
systematically by submitting a couple of runs to the local app.

```python
input = { # Provide any input you want to the app
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
    "application_id": "/Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17",
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

The sample app comes with some simple visuals to illustrate how to produce
assets from your decision model. You can visualize the assets locally with the
following code:

```python
local_app.run_visuals(run_id=run_1)
```

This will open a browser window for each asset produced by the run. You should
see a simple plot like the following:

![Sample visuals][sample-visuals]

## Next steps

You have successfully:

* created a new Nextmv Application,
* ran it locally,
* obtained run results, and
* visualized assets.

After you complete exploring the local experience, you can unleash the full
potential of the Nextmv Platform with [Cloud][cloud-index].

[get-started-existing-app]: ./get-started-existing-app.md
[get-run-result]: #get-a-run-result
[sample-visuals]: ../../images/sample-visuals.png
[cloud-index]: ../cloud/index.md
[runs-tutorial]: ./runs.md
