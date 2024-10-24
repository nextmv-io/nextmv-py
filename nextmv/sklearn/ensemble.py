"""Defines gradient boosting regressor interoperability classes."""

import base64
import pickle
from typing import Any, Dict, Iterable, List

from pydantic import BeforeValidator, ConfigDict, PlainSerializer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from typing_extensions import Annotated

from nextmv import base_model, output
from nextmv.numpy import ndarray, ndarray_from_list, ndarray_to_list
from nextmv.options import Options
from nextmv.options import Parameter as P

from .dummy import DummyRegressorSolution
from .tree import DecisionTreeRegressorSolution

Loss = Annotated[
    Any,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]

GRADIENT_BOOSTING_REGRESSOR_PARAMETERS = (
    P(
        "loss",
        str,
        choices=["squared_error", "absolute_error", "huber", "quantile"],
        description="Loss function to be optimized.",
    ),
    P("learning_rate", float, description="Learning rate shrinks the contribution of each tree by learning_rate."),
    P("n_estimators", int, description="The number of boosting stages to perform."),
    P("subsample", float, description="The fraction of samples to be used for fitting the individual base learners."),
    P(
        "criterion",
        str,
        choices=["friedman_mse", "squared_error"],
        description="The function to measure the quality of a split.",
    ),
    P("min_samples_split", int, description="The minimum number of samples required to split an internal node."),
    P("min_samples_leaf", int, description="The minimum number of samples required to be at a leaf node."),
    P(
        "min_weight_fraction_leaf",
        float,
        description="The minimum weighted fraction of the sum total of weights required to be at a leaf node.",
    ),
    P("max_depth", int, description="Maximum depth of the individual regression estimators."),
    P(
        "min_impurity_decrease",
        float,
        description="""A node will be split if this split induces a decrease of the impurity """
        """greater than or equal to this value.""",
    ),
    P(
        "random_state",
        int,
        description="Controls the random seed given to each Tree estimator at each boosting iteration.",
    ),
    P(
        "max_features",
        int,
        description="The number of features to consider when looking for the best split.",
    ),
    P("alpha", float, description="The alpha-quantile of the huber loss function and the quantile loss function."),
    P("max_leaf_nodes", int, description="Grow trees with max_leaf_nodes in best-first fashion."),
    P(
        "warm_start",
        bool,
        description="""When set to True, reuse the solution of the previous call
        to fit and add more estimators to the ensemble, otherwise, just erase
        the previous solution.""",
    ),
    P(
        "validation_fraction",
        float,
        description="The proportion of training data to set aside as validation set for early stopping.",
    ),
    P(
        "n_iter_no_change",
        int,
        description="""n_iter_no_change is used to decide if early stopping will
        be used to terminate training when validation score is not
        improving.""",
    ),
    P("tol", float, description="Tolerance for the early stopping."),
    P("ccp_alpha", float, description="Complexity parameter used for Minimal Cost-Complexity Pruning."),
)


class GradientBoostingRegressorOptions(Options):
    """Default options for scikit-learn Gradient Boosting Regressor models"""

    def __init__(self, *parameters: P):
        """Initializes options for a scikit-learn Gradient Boosting Regressor model."""
        return super().__init__(
            *GRADIENT_BOOSTING_REGRESSOR_PARAMETERS,
            *parameters,
        )

    def to_dict(self):
        return {k: v for k, v in super().to_dict().items() if v is not None}

    def to_model(self):
        """Instantiates a Gradient Boosting Regressor model from options."""
        names = {p.name for p in GRADIENT_BOOSTING_REGRESSOR_PARAMETERS}
        kwds = {k: v for k, v in self.to_dict().items() if k in names if v is not None}
        return GradientBoostingRegressor(**kwds)


