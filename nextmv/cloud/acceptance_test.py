"""This module contains definitions for acceptance tests."""

from datetime import datetime
from enum import Enum
from typing import List

from nextmv.base_model import BaseModel


class MetricType(str, Enum):
    """Type of metric when doing a comparison."""

    absolute_threshold = "absolute-threshold"
    """Absolute threshold metric type."""
    difference_threshold = "difference-threshold"
    """Difference threshold metric type."""
    direct_comparison = "direct-comparison"
    """Direct comparison metric type."""


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


class MetricParams(BaseModel):
    """Parameters of an acceptance test."""

    operator: Comparison
    """Operator used to compare two metrics."""


class Metric(BaseModel):
    """A metric is a key performance indicator that is used to evaluate the
    performance of a test."""

    field: str
    """Field of the metric."""
    metric_type: MetricType
    """Type of the metric."""
    params: MetricParams
    """Parameters of the metric."""
    statistic: str
    """Statistic of the metric."""


class ComparisonInstance(BaseModel):
    """An app instance used for a comparison."""

    instance_id: str
    """ID of the instance."""
    version_id: str
    """ID of the version."""


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
    metrics: List[Metric]
    """Metrics of the acceptance test."""
    created_at: datetime
    """Creation date of the acceptance test."""
    updated_at: datetime
    """Last update date of the acceptance test."""
