"""Defines the decision tree regressor proxy class."""

import base64
import pickle
from typing import Any, Dict, List, Union

import numpy as np
from pydantic import BeforeValidator, ConfigDict, NonNegativeFloat, PlainSerializer
from sklearn import tree
from typing_extensions import Annotated

from nextmv.base_model import BaseModel
from nextmv.ndarray import ndarray

Tree = Annotated[
    tree._tree.Tree,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: base64.b64encode(pickle.dumps(x))),
]


class DecisionTreeRegressor(BaseModel, tree.DecisionTreeRegressor):
    """Decision Tree Regressor scikit-learn model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Parameters
    criterion: str = "squared_error"
    """The function to measure the quality of a split."""
    splitter: str = "best"
    """The strategy used to choose the split at each node."""
    max_depth: int = None
    """The maximum depth of the tree."""
    min_samples_split: Union[int, float] = 2
    """The minimum number of samples required to split an internal node."""
    min_samples_leaf: Union[int, float] = 1
    """The minimum number of samples required to be at a leaf node."""
    min_weight_fraction_leaf: float = 0.0
    """The minimum weighted fraction of the sum total of weights (of all the
    input samples) required to be at a leaf node."""
    max_features: Union[int, float, str] = None
    """The number of features to consider when looking for the best split."""
    random_state: Union[int, np.random.RandomState] = None
    """Controls the randomness of the estimator."""
    max_leaf_nodes: int = None
    """Grow a tree with max_leaf_nodes in best-first fashion."""
    min_impurity_decrease: float = 0.0
    """A node will be split if this split induces a decrease of the impurity
    greater than or equal to this value."""
    ccp_alpha: NonNegativeFloat = 0.0
    """Complexity parameter used for Minimal Cost-Complexity Pruning."""
    monotonic_cst: List[int] = None
    """Indicates the monotonicity constraint to enforce on each feature."""

    # Attributes
    feature_importances_: ndarray = None  # type: ignore
    """Return the feature importances."""
    max_features_: int = 0
    """The inferred value of max_features.."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None  # type: ignore
    """Names of features seen during fit. Defined only when X has feature names
    that are all strings."""
    n_outputs_: int = 0
    "The number of outputs when fit is performed."
    tree_: Tree = None  # type: ignore
    """The underlying Tree object."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates a Decision Tree Regressor from a dict."""

        if "tree_" in data:
            data["tree_"] = pickle.loads(base64.b64decode(data["tree_"]))

        return super().from_dict(data)
