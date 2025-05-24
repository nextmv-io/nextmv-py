"""Defines sklearn.ensemble statistics interoperability.

This module provides functions to create Nextmv statistics objects from
scikit-learn ensemble models.

Functions
--------
GradientBoostingRegressorStatistics
    Stats for GradientBoostingRegressor models.
RandomForestRegressorStatistics
    Stats for RandomForestRegressor models.
"""

import time
from collections.abc import Iterable
from typing import Optional

from sklearn import ensemble

import nextmv


def GradientBoostingRegressorStatistics(
    model: ensemble.GradientBoostingRegressor,
    X: Iterable,
    y: Iterable,
    sample_weight: float = None,
    run_duration_start: Optional[float] = None,
) -> nextmv.Statistics:
    """Create a Nextmv statistics object from a GradientBoostingRegressor model.

    You can import the `GradientBoostingRegressorStatistics` function directly from `ensemble`:

    ```python
    from nextmv_sklearn.ensemble import GradientBoostingRegressorStatistics
    ```

    This function generates statistics from a scikit-learn GradientBoostingRegressor model.
    The statistics returned are basic and include model depth, feature importances,
    and model score. These statistics can be extended according to custom metrics
    that the user wants to track. The optional `run_duration_start` parameter can
    be used to calculate the total runtime of the training process.

    Parameters
    ----------
    model : ensemble.GradientBoostingRegressor
        The trained scikit-learn GradientBoostingRegressor model.
    X : Iterable
        The input samples used for scoring.
    y : Iterable
        The target values used for scoring.
    sample_weight : float, optional
        The sample weights to apply during scoring, by default None.
    run_duration_start : float, optional
        The start time of the run (as returned by time.time()), by default None.

    Returns
    -------
    nextmv.Statistics
        The Nextmv statistics object containing model metrics.

    Examples
    --------
    >>> from sklearn.ensemble import GradientBoostingRegressor
    >>> from nextmv_sklearn.ensemble import GradientBoostingRegressorStatistics
    >>> import time
    >>>
    >>> # Record start time
    >>> start_time = time.time()
    >>>
    >>> # Train model
    >>> model = GradientBoostingRegressor(n_estimators=100, max_depth=4)
    >>> model.fit(X_train, y_train)
    >>>
    >>> # Create statistics
    >>> stats = GradientBoostingRegressorStatistics(
    ...     model, X_test, y_test, run_duration_start=start_time
    ... )
    >>> print(f"Model score: {stats.result.custom['score']}")
    """

    run = nextmv.RunStatistics()
    if run_duration_start is not None:
        run.duration = time.time() - run_duration_start

    statistics = nextmv.Statistics(
        run=run,
        result=nextmv.ResultStatistics(
            custom={
                "depth": model.max_depth,
                "feature_importances_": model.feature_importances_.tolist(),
                "score": model.score(X, y, sample_weight),
            },
        ),
        series_data=nextmv.SeriesData(),
    )

    if sample_weight is not None:
        statistics.result.custom["sample_weight"] = sample_weight

    return statistics


def RandomForestRegressorStatistics(
    model: ensemble.RandomForestRegressor,
    X: Iterable,
    y: Iterable,
    sample_weight: float = None,
    run_duration_start: Optional[float] = None,
) -> nextmv.Statistics:
    """Create a Nextmv statistics object from a RandomForestRegressor model.

    You can import the `RandomForestRegressorStatistics` function directly from `ensemble`:

    ```python
    from nextmv_sklearn.ensemble import RandomForestRegressorStatistics
    ```

    This function generates statistics from a scikit-learn RandomForestRegressor model.
    The statistics returned include feature importances and model score. These
    statistics can be extended according to custom metrics that the user wants to
    track. The optional `run_duration_start` parameter can be used to calculate
    the total runtime of the training process.

    Parameters
    ----------
    model : ensemble.RandomForestRegressor
        The trained scikit-learn RandomForestRegressor model.
    X : Iterable
        The input samples used for scoring.
    y : Iterable
        The target values used for scoring.
    sample_weight : float, optional
        The sample weights to apply during scoring, by default None.
    run_duration_start : float, optional
        The start time of the run (as returned by time.time()), by default None.

    Returns
    -------
    nextmv.Statistics
        The Nextmv statistics object containing model metrics.

    Examples
    --------
    >>> from sklearn.ensemble import RandomForestRegressor
    >>> from nextmv_sklearn.ensemble import RandomForestRegressorStatistics
    >>> import time
    >>>
    >>> # Record start time
    >>> start_time = time.time()
    >>>
    >>> # Train model
    >>> model = RandomForestRegressor(n_estimators=100, max_depth=None)
    >>> model.fit(X_train, y_train)
    >>>
    >>> # Create statistics
    >>> stats = RandomForestRegressorStatistics(
    ...     model, X_test, y_test, run_duration_start=start_time
    ... )
    >>> print(f"Feature importance: {stats.result.custom['feature_importances_']}")
    """

    run = nextmv.RunStatistics()
    if run_duration_start is not None:
        run.duration = time.time() - run_duration_start

    statistics = nextmv.Statistics(
        run=run,
        result=nextmv.ResultStatistics(
            custom={
                "feature_importances_": model.feature_importances_.tolist(),
                "score": model.score(X, y, sample_weight),
            },
        ),
        series_data=nextmv.SeriesData(),
    )

    if sample_weight is not None:
        statistics.result.custom["sample_weight"] = sample_weight

    return statistics
