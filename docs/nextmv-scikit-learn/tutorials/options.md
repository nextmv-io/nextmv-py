# Options

Use options to capture parameters (i.e.: configurations) for the run. The
`<Model>Options` class captures the native parameters that each model needs to
be instantiated, and the `to_nextmv()` method allows you to convert them to
[`nextmv` options][nextmv-options], for convenience.

## Dummy

!!! tip "Reference"

    Find the reference for the `dummy.options` module [here](../reference/dummy.options.md).

```python
from nextmv_sklearn import dummy

options = dummy.DummyRegressorOptions().to_nextmv()
options.parse()
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or environment variables.

options:
  -h, --help            show this help message and exit
  -strategy {mean,median,quantile,constant}, --strategy {mean,median,quantile,constant}
                        [env var: STRATEGY] (type: str): Strategy to use to generate predictions.
  -constant CONSTANT, --constant CONSTANT
                        [env var: CONSTANT] (type: float): The explicit constant as predicted by the "constant" strategy.
  -quantile QUANTILE, --quantile QUANTILE
                        [env var: QUANTILE] (type: float): The quantile to predict using the "quantile" strategy.
```

## Ensemble

!!! tip "Reference"

    Find the reference for the `ensemble.options` module [here](../reference/ensemble.options.md).

* `GradientBoostingRegressor`

    ```python
    from nextmv_sklearn import ensemble

    options = ensemble.GradientBoostingRegressorOptions().to_nextmv()
    options.parse()
    ```

    ```bash
    $ python main.py --help
    usage: main.py [options]

    Options for main.py. Use command-line arguments (highest precedence) or environment variables.

    options:
      -h, --help            show this help message and exit
      -loss {squared_error,absolute_error,huber,quantile}, --loss {squared_error,absolute_error,huber,quantile}
                            [env var: LOSS] (type: str): Loss function to be optimized.
      -learning_rate LEARNING_RATE, --learning_rate LEARNING_RATE
                            [env var: LEARNING_RATE] (type: float): Learning rate shrinks the contribution of each tree by learning_rate.
      -n_estimators N_ESTIMATORS, --n_estimators N_ESTIMATORS
                            [env var: N_ESTIMATORS] (type: int): The number of boosting stages to perform.
      -subsample SUBSAMPLE, --subsample SUBSAMPLE
                            [env var: SUBSAMPLE] (type: float): The fraction of samples to be used for fitting the individual base learners.
      -criterion {friedman_mse,squared_error}, --criterion {friedman_mse,squared_error}
                            [env var: CRITERION] (type: str): The function to measure the quality of a split.
      -min_samples_split MIN_SAMPLES_SPLIT, --min_samples_split MIN_SAMPLES_SPLIT
                            [env var: MIN_SAMPLES_SPLIT] (type: int): The minimum number of samples required to split an internal node.
      -min_samples_leaf MIN_SAMPLES_LEAF, --min_samples_leaf MIN_SAMPLES_LEAF
                            [env var: MIN_SAMPLES_LEAF] (type: int): The minimum number of samples required to be at a leaf node.
      -min_weight_fraction_leaf MIN_WEIGHT_FRACTION_LEAF, --min_weight_fraction_leaf MIN_WEIGHT_FRACTION_LEAF
                            [env var: MIN_WEIGHT_FRACTION_LEAF] (type: float): The minimum weighted fraction of the sum total of weights required to be at a leaf node.
      -max_depth MAX_DEPTH, --max_depth MAX_DEPTH
                            [env var: MAX_DEPTH] (type: int): Maximum depth of the individual regression estimators.
      -min_impurity_decrease MIN_IMPURITY_DECREASE, --min_impurity_decrease MIN_IMPURITY_DECREASE
                            [env var: MIN_IMPURITY_DECREASE] (type: float): A node will be split if this split induces a decrease of the impurity greater than or equal to this value.
      -random_state RANDOM_STATE, --random_state RANDOM_STATE
                            [env var: RANDOM_STATE] (type: int): Controls the random seed given to each Tree estimator at each boosting iteration.
      -max_features MAX_FEATURES, --max_features MAX_FEATURES
                            [env var: MAX_FEATURES] (type: int): The number of features to consider when looking for the best split.
      -alpha ALPHA, --alpha ALPHA
                            [env var: ALPHA] (type: float): The alpha-quantile of the huber loss function and the quantile loss function.
      -max_leaf_nodes MAX_LEAF_NODES, --max_leaf_nodes MAX_LEAF_NODES
                            [env var: MAX_LEAF_NODES] (type: int): Grow trees with max_leaf_nodes in best-first fashion.
      -warm_start WARM_START, --warm_start WARM_START
                            [env var: WARM_START] (type: bool): When set to True, reuse the solution of the previous call to fit and add more estimators to the ensemble, otherwise,
                            just erase the previous solution.
      -validation_fraction VALIDATION_FRACTION, --validation_fraction VALIDATION_FRACTION
                            [env var: VALIDATION_FRACTION] (type: float): The proportion of training data to set aside as validation set for early stopping.
      -n_iter_no_change N_ITER_NO_CHANGE, --n_iter_no_change N_ITER_NO_CHANGE
                            [env var: N_ITER_NO_CHANGE] (type: int): n_iter_no_change is used to decide if early stopping will be used to terminate training when validation score is
                            not improving.
      -tol TOL, --tol TOL   [env var: TOL] (type: float): Tolerance for the early stopping.
      -ccp_alpha CCP_ALPHA, --ccp_alpha CCP_ALPHA
                            [env var: CCP_ALPHA] (type: float): Complexity parameter used for Minimal Cost-Complexity Pruning.
    ```

