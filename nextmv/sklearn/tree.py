"""Defines decision tree regressor interoperability classes."""

import base64
import pickle
from typing import Any, Dict, Iterable

from pydantic import BeforeValidator, ConfigDict, PlainSerializer
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor
from typing_extensions import Annotated

from nextmv import base_model, options, output
from nextmv.numpy import ndarray, ndarray_from_list, ndarray_to_list

Tree = Annotated[
    tree._tree.Tree,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]


DECISION_TREE_REGRESSOR_PARAMETERS = (
    options.Parameter(
        "criterion",
        str,
        default="squared_error",
        choices=["squared_error", "friedman_mse", "absolute_error", "poisson"],
        description="The function to measure the quality of a split.",
        required=True,
    ),
    options.Parameter(
        "splitter",
        str,
        default="best",
        choices=["best", "random"],
        description="The strategy used to choose the split at each node.",
        required=True,
    ),
    options.Parameter(
        "max_depth",
        int,
        description="The maximum depth of the tree.",
    ),
    options.Parameter(
        "min_samples_split",
        int,
        default=2,
        description="""The minimum number of samples required to split an
        internal node.""",
        required=True,
    ),
    options.Parameter(
        "min_samples_leaf",
        int,
        default=1,
        description="""The minimum number of samples required to be at a leaf
        node.""",
        required=True,
    ),
    options.Parameter(
        "min_weight_fraction_leaf",
        float,
        default=0.0,
        description="""The minimum weighted fraction of the sum total of weights
        (of all the input samples) required to be at a leaf node.""",
        required=True,
    ),
    options.Parameter(
        "max_features",
        int,
        description="""The number of features to consider when looking for the
        best split.""",
    ),
    options.Parameter(
        "random_state",
        int,
        description="Controls the randomness of the estimator.",
    ),
    options.Parameter(
        "max_leaf_nodes",
        int,
        description="Grow a tree with max_leaf_nodes in best-first fashion.",
    ),
    options.Parameter(
        "min_impurity_decrease",
        float,
        default=0.0,
        description="""A node will be split if this split induces a decrease of
        the impurity # greater than or equal to this value.""",
        required=True,
    ),
    options.Parameter(
        "ccp_alpha",
        float,
        default=0.0,
        description="""Complexity parameter used for Minimal Cost-Complexity
        Pruning.""",
        required=True,
    ),
)


class DecisionTreeRegressorOptions(options.Options):
    """Default options for scikit-learn Decision Tree Regressor models"""

    def __init__(self, *parameters: options.Parameter):
        """Initializes options for a scikit-learn Decision Tree Regressor
        model."""
        return super().__init__(
            *DECISION_TREE_REGRESSOR_PARAMETERS,
            *parameters,
        )


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
