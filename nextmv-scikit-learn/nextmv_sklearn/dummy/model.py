"""Defines sklearn.dummy models interoperability.

This module provides integration between nextmv and scikit-learn's dummy models.

Functions
---------
DummyRegressor : function
    Creates a sklearn.dummy.DummyRegressor from provided options.
"""

from sklearn import dummy

import nextmv

from .options import DUMMY_REGRESSOR_PARAMETERS


def DummyRegressor(options: nextmv.Options) -> dummy.DummyRegressor:
    """
    Creates a `sklearn.dummy.DummyRegressor` from the provided options.

    You can import the `DummyRegressor` function directly from `dummy`:

    ```python
    from nextmv_sklearn.dummy import DummyRegressor
    ```

    The DummyRegressor is a regressor that makes predictions using simple rules,
    which can be useful as a baseline for comparison against actual regressors.

    Parameters
    ----------
    options : nextmv.Options
        Options for the DummyRegressor. Should be created using
        DummyRegressorOptions.to_nextmv() from the options module.

    Returns
    -------
    sklearn.dummy.DummyRegressor
        A sklearn.dummy.DummyRegressor instance configured with the provided options.

    Examples
    --------
    >>> from nextmv_sklearn.dummy import DummyRegressor
    >>> from nextmv_sklearn.dummy.options import DummyRegressorOptions
    >>> options = DummyRegressorOptions()
    >>> # Configure options as needed
    >>> regressor = DummyRegressor(options.to_nextmv())
    >>> regressor.fit(X_train, y_train)
    >>> predictions = regressor.predict(X_test)
    """

    names = {p.name for p in DUMMY_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return dummy.DummyRegressor(**opt_dict)
