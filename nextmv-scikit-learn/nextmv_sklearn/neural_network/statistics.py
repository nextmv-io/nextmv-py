"""Defines sklearn.neural_network statistics interoperability.

This module provides functions to convert scikit-learn neural network models
into Nextmv statistics objects.

Functions
---------
MLPRegressorStatistics
    Creates Nextmv statistics from a sklearn.neural_network.MLPRegressor model.
"""

import time
from collections.abc import Iterable
from typing import Optional

from sklearn import neural_network

import nextmv


def MLPRegressorStatistics(
    model: neural_network.MLPRegressor,
    X: Iterable,
    y: Iterable,
    sample_weight: float = None,
    run_duration_start: Optional[float] = None,
) -> nextmv.Statistics:
    """
    Creates a Nextmv statistics object from a sklearn.neural_network.MLPRegressor model.

    You can import the `MLPRegressorStatistics` function directly from `neural_network`:

    ```python
    from nextmv_sklearn.neural_network import MLPRegressorStatistics
    ```

    The statistics returned are quite basic, and should be extended according
    to the custom metrics that the user wants to track. The optional
    `run_duration_start` parameter can be used to set the start time of the whole run.

    Parameters
    ----------
    model : neural_network.MLPRegressor
        The sklearn MLPRegressor model.
    X : Iterable
        The input samples. Acceptable formats are:
        - Dense numpy arrays of shape (n_samples, n_features)
        - Sparse scipy matrices of shape (n_samples, n_features)
        - Pandas DataFrames with shape (n_samples, n_features)
    y : Iterable
        The target values (real numbers for regression).
    sample_weight : float, optional
        Individual weights for each sample. If None, all samples have equal weight.
    run_duration_start : float, optional
        The start time of the run in seconds since the epoch. If provided,
        the duration of the run will be calculated.

    Returns
    -------
    nextmv.Statistics
        The Nextmv statistics object containing:
        - Run statistics including duration if run_duration_start was provided
        - Result statistics with the model's score and optionally sample_weight
        - Empty series data

    Examples
    --------
    >>> from sklearn.neural_network import MLPRegressor
    >>> from nextmv_sklearn.neural_network import MLPRegressorStatistics
    >>> import numpy as np
    >>>
    >>> # Create and train the model
    >>> X = np.array([[0, 0], [1, 1]])
    >>> y = np.array([0, 1])
    >>> start_time = time.time()
    >>> model = MLPRegressor(hidden_layer_sizes=(5,), max_iter=1000)
    >>> model.fit(X, y)
    >>>
    >>> # Create statistics object
    >>> stats = MLPRegressorStatistics(model, X, y, run_duration_start=start_time)
    >>> print(f"Model score: {stats.result.custom['score']}")
    >>> print(f"Run duration: {stats.run.duration} seconds")
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
