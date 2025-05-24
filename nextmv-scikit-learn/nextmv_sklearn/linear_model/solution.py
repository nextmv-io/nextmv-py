"""Defines sklearn.linear_model solution interoperability.

This module provides classes for converting between scikit-learn linear models
and Nextmv compatible representations.

Classes
-------
LinearRegressionSolution
    A Pydantic model representation of scikit-learn's LinearRegression model

Variables
---------
Loss
    A type annotation for serializing loss functions
"""

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
"""
Type annotation for serializing loss functions.

This annotation combines validation and serialization for scikit-learn loss
functions. It uses base64 encoding and pickle to serialize the loss object to a
string.
"""


class LinearRegressionSolution(BaseModel):
    """Linear Regression scikit-learn model representation.

    You can import the `LinearRegressionSolution` class directly from `linear_model`:

    ```python
    from nextmv_sklearn.linear_model import LinearRegressionSolution
    ```

    This class provides a Pydantic model representation of scikit-learn's
    LinearRegression model, with methods for conversion between the scikit-learn
    model and this representation for serialization and deserialization.

    Parameters
    ----------
    coef_ : ndarray, optional
        Estimated coefficients for the linear regression problem.
    rank_ : int, default=0
        Rank of matrix X. Only available when X is dense.
    singular_ : ndarray, optional
        Singular values of X. Only available when X is dense.
    intercept_ : float, default=0
        Independent term in the linear model. Set to 0.0 if fit_intercept=False.
    n_features_in_ : int, default=0
        Number of features seen during fit.
    feature_names_in_ : ndarray, optional
        Names of features seen during fit. Defined only when X has feature names
        that are all strings.

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.linear_model import LinearRegression
    >>> from nextmv_sklearn.linear_model import LinearRegressionSolution
    >>>
    >>> # Create a scikit-learn model and fit it
    >>> X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    >>> y = np.array([1, 2, 2, 3])
    >>> reg = LinearRegression().fit(X, y)
    >>>
    >>> # Convert to LinearRegressionSolution
    >>> solution = LinearRegressionSolution.from_model(reg)
    >>>
    >>> # Convert back to scikit-learn model
    >>> reg_restored = solution.to_model()
    """

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
    def from_dict(cls, data: dict[str, Any]) -> "LinearRegressionSolution":
        """
        Creates a LinearRegressionSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
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
            Instance of LinearRegressionSolution containing the attributes
            from the provided model.

        Examples
        --------
        >>> from sklearn.linear_model import LinearRegression
        >>> import numpy as np
        >>> X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        >>> y = np.array([1, 2, 2, 3])
        >>> reg = LinearRegression().fit(X, y)
        >>> solution = LinearRegressionSolution.from_model(reg)
        """

        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_dict(self):
        """
        Convert a data model instance to a dict with associated class info.

        Returns
        -------
        dict
            Dictionary containing the class module and name, along with the
            model attributes.

        Examples
        --------
        >>> solution = LinearRegressionSolution(coef_=np.array([1.0, 2.0]))
        >>> solution_dict = solution.to_dict()
        >>> print(solution_dict['class']['name'])
        'LinearRegressionSolution'
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

    def to_model(self) -> linear_model.LinearRegression:
        """
        Transforms the LinearRegressionSolution instance into a scikit-learn
        LinearRegression model.

        Returns
        -------
        LinearRegression
            scikit-learn LinearRegression model with attributes set from
            the current LinearRegressionSolution instance.

        Examples
        --------
        >>> # Assuming we have a LinearRegressionSolution instance
        >>> solution = LinearRegressionSolution(
        ...     coef_=np.array([1.0, 2.0]),
        ...     intercept_=0.5
        ... )
        >>> # Convert back to scikit-learn model
        >>> sklearn_model = solution.to_model()
        >>> sklearn_model.coef_
        array([1., 2.])
        >>> sklearn_model.intercept_
        0.5
        """

        m = linear_model.LinearRegression()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