class GradientBoostingRegressorSolution(base_model.BaseModel):
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
    estimators_: List[DecisionTreeRegressorSolution] = None
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
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates a GradientBoostingRegressorSolution from a dict."""

        if "init_" in data:
            data["init_"] = DummyRegressorSolution.from_dict(data["init_"])

        if "estimators_" in data:
            data["estimators_"] = [DecisionTreeRegressorSolution.from_dict(e) for e in data["estimators_"]]

        if "_loss" in data:
            data["loss"] = pickle.loads(base64.b64decode(data["loss"]))

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = ndarray_from_list(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: GradientBoostingRegressor):
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
        d = {k: v for k, v in super().to_dict().items() if v is not None}
        if self.estimators_ is not None:
            d["estimators_"] = [x.to_dict() for x in self.estimators_]
        return d

    def to_model(self):
        m = GradientBoostingRegressor()
        for key in self.model_fields:
            if key == "init_":
                setattr(m, key, self.__dict__[key].to_model())
            elif key == "estimators_":
                estimators = [ndarray_from_list([x.to_model()]) for x in self.__dict__[key]]
                setattr(m, key, ndarray_from_list(estimators))
            else:
                setattr(m, key, self.__dict__[key])
        m._loss = pickle.loads(base64.b64decode(self.loss))
        return m


class GradientBoostingRegressorResultStatistics(output.ResultStatistics):
    """Statistics about a specific Gradient Boosting Regressor result."""

    @classmethod
    def from_model(
        cls,
        model: GradientBoostingRegressor,
        X: Iterable,
        y: Iterable,
        sample_weight: float = None,
        *args,
        **kwds,
    ):
        custom = {
            # "depth": model.get_depth(),
            "feature_importances_": ndarray_to_list(model.feature_importances_),
            # "n_leaves": int(model.get_n_leaves()),
            "score": model.score(X, y, sample_weight),
        }
        if sample_weight is not None:
            custom["sample_weight"] = sample_weight
        custom.update(kwds.get("custom", {}))
        kwds["custom"] = custom

        return cls(*args, **kwds)


RANDOM_FOREST_REGRESSOR_PARAMETERS = (
    P("n_estimators", int, description="The number of trees in the forest."),
    P(
        "criterion",
        str,
        choices=["squared_error", "absolute_error", "friedman_mse", "poisson"],
        description="The function to measure the quality of a split.",
    ),
    P("max_depth", int, description="The maximum depth of the tree."),
    P("min_samples_split", int, description="The minimum number of samples required to split an internal node."),
    P("min_samples_leaf", int, description="The minimum number of samples required to be at a leaf node."),
    P(
        "min_weight_fraction_leaf",
        float,
        description="The minimum weighted fraction of the sum total of weights required to be at a leaf node.",
    ),
    P(
        "max_features",
        int,
        description="The number of features to consider when looking for the best split.",
    ),
    P("max_leaf_nodes", int, description="Grow trees with max_leaf_nodes in best-first fashion."),
    P(
        "min_impurity_decrease",
        float,
        description="""A node will be split if this split induces a decrease of the impurity """
        """greater than or equal to this value.""",
    ),
    P("bootstrap", bool, description="Whether bootstrap samples are used when building trees."),
    P("oob_score", bool, description="Whether to use out-of-bag samples to estimate the generalization score."),
    P("n_jobs", int, description="The number of jobs to run in parallel."),
    P(
        "random_state",
        int,
        description="""Controls both the randomness of the bootstrapping of """
        """the samples used when building trees and the sampling of the features.""",
    ),
    P("verbose", int, description="Controls the verbosity when fitting and predicting."),
    P(
        "warm_start",
        bool,
        description="""When set to True, reuse the solution of the previous """
        """call to fit and add more estimators to the ensemble, otherwise, """
        """just erase the previous solution.""",
    ),
    P("ccp_alpha", float, description="Complexity parameter used for Minimal Cost-Complexity Pruning."),
    P(
        "max_samples",
        int,
        description="""If bootstrap is True, the number of samples to draw """
        """from X to train each base estimator.""",
    ),
    P("monotonic_cst", int, description="Indicates the monotonicity constraint to enforce on each feature."),
)


class RandomForestRegressorOptions(Options):
    """Default options for scikit-learn Random Forest Regressor models"""

    def __init__(self, *parameters: P):
        """Initializes options for a scikit-learn Random Forest Regressor
        model."""
        return super().__init__(
            *RANDOM_FOREST_REGRESSOR_PARAMETERS,
            *parameters,
        )

    def to_dict(self):
        return {k: v for k, v in super().to_dict().items() if v is not None}

    def to_model(self):
        """Instantiates a Random Forest Regressor model from options."""
        names = {p.name for p in RANDOM_FOREST_REGRESSOR_PARAMETERS}
        kwds = {k: v for k, v in self.to_dict().items() if k in names if v is not None}
        return RandomForestRegressor(**kwds)


class RandomForestRegressorSolution(base_model.BaseModel):
    """Random Forest Regressor scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    estimator_: DecisionTreeRegressorSolution = None
    """The child estimator template used to create the collection of fitted
    sub-estimators."""
    estimators_: List[DecisionTreeRegressorSolution] = None
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
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates a RandomForestRegressorSolution from a dict."""

        if "estimator_" in data:
            data["estimator_"] = DecisionTreeRegressorSolution.from_dict(data["estimator_"])

        if "estimators_" in data:
            data["estimators_"] = [DecisionTreeRegressorSolution.from_dict(e) for e in data["estimators_"]]

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = ndarray_from_list(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: RandomForestRegressor):
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
        d = super().to_dict()
        if self.estimator_ is not None:
            d["estimator_"] = self.estimator_.to_dict()
        if self.estimators_ is not None:
            d["estimators_"] = [x.to_dict() for x in self.estimators_]
        return d

    def to_model(self):
        m = RandomForestRegressor()
        for key in self.model_fields:
            if key == "estimator_":
                setattr(m, key, self.__dict__[key].to_model())
            elif key == "estimators_":
                estimators = [x.to_model() for x in self.__dict__[key]]
                setattr(m, key, ndarray_from_list(estimators))
                m.n_estimators = len(estimators)
            else:
                setattr(m, key, self.__dict__[key])
        return m


class RandomForestRegressorResultStatistics(output.ResultStatistics):
    """Statistics about a specific Random Forest Regressor result."""

    @classmethod
    def from_model(
        cls,
        model: RandomForestRegressor,
        X: Iterable,
        y: Iterable,
        sample_weight: float = None,
        *args,
        **kwds,
    ):
        custom = {
            "feature_importances_": ndarray_to_list(model.feature_importances_),
            "score": model.score(X, y, sample_weight),
        }
        if sample_weight is not None:
            custom["sample_weight"] = sample_weight
        custom.update(kwds.get("custom", {}))
        kwds["custom"] = custom

        return cls(*args, **kwds)
