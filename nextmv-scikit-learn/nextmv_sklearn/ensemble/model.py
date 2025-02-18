"""Defines sklearn.ensemble models interoperability."""

from sklearn import ensemble

import nextmv

from .options import GRADIENT_BOOSTING_REGRESSOR_PARAMETERS, RANDOM_FOREST_REGRESSOR_PARAMETERS


def GradientBoostingRegressor(options: nextmv.Options) -> ensemble.GradientBoostingRegressor:
    """
    Creates a `sklearn.ensemble.GradientBoostingRegressor` from the provided
    options.

    Parameters
    ----------
    options : nextmv.Options
        Options for the GradientBoostingRegressor.

    Returns
    -------
    GradientBoostingRegressor
        A sklearn.ensemble.GradientBoostingRegressor instance.
    """

    names = {p.name for p in GRADIENT_BOOSTING_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return ensemble.GradientBoostingRegressor(**opt_dict)


def RandomForestRegressor(options: nextmv.Options) -> ensemble.RandomForestRegressor:
    """
    Creates a `sklearn.ensemble.RandomForestRegressor` from the provided options.

    Parameters
    ----------
    options : nextmv.Options
        Options for the RandomForestRegressor.

    Returns
    -------
    RandomForestRegressor
        A sklearn.ensemble.RandomForestRegressor instance.
    """

    names = {p.name for p in RANDOM_FOREST_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return ensemble.RandomForestRegressor(**opt_dict)
