"""Defines sklearn.tree options interoperability.

This module provides functionality for interfacing with scikit-learn's tree-based
algorithms within the Nextmv framework. It includes classes for configuring
decision tree regressors.

Classes
-------
DecisionTreeRegressorOptions
    Options wrapper for scikit-learn's DecisionTreeRegressor.
"""

import nextmv

DECISION_TREE_REGRESSOR_PARAMETERS = [
    nextmv.Option(
        name="criterion",
        option_type=str,
        choices=["squared_error", "friedman_mse", "absolute_error", "poisson"],
        description="The function to measure the quality of a split.",
        default="squared_error",
    ),
    nextmv.Option(
        name="splitter",
        option_type=str,
        choices=["best", "random"],
        description="The strategy used to choose the split at each node.",
        default="best",
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
        name="random_state",
        option_type=int,
        description="Controls the randomness of the estimator.",
    ),
    nextmv.Option(
        name="max_leaf_nodes",
        option_type=int,
        description="Grow a tree with max_leaf_nodes in best-first fashion.",
    ),
    nextmv.Option(
        name="min_impurity_decrease",
        option_type=float,
        description="A node will be split if this split induces a decrease of the impurity #.",
    ),
    nextmv.Option(
        name="ccp_alpha",
        option_type=float,
        description="Complexity parameter used for Minimal Cost-Complexity Pruning.",
    ),
]
"""
List of Nextmv Option objects for configuring a DecisionTreeRegressor.

Each option corresponds to a hyperparameter of the scikit-learn DecisionTreeRegressor,
providing a consistent interface for setting up decision tree regression models
within the Nextmv ecosystem.

You can import the `DECISION_TREE_REGRESSOR_PARAMETERS` directly from `tree`:

```python
from nextmv_sklearn.tree import DECISION_TREE_REGRESSOR_PARAMETERS
```
"""


class DecisionTreeRegressorOptions:
    """Options for the sklearn.tree.DecisionTreeRegressor.

    You can import the `DecisionTreeRegressorOptions` class directly from `tree`:

    ```python
    from nextmv_sklearn.tree import DecisionTreeRegressorOptions
    ```

    A wrapper class for scikit-learn's DecisionTreeRegressor hyperparameters,
    providing a consistent interface for configuring decision tree regression
    models within the Nextmv ecosystem.

    Attributes
    ----------
    params : list
        List of Nextmv Option objects corresponding to DecisionTreeRegressor parameters.

    Examples
    --------
    >>> from nextmv_sklearn.tree import DecisionTreeRegressorOptions
    >>> options = DecisionTreeRegressorOptions()
    >>> nextmv_options = options.to_nextmv()
    """

    def __init__(self):
        """Initialize a DecisionTreeRegressorOptions instance.

        Configures the default parameters for a decision tree regressor.
        """
        self.params = DECISION_TREE_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object.

        Creates a Nextmv Options instance from the configured decision tree
        regressor parameters.

        Returns
        -------
        nextmv.Options
            A Nextmv options object containing all decision tree regressor parameters.

        Examples
        --------
        >>> options = DecisionTreeRegressorOptions()
        >>> nextmv_options = options.to_nextmv()
        >>> # Access options as CLI arguments
        >>> # python script.py --criterion squared_error --max_depth 5
        """

        return nextmv.Options(*self.params)
