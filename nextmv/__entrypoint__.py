"""
This entrypoint file is meant to be used in the Nextmv Cloud. It is not
intended for a human to use it during local development. It is the standard way
in which a `nextmv.Model` is loaded by using mlflow.
"""

from mlflow.pyfunc import load_model

from nextmv.cloud.manifest import Manifest
from nextmv.input import load_local
from nextmv.model import ModelConfiguration
from nextmv.options import Options
from nextmv.output import write_local


def main() -> None:
    """Entry point for the program."""

    manifest = Manifest.from_yaml(".")

    options = None
    dict_parameters = manifest.python.model.options
    if dict_parameters is not None:
        options = Options.from_dict_parameters(dict_parameters)

    model_configuration = ModelConfiguration(
        name=manifest.python.model.name,
        options=options,
    )
    loaded_model = load_model(
        model_uri=model_configuration.name,
        suppress_warnings=True,
    )

    input = load_local(options=options)
    output = loaded_model.predict(input, params=options.to_dict())

    write_local(output)


if __name__ == "__main__":
    main()
