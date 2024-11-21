from dataclasses import dataclass
from typing import Any, List, Optional

from mlflow.pyfunc import PythonModel

from nextmv.input import Input
from nextmv.options import Options
from nextmv.output import Output

_REQUIREMENTS_FILE = "model_requirements.txt"
_ENTRYPOINT_FILE = "__entrypoint__.py"


class Model(PythonModel):
    """
    Model is the base class for defining a decision model that runs in the Cloud.
    """

    def predict(self, context, model_input, params=None) -> Any:
        """
        The predict method allows us to work with mlflow’s [python_function]
        model flavor.

        [python_function]: https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
        """

        options = Options.from_dict_parameters(params)

        return self.solve(model_input, options)

    def solve(input: Input, options: Options) -> Output:
        """
        The solve method is the main entry point of your model. It takes an
        an input and options and should return an output with a solution
        (decision). You should implement this method with the main logic of
        your decision model.
        """

        raise NotImplementedError


@dataclass
class ModelConfiguration:
    """
    ModelConfiguration is a class that holds the configuration for a
    model. It is used to define how a Python model is encoded and loaded.
    """

    name: str
    """The name of the decision model."""

    requirements: Optional[List[str]] = None
    """A list of Python dependencies that the decision model requires."""
    options: Optional[Options] = None
    """Options that the decision model requires."""
