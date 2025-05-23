"""Defines sklearn.neural_network models interoperability.

This module provides functions for creating and configuring scikit-learn neural network models
using Nextmv options.

Functions
---------
MLPRegressor
    Create a Multi-layer Perceptron regressor with Nextmv options.
"""

from sklearn import neural_network

import nextmv

from .options import MLP_REGRESSOR_PARAMETERS


def MLPRegressor(options: nextmv.Options) -> neural_network.MLPRegressor:
    """
    Creates a `sklearn.neural_network.MLPRegressor` from the provided options.

    You can import the `MLPRegressor` function directly from `neural_network`:

    ```python
    from nextmv_sklearn.neural_network import MLPRegressor
    ```

    This function takes Nextmv options and creates a scikit-learn MLPRegressor model with
    the specified parameters. The options must be compatible with the MLPRegressor parameters
    as defined in the options module.

    Parameters
    ----------
    options : nextmv.Options
        Options for the MLPRegressor. These can include:
        - hidden_layer_sizes : str
            The ith element represents the number of neurons in the ith hidden layer. (e.g. "1,2,3")
        - activation : {'identity', 'logistic', 'tanh', 'relu'}
            Activation function for the hidden layer.
        - solver : {'lbfgs', 'sgd', 'adam'}
            The solver for weight optimization.
        - alpha : float
            Strength of the L2 regularization term.
        - And other parameters as defined in MLP_REGRESSOR_PARAMETERS.

    Returns
    -------
    neural_network.MLPRegressor
        A sklearn.neural_network.MLPRegressor instance configured with the provided options.

    Examples
    --------
    >>> import nextmv
    >>> from nextmv_sklearn.neural_network import MLPRegressor
    >>> from nextmv_sklearn.neural_network.options import MLPRegressorOptions
    >>>
    >>> # Create options
    >>> options = MLPRegressorOptions().to_nextmv()
    >>> options.set("hidden_layer_sizes", "100,50")
    >>> options.set("activation", "relu")
    >>>
    >>> # Create regressor
    >>> regressor = MLPRegressor(options)
    >>> regressor.fit(X_train, y_train)
    >>> predictions = regressor.predict(X_test)
    """

    names = {p.name for p in MLP_REGRESSOR_PARAMETERS}
    opt_dict = {k: v for k, v in options.to_dict().items() if k in names if v is not None}

    return neural_network.MLPRegressor(**opt_dict)
