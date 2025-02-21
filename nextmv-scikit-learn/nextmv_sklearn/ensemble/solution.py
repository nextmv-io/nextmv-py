"""Defines sklearn.ensemble solution interoperability."""

import base64
import pickle
from typing import Annotated, Any

import numpy as np
from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer
from sklearn import ensemble

from ..dummy import DummyRegressorSolution
from ..ndarray import ndarray
from ..tree import DecisionTreeRegressorSolution

Loss = Annotated[
    Any,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]


class GradientBoostingRegressorSolution(BaseModel):
    """Gradient Boosting Regressor scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    n_estimators_: int = 0
    """The number of estimators as selected by early stopping (if
    n_iter_no_change is specified). Otherwise it is set to n_estimators."""
    n_trees_per_iteration_: int = 0
    """The number of trees that are built at each iteration. For regressors,
    this is always 1."""
    oob_improvement_: ndarray = None
    """The improvement in loss on the out-of-bag samples relative to the
    previous iteration."""
    oob_scores_: ndarray = None
    """The full history of the loss values on the out-of-bag samples. Only
    available if subsample < 1.0."""
    oob_score_: float = 0.0
    """The last value of the loss on the out-of-bag samples."""
    train_score_: ndarray = None
    """The i-th score train_score_[i] is the loss of the model at iteration i on
    the in-bag sample."""
    init_: DummyRegressorSolution = None
    """The estimator that provides the initial predictions."""
    estimators_: list[DecisionTreeRegressorSolution] = None
    """The collection of fitted sub-estimators."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit."""
    max_features_: int = 0
    """The inferred value of max_features."""

    # Internal but required to load the model.
    loss: Loss = None

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "GradientBoostingRegressorSolution":
        """
        Creates a GradientBoostingRegressorSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing the model attributes.

        Returns
        -------
        GradientBoostingRegressorSolution
            Instance of GradientBoostingRegressorSolution.
        """

        if "init_" in data:
            data["init_"] = DummyRegressorSolution.from_dict(data["init_"])

        if "estimators_" in data:
            data["estimators_"] = [DecisionTreeRegressorSolution.from_dict(e) for e in data["estimators_"]]

        if "_loss" in data:
            data["loss"] = pickle.loads(base64.b64decode(data["loss"]))

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = np.array(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: ensemble.GradientBoostingRegressor) -> "GradientBoostingRegressorSolution":
        """
        Creates a GradientBoostingRegressorSolution instance from a scikit-learn
        GradientBoostingRegressor model.

        Parameters
        ----------
        model : GradientBoostingRegressor
            scikit-learn GradientBoostingRegressor model.

        Returns
        -------
        GradientBoostingRegressorSolution
            Instance of GradientBoostingRegressor
        """

        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        if "init_" in data:
            data["init_"] = DummyRegressorSolution.from_model(data["init_"])

        if "estimators_" in data:
            data["estimators_"] = [DecisionTreeRegressorSolution.from_model(x[0]) for x in data["estimators_"]]

        data["loss"] = getattr(model, "_loss", None)

        return cls(**data)

    def to_dict(self):
        """Convert a data model instance to a dict with associated class
        info."""

        d = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        if self.estimators_ is not None:
            d["estimators_"] = [x.model_dump(mode="json", exclude_none=True, by_alias=True) for x in self.estimators_]

        t = type(self)
        return {
            "class": {
                "module": t.__module__,
                "name": t.__name__,
            },
            "attributes": d,
        }

    def to_model(self) -> ensemble.GradientBoostingRegressor:
        """
        Transforms the GradientBoostingRegressorSolution instance into a scikit-learn
        GradientBoostingRegressor model.

        Returns
        -------
        GradientBoostingRegressor
            scikit-learn GradientBoostingRegressor model.
        """

        m = ensemble.GradientBoostingRegressor()
        for key in self.model_fields:
            if key == "init_":
                setattr(m, key, self.__dict__[key].to_model())
            elif key == "estimators_":
                estimators = [np.array([x.to_model()]) for x in self.__dict__[key]]
                setattr(m, key, np.array(estimators))
            else:
                setattr(m, key, self.__dict__[key])

        m._loss = pickle.loads(base64.b64decode(self.loss))

        return m


class RandomForestRegressorSolution(BaseModel):
    """Random Forest Regressor scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    estimator_: DecisionTreeRegressorSolution = None
    """The child estimator template used to create the collection of fitted
    sub-estimators."""
    estimators_: list[DecisionTreeRegressorSolution] = None
    """The collection of fitted sub-estimators."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit."""
    n_outputs_: int = 0
    """The number of outputs when fit is performed."""
    oob_score_: float = 0.0
    """Score of the training dataset obtained using an out-of-bag estimate."""
    oob_prediction_: ndarray = None
    """Prediction computed with out-of-bag estimate on the training set."""

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> "RandomForestRegressorSolution":
        """
        Creates a RandomForestRegressorSolution instance from a dictionary.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing the model attributes.

        Returns
        -------
        RandomForestRegressorSolution
            Instance of RandomForestRegressorSolution.
        """

        if "estimator_" in data:
            data["estimator_"] = DecisionTreeRegressorSolution.from_dict(data["estimator_"])

        if "estimators_" in data:
            data["estimators_"] = [DecisionTreeRegressorSolution.from_dict(e) for e in data["estimators_"]]

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = np.array(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: ensemble.RandomForestRegressor) -> "RandomForestRegressorSolution":
        """
        Creates a RandomForestRegressorSolution instance from a scikit-learn
        RandomForestRegressor model.

        Parameters
        ----------
        model : RandomForestRegressor
            scikit-learn RandomForestRegressor model.

        Returns
        -------
        RandomForestRegressorSolution
            Instance of RandomForestRegressor
        """

        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        if "estimator_" in data:
            data["estimator_"] = DecisionTreeRegressorSolution.from_model(data["estimator_"])

        if "estimators_" in data:
            data["estimators_"] = [DecisionTreeRegressorSolution.from_model(x) for x in data["estimators_"]]

        return cls(**data)

    def to_dict(self):
        """Convert a data model instance to a dict with associated class
        info."""

        d = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        if self.estimator_ is not None:
            d["estimator_"] = self.estimator_.model_dump(mode="json", exclude_none=True, by_alias=True)
        if self.estimators_ is not None:
            d["estimators_"] = [x.model_dump(mode="json", exclude_none=True, by_alias=True) for x in self.estimators_]

        t = type(self)
        return {
            "class": {
                "module": t.__module__,
                "name": t.__name__,
            },
            "attributes": d,
        }

    def to_model(self) -> ensemble.RandomForestRegressor:
        """
        Transforms the RandomForestRegressorSolution instance into a scikit-learn
        RandomForestRegressor model.

        Returns
        -------
        RandomForestRegressor
            scikit-learn RandomForestRegressor model.
        """

        m = ensemble.RandomForestRegressor()
        for key in self.model_fields:
            if key == "estimator_":
                setattr(m, key, self.__dict__[key].to_model())
            elif key == "estimators_":
                estimators = [x.to_model() for x in self.__dict__[key]]
                setattr(m, key, np.array(estimators))
                m.n_estimators = len(estimators)
            else:
                setattr(m, key, self.__dict__[key])

        return m
