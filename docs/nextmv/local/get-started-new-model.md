# Get started with a new decision model

If you are new to Nextmv, and want to explore the local experience, this guide
is a great place to start. On the other hand, if you already have a Python
decision model, you can head to the [tutorial on getting started with an
existing model][get-started-existing-model] instead.

Let's dive right in 🤿.

## 1. Initialize

Create a script named `app1.py`, or use a cell of a Jupyter notebook. Copy and
paste the following code into it:

```python
from nextmv import local

local_app = local.Application.initialize()
```

Run the `app1.py` script, or the cell in the Jupyter notebook.

```bash
python app1.py
```

The [`local.Application.initialize`][local-app-initialize] method will create a
new directory (your application) under the current working directory. The dir
is named `app-<RANDOM_IDENTIFIER>`. The app created is a simple hello world
example, and should contain a structure similar to the following:

```text
app-<RANDOM_IDENTIFIER>
├── .gitignore
├── app.yaml
├── input.json
├── main.py
├── README.md
├── requirements.txt
└── src
    ├── __init__.py
    └── visuals.py
```

* You can specify the `src` argument to customize the name of the application
  (directory), and not use a random identifier.
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

The [`app.yaml` manifest][app-manifest] file contains the configuration of the
app. This tutorial is not meant to discuss the app manifest in-depth, however,
these are the main attributes shown in the manifest:

* `type`: it is a `python` application.
* `runtime`: when deployed to Nextmv Cloud, this application can be run on the
  standard `python:3.11` runtime.
* `files`: contains files that make up the executable code of the app. In this case,
  it includes all the files under the `src` directory, and the `main.py` file.
* `python.pip-requirements`: specifies the file with the Python packages that
  need to be installed for the application.

### Make sure it works

`cd` into the app directory and follow the `README.md` to make sure you can run
it.

1. Install packages.

    ```bash
    pip install -r requirements.txt
    ```

1. Run the app.

    ```bash
    cat input.json | python main.py
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

## 2. Start a run

Let's use the mechanisms provided by the `local` package to run the app
systematically by submitting a couple of runs to the local app, using the
[`local.Application.new_run`][local-app-new-run] method.

Create another script, which you can name `app2.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct app `src` (the directory name created above):

```python
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src="<YOUR_APP_SRC>")

# Provide any input you want for the app. This input can come from a file, for
# example.
input = {
    "name": "Patches",
    "radius": 6378,
    "distance": 147.6,
}

# Execute some local runs with the provided input.
run_1 = local_app.new_run(input=input)
print("run_1:", run_1)

run_2 = local_app.new_run(input=input)
print("run_2:", run_2)
```

When you instantiate a [`local.Application`][local-app], the `src` argument
must point to a directory where the [`app.yaml` manifest][app-manifest] file is
located.

This will print the IDs of the runs created. The app runs start in the
background. Run the script, or notebook cell, to get an output similar to this:

```bash
$ python app2.py

run_1: local-lyxnxlsl
run_2: local-ykfq7nej
```

## 3. Get a run result

You can get a run result using the run ID with the
[`local.Application.run_result`][local-app-run-result] method.

Create another script, which you can name `app3.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct run ID (one of the identifiers that were printed in step 2) and
app `src`:

```python
import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src="<YOUR_APP_SRC>")

# Get the result of a specific run by its ID.
result_1 = local_app.run_result(run_id="<RUN_ID_1_PRINTED_IN_STEP_2>")
nextmv.write(result_1)
```

Run the script, or notebook cell, and you should see an output similar to this
one:

```bash
$ python app3.py

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

## 4. Get run information

Runs may take a while to complete. We recommend you poll for the run status
until it is completed. Once the run is completed, you can get the run result as
shown above. To get the run information, use the run ID and the
[`local.Application.run_metadata`][local-app-run-metadata] method.

Create another script, which you can name `app4.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct run ID (one of the identifiers that were printed in step 2) and
app `src`:

```python
import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src="<YOUR_APP_SRC>")

# Get the information of a specific run by its ID.
result_info_2 = local_app.run_metadata(run_id="<RUN_ID_2_PRINTED_IN_STEP_2>")
nextmv.write(result_info_2)
```

Run the script, or notebook cell, and you should see an output similar to this
one:

```bash
$ python app4.py

