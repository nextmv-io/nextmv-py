"""Defines sklearn.neural_network solution interoperability.

This module provides functionality for interacting with scikit-learn's neural network models.

Classes
-------
MLPRegressorSolution
    A Pydantic model representation of scikit-learn's MLPRegressor.

Variables
---------
Loss
    An annotated type for handling loss values in scikit-learn models.
"""

import base64
import pickle
from typing import Annotated, Any, Optional

import numpy as np
from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from sklearn import neural_network

from ..ndarray import ndarray

Loss = Annotated[
    Any,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]
"""
Annotated type for serialization and validation of scikit-learn loss objects.

This type encodes a pickle serialized representation of a loss object as a base64 string,
to ensure that loss objects can be safely serialized and deserialized.
"""


class MLPRegressorSolution(BaseModel):
    """MLP Regressor scikit-learn model representation.

    You can import the `MLPRegressorSolution` class directly from `neural_network`:

    ```python
    from nextmv_sklearn.neural_network import MLPRegressorSolution
    ```

    This class provides a Pydantic model representation of scikit-learn's MLPRegressor
    model, enabling serialization, deserialization, and conversion between model formats.

    Parameters
    ----------
    loss_ : float, default=0.0
        The current loss computed with the loss function.
    best_loss_ : float, default=0.0
        The minimum loss reached by the solver throughout fitting.
    loss_curve_ : list[np.float64], optional
        Loss value evaluated at the end of each training step.
    validation_scores_ : list[float], optional
        The score at each iteration on a held-out validation set.
    best_validation_score_ : float, optional
        The best validation score (i.e. R2 score) that triggered the early stopping.
    t_ : int, default=0
        The number of training samples seen by the solver during fitting.
    coefs_ : list[ndarray], optional
        The ith element in the list represents the weight matrix corresponding to layer i.
    intercepts_ : list[ndarray], optional
        The ith element in the list represents the bias vector corresponding to layer i + 1.
    n_features_in_ : int, default=0
        Number of features seen during fit.
    feature_names_in_ : ndarray, optional
        Names of features seen during fit.
    n_iter_ : int, default=0
        The number of iterations the solver has run.
    n_layers_ : int, default=0
        Number of layers.
    n_outputs_ : int, default=0
        Number of outputs.
    out_activation_ : str, optional
        Name of the output activation function.

    Examples
    --------
    >>> from sklearn.neural_network import MLPRegressor
    >>> from nextmv_sklearn.neural_network import MLPRegressorSolution
    >>>
    >>> # Create and train a sklearn MLPRegressor
    >>> regressor = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500)
    >>> regressor.fit(X_train, y_train)
    >>>
    >>> # Convert to MLPRegressorSolution for serialization
    >>> solution = MLPRegressorSolution.from_model(regressor)
    >>> solution_dict = solution.to_dict()
    >>>
    >>> # Later, recreate the solution and convert back to sklearn model
    >>> restored_solution = MLPRegressorSolution.from_dict(solution_dict["attributes"])
    >>> restored_model = restored_solution.to_model()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    loss_: float = 0.0
    """The current loss computed with the loss function."""
    best_loss_: float = 0.0
    """The minimum loss reached by the solver throughout fitting."""
    loss_curve_: list[np.float64] = None
    """Loss value evaluated at the end of each training step."""
    validation_scores_: Optional[list[float]] = None
    """The score at each iteration on a held-out validation set."""
    best_validation_score_: Optional[float] = None
    """The best validation score (i.e. R2 score) that triggered the early stopping."""
    t_: int = 0
    """The number of training samples seen by the solver during fitting."""
    coefs_: list[ndarray] = None
    """The ith element in the list represents the weight matrix corresponding to layer i."""
    intercepts_: list[ndarray] = None
    """The ith element in the list represents the bias vector corresponding to layer i + 1."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit."""
    n_iter_: int = 0
    """The number of iterations the solver has run."""
    n_layers_: int = 0
    """Number of layers."""
    n_outputs_: int = 0
    """Number of output."""
    out_activation_: str = None
    """Name of the output activation function."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MLPRegressorSolution":
        """
        Creates a MLPRegressorSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary containing the model attributes.

        Returns
        -------
        MLPRegressorSolution
            Instance of MLPRegressorSolution.

        Examples
        --------
        >>> solution_dict = {"loss_": 0.15, "n_layers_": 3, "n_outputs_": 1}
        >>> solution = MLPRegressorSolution.from_dict(solution_dict)
        """

        if "loss_curve_" in data:
            data["loss_curve_"] = [np.float64(val) for val in data["loss_curve_"]]

        if "coefs_" in data:
            data["coefs_"] = [np.array([np.float64(col) for col in row]) for row in data["coefs_"]]

        if "intercepts_" in data:
            data["intercepts_"] = [np.array([np.float64(col) for col in row]) for row in data["intercepts_"]]

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = np.array(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: neural_network.MLPRegressor) -> "MLPRegressorSolution":
        """
        Creates a MLPRegressorSolution instance from a scikit-learn
        MLPRegressor model.

        Parameters
        ----------
        model : MLPRegressor
            scikit-learn MLPRegressor model.

        Returns
        -------
        MLPRegressorSolution
            Instance of MLPRegressorSolution.

        Examples
        --------
        >>> from sklearn.neural_network import MLPRegressor
        >>> regressor = MLPRegressor().fit(X, y)
        >>> solution = MLPRegressorSolution.from_model(regressor)
        """

        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_dict(self) -> dict:
        """
        Convert a data model instance to a dict with associated class info.

        Returns
        -------
        dict
            Dictionary containing class information and model attributes.

        Examples
        --------
        >>> solution = MLPRegressorSolution.from_model(regressor)
        >>> solution_dict = solution.to_dict()
        >>> print(solution_dict["class"]["name"])
        'MLPRegressorSolution'
        """

        d = self.model_dump(mode="json", exclude_none=True, by_alias=True)

        t = type(self)
        return {
            "class": {
                "module": t.__module__,
                "name": t.__name__,
            },
            "attributes": d,
        }

    def to_model(self) -> neural_network.MLPRegressor:
        """
        Transforms the MLPRegressorSolution instance into a scikit-learn
        MLPRegressor model.

        Returns
        -------
        MLPRegressor
            scikit-learn MLPRegressor model.

        Examples
        --------
        >>> solution = MLPRegressorSolution.from_dict(solution_data)
        >>> model = solution.to_model()
        >>> predictions = model.predict(X_test)
        """

        m = neural_network.MLPRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
