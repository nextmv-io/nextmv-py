"""Defines the linear regression proxy class."""

from pydantic import ConfigDict
from sklearn import linear_model

from nextmv.base_model import BaseModel
from nextmv.ndarray import ndarray


class LinearRegression(BaseModel, linear_model.LinearRegression):
    """Linear Regression scikit-learn model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Parameters
    fit_intercept: bool = True
    """Whether to calculate the intercept for this model."""
    copy_X: bool = True
    """If True, X will be copied; else, it may be overwritten."""
    n_jobs: int = None
    """The number of jobs to use for the computation."""
    positive: bool = False
    """When set to True, forces the coefficients to be positive."""

    # Attributes
    coef_: ndarray = None  # type: ignore
    """Estimated coefficients for the linear regression problem."""
    rank_: int = 0
    """Rank of matrix X. Only available when X is dense."""
    singular_: ndarray = None  # type: ignore
    """Singular values of X. Only available when X is dense."""
    intercept_: float = 0
    """Independent term in the linear model. Set to 0.0 if fit_intercept =
    False."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None  # type: ignore
    """Names of features seen during fit. Defined only when X has feature names
    that are all strings."""
