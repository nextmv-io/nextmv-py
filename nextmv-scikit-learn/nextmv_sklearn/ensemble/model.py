"""Defines sklearn.ensemble models interoperability.

This module provides wrappers around scikit-learn ensemble models, allowing
them to be created using Nextmv option objects.

Functions
---------
GradientBoostingRegressor
    Creates a sklearn.ensemble.GradientBoostingRegressor from options.
RandomForestRegressor
    Creates a sklearn.ensemble.RandomForestRegressor from options.
"""

from sklearn import ensemble

import nextmv

from .options import GRADIENT_BOOSTING_REGRESSOR_PARAMETERS, RANDOM_FOREST_REGRESSOR_PARAMETERS


def GradientBoostingRegressor(options: nextmv.Options) -> ensemble.GradientBoostingRegressor:
    """
    Creates a `sklearn.ensemble.GradientBoostingRegressor` from the provided
    options.

    You can import the `GradientBoostingRegressor` function directly from `ensemble`:

    ```python
    from nextmv_sklearn.ensemble import GradientBoostingRegressor
    ```

    This function takes a Nextmv Options object and converts it to the appropriate
    parameters for the scikit-learn GradientBoostingRegressor.

    Parameters
    ----------
    options : nextmv.Options
        Options for the GradientBoostingRegressor. Should contain parameters
        defined in GRADIENT_BOOSTING_REGRESSOR_PARAMETERS.

    Returns
    -------
    ensemble.GradientBoostingRegressor
        A sklearn.ensemble.GradientBoostingRegressor instance.

    Examples
    --------
    >>> from nextmv_sklearn.ensemble.options import GradientBoostingRegressorOptions
    >>> options = GradientBoostingRegressorOptions().to_nextmv()
    >>> options.set("n_estimators", 100)
    >>> options.set("learning_rate", 0.1)
    >>> gbr = GradientBoostingRegressor(options)
    """

    names = {p.name for p in GRADIENT_BOOSTING_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return ensemble.GradientBoostingRegressor(**opt_dict)


def RandomForestRegressor(options: nextmv.Options) -> ensemble.RandomForestRegressor:
    """
    Creates a `sklearn.ensemble.RandomForestRegressor` from the provided options.

    You can import the `RandomForestRegressor` function directly from `ensemble`:

    ```python
    from nextmv_sklearn.ensemble import RandomForestRegressor
    ```

    This function takes a Nextmv Options object and converts it to the appropriate
    parameters for the scikit-learn RandomForestRegressor.

    Parameters
    ----------
    options : nextmv.Options
        Options for the RandomForestRegressor. Should contain parameters
        defined in RANDOM_FOREST_REGRESSOR_PARAMETERS.

    Returns
    -------
    ensemble.RandomForestRegressor
        A sklearn.ensemble.RandomForestRegressor instance.

    Examples
    --------
    >>> from nextmv_sklearn.ensemble.options import RandomForestRegressorOptions
    >>> options = RandomForestRegressorOptions().to_nextmv()
    >>> options.set("n_estimators", 100)
    >>> options.set("max_depth", 10)
    >>> rfr = RandomForestRegressor(options)
    """

    names = {p.name for p in RANDOM_FOREST_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return ensemble.RandomForestRegressor(**opt_dict)
