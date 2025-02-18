"""Defines sklearn.tree options interoperability."""

import nextmv

DECISION_TREE_REGRESSOR_PARAMETERS = [
    nextmv.Parameter(
        name="criterion",
        param_type=str,
        choices=["squared_error", "friedman_mse", "absolute_error", "poisson"],
        description="The function to measure the quality of a split.",
        default="squared_error",
    ),
    nextmv.Parameter(
        name="splitter",
        param_type=str,
        choices=["best", "random"],
        description="The strategy used to choose the split at each node.",
        default="best",
    ),
    nextmv.Parameter(
        name="max_depth",
        param_type=int,
        description="The maximum depth of the tree.",
    ),
    nextmv.Parameter(
        name="min_samples_split",
        param_type=int,
        description="The minimum number of samples required to split an internal node.",
    ),
    nextmv.Parameter(
        name="min_samples_leaf",
        param_type=int,
        description="The minimum number of samples required to be at a leaf node.",
    ),
    nextmv.Parameter(
        name="min_weight_fraction_leaf",
        param_type=float,
        description="The minimum weighted fraction of the sum total of weights required to be at a leaf node.",
    ),
    nextmv.Parameter(
        name="max_features",
        param_type=int,
        description="The number of features to consider when looking for the best split.",
    ),
    nextmv.Parameter(
        name="random_state",
        param_type=int,
        description="Controls the randomness of the estimator.",
    ),
    nextmv.Parameter(
        name="max_leaf_nodes",
        param_type=int,
        description="Grow a tree with max_leaf_nodes in best-first fashion.",
    ),
    nextmv.Parameter(
        name="min_impurity_decrease",
        param_type=float,
        description="A node will be split if this split induces a decrease of the impurity #.",
    ),
    nextmv.Parameter(
        name="ccp_alpha",
        param_type=float,
        description="Complexity parameter used for Minimal Cost-Complexity Pruning.",
    ),
]


class DecisionTreeRegressorOptions:
    """Options for the sklearn.tree.DecisionTreeRegressor."""

    def __init__(self):
        self.params = DECISION_TREE_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
