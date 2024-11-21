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
    Model is the base class for defining a decision model that runs in Nextmv
    Cloud. You must create a subclass of this class and implement the `solve`
    method. The `solve` method is the main entry point of your model and should
    return an output with a solution (decision).

    Example
    -------
    ```python
    import nextroute

    import nextmv


    # Define the model that makes decisions. This model uses the Nextroute library
    # to solve a routing problem.
    class DecisionModel(nextmv.Model):
        def solve(self, input: nextmv.Input, options: nextmv.Options) -> nextmv.Output:
            nextroute_input = nextroute.schema.Input.from_dict(input.data)
            nextroute_options = nextroute.Options.extract_from_dict(options.to_dict())
            nextroute_output = nextroute.solve(nextroute_input, nextroute_options)

            return nextmv.Output(
                options=options,
                solution=nextroute_output.solutions[0].to_dict(),
                statistics=nextroute_output.statistics.to_dict(),
            )
        ```
    """

    def predict(self, context, model_input, params=None) -> Any:
        """
        The predict method allows us to work with mlflow’s [python_function]
        model flavor. Warning: This method should not be used or overridden
        directly. Instead, you should implement the `solve` method.

        [python_function]: https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
        """

        options = Options.from_dict(params)

        return self.solve(model_input, options)

    def solve(input: Input, options: Options) -> Output:
        """
        The `solve` method is the main entry point of your model. It takes an
        an `input` and `options` and should return an output with a solution
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
