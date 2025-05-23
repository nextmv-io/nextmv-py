"""Defines sklearn.ensemble options interoperability.

This module provides classes to handle scikit-learn ensemble model options for integration with Nextmv.

Classes
-------
GradientBoostingRegressorOptions
    Options wrapper for sklearn.ensemble.GradientBoostingRegressor.
RandomForestRegressorOptions
    Options wrapper for sklearn.ensemble.RandomForestRegressor.

Variables
---------
GRADIENT_BOOSTING_REGRESSOR_PARAMETERS
    List of option parameters for GradientBoostingRegressor.
RANDOM_FOREST_REGRESSOR_PARAMETERS
    List of option parameters for RandomForestRegressor.
"""

import nextmv

GRADIENT_BOOSTING_REGRESSOR_PARAMETERS = [
    nextmv.Option(
        name="loss",
        option_type=str,
        choices=["squared_error", "absolute_error", "huber", "quantile"],
        description="Loss function to be optimized.",
    ),
    nextmv.Option(
        name="learning_rate",
        option_type=float,
        description="Learning rate shrinks the contribution of each tree by learning_rate.",
    ),
    nextmv.Option(
        name="n_estimators",
        option_type=int,
        description="The number of boosting stages to perform.",
    ),
    nextmv.Option(
        name="subsample",
        option_type=float,
        description="The fraction of samples to be used for fitting the individual base learners.",
    ),
    nextmv.Option(
        name="criterion",
        option_type=str,
        choices=["friedman_mse", "squared_error"],
        description="The function to measure the quality of a split.",
    ),
    nextmv.Option(
        name="min_samples_split",
        option_type=int,
        description="The minimum number of samples required to split an internal node.",
    ),
    nextmv.Option(
        name="min_samples_leaf",
        option_type=int,
        description="The minimum number of samples required to be at a leaf node.",
    ),
    nextmv.Option(
        name="min_weight_fraction_leaf",
        option_type=float,
        description="The minimum weighted fraction of the sum total of weights required to be at a leaf node.",
    ),
    nextmv.Option(
        name="max_depth",
        option_type=int,
        description="Maximum depth of the individual regression estimators.",
    ),
    nextmv.Option(
        name="min_impurity_decrease",
        option_type=float,
        description="A node will be split if this split induces a decrease of the impurity greater than "
        "or equal to this value.",
    ),
    nextmv.Option(
        name="random_state",
        option_type=int,
        description="Controls the random seed given to each Tree estimator at each boosting iteration.",
    ),
    nextmv.Option(
        name="max_features",
        option_type=int,
        description="The number of features to consider when looking for the best split.",
    ),
    nextmv.Option(
        name="alpha",
        option_type=float,
        description="The alpha-quantile of the huber loss function and the quantile loss function.",
    ),
    nextmv.Option(
        name="max_leaf_nodes",
        option_type=int,
        description="Grow trees with max_leaf_nodes in best-first fashion.",
    ),
    nextmv.Option(
        name="warm_start",
        option_type=bool,
        description="When set to True, reuse the solution of the previous call to fit and add more estimators "
        "to the ensemble, otherwise, just erase the previous solution.",
    ),
    nextmv.Option(
        name="validation_fraction",
        option_type=float,
        description="The proportion of training data to set aside as validation set for early stopping.",
    ),
    nextmv.Option(
        name="n_iter_no_change",
        option_type=int,
        description="n_iter_no_change is used to decide if early stopping will be used to terminate training "
        "when validation score is not improving.",
    ),
    nextmv.Option(
        name="tol",
        option_type=float,
        description="Tolerance for the early stopping.",
    ),
    nextmv.Option(
        name="ccp_alpha",
        option_type=float,
        description="Complexity parameter used for Minimal Cost-Complexity Pruning.",
    ),
]
"""
Parameters for scikit-learn's GradientBoostingRegressor.

You can import the `GRADIENT_BOOSTING_REGRESSOR_PARAMETERS` constant directly
from `ensemble`:

```python
from nextmv_sklearn.ensemble import GRADIENT_BOOSTING_REGRESSOR_PARAMETERS
```

This constant defines all available parameters that can be configured for the
scikit-learn GradientBoostingRegressor model through Nextmv options system.

See Also
--------
sklearn.ensemble.GradientBoostingRegressor : The scikit-learn class this configures.
GradientBoostingRegressorOptions : Class that uses these parameters.
"""


