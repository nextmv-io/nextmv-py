import logging
import os
import shutil
import warnings
from dataclasses import dataclass
from typing import Any, Optional

from nextmv.input import Input
from nextmv.logger import log
from nextmv.options import Options
from nextmv.output import Output

# The following block of code is used to suppress warnings from mlflow. We
# suppress these warnings because they are not relevant to the user, and they
# are not actionable.
original_showwarning = warnings.showwarning


def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    # .../site-packages/mlflow/pyfunc/utils/data_validation.py:134: UserWarning:Add
    # type hints to the `predict` method to enable data validation and automatic
    # signature inference during model logging. Check
    # https://mlflow.org/docs/latest/model/python_model.html#type-hint-usage-in-pythonmodel
    # for more details.
    if "mlflow/pyfunc/utils/data_validation.py" in filename:
        return

    # .../site-packages/mlflow/pyfunc/__init__.py:3212: UserWarning: An input
    # example was not provided when logging the model. To ensure the model
    # signature functions correctly, specify the `input_example` parameter. See
    # https://mlflow.org/docs/latest/model/signatures.html#model-input-example
    # for more details about the benefits of using input_example.
    if "mlflow/pyfunc/__init__.py" in filename:
        return

    original_showwarning(message, category, filename, lineno, file, line)


warnings.showwarning = custom_showwarning

# When working with the `Model`, we expect to be working in a notebook
# environment, and not interact with the local filesystem a lot. We use the
# `ModelConfiguration` to specify the dependencies that the `Model` requires.
# To work with the "push" logic of uploading an app to Nextmv Cloud, we need a
# requirement file that we use to gather dependencies, install them, and bundle
# them in the app. This file is used as a placeholder for the dependencies that
# the model requires and that we install and bundle with the app.
_REQUIREMENTS_FILE = "model_requirements.txt"

# When working in a notebook environment, we don’t really create a `main.py`
# file with the main entrypoint of the program. Because the logic is mostly
# encoded inside the `Model` class, we need to create a `main.py` file that we
# can run in Nextmv Cloud. This file is used as that entrypoint.
_ENTRYPOINT_FILE = "__entrypoint__.py"

_MLFLOW_DEPENDENCY = "mlflow>=2.18.0"


@dataclass
class ModelConfiguration:
    """
    ModelConfiguration is a class that holds the configuration for a
    model. It is used to define how a Python model is encoded and loaded.

    The `name` is required, and should be a personalized name for the model.

    You may specify the `requirements` that your decision model requires. This
    is done by passing a list of requirements, as if they were lines in a
    `requirements.txt` file. An example of this is `["nextmv==0.1.0"]`.

    Lastly, if your decision model requires options, you may specify them by
    passing an instance of `Options`.
    """

    name: str
    """The name of the decision model."""

    requirements: Optional[list[str]] = None
    """A list of Python dependencies that the decision model requires."""
    options: Optional[Options] = None
    """Options that the decision model requires."""


