"""Defines sklearn.tree models interoperability.

Functions
---------
DecisionTreeRegressor
    Creates a scikit-learn DecisionTreeRegressor from provided options
"""

from sklearn import tree

import nextmv

from .options import DECISION_TREE_REGRESSOR_PARAMETERS


def DecisionTreeRegressor(options: nextmv.Options) -> tree.DecisionTreeRegressor:
    """
    Creates a `sklearn.tree.DecisionTreeRegressor` from the provided options.

    You can import the `DecisionTreeRegressor` function directly from `tree`:

    ```python
    from nextmv_sklearn.tree import DecisionTreeRegressor
    ```

    This function uses the options to create a scikit-learn DecisionTreeRegressor
    model with the specified parameters. It extracts parameter values from the
    Nextmv options object and passes them to the scikit-learn constructor.

    Parameters
    ----------
    options : nextmv.Options
        Options for the DecisionTreeRegressor. Can contain the following parameters:
        - criterion : str, default='squared_error'
            The function to measure the quality of a split.
        - splitter : str, default='best'
            The strategy used to choose the split at each node.
        - max_depth : int, optional
            The maximum depth of the tree.
        - min_samples_split : int, optional
            The minimum number of samples required to split an internal node.
        - min_samples_leaf : int, optional
            The minimum number of samples required to be at a leaf node.
        - min_weight_fraction_leaf : float, optional
            The minimum weighted fraction of the sum total of weights required
            to be at a leaf node.
        - max_features : int, optional
            The number of features to consider when looking for the best split.
        - random_state : int, optional
            Controls the randomness of the estimator.
        - max_leaf_nodes : int, optional
            Grow a tree with max_leaf_nodes in best-first fashion.
        - min_impurity_decrease : float, optional
            A node will be split if this split induces a decrease of the impurity.
        - ccp_alpha : float, optional
            Complexity parameter used for Minimal Cost-Complexity Pruning.

    Returns
    -------
    DecisionTreeRegressor
        A sklearn.tree.DecisionTreeRegressor instance.

    Examples
    --------
    >>> from nextmv_sklearn.tree import DecisionTreeRegressorOptions
    >>> from nextmv_sklearn.tree import DecisionTreeRegressor
    >>>
    >>> # Create options for the regressor
    >>> options = DecisionTreeRegressorOptions().to_nextmv()
    >>>
    >>> # Set specific parameters if needed
    >>> options.set("max_depth", 5)
    >>> options.set("min_samples_split", 2)
    >>>
    >>> # Create the regressor model
    >>> regressor = DecisionTreeRegressor(options)
    >>>
    >>> # Use the regressor with scikit-learn API
    >>> X = [[0, 0], [1, 1], [2, 2], [3, 3]]
    >>> y = [0, 1, 2, 3]
    >>> regressor.fit(X, y)
    >>> regressor.predict([[4, 4]])
    """

    names = {p.name for p in DECISION_TREE_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return tree.DecisionTreeRegressor(**opt_dict)