class GradientBoostingRegressorOptions:
    """Options for the sklearn.ensemble.GradientBoostingRegressor.

    You can import the `GradientBoostingRegressorOptions` class directly from `ensemble`:

    ```python
    from nextmv_sklearn.ensemble import GradientBoostingRegressorOptions
    ```

    This class provides configuration options for scikit-learn's GradientBoostingRegressor,
    allowing integration with Nextmv's options system. It encapsulates all parameters
    available for the scikit-learn implementation.

    Attributes
    ----------
    params : list
        List of Nextmv options parameters for GradientBoostingRegressor configuration.

    Examples
    --------
    >>> from nextmv_sklearn.ensemble import GradientBoostingRegressorOptions
    >>> options = GradientBoostingRegressorOptions()
    >>> nextmv_options = options.to_nextmv()
    """

    def __init__(self):
        """Initialize GradientBoostingRegressorOptions.

        Sets up the parameters from the predefined list of GradientBoostingRegressor
        parameters.
        """
        self.params = GRADIENT_BOOSTING_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object.

        Transforms the internal parameters into a Nextmv options object that can be
        used for configuration and command-line parsing.

        Returns
        -------
        nextmv.Options
            A Nextmv options object containing all parameters for the GradientBoostingRegressor.
        """

        return nextmv.Options(*self.params)


RANDOM_FOREST_REGRESSOR_PARAMETERS = [
    nextmv.Option(
        name="n_estimators",
        option_type=int,
        description="The number of trees in the forest.",
    ),
    nextmv.Option(
        name="criterion",
        option_type=str,
        choices=["squared_error", "absolute_error", "friedman_mse", "poisson"],
        description="The function to measure the quality of a split.",
    ),
    nextmv.Option(
        name="max_depth",
        option_type=int,
        description="The maximum depth of the tree.",
    ),
    nextmv.Option(
        name="min_samples_split",
        option_type=int,
        description="The minimum number of samples required to split an internal node.",
    ),
    nextmv.Option(
        name="min_samples_leaf",
        option_type=int,
        description="The minimum number of samples required to be at a leaf node.",
    ),
    nextmv.Option(
        name="min_weight_fraction_leaf",
        option_type=float,
        description="The minimum weighted fraction of the sum total of weights required to be at a leaf node.",
    ),
    nextmv.Option(
        name="max_features",
        option_type=int,
        description="The number of features to consider when looking for the best split.",
    ),
    nextmv.Option(
        name="max_leaf_nodes",
        option_type=int,
        description="Grow trees with max_leaf_nodes in best-first fashion.",
    ),
    nextmv.Option(
        name="min_impurity_decrease",
        option_type=float,
        description="A node will be split if this split induces a decrease of the impurity greater than or "
        "equal to this value.",
    ),
    nextmv.Option(
        name="bootstrap",
        option_type=bool,
        description="Whether bootstrap samples are used when building trees.",
    ),
    nextmv.Option(
        name="oob_score",
        option_type=bool,
        description="Whether to use out-of-bag samples to estimate the generalization score.",
    ),
    nextmv.Option(
        name="n_jobs",
        option_type=int,
        description="The number of jobs to run in parallel.",
    ),
    nextmv.Option(
        name="random_state",
        option_type=int,
        description="Controls both the randomness of the bootstrapping of the samples used when building "
        "trees and the sampling of the features.",
    ),
    nextmv.Option(
        name="verbose",
        option_type=int,
        description="Controls the verbosity when fitting and predicting.",
    ),
    nextmv.Option(
        name="warm_start",
        option_type=bool,
        description="When set to True, reuse the solution of the previous call to fit and add more estimators "
        "to the ensemble, otherwise, just erase the previous solution.",
    ),
    nextmv.Option(
        name="ccp_alpha",
        option_type=float,
        description="Complexity parameter used for Minimal Cost-Complexity Pruning.",
    ),
    nextmv.Option(
        name="max_samples",
        option_type=int,
        description="If bootstrap is True, the number of samples to draw from X to train each base estimator.",
    ),
    nextmv.Option(
        name="monotonic_cst",
        option_type=int,
        description="Indicates the monotonicity constraint to enforce on each feature.",
    ),
]
"""
Parameters for scikit-learn's RandomForestRegressor.

You can import the `RANDOM_FOREST_REGRESSOR_PARAMETERS` constant directly from `ensemble`:

```python
from nextmv_sklearn.ensemble import RANDOM_FOREST_REGRESSOR_PARAMETERS
```

This constant defines all available parameters that can be configured for the
scikit-learn RandomForestRegressor model through Nextmv options system.

See Also
--------
sklearn.ensemble.RandomForestRegressor : The scikit-learn class this configures.
RandomForestRegressorOptions : Class that uses these parameters.
"""


class RandomForestRegressorOptions:
    """Options for the sklearn.ensemble.RandomForestRegressor.

    You can import the `RandomForestRegressorOptions` class directly from `ensemble`:

    ```python
    from nextmv_sklearn.ensemble import RandomForestRegressorOptions
    ```

    This class provides configuration options for scikit-learn's RandomForestRegressor,
    allowing integration with Nextmv's options system. It encapsulates all parameters
    available for the scikit-learn implementation.

    Attributes
    ----------
    params : list
        List of Nextmv options parameters for RandomForestRegressor configuration.

    Examples
    --------
    >>> from nextmv_sklearn.ensemble import RandomForestRegressorOptions
    >>> options = RandomForestRegressorOptions()
    >>> nextmv_options = options.to_nextmv()
    """

    def __init__(self):
        """Initialize RandomForestRegressorOptions.

        Sets up the parameters from the predefined list of RandomForestRegressor
        parameters.
        """
        self.params = RANDOM_FOREST_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object.

        Transforms the internal parameters into a Nextmv options object that can be
        used for configuration and command-line parsing.

        Returns
        -------
        nextmv.Options
            A Nextmv options object containing all parameters for the RandomForestRegressor.
        """

        return nextmv.Options(*self.params)
