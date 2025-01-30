"""This module contains definitions for acceptance tests."""

from datetime import datetime
from enum import Enum
from typing import Optional

from nextmv.base_model import BaseModel


class MetricType(str, Enum):
    """Type of metric when doing a comparison."""

    direct_comparison = "direct-comparison"
    """Direct comparison metric type."""


class StatisticType(str, Enum):
    """
    Type of statistical process for collapsing multiple values of a metric
    (from multiple runs) into a single value.
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
    """Comparison to use for two metrics."""

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
    """Type of tolerance used for a metric."""

    undefined = ""
    """Undefined tolerance type."""
    absolute = "absolute"
    """Absolute tolerance type."""
    relative = "relative"
    """Relative tolerance type."""


class ExperimentStatus(str, Enum):
    """Status of an acceptance test."""

    started = "started"
    """The experiment has started."""
    completed = "completed"
    """The experiment was completed."""
    failed = "failed"
    """The experiment failed."""
    draft = "draft"
    """The experiment is a draft."""
    canceled = "canceled"
    """The experiment was canceled."""
    unknown = "unknown"
    """The experiment status is unknown."""


class MetricTolerance(BaseModel):
    """Tolerance used for a metric."""

    type: ToleranceType
    """Type of tolerance."""
    value: float
    """Value of the tolerance."""


class MetricParams(BaseModel):
    """Parameters of an acceptance test."""

    operator: Comparison
    """Operator used to compare two metrics."""
    tolerance: MetricTolerance
    """Tolerance used for the comparison."""


class Metric(BaseModel):
    """A metric is a key performance indicator that is used to evaluate the
    performance of a test."""

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
    """An app instance used for a comparison."""

    instance_id: str
    """ID of the instance."""
    version_id: str
    """ID of the version."""


class DistributionSummaryStatistics(BaseModel):
    """Statistics of a distribution summary."""

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
    """Percentiles of a distribution."""

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
    """Statistics of a metric result."""

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
    """Statistics of a metric."""

    control: ResultStatistics
    """Control statistics."""
    candidate: ResultStatistics
    """Candidate statistics."""


class MetricResult(BaseModel):
    """Result of a metric."""

    metric: Metric
    """Metric of the result."""
    statistics: MetricStatistics
    """Statistics of the metric."""
    passed: bool
    """Whether the candidate passed for the metric (or not)."""


class AcceptanceTestResults(BaseModel):
    """Results of an acceptance test."""

    passed: bool
    """Whether the acceptance test passed (or not)."""
    metric_results: Optional[list[MetricResult]] = None
    """Results of the metrics."""
    error: Optional[str] = None
    """Error message if the acceptance test failed."""


class AcceptanceTest(BaseModel):
    """An acceptance test gives a go/no-go decision criteria for a set of
    metrics. It relies on a batch experiment."""

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
    status: Optional[ExperimentStatus] = ExperimentStatus.unknown
    """Status of the acceptance test."""
    results: Optional[AcceptanceTestResults] = None
    """Results of the acceptance test."""
