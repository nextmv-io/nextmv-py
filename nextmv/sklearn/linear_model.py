"""Defines the linear regression proxy class."""

from typing import Any, Dict, Iterable

from pydantic import ConfigDict
from sklearn.linear_model import LinearRegression

from nextmv import base_model, options, output
from nextmv.sklearn import ndarray

LINEAR_REGRESSION_PARAMETERS = (
    options.Parameter(
        "fit_intercept",
        bool,
        True,
        description="Whether to calculate the intercept for this model.",
        required=True,
    ),
    options.Parameter(
        "copy_X",
        bool,
        True,
        description="If True, X will be copied; else, it may be overwritten.",
        required=True,
    ),
    options.Parameter(
        "n_jobs",
        int,
        None,
        description="The number of jobs to use for the computation.",
    ),
    options.Parameter(
        "positive",
        bool,
        False,
        description="When set to True, forces the coefficients to be positive.",
        required=True,
    ),
)


class LinearRegressionOptions(options.Options):
    """Default options for scikit-learn Linear Regression models"""

    def __init__(self, *parameters: options.Parameter):
        """Initializes options for a scikit-learn Linear Regression model."""
        return super().__init__(
            *LINEAR_REGRESSION_PARAMETERS,
            *parameters,
        )


class LinearRegressionSolution(base_model.BaseModel):
    """Linear Regression scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    coef_: ndarray.ndarray = None
    """Estimated coefficients for the linear regression problem."""
    rank_: int = 0
    """Rank of matrix X. Only available when X is dense."""
    singular_: ndarray.ndarray = None
    """Singular values of X. Only available when X is dense."""
    intercept_: float = 0
    """Independent term in the linear model. Set to 0.0 if fit_intercept =
    False."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray.ndarray = None
    """Names of features seen during fit. Defined only when X has feature names
    that are all strings."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates a Linear Regression object from a dict."""

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray.ndarray:
                data[key] = ndarray.from_list(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: LinearRegression):
        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_model(self):
        m = LinearRegression()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])
        return m


class LinearRegressionResultStatistics(output.ResultStatistics):
    """Statistics about a specific Linear Regression result."""

    @classmethod
    def from_model(
        cls,
        model: LinearRegression,
        X: Iterable,
        y: Iterable,
        sample_weight: float = None,
        *args,
        **kwds,
    ):
        custom = {"score": model.score(X, y, sample_weight)}
        if sample_weight is not None:
            custom["sample_weight"] = sample_weight
        custom.update(kwds.get("custom", {}))
        kwds["custom"] = custom

        return cls(*args, **kwds)
