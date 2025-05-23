"""Defines sklearn.linear_model models interoperability.

This module provides functions to create scikit-learn linear model instances
from Nextmv options.

Functions
---------
LinearRegression
    Creates a scikit-learn LinearRegression model from Nextmv options.
"""

from sklearn import linear_model

import nextmv

from .options import LINEAR_REGRESSION_PARAMETERS


def LinearRegression(options: nextmv.Options) -> linear_model.LinearRegression:
    """
    Creates a `sklearn.linear_model.LinearRegression` from the provided
    options.

    You can import the `LinearRegression` function directly from `linear_model`:

    ```python
    from nextmv_sklearn.linear_model import LinearRegression
    ```

    This function takes a Nextmv options object and configures a scikit-learn
    LinearRegression model with the appropriate parameters. It extracts
    parameter values from the options object that match the expected parameters
    for LinearRegression.

    Parameters
    ----------
    options : nextmv.Options
        Options for the LinearRegression. Can include the following parameters:

        - fit_intercept : bool, default=True
            Whether to calculate the intercept for this model.
        - copy_X : bool, default=True
            If True, X will be copied; else, it may be overwritten.
        - n_jobs : int, default=None
            The number of jobs to use for the computation.
        - positive : bool, default=False
            When set to True, forces the coefficients to be positive.

    Returns
    -------
    sklearn.linear_model.LinearRegression
        A scikit-learn LinearRegression instance configured with the
        parameters from the options.

    Examples
    --------
    >>> from nextmv_sklearn.linear_model.options import LinearRegressionOptions
    >>> options = LinearRegressionOptions().to_nextmv()
    >>> # Modify options if needed
    >>> options.fit_intercept = False
    >>> model = LinearRegression(options)
    """

    names = {p.name for p in LINEAR_REGRESSION_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return linear_model.LinearRegression(**opt_dict)
