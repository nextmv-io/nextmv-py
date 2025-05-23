# Push to an Application

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

A Nextmv Cloud Application is a decision model that be executed remotely on the
Nextmv Platform. An application is an executable program that fulfills the
following minimum requirements:

1. Must read from either `stdin` or a file.
2. Must write results either to `stdout` or a file.
3. Must contain an [`app.yaml` manifest][app-manifest] in the root of your app
project.

To push an app to Nextmv Cloud using the `nextmv` Python SDK, you can use one
of the following strategies:

* [External strategy][external-strategy]: push an app that is composed of files
      in a directory.
* [Internal strategy][internal-strategy]: push an app that is created from a
  [`nextmv.Model`][model].

## External strategy

The external strategy consists of specifying `app_dir`, which is the path to an
app’s root directory. The app is composed of files in a directory and those
apps are packaged and pushed to Nextmv Cloud. This is language-agnostic and can
work for an app written in any language.

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

## Internal strategy

The internal strategy consists of specifying a `model` and
`model_configuration`. This acts as a Python-native strategy called "Apps from
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
[model]: ../model.md
[app-manifest]: https://docs.nextmv.io/docs/using-nextmv/deploy/app/manifest
[external-strategy]: #external-strategy
[internal-strategy]: #internal-strategy
