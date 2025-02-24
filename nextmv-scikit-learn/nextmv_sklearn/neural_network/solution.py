"""Defines sklearn.neural_network solution interoperability."""

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


class MLPRegressorSolution(BaseModel):
    """MLP Regressor scikit-learn model representation."""

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
    def from_dict(cls, data: dict[str, any]) -> "MLPRegressorSolution":
        """
        Creates a MLPRegressorSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing the model attributes.

        Returns
        -------
        MLPRegressorSolution
            Instance of MLPRegressorSolution.
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
            Instance of MLPRegressor
        """

        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_dict(self):
        """Convert a data model instance to a dict with associated class
        info."""

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
        """

        m = neural_network.MLPRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
