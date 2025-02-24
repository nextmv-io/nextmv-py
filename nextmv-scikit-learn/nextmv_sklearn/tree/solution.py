"""Defines sklearn.tree solution interoperability."""

import base64
import pickle
from typing import Annotated

import numpy as np
from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from sklearn import tree

from ..ndarray import ndarray

Tree = Annotated[
    tree._tree.Tree,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]


class DecisionTreeRegressorSolution(BaseModel):
    """Decision Tree Regressor scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    max_features_: int = 0
    """The inferred value of max_features.."""
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
    def from_dict(cls, data: dict[str, any]) -> "DecisionTreeRegressorSolution":
        """
        Creates a DecisionTreeRegressorSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing the model attributes.

        Returns
        -------
        DecisionTreeRegressorSolution
            Instance of DecisionTreeRegressorSolution.
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
        model : DecisionTreeRegressor
            scikit-learn DecisionTreeRegressor model.

        Returns
        -------
        DecisionTreeRegressorSolution
            Instance of DecisionTreeRegressor
        """

        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_dict(self):
        """Convert a data model instance to a dict with associated class info."""

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
        DecisionTreeRegressor
            scikit-learn DecisionTreeRegressor model.
        """
        m = tree.DecisionTreeRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
