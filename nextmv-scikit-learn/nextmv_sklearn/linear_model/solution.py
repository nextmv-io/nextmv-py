"""Defines sklearn.linear_model solution interoperability."""

import base64
import pickle
from typing import Annotated, Any

import numpy as np
from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from sklearn import linear_model

from ..ndarray import ndarray

Loss = Annotated[
    Any,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]


class LinearRegressionSolution(BaseModel):
    """Linear Regression scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    coef_: ndarray = None
    """Estimated coefficients for the linear regression problem."""
    rank_: int = 0
    """Rank of matrix X. Only available when X is dense."""
    singular_: ndarray = None
    """Singular values of X. Only available when X is dense."""
    intercept_: float = 0
    """Independent term in the linear model. Set to 0.0 if fit_intercept =
    False."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit. Defined only when X has feature names
    that are all strings."""

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "LinearRegressionSolution":
        """
        Creates a LinearRegressionSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing the model attributes.

        Returns
        -------
        LinearRegressionSolution
            Instance of LinearRegressionSolution.
        """

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = np.array(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: linear_model.LinearRegression) -> "LinearRegressionSolution":
        """
        Creates a LinearRegressionSolution instance from a scikit-learn
        LinearRegression model.

        Parameters
        ----------
        model : LinearRegression
            scikit-learn LinearRegression model.

        Returns
        -------
        LinearRegressionSolution
            Instance of LinearRegression
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

    def to_model(self) -> linear_model.LinearRegression:
        """
        Transforms the LinearRegressionSolution instance into a scikit-learn
        LinearRegression model.

        Returns
        -------
        LinearRegression
            scikit-learn LinearRegression model.
        """

        m = linear_model.LinearRegression()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
