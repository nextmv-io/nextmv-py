"""Defines sklearn.dummy statistics interoperability.

This module provides utilities for integrating scikit-learn dummy models with Nextmv statistics.

Functions
---------
DummyRegressorStatistics
    Creates a Nextmv statistics object from a sklearn.dummy.DummyRegressor model.
"""

import time
from collections.abc import Iterable
from typing import Optional

from sklearn import dummy

import nextmv


def DummyRegressorStatistics(
    model: dummy.DummyRegressor,
    X: Iterable,
    y: Iterable,
    sample_weight: float = None,
    run_duration_start: Optional[float] = None,
) -> nextmv.Statistics:
    """
    Creates a Nextmv statistics object from a sklearn.dummy.DummyRegressor model.

    You can import the `DummyRegressorStatistics` function directly from `dummy`:

    ```python
    from nextmv_sklearn.dummy import DummyRegressorStatistics
    ```

    The statistics returned are quite basic, and should be extended
    according to the custom metrics that the user wants to track. The optional
    `run_duration_start` parameter can be used to set the start time of the
    whole run.

    Parameters
    ----------
    model : dummy.DummyRegressor
        The sklearn DummyRegressor model.
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
        The Nextmv statistics object.

    Examples
    --------
    >>> from sklearn.dummy import DummyRegressor
    >>> from nextmv_sklearn.dummy import DummyRegressorStatistics
    >>> import numpy as np
    >>>
    >>> # Create a dummy regressor
    >>> model = DummyRegressor(strategy='mean')
    >>> X = np.array([[1, 2], [3, 4], [5, 6]])
    >>> y = np.array([1, 2, 3])
    >>> model.fit(X, y)
    >>>
    >>> # Create statistics object
    >>> start_time = time.time()
    >>> # ... perform operations
    >>> stats = DummyRegressorStatistics(model, X, y, run_duration_start=start_time)
    >>> print(stats.result.custom["score"])  # Access the model score
    """

    run = nextmv.RunStatistics()
    if run_duration_start is not None:
        run.duration = time.time() - run_duration_start

    statistics = nextmv.Statistics(
        run=run,
        result=nextmv.ResultStatistics(
            custom={"score": model.score(X, y, sample_weight)},
        ),
        series_data=nextmv.SeriesData(),
    )

    if sample_weight is not None:
        statistics.result.custom["sample_weight"] = sample_weight

    return statistics
