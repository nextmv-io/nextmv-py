"""
Definitions for acceptance tests in the Nextmv Cloud platform.

This module provides classes and enumerations for working with acceptance tests
in the Nextmv Cloud platform. Acceptance tests are used to compare the performance
of different versions of an app against a set of metrics.

Classes
-------
MetricType : Enum
    Type of metric when doing a comparison.
StatisticType : Enum
    Type of statistical process for collapsing multiple values of a metric.
Comparison : Enum
    Comparison operators to use for comparing two metrics.
ToleranceType : Enum
    Type of tolerance used for a metric.
ExperimentStatus : Enum
    Status of an acceptance test experiment.
MetricTolerance : BaseModel
    Tolerance used for a metric in an acceptance test.
MetricParams : BaseModel
    Parameters of a metric comparison in an acceptance test.
Metric : BaseModel
    A metric used to evaluate the performance of a test.
ComparisonInstance : BaseModel
    An app instance used for a comparison in an acceptance test.
DistributionSummaryStatistics : BaseModel
    Statistics of a distribution summary for metric results.
DistributionPercentiles : BaseModel
    Percentiles of a metric value distribution.
ResultStatistics : BaseModel
    Statistics of a single instance's metric results.
MetricStatistics : BaseModel
    Statistics of a metric comparing control and candidate instances.
MetricResult : BaseModel
    Result of a metric evaluation in an acceptance test.
AcceptanceTestResults : BaseModel
    Results of an acceptance test.
AcceptanceTest : BaseModel
    An acceptance test for evaluating app instances.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from nextmv.base_model import BaseModel
from nextmv.cloud.batch_experiment import ExperimentStatus


class MetricType(str, Enum):
    """
    Type of metric when doing a comparison.

    You can import the `MetricType` class directly from `cloud`:

    ```python
    from nextmv.cloud import MetricType
    ```

    This enumeration defines the different types of metrics that can be used
    when comparing two runs in an acceptance test.

    Attributes
    ----------
    direct_comparison : str
        Direct comparison between metric values.

    Examples
    --------
    >>> from nextmv.cloud import MetricType
    >>> metric_type = MetricType.direct_comparison
    >>> metric_type
    <MetricType.direct_comparison: 'direct-comparison'>
    """

    direct_comparison = "direct-comparison"
    """Direct comparison metric type."""


class StatisticType(str, Enum):
    """
    Type of statistical process for collapsing multiple values of a metric.

    You can import the `StatisticType` class directly from `cloud`:

    ```python
    from nextmv.cloud import StatisticType
    ```

    This enumeration defines the different statistical methods that can be used
    to summarize multiple values of a metric from multiple runs into a single
    value.

    Attributes
    ----------
    min : str
        Minimum value.
    max : str
        Maximum value.
    mean : str
        Mean value.
    std : str
        Standard deviation.
    shifted_geometric_mean : str
        Shifted geometric mean.
    p01 : str
        1st percentile.
    p05 : str
        5th percentile.
    p10 : str
        10th percentile.
    p25 : str
        25th percentile.
    p50 : str
        50th percentile (median).
    p75 : str
        75th percentile.
    p90 : str
        90th percentile.
    p95 : str
        95th percentile.
    p99 : str
        99th percentile.

    Examples
    --------
    >>> from nextmv.cloud import StatisticType
    >>> stat_type = StatisticType.mean
    >>> stat_type
    <StatisticType.mean: 'mean'>
    """

    min = "min"
    """Minimum value."""
    max = "max"
    """Maximum value."""
    mean = "mean"
    """Mean value."""
    std = "std"
    """Standard deviation."""
    shifted_geometric_mean = "shifted_geometric_mean"
    """Shifted geometric mean."""
    p01 = "p01"
    """1st percentile."""
    p05 = "p05"
    """5th percentile."""
    p10 = "p10"
    """10th percentile."""
    p25 = "p25"
    """25th percentile."""
    p50 = "p50"
    """50th percentile."""
    p75 = "p75"
    """75th percentile."""
    p90 = "p90"
    """90th percentile."""
    p95 = "p95"
    """95th percentile."""
    p99 = "p99"
    """99th percentile."""


class Comparison(str, Enum):
    """
    Comparison operators to use for comparing two metrics.

    You can import the `Comparison` class directly from `cloud`:

    ```python
    from nextmv.cloud import Comparison
    ```

    This enumeration defines the different comparison operators that can be used
    to compare two metric values in an acceptance test.

    Attributes
    ----------
    equal_to : str
        Equal to operator (==).
    greater_than : str
        Greater than operator (>).
    greater_than_or_equal_to : str
        Greater than or equal to operator (>=).
    less_than : str
        Less than operator (<).
    less_than_or_equal_to : str
        Less than or equal to operator (<=).
    not_equal_to : str
        Not equal to operator (!=).

    Examples
    --------
    >>> from nextmv.cloud import Comparison
    >>> op = Comparison.greater_than
    >>> op
    <Comparison.greater_than: 'gt'>
    """

    equal_to = "eq"
    """Equal to metric type."""
    greater_than = "gt"
    """Greater than metric type."""
    greater_than_or_equal_to = "ge"
    """Greater than or equal to metric type."""
    less_than = "lt"
    """Less than metric type."""
    less_than_or_equal_to = "le"
    """Less than or equal to metric type."""
    not_equal_to = "ne"
    """Not equal to metric type."""


class ToleranceType(str, Enum):
    """
    Type of tolerance used for a metric.

    You can import the `ToleranceType` class directly from `cloud`:

    ```python
    from nextmv.cloud import ToleranceType
    ```

    This enumeration defines the different types of tolerances that can be used
    when comparing metrics in acceptance tests.

    Attributes
    ----------
    undefined : str
        Undefined tolerance type (empty string).
    absolute : str
        Absolute tolerance type, using a fixed value.
    relative : str
        Relative tolerance type, using a percentage.

    Examples
    --------
    >>> from nextmv.cloud import ToleranceType
    >>> tol_type = ToleranceType.absolute
    >>> tol_type
    <ToleranceType.absolute: 'absolute'>
    """

    undefined = ""
    """Undefined tolerance type."""
    absolute = "absolute"
    """Absolute tolerance type."""
    relative = "relative"
    """Relative tolerance type."""


class MetricTolerance(BaseModel):
    """
    Tolerance used for a metric in an acceptance test.

    You can import the `MetricTolerance` class directly from `cloud`:

    ```python
    from nextmv.cloud import MetricTolerance
    ```

    This class defines the tolerance to be applied when comparing metric values,
    which can be either absolute or relative.

    Attributes
    ----------
    type : ToleranceType
        Type of tolerance (absolute or relative).
    value : float
        Value of the tolerance.

    Examples
    --------
    >>> from nextmv.cloud import MetricTolerance, ToleranceType
    >>> tolerance = MetricTolerance(type=ToleranceType.absolute, value=0.1)
    >>> tolerance.type
    <ToleranceType.absolute: 'absolute'>
    >>> tolerance.value
    0.1
    """

    type: ToleranceType
    """Type of tolerance."""
    value: float
    """Value of the tolerance."""


class MetricParams(BaseModel):
    """
    Parameters of a metric comparison in an acceptance test.

    You can import the `MetricParams` class directly from `cloud`:

    ```python
    from nextmv.cloud import MetricParams
    ```

    This class defines the parameters used for comparing metric values,
    including the comparison operator and tolerance.

    Attributes
    ----------
    operator : Comparison
        Operator used to compare two metrics (e.g., greater than, less than).
    tolerance : MetricTolerance
        Tolerance used for the comparison.

    Examples
    --------
    >>> from nextmv.cloud import MetricParams, Comparison, MetricTolerance, ToleranceType
    >>> params = MetricParams(
    ...     operator=Comparison.less_than,
    ...     tolerance=MetricTolerance(type=ToleranceType.absolute, value=0.5)
    ... )
    >>> params.operator
    <Comparison.less_than: 'lt'>
    """

    operator: Comparison
    """Operator used to compare two metrics."""
    tolerance: MetricTolerance
    """Tolerance used for the comparison."""


class Metric(BaseModel):
    """
    A metric used to evaluate the performance of a test.

    You can import the `Metric` class directly from `cloud`:

    ```python
    from nextmv.cloud import Metric
    ```

    A metric is a key performance indicator that is used to evaluate the
    performance of a test. It defines the field to measure, the type of
    comparison, and the statistical method to use.

    Attributes
    ----------
    field : str
        Field of the metric to measure (e.g., "solution.objective").
    metric_type : MetricType
        Type of the metric comparison.
    params : MetricParams
        Parameters of the metric comparison.
    statistic : StatisticType
        Type of statistical process for collapsing multiple values into a single value.

    Examples
    --------
    >>> from nextmv.cloud import (
    ...     Metric, MetricType, MetricParams, Comparison,
    ...     MetricTolerance, ToleranceType, StatisticType
    ... )
    >>> metric = Metric(
    ...     field="solution.objective",
    ...     metric_type=MetricType.direct_comparison,
    ...     params=MetricParams(
    ...         operator=Comparison.less_than,
    ...         tolerance=MetricTolerance(
    ...             type=ToleranceType.relative,
    ...             value=0.05
    ...         )
    ...     ),
    ...     statistic=StatisticType.mean
    ... )
    >>> metric.field
    'solution.objective'
    """

    field: str
    """Field of the metric."""
    metric_type: MetricType
    """Type of the metric."""
    params: MetricParams
    """Parameters of the metric."""
    statistic: StatisticType
    """
    Type of statistical process for collapsing multiple values of a metric
    (from multiple runs) into a single value.
    """


class ComparisonInstance(BaseModel):
    """
    An app instance used for a comparison in an acceptance test.

    You can import the `ComparisonInstance` class directly from `cloud`:

    ```python
    from nextmv.cloud import ComparisonInstance
    ```

    This class represents an app instance used in a comparison,
    identifying both the instance and its version.

    Attributes
    ----------
    instance_id : str
        ID of the instance.
    version_id : str
        ID of the version.

    Examples
    --------
    >>> from nextmv.cloud import ComparisonInstance
    >>> instance = ComparisonInstance(
    ...     instance_id="instance-123",
    ...     version_id="version-456"
    ... )
    >>> instance.instance_id
    'instance-123'
    >>> instance.version_id
    'version-456'
    """

    instance_id: str
    """ID of the instance."""
    version_id: str
    """ID of the version."""


class DistributionSummaryStatistics(BaseModel):
    """
    Statistics of a distribution summary for metric results.

    You can import the `DistributionSummaryStatistics` class directly from `cloud`:

    ```python
    from nextmv.cloud import DistributionSummaryStatistics
    ```

    This class contains statistical measures summarizing the distribution of
    metric values across multiple runs.

    Attributes
    ----------
    min : float
        Minimum value in the distribution.
    max : float
        Maximum value in the distribution.
    count : int
        Count of runs in the distribution.
    mean : float
        Mean value of the distribution.
    std : float
        Standard deviation of the distribution.
    shifted_geometric_mean : float
        Shifted geometric mean of the distribution.
    shift_parameter : float
        Shift parameter used for the geometric mean calculation.

    Examples
    --------
    >>> from nextmv.cloud import DistributionSummaryStatistics
    >>> stats = DistributionSummaryStatistics(
    ...     min=10.0,
    ...     max=20.0,
    ...     count=5,
    ...     mean=15.0,
    ...     std=4.0,
    ...     shifted_geometric_mean=14.5,
    ...     shift_parameter=1.0
    ... )
    >>> stats.mean
    15.0
    >>> stats.count
    5
    """

    min: float
    """Minimum value."""
    max: float
    """Maximum value."""
    count: int
    """Count of runs."""
    mean: float
    """Mean value."""
    std: float
    """Standard deviation."""
    shifted_geometric_mean: float
    """Shifted geometric mean."""
    shift_parameter: float
    """Shift parameter of the geometric mean."""


class DistributionPercentiles(BaseModel):
    """
    Percentiles of a metric value distribution.

    You can import the `DistributionPercentiles` class directly from `cloud`:

    ```python
    from nextmv.cloud import DistributionPercentiles
    ```

    This class contains the different percentiles of a distribution of metric values
    across multiple runs.

    Attributes
    ----------
    p01 : float
        1st percentile of the distribution.
    p05 : float
        5th percentile of the distribution.
    p10 : float
        10th percentile of the distribution.
    p25 : float
        25th percentile of the distribution.
    p50 : float
        50th percentile of the distribution (median).
    p75 : float
        75th percentile of the distribution.
    p90 : float
        90th percentile of the distribution.
    p95 : float
        95th percentile of the distribution.
    p99 : float
        99th percentile of the distribution.

    Examples
    --------
    >>> from nextmv.cloud import DistributionPercentiles
    >>> percentiles = DistributionPercentiles(
    ...     p01=10.0,
    ...     p05=12.0,
    ...     p10=13.0,
    ...     p25=14.0,
    ...     p50=15.0,
    ...     p75=16.0,
    ...     p90=17.0,
    ...     p95=18.0,
    ...     p99=19.0
    ... )
    >>> percentiles.p50  # median
    15.0
    """

    p01: float
    """1st percentile."""
    p05: float
    """5th percentile."""
    p10: float
    """10th percentile."""
    p25: float
    """25th percentile."""
    p50: float
    """50th percentile."""
    p75: float
    """75th percentile."""
    p90: float
    """90th percentile."""
    p95: float
    """95th percentile."""
    p99: float
    """99th percentile."""


class ResultStatistics(BaseModel):
    """
    Statistics of a single instance's metric results.

    You can import the `ResultStatistics` class directly from `cloud`:

    ```python
    from nextmv.cloud import ResultStatistics
    ```

    This class aggregates the statistical information about the metric results
    for a specific instance in a comparison.

    Attributes
    ----------
    instance_id : str
        ID of the instance.
    version_id : str
        ID of the version.
    number_of_runs_total : int
        Total number of runs included in the statistics.
    distribution_summary_statistics : DistributionSummaryStatistics
        Summary statistics of the metric value distribution.
    distribution_percentiles : DistributionPercentiles
        Percentiles of the metric value distribution.

    Examples
    --------
    >>> from nextmv.cloud import (
    ...     ResultStatistics, DistributionSummaryStatistics, DistributionPercentiles
    ... )
    >>> result_stats = ResultStatistics(
    ...     instance_id="instance-123",
    ...     version_id="version-456",
    ...     number_of_runs_total=10,
    ...     distribution_summary_statistics=DistributionSummaryStatistics(
    ...         min=10.0,
    ...         max=20.0,
    ...         count=10,
    ...         mean=15.0,
    ...         std=3.0,
    ...         shifted_geometric_mean=14.5,
    ...         shift_parameter=1.0
    ...     ),
    ...     distribution_percentiles=DistributionPercentiles(
    ...         p01=10.5,
    ...         p05=11.0,
    ...         p10=12.0,
    ...         p25=13.5,
    ...         p50=15.0,
    ...         p75=16.5,
    ...         p90=18.0,
    ...         p95=19.0,
    ...         p99=19.5
    ...     )
    ... )
    >>> result_stats.number_of_runs_total
    10
    """

    instance_id: str
    """ID of the instance."""
    version_id: str
    """ID of the version."""
    number_of_runs_total: int
    """Number of runs."""
    distribution_summary_statistics: DistributionSummaryStatistics
    """Distribution summary statistics."""
    distribution_percentiles: DistributionPercentiles
    """Distribution percentiles."""


class MetricStatistics(BaseModel):
    """
    Statistics of a metric comparing control and candidate instances.

    You can import the `MetricStatistics` class directly from `cloud`:

    ```python
    from nextmv.cloud import MetricStatistics
    ```

    This class holds the statistical information for both the control and candidate
    instances being compared in the acceptance test.

    Attributes
    ----------
    control : ResultStatistics
        Statistics for the control instance.
    candidate : ResultStatistics
        Statistics for the candidate instance.

    Examples
    --------
    >>> from nextmv.cloud import (
    ...     MetricStatistics, ResultStatistics,
    ...     DistributionSummaryStatistics, DistributionPercentiles
    ... )
    >>> stats = MetricStatistics(
    ...     control=ResultStatistics(
    ...         instance_id="control-instance",
    ...         version_id="control-version",
    ...         number_of_runs_total=10,
    ...         distribution_summary_statistics=DistributionSummaryStatistics(
    ...             min=10.0, max=20.0, count=10, mean=15.0, std=3.0,
    ...             shifted_geometric_mean=14.5, shift_parameter=1.0
    ...         ),
    ...         distribution_percentiles=DistributionPercentiles(
    ...             p01=10.5, p05=11.0, p10=12.0, p25=13.5, p50=15.0,
    ...             p75=16.5, p90=18.0, p95=19.0, p99=19.5
    ...         )
    ...     ),
    ...     candidate=ResultStatistics(
    ...         instance_id="candidate-instance",
    ...         version_id="candidate-version",
    ...         number_of_runs_total=10,
    ...         distribution_summary_statistics=DistributionSummaryStatistics(
    ...             min=9.0, max=18.0, count=10, mean=13.0, std=2.5,
    ...             shifted_geometric_mean=12.8, shift_parameter=1.0
    ...         ),
    ...         distribution_percentiles=DistributionPercentiles(
    ...             p01=9.5, p05=10.0, p10=11.0, p25=12.0, p50=13.0,
    ...             p75=14.0, p90=15.5, p95=16.5, p99=17.5
    ...         )
    ...     )
    ... )
    >>> stats.control.mean > stats.candidate.mean
    True
    """

    control: ResultStatistics
    """Control statistics."""
    candidate: ResultStatistics
    """Candidate statistics."""


class MetricResult(BaseModel):
    """
    Result of a metric evaluation in an acceptance test.

    You can import the `MetricResult` class directly from `cloud`:

    ```python
    from nextmv.cloud import MetricResult
    ```

    This class represents the result of evaluating a specific metric in an
    acceptance test, including whether the candidate passed according to this metric.

    Attributes
    ----------
    metric : Metric
        The metric that was evaluated.
    statistics : MetricStatistics
        Statistics comparing control and candidate instances for this metric.
    passed : bool
        Whether the candidate passed for this metric.

    Examples
    --------
    >>> from nextmv.cloud import (
    ...     MetricResult, Metric, MetricType, MetricParams, Comparison,
    ...     MetricTolerance, ToleranceType, StatisticType, MetricStatistics
    ... )
    >>> # Assume we have statistics object already created
    >>> result = MetricResult(
    ...     metric=Metric(
    ...         field="solution.objective",
    ...         metric_type=MetricType.direct_comparison,
    ...         params=MetricParams(
    ...             operator=Comparison.less_than,
    ...             tolerance=MetricTolerance(
    ...                 type=ToleranceType.relative,
    ...                 value=0.05
    ...             )
    ...         ),
    ...         statistic=StatisticType.mean
    ...     ),
    ...     statistics=statistics,  # previously created statistics object
    ...     passed=True
    ... )
    >>> result.passed
    True
    """

    metric: Metric
    """Metric of the result."""
    statistics: MetricStatistics
    """Statistics of the metric."""
    passed: bool
    """Whether the candidate passed for the metric (or not)."""


class AcceptanceTestResults(BaseModel):
    """
    Results of an acceptance test.

    You can import the `AcceptanceTestResults` class directly from `cloud`:

    ```python
    from nextmv.cloud import AcceptanceTestResults
    ```

    This class contains the overall results of an acceptance test, including
    whether the test passed and detailed results for each metric.

    Attributes
    ----------
    passed : bool
        Whether the acceptance test passed overall.
    metric_results : list[MetricResult], optional
        Results for each metric in the test.
    error : str, optional
        Error message if the acceptance test failed.

    Examples
    --------
    >>> from nextmv.cloud import AcceptanceTestResults
    >>> # Assume metric_results is a list of MetricResult objects
    >>> results = AcceptanceTestResults(
    ...     passed=True,
    ...     metric_results=metric_results  # previously created list of results
    ... )
    >>> results.passed
    True
    >>>
    >>> # Example with error
    >>> error_results = AcceptanceTestResults(
    ...     passed=False,
    ...     error="Experiment failed to complete"
    ... )
    >>> error_results.passed
    False
    >>> error_results.error
    'Experiment failed to complete'
    """

    passed: bool
    """Whether the acceptance test passed (or not)."""
    metric_results: Optional[list[MetricResult]] = None
    """Results of the metrics."""
    error: Optional[str] = None
    """Error message if the acceptance test failed."""


class AcceptanceTest(BaseModel):
    """
    An acceptance test for evaluating app instances.

    You can import the `AcceptanceTest` class directly from `cloud`:

    ```python
    from nextmv.cloud import AcceptanceTest
    ```

    An acceptance test gives a go/no-go decision criteria for a set of
    metrics. It relies on a batch experiment to compare a candidate app instance
    against a control app instance.

    Attributes
    ----------
    id : str
        ID of the acceptance test.
    name : str
        Name of the acceptance test.
    description : str
        Description of the acceptance test.
    app_id : str
        ID of the app that owns the acceptance test.
    experiment_id : str
        ID of the batch experiment underlying the acceptance test.
    control : ComparisonInstance
        Control instance of the acceptance test.
    candidate : ComparisonInstance
        Candidate instance of the acceptance test.
    metrics : list[Metric]
        Metrics to evaluate in the acceptance test.
    created_at : datetime
        Creation date of the acceptance test.
    updated_at : datetime
        Last update date of the acceptance test.
    status : ExperimentStatus, optional
        Status of the acceptance test.
    results : AcceptanceTestResults, optional
        Results of the acceptance test.

    Examples
    --------
    >>> from nextmv.cloud import (
    ...     AcceptanceTest, ComparisonInstance, Metric, ExperimentStatus
    ... )
    >>> from datetime import datetime
    >>> test = AcceptanceTest(
    ...     id="test-123",
    ...     name="Performance acceptance test",
    ...     description="Testing performance improvements",
    ...     app_id="app-456",
    ...     experiment_id="exp-789",
    ...     control=ComparisonInstance(
    ...         instance_id="control-instance",
    ...         version_id="control-version"
    ...     ),
    ...     candidate=ComparisonInstance(
    ...         instance_id="candidate-instance",
    ...         version_id="candidate-version"
    ...     ),
    ...     metrics=[metric1, metric2],  # previously created metrics
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now(),
    ...     status=ExperimentStatus.started
    ... )
    >>> test.status
    <ExperimentStatus.started: 'started'>
    """

    id: str
    """ID of the acceptance test."""
    name: str
    """Name of the acceptance test."""
    description: str
    """Description of the acceptance test."""
    app_id: str
    """ID of the app that owns the acceptance test."""
    experiment_id: str
    """ID of the batch experiment underlying in the acceptance test."""
    control: ComparisonInstance
    """Control instance of the acceptance test."""
    candidate: ComparisonInstance
    """Candidate instance of the acceptance test."""
    metrics: list[Metric]
    """Metrics of the acceptance test."""
    created_at: datetime
    """Creation date of the acceptance test."""
    updated_at: datetime
    """Last update date of the acceptance test."""
    status: Optional[ExperimentStatus] = ExperimentStatus.UNKNOWN
    """Status of the acceptance test."""
    results: Optional[AcceptanceTestResults] = None
    """Results of the acceptance test."""
