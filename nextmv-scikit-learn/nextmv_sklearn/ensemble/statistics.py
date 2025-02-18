"""Defines sklearn.ensemble statistics interoperability."""

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
    """
    Creates a Nextmv statistics object from a
    sklearn.ensemble.GradientBoostingRegressor  model. The statistics returned
    are quite basic, and should be extended according to the custom metrics
    that the user wants to track. The optional `run_duration_start` parameter
    can be used to set the start time of the whole run.

    Example:
    ----------
    >>> model = GradientBoostingRegressor(options)
    >>> ...
    >>> stats = GradientBoostingRegressorStatistics(model, ...)
    >>> ... # Add information to the statistics object.

    Parameters:
    ----------
    model : ensemble.GradientBoostingRegressor
        The sklearn GradientBoostingRegressor model.
    X : Iterable
        The input samples.
    y : Iterable
        The target values.
    sample_weight : float, optional
        The sample weights, by default None.
    run_duration_start : float, optional
        The start time of the run, by default None.

    Returns:
    ----------
    nextmv.Statistics
        The Nextmv statistics object.
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
    """
    Creates a Nextmv statistics object from a
    sklearn.ensemble.RandomForestRegressor model. The statistics returned
    are quite basic, and should be extended according to the custom metrics
    that the user wants to track. The optional `run_duration_start` parameter
    can be used to set the start time of the whole run.

    Example:
    ----------
    >>> model = RandomForestRegressor(options)
    >>> ...
    >>> stats = RandomForestRegressorStatistics(model, ...)
    >>> ... # Add information to the statistics object.

    Parameters:
    ----------
    model : ensemble.RandomForestRegressor
        The sklearn RandomForestRegressor model.
    X : Iterable
        The input samples.
    y : Iterable
        The target values.
    sample_weight : float, optional
        The sample weights, by default None.
    run_duration_start : float, optional
        The start time of the run, by default None.

    Returns:
    ----------
    nextmv.Statistics
        The Nextmv statistics object.
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
