"""Defines sklearn.dummy solution interoperability."""

import numpy as np
from pydantic import BaseModel, ConfigDict
from sklearn import dummy

from ..ndarray import ndarray


class DummyRegressorSolution(BaseModel):
    """Dummy Regressor scikit-learn model representation."""

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
    def from_dict(cls, data: dict[str, any]) -> "DummyRegressorSolution":
        """
        Creates a DummyRegressorSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing the model attributes.

        Returns
        -------
        DummyRegressorSolution
            Instance of DummyRegressorSolution.
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

        Parameters
        ----------
        model : DummyRegressor
            scikit-learn DummyRegressor model.

        Returns
        -------
        DummyRegressorSolution
            Instance of DummyRegressor
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

        Returns
        -------
        DummyRegressor
            scikit-learn DummyRegressor model.
        """
        m = dummy.DummyRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])

        return m
