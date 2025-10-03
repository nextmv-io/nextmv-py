# Push to an Application

!!! tip "Reference"

    Find the reference for the `Application` class [here](./reference/application.md).

A Nextmv Cloud Application is a decision model that be executed remotely on the
Nextmv Platform. An application is an executable program that fulfills the
following minimum requirements:

1. Must read from either `stdin` or a file.
2. Must write results either to `stdout` or a file.
3. Depending on the push strategy (see below), may require an `app.yaml`
   manifest file and an entrypoint (`main.py`, `main`, `main.jar`, etc.).

To push an app to Nextmv Cloud using the `nextmv` Python SDK, you can use one
of the following strategies:

* [File strategy][file-strategy]: push an _existing_ app that exists
      as file(s) in a directory. This is the most common strategy.
* [Object strategy][object-strategy]: push an app that is created from a
  [`nextmv.Model`][model] directly from the in-memory object.

## File strategy

The file strategy assumes that the model exists as source code on disk. We can
distinguish between two types of file strategies:

* **Directory based**: the app is described with an [`app.yaml`][app-manifest]
  manifest file.
* **Code based**: the app is described in Python as code.

### Directory based

The directory based file strategy consists of specifying `app_dir`, which is the
path to an app’s root directory. The app is composed of files in a directory and
those apps are packaged and pushed to Nextmv Cloud. This is language-agnostic
and works for an app written in any language. It is particularly useful when the
app is already structured as a directory with the necessary files (like apps
cloned from [community apps][community-apps]).

Place the following script in the root of your app directory and run it to push
your app to the Nextmv Cloud. This is equivalent to using the [Nextmv CLI][cli]
and running `nextmv app push`.

```python
import os
from nextmv import cloud


client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

app.push()  # Use verbose=True for step-by-step output.
```

You can also specify the `app_dir` parameter to point to a specific directory.

The typical structure of an app directory for the directory based file strategy
looks like this:

```txt
.
├── app.yaml          # Describes the app and its dependencies
├── requirements.txt  # Lists the dependencies
├── main.py           # The actual app / model code
└── push.py           # Python script to define and push the app (see below)
```

### Code based

The code based file strategy consists of describing your app in Python and
pushing it to Nextmv Cloud. This is very similar to the directory based
approach, but you can define your app as code and keep it in a single file.
This approach is still language-agnostic.

For example, if you have a simply Python app consisting of a single `main.py`
file, you can push it to Nextmv Cloud using the following `push.py` script. This
example is based on the [python-ortools-knapsack][python-ortools-knapsack] app
from the [community apps][community-apps] repository.

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

# Describe your app and push it to Nextmv Cloud.
app.push(
    manifest=cloud.Manifest(
        # List the files that are part of your app.
        files=["main.py"], 
        python=cloud.ManifestPython(
            # Specify the dependencies of your app.
            pip_requirements=[
                "nextmv==0.28.1",
                "ortools==9.12.4544",
            ],
        ),
        type=cloud.ManifestType.PYTHON,
        runtime=cloud.ManifestRuntime.PYTHON,
    ),
)
```

The typical structure of an app directory for the code based file strategy looks
like this:

```txt
.
├── main.py           # The actual app / model code
└── push.py           # Python script to define and push the app (see below)
```

## Object strategy

The object strategy consists of specifying a `model` and `model_configuration`.
This is useful when you are in an interactive environment like a Jupyter
notebook or a Python script, and you want to push the model _object_ directly.

This acts as a Python-native strategy called "Apps from
Models", where an app is created from a [`Nextmv.Model`][model]. The model is
encoded, some dependencies and accompanying files are packaged, and the app is
pushed to Nextmv Cloud. To push a `nextmv.Model` to Nextmv Cloud, you need
optional dependencies. You can install them by running:

```bash
pip install "nextmv[all]"
```

Once all the optional dependencies are installed, you can push the app to
Nextmv Cloud.

```python
import os

import nextmv
from nextmv import cloud


class CustomDecisionModel(nextmv.Model):
    def solve(self, input: nextmv.Input) -> nextmv.Output:
        """Implement the logic to solve the decision problem here."""
        pass

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

model = CustomDecisionModel()
options = nextmv.Options() # Define the options here.
model_configuration = nextmv.ModelConfiguration(
    name="custom_decision_model",
    requirements=[ # Acts as a requirements.txt file.
        "nextmv>=0.21.0",
        # Add any other dependencies here.
    ],
    options=options,
)
manifest = nextmv.cloud.Manifest.from_model_configuration(model_configuration)

app.push( # Use verbose=True for step-by-step output.
    manifest=manifest,
    model=model,
    model_configuration=model_configuration,
)
```

[cli]: https://docs.nextmv.io/docs/using-nextmv/reference/cli
[model]: ../modeling/model.md
[app-manifest]: https://docs.nextmv.io/docs/using-nextmv/deploy/app/manifest
[file-strategy]: #file-strategy
[object-strategy]: #object-strategy
[community-apps]: https://github.com/nextmv-io/community-apps
[python-ortools-knapsack]: https://github.com/nextmv-io/community-apps/tree/develop/python-ortools-knapsack
