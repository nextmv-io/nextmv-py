"""
Model module for creating and saving decision models in Nextmv Cloud.

This module provides the base classes and functionality for creating decision models
that can be deployed and run in Nextmv Cloud. The main components are:

Classes
-------
Model
    Base class for defining decision models.
ModelConfiguration
    Configuration for packaging and deploying models.

Models defined using this module can be packaged with their dependencies and
deployed to Nextmv Cloud for execution.
"""

import logging
import os
import shutil
import warnings
from dataclasses import dataclass
from typing import Any, Optional

from nextmv.input import Input
from nextmv.logger import log
from nextmv.options import Options, OptionsEnforcement
from nextmv.output import Output

# The following block of code is used to suppress warnings from mlflow. We
# suppress these warnings because they are not relevant to the user, and they
# are not actionable.

"""
Module-level function and variable to suppress warnings from mlflow.
"""

_original_showwarning = warnings.showwarning
"""Original showwarning function from the warnings module."""


def _custom_showwarning(message, category, filename, lineno, file=None, line=None):
    """
    Custom warning handler that suppresses specific mlflow warnings.

    This function filters out non-actionable warnings from the mlflow library
    to keep the console output clean and relevant for the user.

    Parameters
    ----------
    message : str
        The warning message.
    category : Warning
        The warning category.
    filename : str
        The filename where the warning was raised.
    lineno : int
        The line number where the warning was raised.
    file : file, optional
        The file to write the warning to.
    line : str, optional
        The line of source code to be included in the warning message.

    Returns
    -------
    None
        If the warning matches certain patterns, the function returns early
        without showing the warning. Otherwise, it delegates to the original
        warning handler.
    """
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

    _original_showwarning(message, category, filename, lineno, file, line)


warnings.showwarning = _custom_showwarning

# When working with the `Model`, we expect to be working in a notebook
# environment, and not interact with the local filesystem a lot. We use the
# `ModelConfiguration` to specify the dependencies that the `Model` requires.
# To work with the "push" logic of uploading an app to Nextmv Cloud, we need a
# requirement file that we use to gather dependencies, install them, and bundle
# them in the app. This file is used as a placeholder for the dependencies that
# the model requires and that we install and bundle with the app.
_REQUIREMENTS_FILE = "model_requirements.txt"

# When working in a notebook environment, we don't really create a `main.py`
# file with the main entrypoint of the program. Because the logic is mostly
# encoded inside the `Model` class, we need to create a `main.py` file that we
# can run in Nextmv Cloud. This file is used as that entrypoint.
_ENTRYPOINT_FILE = "__entrypoint__.py"


# Required mlflow dependency version for model packaging.
_MLFLOW_DEPENDENCY = "mlflow>=2.18.0"


@dataclass
class ModelConfiguration:
    """
    Configuration class for Nextmv models.

    You can import the `ModelConfiguration` class directly from `nextmv`:

    ```python
    from nextmv import ModelConfiguration
    ```

    This class holds the configuration for a model, defining how a Python model
    is encoded and loaded for use in Nextmv Cloud.

    Parameters
    ----------
    name : str
        A personalized name for the model. This is required.
    requirements : list[str], optional
        A list of Python dependencies that the decision model requires,
        formatted as they would appear in a requirements.txt file.
    options : Options, optional
        Options that the decision model requires.
    options_enforcement:
        Enforcement of options for the model. This controls how options
        are handled when the model is run.

    Examples
    --------
    >>> from nextmv import ModelConfiguration, Options
    >>> config = ModelConfiguration(
    ...     name="my_routing_model",
    ...     requirements=["nextroute>=1.0.0"],
    ...     options=Options({"max_time": 60}),
    ...     options_enforcement=OptionsEnforcement(
                strict=True,
                validation_enforce=True
            )
    ... )
    """

    name: str
    """The name of the decision model."""
    requirements: Optional[list[str]] = None
    """A list of Python dependencies that the decision model requires."""
    options: Optional[Options] = None
    """Options that the decision model requires."""
    options_enforcement: Optional[OptionsEnforcement] = None
    """Enforcement of options for the model."""


