"""Defines sklearn.neural_network statistics interoperability."""

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
    Creates a Nextmv statistics object from a
    sklearn.neural_network.MLPRegressor model. The statistics returned
    are quite basic, and should be extended according to the custom metrics
    that the user wants to track. The optional `run_duration_start` parameter
    can be used to set the start time of the whole run.

    Example:
    ----------
    >>> model = MLPRegressor(options)
    >>> ...
    >>> stats = MLPRegressorStatistics(model, ...)
    >>> ... # Add information to the statistics object.

    Parameters:
    ----------
    model : neural_network.MLPRegressor
        The sklearn MLPRegressor model.
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
                "score": model.score(X, y, sample_weight),
            },
        ),
        series_data=nextmv.SeriesData(),
    )

    if sample_weight is not None:
        statistics.result.custom["sample_weight"] = sample_weight

    return statistics
