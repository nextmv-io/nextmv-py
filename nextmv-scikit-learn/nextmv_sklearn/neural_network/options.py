"""Defines sklearn.neural_network models interoperability.

This module provides options classes for scikit-learn neural network models
that can be used with the Nextmv platform.

Classes
-------
MLPRegressorOptions
    Options class for scikit-learn's MLPRegressor.

Variables
---------
MLP_REGRESSOR_PARAMETERS
    List of Nextmv Option objects for MLPRegressor.
"""

import nextmv

MLP_REGRESSOR_PARAMETERS = [
    nextmv.Option(
        name="hidden_layer_sizes",
        option_type=str,
        description='The ith element represents the number of neurons in the ith hidden layer. (e.g. "1,2,3")',
    ),
    nextmv.Option(
        name="activation",
        option_type=str,
        choices=["identity", "logistic", "tanh", "relu"],
        description="Activation function for the hidden layer.",
    ),
    nextmv.Option(
        name="solver",
        option_type=str,
        choices=["lbfgs", "sgd", "adam"],
        description="The solver for weight optimization.",
    ),
    nextmv.Option(
        name="alpha",
        option_type=float,
        description="Strength of the L2 regularization term.",
    ),
    nextmv.Option(
        name="batch_size",
        option_type=int,
        description="Size of minibatches for stochastic optimizers.",
    ),
    nextmv.Option(
        name="learning_rate",
        option_type=str,
        choices=["constant", "invscaling", "adaptive"],
        description="Learning rate schedule for weight updates.",
    ),
    nextmv.Option(
        name="learning_rate_init",
        option_type=float,
        description="The initial learning rate used.",
    ),
    nextmv.Option(
        name="power_t",
        option_type=float,
        description="The exponent for inverse scaling learning rate.",
    ),
    nextmv.Option(
        name="max_iter",
        option_type=int,
        description="Maximum number of iterations.",
    ),
    nextmv.Option(
        name="shuffle",
        option_type=bool,
        description="Whether to shuffle samples in each iteration.",
    ),
    nextmv.Option(
        name="random_state",
        option_type=int,
        description="Determines random number generation for weights and "
        "bias initialization, train-test split if early stopping is used, "
        "and batch sampling when solver='sgd' or 'adam'.",
    ),
    nextmv.Option(
        name="tol",
        option_type=float,
        description="Tolerance for the optimization.",
    ),
    nextmv.Option(
        name="verbose",
        option_type=bool,
        description="Whether to print progress messages to stdout.",
    ),
    nextmv.Option(
        name="warm_start",
        option_type=bool,
        description="When set to True, reuse the solution of the previous call to fit as initialization.",
    ),
    nextmv.Option(
        name="momentum",
        option_type=float,
        description="Momentum for gradient descent update.",
    ),
    nextmv.Option(
        name="nesterovs_momentum",
        option_type=bool,
        description="Whether to use Nesterov's momentum.",
    ),
    nextmv.Option(
        name="early_stopping",
        option_type=bool,
        description="Whether to use early stopping to terminate training when validation score is not improving.",
    ),
    nextmv.Option(
        name="validation_fraction",
        option_type=float,
        description="The proportion of training data to set aside as validation set for early stopping.",
    ),
    nextmv.Option(
        name="beta_1",
        option_type=float,
        description="Exponential decay rate for estimates of first moment vector in adam.",
    ),
    nextmv.Option(
        name="beta_2",
        option_type=float,
        description="Exponential decay rate for estimates of second moment vector in adam.",
    ),
    nextmv.Option(
        name="epsilon",
        option_type=float,
        description="Value for numerical stability in adam.",
    ),
    nextmv.Option(
        name="n_iter_no_change",
        option_type=int,
        description="Maximum number of epochs to not meet tol improvement.",
    ),
    nextmv.Option(
        name="max_fun",
        option_type=int,
        description="Only used when solver='lbfgs'.",
    ),
]
"""List of options for scikit-learn's MLPRegressor.

You can import the MLP_REGRESSOR_PARAMETERS directly from neural_network:

```python
from nextmv_sklearn.neural_network import MLP_REGRESSOR_PARAMETERS
```

This list contains all the parameters that can be configured for a MLPRegressor
model from scikit-learn. Each option is defined as a nextmv.Option object.
"""


class MLPRegressorOptions:
    """Options for the sklearn.neural_newtork.MLPRegressor.

    You can import the MLPRegressorOptions class directly from neural_network:

    ```python
    from nextmv_sklearn.neural_network import MLPRegressorOptions
    ```

    This class provides a convenient way to configure options for the
    scikit-learn MLPRegressor model to be used with Nextmv platform.

    Attributes
    ----------
    params : list
        List of nextmv.Option objects that define the parameters for the MLPRegressor.

    Examples
    --------
    >>> from nextmv_sklearn.neural_network import MLPRegressorOptions
    >>> options = MLPRegressorOptions()
    >>> nextmv_options = options.to_nextmv()
    """

    def __init__(self):
        self.params = MLP_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object.

        Returns
        -------
        nextmv.Options
            A Nextmv options object containing all the parameters for the MLPRegressor.

        Examples
        --------
        >>> options = MLPRegressorOptions()
        >>> nextmv_options = options.to_nextmv()
        >>> # Use nextmv_options with a Nextmv model
        """

        return nextmv.Options(*self.params)
