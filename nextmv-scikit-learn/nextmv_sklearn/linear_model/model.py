"""Defines sklearn.linear_model models interoperability."""

from sklearn import linear_model

import nextmv

from .options import LINEAR_REGRESSION_PARAMETERS


def LinearRegression(options: nextmv.Options) -> linear_model.LinearRegression:
    """
    Creates a `sklearn.linear_model.LinearRegression` from the provided
    options.

    Parameters
    ----------
    options : nextmv.Options
        Options for the LinearRegression.

    Returns
    -------
    LinearRegression
        A sklearn.linear_model.LinearRegression instance.
    """

    names = {p.name for p in LINEAR_REGRESSION_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return linear_model.LinearRegression(**opt_dict)
