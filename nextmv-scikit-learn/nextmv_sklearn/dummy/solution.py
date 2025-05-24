"""Defines sklearn.dummy solution interoperability.

This module provides classes and utilities for working with scikit-learn's
dummy models in the Nextmv ecosystem.

Classes
-------
DummyRegressorSolution
    A Pydantic model representation of scikit-learn's DummyRegressor.
    It allows for serialization, deserialization, and conversion between
    the scikit-learn model and this representation.
"""

from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict
from sklearn import dummy

from nextmv_sklearn.ndarray import ndarray


class DummyRegressorSolution(BaseModel):
    """Dummy Regressor scikit-learn model representation.

    You can import the `DummyRegressorSolution` class directly from `dummy`:

    ```python
    from nextmv_sklearn.dummy import DummyRegressorSolution
    ```

    This class provides a Pydantic model representation of scikit-learn's
    DummyRegressor model. It allows for serialization, deserialization,
    and conversion between the scikit-learn model and this representation.

    Parameters
    ----------
    constant_ : ndarray
        Mean or median or quantile of the training targets or constant value
        given by the user.
    n_features_in_ : int
        Number of features seen during fit.
    feature_names_in_ : ndarray
        Names of features seen during fit. Defined only when X has feature names
        that are all strings.
    n_outputs_ : int
        Number of outputs.

    Examples
    --------
    >>> from sklearn.dummy import DummyRegressor
    >>> from nextmv_sklearn.dummy import DummyRegressorSolution
    >>> # Train a scikit-learn dummy regressor
    >>> model = DummyRegressor(strategy="mean")
    >>> model.fit([[1], [2], [3]], [4, 5, 6])
    >>> # Convert to DummyRegressorSolution
    >>> solution = DummyRegressorSolution.from_model(model)
    >>> # Convert back to scikit-learn model
    >>> model_restored = solution.to_model()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    constant_: ndarray = None
    """Mean or median or quantile of the training targets or constant value
    given by the user."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit. Defined only when X has feature names
    that are all strings."""
    n_outputs_: int = 0
    """Number of outputs."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DummyRegressorSolution":
        """
        Creates a DummyRegressorSolution instance from a dictionary.

        This method creates an instance of DummyRegressorSolution from a dictionary
        containing model attributes. It converts any array-like attributes to
        numpy arrays.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary containing the model attributes.

        Returns
        -------
        DummyRegressorSolution
            Instance of DummyRegressorSolution.

        Examples
        --------
        >>> from nextmv_sklearn.dummy import DummyRegressorSolution
        >>> data = {
        ...     'constant_': [5.0],
        ...     'n_features_in_': 1,
        ...     'feature_names_in_': ['x'],
        ...     'n_outputs_': 1
        ... }
        >>> solution = DummyRegressorSolution.from_dict(data)
        >>> solution.n_features_in_
        1
        """

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = np.array(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: dummy.DummyRegressor) -> "DummyRegressorSolution":
        """
        Creates a DummyRegressorSolution instance from a scikit-learn
        DummyRegressor model.

        This method extracts relevant attributes from a scikit-learn DummyRegressor
        model and creates a DummyRegressorSolution instance with those attributes.

        Parameters
        ----------
        model : dummy.DummyRegressor
            scikit-learn DummyRegressor model.

        Returns
        -------
        DummyRegressorSolution
            Instance of DummyRegressorSolution containing the model's attributes.

        Examples
        --------
        >>> from sklearn.dummy import DummyRegressor
        >>> from nextmv_sklearn.dummy import DummyRegressorSolution
        >>> # Create and fit a scikit-learn model
        >>> model = DummyRegressor().fit([[1, 2], [3, 4]], [5, 6])
        >>> # Convert to DummyRegressorSolution
        >>> solution = DummyRegressorSolution.from_model(model)
        >>> solution.n_features_in_
        2
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

        This method converts the instance to a dictionary that includes class
        information (module and name) and the model's attributes.

        Returns
        -------
        dict
            Dictionary containing class information and attributes of the model.

        Examples
        --------
        >>> from sklearn.dummy import DummyRegressor
        >>> from nextmv_sklearn.dummy import DummyRegressorSolution
        >>> model = DummyRegressor().fit([[1], [2]], [1, 2])
        >>> solution = DummyRegressorSolution.from_model(model)
        >>> solution_dict = solution.to_dict()
        >>> print(solution_dict['class']['name'])
        'DummyRegressorSolution'
        """

        t = type(self)
        d = self.model_dump(mode="json", exclude_none=True, by_alias=True)

        return {
            "class": {
                "module": t.__module__,
                "name": t.__name__,
            },
            "attributes": d,
        }

    def to_model(self) -> dummy.DummyRegressor:
        """
        Transforms the DummyRegressorSolution instance into a scikit-learn
        DummyRegressor model.

        This method creates a new scikit-learn DummyRegressor model and sets its
        attributes based on the current instance's attributes.

        Returns
        -------
        dummy.DummyRegressor
            scikit-learn DummyRegressor model with attributes copied from this instance.

        Examples
        --------
        >>> from sklearn.dummy import DummyRegressor
        >>> from nextmv_sklearn.dummy import DummyRegressorSolution
        >>> # Create a solution instance
        >>> solution = DummyRegressorSolution(
        ...     constant_=np.array([5.0]),
        ...     n_features_in_=2,
        ...     n_outputs_=1
        ... )
        >>> # Convert to scikit-learn model
        >>> model = solution.to_model()
        >>> isinstance(model, DummyRegressor)
        True
        """
        m = dummy.DummyRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
