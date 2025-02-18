"""Defines sklearn.neural_network models interoperability."""

import nextmv

MLP_REGRESSOR_PARAMETERS = [
    nextmv.Parameter(
        name="hidden_layer_sizes",
        param_type=str,
        description='The ith element represents the number of neurons in the ith hidden layer. (e.g. "1,2,3")',
    ),
    nextmv.Parameter(
        name="activation",
        param_type=str,
        choices=["identity", "logistic", "tanh", "relu"],
        description="Activation function for the hidden layer.",
    ),
    nextmv.Parameter(
        name="solver",
        param_type=str,
        choices=["lbfgs", "sgd", "adam"],
        description="The solver for weight optimization.",
    ),
    nextmv.Parameter(
        name="alpha",
        param_type=float,
        description="Strength of the L2 regularization term.",
    ),
    nextmv.Parameter(
        name="batch_size",
        param_type=int,
        description="Size of minibatches for stochastic optimizers.",
    ),
    nextmv.Parameter(
        name="learning_rate",
        param_type=str,
        choices=["constant", "invscaling", "adaptive"],
        description="Learning rate schedule for weight updates.",
    ),
    nextmv.Parameter(
        name="learning_rate_init",
        param_type=float,
        description="The initial learning rate used.",
    ),
    nextmv.Parameter(
        name="power_t",
        param_type=float,
        description="The exponent for inverse scaling learning rate.",
    ),
    nextmv.Parameter(
        name="max_iter",
        param_type=int,
        description="Maximum number of iterations.",
    ),
    nextmv.Parameter(
        name="shuffle",
        param_type=bool,
        description="Whether to shuffle samples in each iteration.",
    ),
    nextmv.Parameter(
        name="random_state",
        param_type=int,
        description="Determines random number generation for weights and "
        "bias initialization, train-test split if early stopping is used, "
        "and batch sampling when solver='sgd' or 'adam'.",
    ),
    nextmv.Parameter(
        name="tol",
        param_type=float,
        description="Tolerance for the optimization.",
    ),
    nextmv.Parameter(
        name="verbose",
        param_type=bool,
        description="Whether to print progress messages to stdout.",
    ),
    nextmv.Parameter(
        name="warm_start",
        param_type=bool,
        description="When set to True, reuse the solution of the previous call to fit as initialization.",
    ),
    nextmv.Parameter(
        name="momentum",
        param_type=float,
        description="Momentum for gradient descent update.",
    ),
    nextmv.Parameter(
        name="nesterovs_momentum",
        param_type=bool,
        description="Whether to use Nesterov's momentum.",
    ),
    nextmv.Parameter(
        name="early_stopping",
        param_type=bool,
        description="Whether to use early stopping to terminate training when validation score is not improving.",
    ),
    nextmv.Parameter(
        name="validation_fraction",
        param_type=float,
        description="The proportion of training data to set aside as validation set for early stopping.",
    ),
    nextmv.Parameter(
        name="beta_1",
        param_type=float,
        description="Exponential decay rate for estimates of first moment vector in adam.",
    ),
    nextmv.Parameter(
        name="beta_2",
        param_type=float,
        description="Exponential decay rate for estimates of second moment vector in adam.",
    ),
    nextmv.Parameter(
        name="epsilon",
        param_type=float,
        description="Value for numerical stability in adam.",
    ),
    nextmv.Parameter(
        name="n_iter_no_change",
        param_type=int,
        description="Maximum number of epochs to not meet tol improvement.",
    ),
    nextmv.Parameter(
        name="max_fun",
        param_type=int,
        description="Only used when solver='lbfgs'.",
    ),
]


class MLPRegressorOptions:
    """Options for the sklearn.neural_newtork.MLPRegressor."""

    def __init__(self):
        self.params = MLP_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