* `RandomForestRegressor`

    ```python
    from nextmv_sklearn import ensemble

    options = ensemble.RandomForestRegressorOptions().to_nextmv()
    options.parse()
    ```

    ```bash
    $ python main.py --help
    usage: main.py [options]

    Options for main.py. Use command-line arguments (highest precedence) or environment variables.

    options:
      -h, --help            show this help message and exit
      -n_estimators N_ESTIMATORS, --n_estimators N_ESTIMATORS
                            [env var: N_ESTIMATORS] (type: int): The number of trees in the forest.
      -criterion {squared_error,absolute_error,friedman_mse,poisson}, --criterion {squared_error,absolute_error,friedman_mse,poisson}
                            [env var: CRITERION] (type: str): The function to measure the quality of a split.
      -max_depth MAX_DEPTH, --max_depth MAX_DEPTH
                            [env var: MAX_DEPTH] (type: int): The maximum depth of the tree.
      -min_samples_split MIN_SAMPLES_SPLIT, --min_samples_split MIN_SAMPLES_SPLIT
                            [env var: MIN_SAMPLES_SPLIT] (type: int): The minimum number of samples required to split an internal node.
      -min_samples_leaf MIN_SAMPLES_LEAF, --min_samples_leaf MIN_SAMPLES_LEAF
                            [env var: MIN_SAMPLES_LEAF] (type: int): The minimum number of samples required to be at a leaf node.
      -min_weight_fraction_leaf MIN_WEIGHT_FRACTION_LEAF, --min_weight_fraction_leaf MIN_WEIGHT_FRACTION_LEAF
                            [env var: MIN_WEIGHT_FRACTION_LEAF] (type: float): The minimum weighted fraction of the sum total of weights required to be at a leaf node.
      -max_features MAX_FEATURES, --max_features MAX_FEATURES
                            [env var: MAX_FEATURES] (type: int): The number of features to consider when looking for the best split.
      -max_leaf_nodes MAX_LEAF_NODES, --max_leaf_nodes MAX_LEAF_NODES
                            [env var: MAX_LEAF_NODES] (type: int): Grow trees with max_leaf_nodes in best-first fashion.
      -min_impurity_decrease MIN_IMPURITY_DECREASE, --min_impurity_decrease MIN_IMPURITY_DECREASE
                            [env var: MIN_IMPURITY_DECREASE] (type: float): A node will be split if this split induces a decrease of the impurity greater than or equal to this value.
      -bootstrap BOOTSTRAP, --bootstrap BOOTSTRAP
                            [env var: BOOTSTRAP] (type: bool): Whether bootstrap samples are used when building trees.
      -oob_score OOB_SCORE, --oob_score OOB_SCORE
                            [env var: OOB_SCORE] (type: bool): Whether to use out-of-bag samples to estimate the generalization score.
      -n_jobs N_JOBS, --n_jobs N_JOBS
                            [env var: N_JOBS] (type: int): The number of jobs to run in parallel.
      -random_state RANDOM_STATE, --random_state RANDOM_STATE
                            [env var: RANDOM_STATE] (type: int): Controls both the randomness of the bootstrapping of the samples used when building trees and the sampling of the
                            features.
      -verbose VERBOSE, --verbose VERBOSE
                            [env var: VERBOSE] (type: int): Controls the verbosity when fitting and predicting.
      -warm_start WARM_START, --warm_start WARM_START
                            [env var: WARM_START] (type: bool): When set to True, reuse the solution of the previous call to fit and add more estimators to the ensemble, otherwise,
                            just erase the previous solution.
      -ccp_alpha CCP_ALPHA, --ccp_alpha CCP_ALPHA
                            [env var: CCP_ALPHA] (type: float): Complexity parameter used for Minimal Cost-Complexity Pruning.
      -max_samples MAX_SAMPLES, --max_samples MAX_SAMPLES
                            [env var: MAX_SAMPLES] (type: int): If bootstrap is True, the number of samples to draw from X to train each base estimator.
      -monotonic_cst MONOTONIC_CST, --monotonic_cst MONOTONIC_CST
                            [env var: MONOTONIC_CST] (type: int): Indicates the monotonicity constraint to enforce on each feature.
    ```

