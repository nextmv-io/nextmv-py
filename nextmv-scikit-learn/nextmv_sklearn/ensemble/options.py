"""Defines sklearn.ensemble options interoperability."""

import nextmv

GRADIENT_BOOSTING_REGRESSOR_PARAMETERS = [
    nextmv.Parameter(
        name="loss",
        param_type=str,
        choices=["squared_error", "absolute_error", "huber", "quantile"],
        description="Loss function to be optimized.",
    ),
    nextmv.Parameter(
        name="learning_rate",
        param_type=float,
        description="Learning rate shrinks the contribution of each tree by learning_rate.",
    ),
    nextmv.Parameter(
        name="n_estimators",
        param_type=int,
        description="The number of boosting stages to perform.",
    ),
    nextmv.Parameter(
        name="subsample",
        param_type=float,
        description="The fraction of samples to be used for fitting the individual base learners.",
    ),
    nextmv.Parameter(
        name="criterion",
        param_type=str,
        choices=["friedman_mse", "squared_error"],
        description="The function to measure the quality of a split.",
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
        name="max_depth",
        param_type=int,
        description="Maximum depth of the individual regression estimators.",
    ),
    nextmv.Parameter(
        name="min_impurity_decrease",
        param_type=float,
        description="A node will be split if this split induces a decrease of the impurity greater than "
        "or equal to this value.",
    ),
    nextmv.Parameter(
        name="random_state",
        param_type=int,
        description="Controls the random seed given to each Tree estimator at each boosting iteration.",
    ),
    nextmv.Parameter(
        name="max_features",
        param_type=int,
        description="The number of features to consider when looking for the best split.",
    ),
    nextmv.Parameter(
        name="alpha",
        param_type=float,
        description="The alpha-quantile of the huber loss function and the quantile loss function.",
    ),
    nextmv.Parameter(
        name="max_leaf_nodes",
        param_type=int,
        description="Grow trees with max_leaf_nodes in best-first fashion.",
    ),
    nextmv.Parameter(
        name="warm_start",
        param_type=bool,
        description="When set to True, reuse the solution of the previous call to fit and add more estimators "
        "to the ensemble, otherwise, just erase the previous solution.",
    ),
    nextmv.Parameter(
        name="validation_fraction",
        param_type=float,
        description="The proportion of training data to set aside as validation set for early stopping.",
    ),
    nextmv.Parameter(
        name="n_iter_no_change",
        param_type=int,
        description="n_iter_no_change is used to decide if early stopping will be used to terminate training "
        "when validation score is not improving.",
    ),
    nextmv.Parameter(
        name="tol",
        param_type=float,
        description="Tolerance for the early stopping.",
    ),
    nextmv.Parameter(
        name="ccp_alpha",
        param_type=float,
        description="Complexity parameter used for Minimal Cost-Complexity Pruning.",
    ),
]


class GradientBoostingRegressorOptions:
    """Options for the sklearn.ensemble.GradientBoostingRegressor."""

    def __init__(self):
        self.params = GRADIENT_BOOSTING_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)


RANDOM_FOREST_REGRESSOR_PARAMETERS = [
    nextmv.Parameter(
        name="n_estimators",
        param_type=int,
        description="The number of trees in the forest.",
    ),
    nextmv.Parameter(
        name="criterion",
        param_type=str,
        choices=["squared_error", "absolute_error", "friedman_mse", "poisson"],
        description="The function to measure the quality of a split.",
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
        name="max_leaf_nodes",
        param_type=int,
        description="Grow trees with max_leaf_nodes in best-first fashion.",
    ),
    nextmv.Parameter(
        name="min_impurity_decrease",
        param_type=float,
        description="A node will be split if this split induces a decrease of the impurity greater than or "
        "equal to this value.",
    ),
    nextmv.Parameter(
        name="bootstrap",
        param_type=bool,
        description="Whether bootstrap samples are used when building trees.",
    ),
    nextmv.Parameter(
        name="oob_score",
        param_type=bool,
        description="Whether to use out-of-bag samples to estimate the generalization score.",
    ),
    nextmv.Parameter(
        name="n_jobs",
        param_type=int,
        description="The number of jobs to run in parallel.",
    ),
    nextmv.Parameter(
        name="random_state",
        param_type=int,
        description="Controls both the randomness of the bootstrapping of the samples used when building "
        "trees and the sampling of the features.",
    ),
    nextmv.Parameter(
        name="verbose",
        param_type=int,
        description="Controls the verbosity when fitting and predicting.",
    ),
    nextmv.Parameter(
        name="warm_start",
        param_type=bool,
        description="When set to True, reuse the solution of the previous call to fit and add more estimators "
        "to the ensemble, otherwise, just erase the previous solution.",
    ),
    nextmv.Parameter(
        name="ccp_alpha",
        param_type=float,
        description="Complexity parameter used for Minimal Cost-Complexity Pruning.",
    ),
    nextmv.Parameter(
        name="max_samples",
        param_type=int,
        description="If bootstrap is True, the number of samples to draw from X to train each base estimator.",
    ),
    nextmv.Parameter(
        name="monotonic_cst",
        param_type=int,
        description="Indicates the monotonicity constraint to enforce on each feature.",
    ),
]


class RandomForestRegressorOptions:
    """Options for the sklearn.ensemble.RandomForestRegressor."""

    def __init__(self):
        self.params = RANDOM_FOREST_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
