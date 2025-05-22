"""
When working in a notebook environment, we don't really create a `main.py` file
with the main entrypoint of the program. Because the logic is mostly encoded
inside the `Model` class, we need to create a `main.py` file that we can run in
Nextmv Cloud. This file is used as that entrypoint. It is not intended for a
human to use it during local development. It is the standard way in which a
`nextmv.Model` is loaded by using mlflow.
"""

from mlflow.pyfunc import load_model

import nextmv
from nextmv import cloud


def main() -> None:
    """Entry point for the program."""

    manifest = cloud.Manifest.from_yaml(".")

    # Load the options from the manifest.
    options = manifest.extract_options()

    # Load the model.
    loaded_model = load_model(
        model_uri=manifest.python.model.name,
        suppress_warnings=True,
    )

    # Load the input and solve the model by using mlflow's inference API.
    input = nextmv.load(options=options)
    output = loaded_model.predict(input)

    # Write the output.
    nextmv.write(output)


if __name__ == "__main__":
    main()
