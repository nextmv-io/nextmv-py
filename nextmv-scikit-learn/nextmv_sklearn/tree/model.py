"""Defines sklearn.tree models interoperability."""

from sklearn import tree

import nextmv

from .options import DECISION_TREE_REGRESSOR_PARAMETERS


def DecisionTreeRegressor(options: nextmv.Options) -> tree.DecisionTreeRegressor:
    """
    Creates a `sklearn.tree.DecisionTreeRegressor` from the provided options.

    Parameters
    ----------
    options : nextmv.Options
        Options for the DecisionTreeRegressor.

    Returns
    -------
    DecisionTreeRegressor
        A sklearn.tree.DecisionTreeRegressor instance.
    """

    names = {p.name for p in DECISION_TREE_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return tree.DecisionTreeRegressor(**opt_dict)
