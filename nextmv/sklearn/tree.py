"""Defines decision tree regressor interoperability classes."""

import base64
import pickle
from typing import Any, Dict, Iterable

from pydantic import BeforeValidator, ConfigDict, PlainSerializer
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor
from typing_extensions import Annotated

from nextmv import base_model, output
from nextmv.numpy import ndarray, ndarray_from_list, ndarray_to_list
from nextmv.options import Options
from nextmv.options import Parameter as P

Tree = Annotated[
    tree._tree.Tree,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]


DECISION_TREE_REGRESSOR_PARAMETERS = (
    P(
        "criterion",
        str,
        choices=["squared_error", "friedman_mse", "absolute_error", "poisson"],
        description="The function to measure the quality of a split.",
    ),
    P("splitter", str, choices=["best", "random"], description="The strategy used to choose the split at each node."),
    P("max_depth", int, description="The maximum depth of the tree."),
    P("min_samples_split", int, description="The minimum number of samples required to split an internal node."),
    P("min_samples_leaf", int, description="The minimum number of samples required to be at a leaf node."),
    P(
        "min_weight_fraction_leaf",
        float,
        description="The minimum weighted fraction of the sum total of weights required to be at a leaf node.",
    ),
    P("max_features", int, description="The number of features to consider when looking for the best split."),
    P("random_state", int, description="Controls the randomness of the estimator."),
    P("max_leaf_nodes", int, description="Grow a tree with max_leaf_nodes in best-first fashion."),
    P(
        "min_impurity_decrease",
        float,
        description="A node will be split if this split induces a decrease of the impurity #.",
    ),
    P("ccp_alpha", float, description="Complexity parameter used for Minimal Cost-Complexity Pruning."),
)


class DecisionTreeRegressorOptions(Options):
    """Default options for scikit-learn Decision Tree Regressor models"""

    def __init__(self, *parameters: P):
        """Initializes options for a scikit-learn Decision Tree Regressor model."""
        return super().__init__(
            *DECISION_TREE_REGRESSOR_PARAMETERS,
            *parameters,
        )

    def to_dict(self):
        return {k: v for k, v in super().to_dict().items() if v is not None}

    def to_model(self):
        """Instantiates a Decision Tree Regressor model from options."""
        names = {p.name for p in DECISION_TREE_REGRESSOR_PARAMETERS}
        kwds = {k: v for k, v in self.to_dict().items() if k in names if v is not None}
        return DecisionTreeRegressor(**kwds)


class DecisionTreeRegressorSolution(base_model.BaseModel):
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
    "The number of outputs when fit is performed."
    tree_: Tree = None  # type: ignore
    """The underlying Tree object."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates a DecisionTreeRegressor object from a dict."""

        if "tree_" in data:
            data["tree_"] = pickle.loads(base64.b64decode(data["tree_"]))

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = ndarray_from_list(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: DecisionTreeRegressor):
        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_model(self):
        m = DecisionTreeRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])
        return m


class DecisionTreeRegressorResultStatistics(output.ResultStatistics):
    """Statistics about a specific Decision Tree Regressor result."""

    @classmethod
    def from_model(
        cls,
        model: DecisionTreeRegressor,
        X: Iterable,
        y: Iterable,
        sample_weight: float = None,
        *args,
        **kwds,
    ):
        custom = {
            "depth": model.get_depth(),
            "feature_importances_": ndarray_to_list(model.feature_importances_),
            "n_leaves": int(model.get_n_leaves()),
            "score": model.score(X, y, sample_weight),
        }
        if sample_weight is not None:
            custom["sample_weight"] = sample_weight
        custom.update(kwds.get("custom", {}))
        kwds["custom"] = custom

        return cls(*args, **kwds)
