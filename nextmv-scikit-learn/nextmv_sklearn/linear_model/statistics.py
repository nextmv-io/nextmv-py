"""Defines sklearn.linear_model statistics interoperability.

This module provides functions to create Nextmv statistics objects from sklearn
linear models.

Functions
---------
LinearRegressionStatistics
    Creates a Nextmv statistics object from a sklearn.linear_model.LinearRegression model.
"""

import time
from collections.abc import Iterable
from typing import Optional

from sklearn import linear_model

import nextmv


def LinearRegressionStatistics(
    model: linear_model.LinearRegression,
    X: Iterable,
    y: Iterable,
    sample_weight: float = None,
    run_duration_start: Optional[float] = None,
) -> nextmv.Statistics:
    """
    Creates a Nextmv statistics object from a sklearn.linear_model.LinearRegression model.

    You can import the `LinearRegressionStatistics` function directly from `linear_model`:

    ```python
    from nextmv_sklearn.linear_model import LinearRegressionStatistics
    ```

    The statistics returned are quite basic, and should be extended according to the custom
    metrics that the user wants to track. The optional `run_duration_start` parameter
    can be used to set the start time of the whole run.

    Parameters
    ----------
    model : linear_model.LinearRegression
        The sklearn LinearRegression model.
    X : Iterable
        The input samples.
    y : Iterable
        The target values.
    sample_weight : float, optional
        The sample weights, by default None.
    run_duration_start : float, optional
        The start time of the run, by default None.

    Returns
    -------
    nextmv.Statistics
        The Nextmv statistics object with basic model metrics.

    Examples
    --------
    >>> from sklearn.linear_model import LinearRegression
    >>> from nextmv_sklearn.linear_model import LinearRegressionStatistics
    >>> import numpy as np
    >>> X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    >>> y = np.dot(X, np.array([1, 2])) + 3
    >>> model = LinearRegression()
    >>> model.fit(X, y)
    >>> stats = LinearRegressionStatistics(model, X, y)
    >>> print(stats.result.custom['score'])  # R^2 score
    1.0
    """

    run = nextmv.RunStatistics()
    if run_duration_start is not None:
        run.duration = time.time() - run_duration_start

    statistics = nextmv.Statistics(
        run=run,
        result=nextmv.ResultStatistics(
            custom={
                "score": model.score(X, y, sample_weight),
            },
        ),
        series_data=nextmv.SeriesData(),
    )

    if sample_weight is not None:
        statistics.result.custom["sample_weight"] = sample_weight

    return statistics
