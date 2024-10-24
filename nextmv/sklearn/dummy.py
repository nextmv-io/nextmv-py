"""Defines dummy regressor interoperability classes."""

from typing import Any, Dict, Iterable

from pydantic import ConfigDict
from sklearn.dummy import DummyRegressor

from nextmv import base_model, output
from nextmv.numpy import ndarray, ndarray_from_list
from nextmv.options import Options
from nextmv.options import Parameter as P

DUMMY_REGRESSOR_PARAMETERS = (
    P(
        "strategy",
        str,
        choices=["mean", "median", "quantile", "constant"],
        description="Strategy to use to generate predictions.",
    ),
    P("constant", float, description='The explicit constant as predicted by the "constant" strategy.'),
    P("quantile", float, description='The quantile to predict using the "quantile" strategy.'),
)


class DummyRegressorOptions(Options):
    """Default options for scikit-learn Dummy Regressor models"""

    def __init__(self, *parameters: P):
        """Initializes options for a scikit-learn Dummy Regressor model."""
        return super().__init__(
            *DUMMY_REGRESSOR_PARAMETERS,
            *parameters,
        )

    def to_dict(self):
        return {k: v for k, v in super().to_dict().items() if v is not None}

    def to_model(self):
        """Instantiates a Dummy Regressor model from options."""
        names = {p.name for p in DUMMY_REGRESSOR_PARAMETERS}
        kwds = {k: v for k, v in self.to_dict().items() if k in names if v is not None}
        return DummyRegressor(**kwds)


class DummyRegressorSolution(base_model.BaseModel):
    """Dummy Regressor scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    constant_: ndarray = None
    """Mean or median or quantile of the training targets or constant value
    given by the user."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit. Defined only when X has feature names
    that are all strings."""
    n_outputs_: int = 0
    """Number of outputs."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates a Dummy Regressor object from a dict."""

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = ndarray_from_list(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: DummyRegressor):
        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_model(self):
        m = DummyRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])
        return m


class DummyRegressorResultStatistics(output.ResultStatistics):
    """Statistics about a specific Dummy Regressor result."""

    @classmethod
    def from_model(
        cls,
        model: DummyRegressor,
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