## Linear model

!!! tip "Reference"

    Find the reference for the `linear_model.options` module [here](../reference/linear_model.options.md).

```python
from nextmv_sklearn import linear_model

options = linear_model.LinearRegressionOptions().to_nextmv()
options.parse()
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or environment variables.

options:
  -h, --help            show this help message and exit
  -fit_intercept FIT_INTERCEPT, --fit_intercept FIT_INTERCEPT
                        [env var: FIT_INTERCEPT] (type: bool): Whether to calculate the intercept for this model.
  -copy_X COPY_X, --copy_X COPY_X
                        [env var: COPY_X] (type: bool): If True, X will be copied; else, it may be overwritten.
  -n_jobs N_JOBS, --n_jobs N_JOBS
                        [env var: N_JOBS] (type: int): The number of jobs to use for the computation.
  -positive POSITIVE, --positive POSITIVE
                        [env var: POSITIVE] (type: bool): When set to True, forces the coefficients to be positive.
```

## Neural network

!!! tip "Reference"

    Find the reference for the `neural_network.options` module [here](../reference/neural_network.options.md).

```python
from nextmv_sklearn import neural_network

options = neural_network.MLPRegressorOptions().to_nextmv()
options.parse()
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or environment variables.

options:
  -h, --help            show this help message and exit
  -hidden_layer_sizes HIDDEN_LAYER_SIZES, --hidden_layer_sizes HIDDEN_LAYER_SIZES
                        [env var: HIDDEN_LAYER_SIZES] (type: str): The ith element represents the number of neurons in the ith hidden layer. (e.g. "1,2,3")
  -activation {identity,logistic,tanh,relu}, --activation {identity,logistic,tanh,relu}
                        [env var: ACTIVATION] (type: str): Activation function for the hidden layer.
  -solver {lbfgs,sgd,adam}, --solver {lbfgs,sgd,adam}
                        [env var: SOLVER] (type: str): The solver for weight optimization.
  -alpha ALPHA, --alpha ALPHA
                        [env var: ALPHA] (type: float): Strength of the L2 regularization term.
  -batch_size BATCH_SIZE, --batch_size BATCH_SIZE
                        [env var: BATCH_SIZE] (type: int): Size of minibatches for stochastic optimizers.
  -learning_rate {constant,invscaling,adaptive}, --learning_rate {constant,invscaling,adaptive}
                        [env var: LEARNING_RATE] (type: str): Learning rate schedule for weight updates.
  -learning_rate_init LEARNING_RATE_INIT, --learning_rate_init LEARNING_RATE_INIT
                        [env var: LEARNING_RATE_INIT] (type: float): The initial learning rate used.
  -power_t POWER_T, --power_t POWER_T
                        [env var: POWER_T] (type: float): The exponent for inverse scaling learning rate.
  -max_iter MAX_ITER, --max_iter MAX_ITER
                        [env var: MAX_ITER] (type: int): Maximum number of iterations.
  -shuffle SHUFFLE, --shuffle SHUFFLE
                        [env var: SHUFFLE] (type: bool): Whether to shuffle samples in each iteration.
  -random_state RANDOM_STATE, --random_state RANDOM_STATE
                        [env var: RANDOM_STATE] (type: int): Determines random number generation for weights and bias initialization, train-test split if early stopping is used,
                        and batch sampling when solver='sgd' or 'adam'.
  -tol TOL, --tol TOL   [env var: TOL] (type: float): Tolerance for the optimization.
  -verbose VERBOSE, --verbose VERBOSE
                        [env var: VERBOSE] (type: bool): Whether to print progress messages to stdout.
  -warm_start WARM_START, --warm_start WARM_START
                        [env var: WARM_START] (type: bool): When set to True, reuse the solution of the previous call to fit as initialization.
  -momentum MOMENTUM, --momentum MOMENTUM
                        [env var: MOMENTUM] (type: float): Momentum for gradient descent update.
  -nesterovs_momentum NESTEROVS_MOMENTUM, --nesterovs_momentum NESTEROVS_MOMENTUM
                        [env var: NESTEROVS_MOMENTUM] (type: bool): Whether to use Nesterov's momentum.
  -early_stopping EARLY_STOPPING, --early_stopping EARLY_STOPPING
                        [env var: EARLY_STOPPING] (type: bool): Whether to use early stopping to terminate training when validation score is not improving.
  -validation_fraction VALIDATION_FRACTION, --validation_fraction VALIDATION_FRACTION
                        [env var: VALIDATION_FRACTION] (type: float): The proportion of training data to set aside as validation set for early stopping.
  -beta_1 BETA_1, --beta_1 BETA_1
                        [env var: BETA_1] (type: float): Exponential decay rate for estimates of first moment vector in adam.
  -beta_2 BETA_2, --beta_2 BETA_2
                        [env var: BETA_2] (type: float): Exponential decay rate for estimates of second moment vector in adam.
  -epsilon EPSILON, --epsilon EPSILON
                        [env var: EPSILON] (type: float): Value for numerical stability in adam.
  -n_iter_no_change N_ITER_NO_CHANGE, --n_iter_no_change N_ITER_NO_CHANGE
                        [env var: N_ITER_NO_CHANGE] (type: int): Maximum number of epochs to not meet tol improvement.
  -max_fun MAX_FUN, --max_fun MAX_FUN
                        [env var: MAX_FUN] (type: int): Only used when solver='lbfgs'.
```

