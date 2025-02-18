"""Defines sklearn.dummy models interoperability."""

from sklearn import dummy

import nextmv

from .options import DUMMY_REGRESSOR_PARAMETERS


def DummyRegressor(options: nextmv.Options) -> dummy.DummyRegressor:
    """
    Creates a `sklearn.dummy.DummyRegressor` from the provided options.

    Parameters
    ----------
    options : nextmv.Options
        Options for the DummyRegressor.

    Returns
    -------
    DummyRegressor
        A sklearn.dummy.DummyRegressor instance.
    """

    names = {p.name for p in DUMMY_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return dummy.DummyRegressor(**opt_dict)