class Model:
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
        def solve(self, input: nextmv.Input) -> nextmv.Output:
            nextroute_input = nextroute.schema.Input.from_dict(input.data)
            nextroute_options = nextroute.Options.extract_from_dict(input.options.to_dict())
            nextroute_output = nextroute.solve(nextroute_input, nextroute_options)

            return nextmv.Output(
                options=input.options,
                solution=nextroute_output.solutions[0].to_dict(),
                statistics=nextroute_output.statistics.to_dict(),
            )
        ```
    """

    def solve(self, input: Input) -> Output:
        """
        The `solve` method is the main entry point of your model. You must
        implement this method yourself. It receives a `nextmv.Input` and should
        process it to produce a `nextmv.Output`, which is the solution to the
        decision model/problem.

        Parameters
        ----------
        input : Input
            The input data that the model will use to make a decision.

        Returns
        -------
        Output
            The output of the model, which is the solution to the decision
            model/problem.
        """

        raise NotImplementedError

    def save(model_self, model_dir: str, configuration: ModelConfiguration) -> None:
        """
        Save the model to the local filesystem, in the location given by `dir`.
        The model is saved according to the configuration provided, which is of
        type `ModelConfiguration`.

        Parameters
        ----------
        dir : str
            The directory where the model will be saved.
        configuration : ModelConfiguration
            The configuration of the model, which defines how the model is
            saved and loaded.
        """

        # mlflow is a big package. We don’t want to make it a dependency of
        # `nextmv` because it is not always needed. We only need it if we are
        # working with the "app from model" logic, which involves working with
        # this `Model` class.
        try:
            import mlflow as mlflow
        except ImportError as e:
            raise ImportError(
                "mlflow is not installed. Please install optional dependencies with `pip install nextmv[all]`"
            ) from e

        finally:
            from mlflow.models import infer_signature
            from mlflow.pyfunc import PythonModel, save_model

        class MLFlowModel(PythonModel):
            """
            The `MLFlowModel` class exists as a transient class to translate a
            Nextmv `DecisionModel` into an `mlflow.pyfunc.PythonModel`. This
            class must comply with the inference API of mlflow, which is why it
            has a `predict` method. The translation happens by having this
            `predict` method call the user-defined `solve` method of the
            `DecisionModel`.
            """

            def predict(
                self,
                context,
                model_input,
                params: Optional[dict[str, Any]] = None,
            ) -> Any:
                """
                The predict method allows us to work with mlflow’s [python_function]
                model flavor. Warning: This method should not be used or overridden
                directly. Instead, you should implement the `solve` method.

                [python_function]: https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
                """

                return model_self.solve(model_input)

        # Some annoying logging from mlflow must be disabled.
        logging.disable(logging.CRITICAL)

        _cleanup_python_model(model_dir, configuration, verbose=False)

        signature = None
        if configuration.options is not None:
            options_dict = configuration.options.to_dict()
            signature = infer_signature(
                params=options_dict,
            )

        # We use mlflow to save the model to the local filesystem, to be able to
        # load it later on.
        model_path = os.path.join(model_dir, configuration.name)
        save_model(
            path=model_path,  # Customize the name of the model location.
            infer_code_paths=True,  # Makes the imports portable.
            python_model=MLFlowModel(),
            signature=signature,  # Allows us to work with our own `Options` class.
        )

        # Create an auxiliary requirements file with the model dependencies.
        requirements_file = os.path.join(model_dir, _REQUIREMENTS_FILE)
        with open(requirements_file, "w") as file:
            file.write(f"{_MLFLOW_DEPENDENCY}\n")
            reqs = configuration.requirements
            if reqs is not None:
                for req in reqs:
                    file.write(f"{req}\n")

        # Adds the main.py file to the app_dir by coping the `entrypoint.py` file
        # which is one level up from this file.
        entrypoint_file = os.path.join(os.path.dirname(__file__), _ENTRYPOINT_FILE)
        shutil.copy2(entrypoint_file, os.path.join(model_dir, "main.py"))


def _cleanup_python_model(
    model_dir: str,
    model_configuration: Optional[ModelConfiguration] = None,
    verbose: bool = False,
) -> None:
    """Cleans up the Python-specific model packaging logic."""

    if model_configuration is None:
        return

    model_path = os.path.join(model_dir, model_configuration.name)
    if os.path.exists(model_path):
        shutil.rmtree(model_path)

    mlruns_path = os.path.join(model_dir, "mlruns")
    if os.path.exists(mlruns_path):
        shutil.rmtree(mlruns_path)

    requirements_file = os.path.join(model_dir, _REQUIREMENTS_FILE)
    if os.path.exists(requirements_file):
        os.remove(requirements_file)

    main_file = os.path.join(model_dir, "main.py")
    if os.path.exists(main_file):
        os.remove(main_file)

    if verbose:
        log("🧹 Cleaned up Python model artifacts.")