## Tree

!!! tip "Reference"

    Find the reference for the `tree.options` module [here](../reference/tree.options.md).

```python
from nextmv_sklearn import tree

options = tree.DecisionTreeRegressorOptions().to_nextmv()
options.parse()
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or environment variables.

options:
  -h, --help            show this help message and exit
  -criterion {squared_error,friedman_mse,absolute_error,poisson}, --criterion {squared_error,friedman_mse,absolute_error,poisson}
                        [env var: CRITERION] (default: squared_error) (type: str): The function to measure the quality of a split.
  -splitter {best,random}, --splitter {best,random}
                        [env var: SPLITTER] (default: best) (type: str): The strategy used to choose the split at each node.
  -max_depth MAX_DEPTH, --max_depth MAX_DEPTH
                        [env var: MAX_DEPTH] (type: int): The maximum depth of the tree.
  -min_samples_split MIN_SAMPLES_SPLIT, --min_samples_split MIN_SAMPLES_SPLIT
                        [env var: MIN_SAMPLES_SPLIT] (type: int): The minimum number of samples required to split an internal node.
  -min_samples_leaf MIN_SAMPLES_LEAF, --min_samples_leaf MIN_SAMPLES_LEAF
                        [env var: MIN_SAMPLES_LEAF] (type: int): The minimum number of samples required to be at a leaf node.
  -min_weight_fraction_leaf MIN_WEIGHT_FRACTION_LEAF, --min_weight_fraction_leaf MIN_WEIGHT_FRACTION_LEAF
                        [env var: MIN_WEIGHT_FRACTION_LEAF] (type: float): The minimum weighted fraction of the sum total of weights required to be at a leaf node.
  -max_features MAX_FEATURES, --max_features MAX_FEATURES
                        [env var: MAX_FEATURES] (type: int): The number of features to consider when looking for the best split.
  -random_state RANDOM_STATE, --random_state RANDOM_STATE
                        [env var: RANDOM_STATE] (type: int): Controls the randomness of the estimator.
  -max_leaf_nodes MAX_LEAF_NODES, --max_leaf_nodes MAX_LEAF_NODES
                        [env var: MAX_LEAF_NODES] (type: int): Grow a tree with max_leaf_nodes in best-first fashion.
  -min_impurity_decrease MIN_IMPURITY_DECREASE, --min_impurity_decrease MIN_IMPURITY_DECREASE
                        [env var: MIN_IMPURITY_DECREASE] (type: float): A node will be split if this split induces a decrease of the impurity #.
  -ccp_alpha CCP_ALPHA, --ccp_alpha CCP_ALPHA
                        [env var: CCP_ALPHA] (type: float): Complexity parameter used for Minimal Cost-Complexity Pruning.
```

