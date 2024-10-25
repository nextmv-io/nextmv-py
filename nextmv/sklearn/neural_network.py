"""Defines Multi-layer Perceptron regressor interoperability classes."""

from typing import Any, Dict, Iterable, List, Optional

import numpy as np
from pydantic import ConfigDict
from sklearn.neural_network import MLPRegressor

from nextmv import base_model, output
from nextmv.numpy import ndarray, ndarray_from_list
from nextmv.options import Options
from nextmv.options import Parameter as P

MLP_REGRESSOR_PARAMETERS = (
    P(
        "hidden_layer_sizes",
        str,
        description='The ith element represents the number of neurons in the ith hidden layer. (e.g. "1,2,3")',
    ),
    P(
        "activation",
        str,
        choices=["identity", "logistic", "tanh", "relu"],
        description="Activation function for the hidden layer.",
    ),
    P("solver", str, choices=["lbfgs", "sgd", "adam"], description="The solver for weight optimization."),
    P("alpha", float, description="Strength of the L2 regularization term."),
    P("batch_size", int, description="Size of minibatches for stochastic optimizers."),
    P(
        "learning_rate",
        str,
        choices=["constant", "invscaling", "adaptive"],
        description="Learning rate schedule for weight updates.",
    ),
    P("learning_rate_init", float, description="The initial learning rate used."),
    P("power_t", float, description="The exponent for inverse scaling learning rate."),
    P("max_iter", int, description="Maximum number of iterations."),
    P("shuffle", bool, description="Whether to shuffle samples in each iteration."),
    P(
        "random_state",
        int,
        description="""Determines random number generation for weights and """
        """bias initialization, train-test split if early stopping is used, """
        """and batch sampling when solver='sgd' or 'adam'.""",
    ),
    P("tol", float, description="Tolerance for the optimization."),
    P("verbose", bool, description="Whether to print progress messages to stdout."),
    P(
        "warm_start",
        bool,
        description="When set to True, reuse the solution of the previous call to fit as initialization.",
    ),
    P("momentum", float, description="Momentum for gradient descent update."),
    P("nesterovs_momentum", bool, description="Whether to use Nesterov's momentum."),
    P(
        "early_stopping",
        bool,
        description="Whether to use early stopping to terminate training when validation score is not improving.",
    ),
    P(
        "validation_fraction",
        float,
        description="The proportion of training data to set aside as validation set for early stopping.",
    ),
    P("beta_1", float, description="Exponential decay rate for estimates of first moment vector in adam."),
    P("beta_2", float, description="Exponential decay rate for estimates of second moment vector in adam."),
    P("epsilon", float, description="Value for numerical stability in adam."),
    P("n_iter_no_change", int, description="Maximum number of epochs to not meet tol improvement."),
    P("max_fun", int, description="Only used when solver='lbfgs'."),
)


class MLPRegressorOptions(Options):
    """Default options for scikit-learn Multi-layer Perceptron Regressor models"""

    def __init__(self, *parameters: P):
        """Initializes options for a scikit-learn Multi-layer Perceptron Regressor model."""
        return super().__init__(
            *MLP_REGRESSOR_PARAMETERS,
            *parameters,
        )

    def to_dict(self):
        return {k: v for k, v in super().to_dict().items() if v is not None}

    def to_model(self):
        """Instantiates a Multi-layer Perceptron Regressor model from options."""
        names = {p.name for p in MLP_REGRESSOR_PARAMETERS}
        kwds = {k: v for k, v in self.to_dict().items() if k in names if v is not None}
        return MLPRegressor(**kwds)


class MLPRegressorSolution(base_model.BaseModel):
    """Multi-layer Perceptron Regressor scikit-learn model representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    loss_: float = 0.0
    """The current loss computed with the loss function."""
    best_loss_: float = 0.0
    """The minimum loss reached by the solver throughout fitting."""
    loss_curve_: List[np.float64] = None
    """Loss value evaluated at the end of each training step."""
    validation_scores_: Optional[List[float]] = None
    """The score at each iteration on a held-out validation set."""
    best_validation_score_: Optional[float] = None
    """The best validation score (i.e. R2 score) that triggered the early stopping."""
    t_: int = 0
    """The number of training samples seen by the solver during fitting."""
    coefs_: List[ndarray] = None
    """The ith element in the list represents the weight matrix corresponding to layer i."""
    intercepts_: List[ndarray] = None
    """The ith element in the list represents the bias vector corresponding to layer i + 1."""
    n_features_in_: int = 0
    """Number of features seen during fit."""
    feature_names_in_: ndarray = None
    """Names of features seen during fit."""
    n_iter_: int = 0
    """The number of iterations the solver has run."""
    n_layers_: int = 0
    """Number of layers."""
    n_outputs_: int = 0
    """Number of output."""
    out_activation_: str = None
    """Name of the output activation function.q"""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates an MLPRegressor object from a dict."""

        if "loss_curve_" in data:
            data["loss_curve_"] = [np.float64(val) for val in data["loss_curve_"]]

        if "coefs_" in data:
            data["coefs_"] = [ndarray_from_list([np.float64(col) for col in row]) for row in data["coefs_"]]

        if "intercepts_" in data:
            data["intercepts_"] = [ndarray_from_list([np.float64(col) for col in row]) for row in data["intercepts_"]]

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray:
                data[key] = ndarray_from_list(data[key])

        return cls(**data)

    @classmethod
    def from_model(cls, model: MLPRegressor):
        data = {}
        for key in cls.__annotations__:
            try:
                data[key] = getattr(model, key)
            except AttributeError:
                pass

        return cls(**data)

    def to_model(self):
        m = MLPRegressor()
        for key in self.model_fields:
            setattr(m, key, self.__dict__[key])
        return m


class MLPRegressorResultStatistics(output.ResultStatistics):
    """Statistics about a specific Multi-layer Perceptron Regressor result."""

    @classmethod
    def from_model(
        cls,
        model: MLPRegressor,
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
