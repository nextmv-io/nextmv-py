"""Defines sklearn.neural_network models interoperability."""

from sklearn import neural_network

import nextmv

from .options import MLP_REGRESSOR_PARAMETERS


def MLPRegressor(options: nextmv.Options) -> neural_network.MLPRegressor:
    """
    Creates a `sklearn.neural_network.MLPRegressor` from the provided
    options.

    Parameters
    ----------
    options : nextmv.Options
        Options for the LinearRegression.

    Returns
    -------
    MLPRegressor
        A sklearn.neural_network.MLPRegressor instance.
    """

    names = {p.name for p in MLP_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return neural_network.MLPRegressor(**opt_dict)