## Merge options together

You can merge [`nextmv.Options`][nextmv-options] together using the `merge`
method.

```python
from nextmv_sklearn import dummy, linear_model

opt1 = linear_model.LinearRegressionOptions().to_nextmv()
opt2 = dummy.DummyRegressorOptions().to_nextmv()

options = opt1.merge(opt2)
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or environment variables.

options:
  -h, --help            show this help message and exit
  -fit_intercept FIT_INTERCEPT, --fit_intercept FIT_INTERCEPT
                        [env var: FIT_INTERCEPT] (type: bool): Whether to calculate the intercept for this model.
  -copy_X COPY_X, --copy_X COPY_X
                        [env var: COPY_X] (type: bool): If True, X will be copied; else, it may be overwritten.
  -n_jobs N_JOBS, --n_jobs N_JOBS
                        [env var: N_JOBS] (type: int): The number of jobs to use for the computation.
  -positive POSITIVE, --positive POSITIVE
                        [env var: POSITIVE] (type: bool): When set to True, forces the coefficients to be positive.
  -strategy {mean,median,quantile,constant}, --strategy {mean,median,quantile,constant}
                        [env var: STRATEGY] (type: str): Strategy to use to generate predictions.
  -constant CONSTANT, --constant CONSTANT
                        [env var: CONSTANT] (type: float): The explicit constant as predicted by the "constant" strategy.
  -quantile QUANTILE, --quantile QUANTILE
                        [env var: QUANTILE] (type: float): The quantile to predict using the "quantile" strategy.
```

Notice how the `LinearRegressionOptions` are merged with the
`DummyRegressorOptions` and you can access the options from both sets.

[nextmv-options]: ../../nextmv/tutorials/options.md