class Model:
    """
    Base class for defining decision models that run in Nextmv Cloud.

    You can import the `Model` class directly from `nextmv`:

    ```python
    from nextmv import Model
    ```

    This class serves as a foundation for creating decision models that can be
    deployed to Nextmv Cloud. Subclasses must implement the `solve` method,
    which is the main entry point for processing inputs and producing decisions.

    Methods
    -------
    solve(input)
        Process input data and produce a decision output.
    save(model_dir, configuration)
        Save the model to the filesystem for deployment.

    Examples
    --------
    >>> import nextroute
    >>> import nextmv
    >>>
    >>> class DecisionModel(nextmv.Model):
    ...     def solve(self, input: nextmv.Input) -> nextmv.Output:
    ...         nextroute_input = nextroute.schema.Input.from_dict(input.data)
    ...         nextroute_options = nextroute.Options.extract_from_dict(input.options.to_dict())
    ...         nextroute_output = nextroute.solve(nextroute_input, nextroute_options)
    ...
    ...         return nextmv.Output(
    ...             options=input.options,
    ...             solution=nextroute_output.solutions[0].to_dict(),
    ...             statistics=nextroute_output.statistics.to_dict(),
    ...         )
    """

    def solve(self, input: Input) -> Output:
        """
        Process input data and produce a decision output.

        This is the main entry point of your model that you must implement in
        subclasses. It receives input data and should process it to produce an
        output containing the solution to the decision problem.

        Parameters
        ----------
        input : Input
            The input data that the model will use to make a decision.

        Returns
        -------
        Output
            The output of the model, which is the solution to the decision
            model/problem.

        Raises
        ------
        NotImplementedError
            When called on the base Model class, as this method must be
            implemented by subclasses.

        Examples
        --------
        >>> def solve(self, input: Input) -> Output:
        ...     # Process input data
        ...     result = self._process_data(input.data)
        ...
        ...     # Return formatted output
        ...     return Output(
        ...         options=input.options,
        ...         solution=result,
        ...         statistics={"processing_time": 0.5}
        ...     )
        """

        raise NotImplementedError

    def save(model_self, model_dir: str, configuration: ModelConfiguration) -> None:
        """
        Save the model to the local filesystem for deployment.

        This method packages the model according to the provided configuration,
        creating all necessary files and dependencies for deployment to Nextmv
        Cloud.

        Parameters
        ----------
        model_dir : str
            The directory where the model will be saved.
        configuration : ModelConfiguration
            The configuration of the model, which defines how the model is
            saved and loaded.

        Raises
        ------
        ImportError
            If mlflow is not installed, which is required for model packaging.

        Notes
        -----
        This method uses mlflow for model packaging, creating the necessary
        files and directory structure for deployment.

        Examples
        --------
        >>> model = MyDecisionModel()
        >>> config = ModelConfiguration(
        ...     name="routing_model",
        ...     requirements=["pandas", "numpy"]
        ... )
        >>> model.save("/tmp/my_model", config)
        """

        # mlflow is a big package. We don't want to make it a dependency of
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
            Transient class to translate a Nextmv Decision Model into an MLflow PythonModel.

            This class complies with the MLflow inference API, implementing a `predict`
            method that calls the user-defined `solve` method of the Nextmv Decision Model.

            Methods
            -------
            predict(context, model_input, params)
                MLflow-compliant predict method that delegates to the Nextmv model's solve method.
            """

            def predict(
                self,
                context,
                model_input,
                params: Optional[dict[str, Any]] = None,
            ) -> Any:
                """
                MLflow-compliant prediction method that calls the Nextmv model's solve method.

                This method enables compatibility with MLflow's python_function model flavor.

                Parameters
                ----------
                context : mlflow.pyfunc.PythonModelContext
                    The MLflow model context.
                model_input : Any
                    The input data for prediction, passed to the solve method.
                params : Optional[dict[str, Any]], optional
                    Additional parameters for prediction.

                Returns
                -------
                Any
                    The result from the Nextmv model's solve method.

                Notes
                -----
                This method should not be used or overridden directly. Instead,
                implement the `solve` method in your Nextmv Model subclass.
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
    """
    Clean up Python-specific model packaging artifacts.

    This function removes temporary files and directories created during the
    model packaging process.

    Parameters
    ----------
    model_dir : str
        The directory where the model was saved.
    model_configuration : Optional[ModelConfiguration], optional
        The configuration of the model. If None, the function returns early.
    verbose : bool, default=False
        If True, log a message when cleanup is complete.

    Returns
    -------
    None
        This function does not return anything.

    Notes
    -----
    Files and directories removed include:
    - The model directory itself
    - The mlruns directory created by MLflow
    - The requirements file
    - The main.py file
    """

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