{
  "description": "Local run created at 2025-11-14T19:43:15.237810Z",
  "id": "local-ykfq7nej",
  "metadata": {
    "application_id": "app-ptpe0h5s",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-11-14T19:43:15.237810Z",
    "duration": 766.6,
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
  "name": "local run local-ykfq7nej",
  "user_email": "",
  "console_url": ""
}
```

As you can see, the run information contains metadata about the run, such as
its status, creation time, and more.

## 5. All in one

Since runs are started in the background, you should poll until the run
succeeds (or fails) to get the results. You can use the
[`local.Application.new_run_with_result`][local-app-new-run-with-result] method
to do everything:

1. Start a run
2. Poll for results
3. Return them

Create another script, which you can name `app5.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct app `src`:

```python
import nextmv
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src="<YOUR_APP_SRC>")

# Provide any input you want for the app. This input can come from a file, for
# example.
input = {
    "name": "Patches",
    "radius": 6378,
    "distance": 147.6,
}

# Start a new run and get its result immediately.
result_3 = local_app.new_run_with_result(input=input)
nextmv.write(result_3)
```

Run the script, or notebook cell, and you should see an output similar to the
one shown in the [getting a run result section][get-run-result].

```bash
$ python app5.py

{
  "description": "Local run created at 2025-11-14T20:12:13.058486Z",
  "id": "local-xfsgm9t7",
  "metadata": {
    "application_id": "app-ptpe0h5s",
    "application_instance_id": "",
    "application_version_id": "",
    "created_at": "2025-11-14T20:12:13.058486Z",
    "duration": 759.4,
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
  "name": "local run local-xfsgm9t7",
  "user_email": "",
  "console_url": "",
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

The complete methodology for running is discussed in detail in the [runs
tutorial][runs-tutorial].

## 6. Visualize assets

The sample app comes with some simple visuals to illustrate how to produce
assets from your decision model. You can visualize the assets locally with the
[`local.Application.run_visuals`][local-app-run-visuals] method.

Create another script, which you can name `app6.py`, or use another cell in the
Jupyter notebook. Copy and paste the following code into it, making sure you
use the correct run ID (one of the identifiers that were printed in step 2) and
app `src`:

```python
from nextmv import local

# Instantiate the local application.
local_app = local.Application(src="<YOUR_APP_SRC>")

# Display the visuals of a specific run by its ID.
local_app.run_visuals(run_id="<RUN_ID_1_PRINTED_IN_STEP_2>")
```

This will open a browser window for each asset produced by the run. You should
see a simple plot like the following:

![Sample visuals][sample-visuals]

!!! warning

    The `run_visuals` method may not work as expected in a Jupyter notebook
    environment. We recommend running it from a script executed in a terminal.

## 7. Understanding what happened

If you inspect the application directory created in step 1 again, you will see
a structure similar to the following:

```text
app-<RANDOM_IDENTIFIER>
├── .gitignore
├── .nextmv
│   └── runs
│       ├── {RUN_ID_1}
│       │   ├── inputs
│       │   │   └── input.json
│       │   ├── {RUN_ID_1}.json
│       │   ├── logs
│       │   │   └── logs.log
│       │   ├── outputs
│       │   │   ├── assets
│       │   │   │   └── assets.json
│       │   │   ├── solutions
│       │   │   │   └── solution.json
│       │   │   └── statistics
│       │   │       └── statistics.json
│       │   └── visuals
│       │       └── Charts_0.html
│       ├── {RUN_ID_2}
│       │   ├── inputs
│       │   │   └── input.json
│       │   ├── {RUN_ID_2}.json
│       │   ├── logs
│       │   │   └── logs.log
│       │   ├── outputs
│       │   │   ├── assets
│       │   │   │   └── assets.json
│       │   │   ├── solutions
│       │   │   │   └── solution.json
│       │   │   └── statistics
│       │   │       └── statistics.json
│       │   └── visuals
│       │       └── Charts_0.html
│       └── {RUN_ID_3}
│           ├── inputs
│           │   └── input.json
│           ├── {RUN_ID_3}.json
│           ├── logs
│           │   └── logs.log
│           ├── outputs
│           │   ├── assets
│           │   │   └── assets.json
│           │   ├── solutions
│           │   │   └── solution.json
│           │   └── statistics
│           │       └── statistics.json
│           └── visuals
│               └── Charts_0.html
├── app.yaml
├── input.json
├── main.py
├── README.md
├── requirements.txt
└── src
    ├── __init__.py
    └── visuals.py
```

The `.nextmv` dir is used to store and manage the `local` applications runs in
a structured way. The `local` package is used to interact with these files,
with methods for starting runs, retrieving results, visualizing charts, and
more.

🎉🎉🎉 Congratulations, you have finished this tutorial!

## Next steps

You have successfully:

* Created a new Nextmv Application.
* Ran it locally.
* Obtained run results.
* Visualized assets.

After you complete exploring the `local` experience, you can unleash the full
potential of the Nextmv Platform with [Cloud][cloud-index].

[get-run-result]: #3-get-a-run-result
[sample-visuals]: ../../images/sample-visuals.png
[cloud-index]: ../cloud/index.md
[runs-tutorial]: ./runs.md
[local-app]: ./reference/application.md#nextmv.nextmv.local.application.Application
[local-app-initialize]: ./reference/application.md#nextmv.nextmv.local.application.Application.initialize
[local-app-new-run]: ./reference/application.md#nextmv.nextmv.local.application.Application.new_run
[local-app-run-result]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_result
[local-app-run-metadata]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_metadata
[local-app-new-run-with-result]: ./reference/application.md#nextmv.nextmv.local.application.Application.new_run_with_result
[local-app-run-visuals]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_visuals
[app-manifest]: https://docs.nextmv.io/docs/using-nextmv/deploy/app/manifest
[get-started-existing-model]: ./get-started-existing-model.md
