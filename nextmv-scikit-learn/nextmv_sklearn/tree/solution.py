"""Defines sklearn.tree solution interoperability.

This module provides classes for working with scikit-learn tree models.

Classes
-------
DecisionTreeRegressorSolution
    Represents a scikit-learn DecisionTreeRegressor model, allowing conversion
    to and from a serializable format.
"""

import base64
import pickle
from typing import Annotated, Any

import numpy as np
from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from sklearn import tree

from ..ndarray import ndarray

Tree = Annotated[
    tree._tree.Tree,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]
"""
Type annotation for handling scikit-learn Tree objects.

This type is annotated with Pydantic validators and serializers to handle
the conversion between scikit-learn Tree objects and base64-encoded strings
for JSON serialization.
"""


class DecisionTreeRegressorSolution(BaseModel):
    """Decision Tree Regressor scikit-learn model representation.

    You can import the `DecisionTreeRegressorSolution` class directly from `tree`:

    ```python
    from nextmv_sklearn.tree import DecisionTreeRegressorSolution
    ```

    This class provides functionality to convert between scikit-learn's
    DecisionTreeRegressor model and a serializable format. It enables
    saving and loading trained models through dictionaries or JSON.

    Parameters
    ----------
    max_features_ : int, default=0
        The inferred value of max_features.
    n_features_in_ : int, default=0
        Number of features seen during fit.
    feature_names_in_ : ndarray, default=None
        Names of features seen during fit.
    n_outputs_ : int, default=0
        The number of outputs when fit is performed.
    tree_ : Tree, default=None
        The underlying Tree object.

    Examples
    --------
    >>> from sklearn.datasets import load_diabetes
    >>> from sklearn.tree import DecisionTreeRegressor
    >>> from nextmv_sklearn.tree import DecisionTreeRegressorSolution
    >>>
    >>> # Train a scikit-learn model
    >>> X, y = load_diabetes(return_X_y=True)
    >>> model = DecisionTreeRegressor().fit(X, y)
    >>>
    >>> # Convert to solution object
    >>> solution = DecisionTreeRegressorSolution.from_model(model)
    >>>
    >>> # Convert to dictionary for serialization
    >>> model_dict = solution.to_dict()
    >>>
    >>> # Recreate solution from dictionary
    >>> restored = DecisionTreeRegressorSolution.from_dict(model_dict["attributes"])
    >>>
    >>> # Convert back to scikit-learn model
    >>> restored_model = restored.to_model()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    max_features_: int = 0
    """The inferred value of max_features."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit. Defined only when X has feature names
    that are all strings."""
    n_outputs_: int = 0
    """The number of outputs when fit is performed."""
    tree_: Tree = None  # type: ignore
    """The underlying Tree object."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DecisionTreeRegressorSolution":
        """
        Creates a DecisionTreeRegressorSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary containing the model attributes.

        Returns
        -------
        DecisionTreeRegressorSolution
            Instance of DecisionTreeRegressorSolution.

        Examples
        --------
        >>> solution_dict = {
        ...     "max_features_": 10,
        ...     "n_features_in_": 10,
        ...     "n_outputs_": 1,
        ...     "tree_": "base64encodedtreedata"
        ... }
        >>> solution = DecisionTreeRegressorSolution.from_dict(solution_dict)
        """

        if "tree_" in data:
            data["tree_"] = pickle.loads(base64.b64decode(data["tree_"]))

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = np.array(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: tree.DecisionTreeRegressor) -> "DecisionTreeRegressorSolution":
        """
        Creates a DecisionTreeRegressorSolution instance from a scikit-learn
        DecisionTreeRegressor model.

        Parameters
        ----------
        model : tree.DecisionTreeRegressor
            scikit-learn DecisionTreeRegressor model.

        Returns
        -------
        DecisionTreeRegressorSolution
            Instance of DecisionTreeRegressorSolution.

        Examples
        --------
        >>> from sklearn.datasets import load_diabetes
        >>> from sklearn.tree import DecisionTreeRegressor
        >>> X, y = load_diabetes(return_X_y=True)
        >>> model = DecisionTreeRegressor().fit(X, y)
        >>> solution = DecisionTreeRegressorSolution.from_model(model)
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
            Dictionary with class information and model attributes.
            The dictionary has two main keys:
            - 'class': Contains module and class name information
            - 'attributes': Contains the serialized model attributes

        Examples
        --------
        >>> solution = DecisionTreeRegressorSolution(max_features_=10)
        >>> solution_dict = solution.to_dict()
        >>> print(solution_dict['class']['name'])
        'DecisionTreeRegressorSolution'
        """

        t = type(self)
        return {
            "class": {
                "module": t.__module__,
                "name": t.__name__,
            },
            "attributes": self.model_dump(mode="json", exclude_none=True, by_alias=True),
        }

    def to_model(self) -> tree.DecisionTreeRegressor:
        """
        Transforms the DecisionTreeRegressorSolution instance into a scikit-learn
        DecisionTreeRegressor model.

        Returns
        -------
        tree.DecisionTreeRegressor
            scikit-learn DecisionTreeRegressor model.

        Examples
        --------
        >>> solution = DecisionTreeRegressorSolution(max_features_=10, n_features_in_=10)
        >>> model = solution.to_model()
        >>> isinstance(model, tree.DecisionTreeRegressor)
        True
        """
        m = tree.DecisionTreeRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
