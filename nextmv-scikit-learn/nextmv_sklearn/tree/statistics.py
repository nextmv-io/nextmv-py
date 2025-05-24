"""Scikit-learn tree module statistics interoperability for Nextmv.

This module provides functionality to integrate scikit-learn tree-based models
with Nextmv statistics tracking.

Functions
--------
DecisionTreeRegressorStatistics
    Convert a DecisionTreeRegressor model to Nextmv statistics format.
"""

import time
from collections.abc import Iterable
from typing import Optional

from sklearn import tree

import nextmv


def DecisionTreeRegressorStatistics(
    model: tree.DecisionTreeRegressor,
    X: Iterable,
    y: Iterable,
    sample_weight: float = None,
    run_duration_start: Optional[float] = None,
) -> nextmv.Statistics:
    """Create a Nextmv statistics object from a scikit-learn DecisionTreeRegressor model.

    You can import the `DecisionTreeRegressorStatistics` function directly from `tree`:

    ```python
    from nextmv_sklearn.tree import DecisionTreeRegressorStatistics
    ```

    Converts a trained scikit-learn DecisionTreeRegressor model into Nextmv statistics
    format. The statistics include model depth, feature importances, number of leaves,
    and model score. Additional custom metrics can be added by the user after this
    function returns. The optional `run_duration_start` parameter can be used to track
    the total runtime of the modeling process.

    Parameters
    ----------
    model : tree.DecisionTreeRegressor
        The trained scikit-learn DecisionTreeRegressor model.
    X : Iterable
        The input features used for scoring the model.
    y : Iterable
        The target values used for scoring the model.
    sample_weight : float, optional
        The sample weights used for scoring, by default None.
    run_duration_start : float, optional
        The timestamp when the model run started, typically from time.time(),
        by default None.

    Returns
    -------
    nextmv.Statistics
        A Nextmv statistics object containing model performance metrics.

    Examples
    --------
    >>> from sklearn.tree import DecisionTreeRegressor
    >>> from nextmv_sklearn.tree import DecisionTreeRegressorStatistics
    >>> import time
    >>>
    >>> # Record start time
    >>> start_time = time.time()
    >>>
    >>> # Train model
    >>> model = DecisionTreeRegressor(max_depth=5)
    >>> model.fit(X_train, y_train)
    >>>
    >>> # Create statistics
    >>> stats = DecisionTreeRegressorStatistics(
    ...     model, X_test, y_test, run_duration_start=start_time
    ... )
    >>>
    >>> # Add additional metrics
    >>> stats.result.custom["my_custom_metric"] = custom_value
    """

    run = nextmv.RunStatistics()
    if run_duration_start is not None:
        run.duration = time.time() - run_duration_start

    statistics = nextmv.Statistics(
        run=run,
        result=nextmv.ResultStatistics(
            custom={
                "depth": model.get_depth(),
                "feature_importances_": model.feature_importances_.tolist(),
                "n_leaves": int(model.get_n_leaves()),
                "score": model.score(X, y, sample_weight),
            },
        ),
        series_data=nextmv.SeriesData(),
    )

    if sample_weight is not None:
        statistics.result.custom["sample_weight"] = sample_weight

    return statistics
