# Model

Each sub-module of `nextmv_sklearn` has a convenience function for creating
native `sklearn` model objects from `nextmv.Options`. This convenience function
allows you to set up a model using the parameters that are customized through
options. Notice that the return type is an `sklearn.<Model>`.

Consider the following examples, which make use of the classic diabetes dataset
to fit a model and then make a prediction.

## Dummy

!!! tip "Reference"

    Find the reference for the `dummy.model` module [here](../reference/dummy/model.md).

```python
import time

from nextmv_sklearn import dummy
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)

start_time = time.time()

options = dummy.DummyRegressorOptions().to_nextmv()
model = dummy.DummyRegressor(options)

fit = model.fit(X, y)
print(fit.predict(X[:1]))
```

Run the script:

```bash
$ python main.py --help
[152.13348416]
```

## Ensemble

!!! tip "Reference"

    Find the reference for the `ensemble.model` module [here](../reference/ensemble/model.md).

* `GradientBoostingRegressor`

    ```python
    import time

    from nextmv_sklearn import ensemble
    from sklearn.datasets import load_diabetes

    X, y = load_diabetes(return_X_y=True)

    start_time = time.time()

    options = ensemble.GradientBoostingRegressorOptions().to_nextmv()
    model = ensemble.GradientBoostingRegressor(options)

    fit = model.fit(X, y)
    print(fit.predict(X[:1]))
    ```

    Run the script:

    ```bash
    $ python main.py --help
    [200.87337372]
    ```

* `RandomForestRegressor`

    ```python
    import time

    from nextmv_sklearn import ensemble
    from sklearn.datasets import load_diabetes

    X, y = load_diabetes(return_X_y=True)

    start_time = time.time()

    options = ensemble.RandomForestRegressorOptions().to_nextmv()
    model = ensemble.RandomForestRegressor(options)

    fit = model.fit(X, y)
    print(fit.predict(X[:1]))
    ```

    Run the script:

    ```bash
    $ python main.py --help
    [180.54]
    ```

## Linear model

!!! tip "Reference"

    Find the reference for the `linear_model.model` module [here](../reference/linear_model/model.md).

```python
import time

from nextmv_sklearn import linear_model
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)

start_time = time.time()

options = linear_model.LinearRegressionOptions().to_nextmv()
model = linear_model.LinearRegression(options)

fit = model.fit(X, y)
print(fit.predict(X[:1]))
```

Run the script:

```bash
$ python main.py --help
[206.11667725]
```

## Neural network

!!! tip "Reference"

    Find the reference for the `neural_network.model` module [here](../reference/neural_network/model.md).

```python
import time

from nextmv_sklearn import neural_network
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)

start_time = time.time()

options = neural_network.MLPRegressorOptions().to_nextmv()
model = neural_network.MLPRegressor(options)

fit = model.fit(X, y)
print(fit.predict(X[:1]))
```

Run the script:

```bash
$ python main.py -max_iter 2500
[195.53288524]
```

## Tree

!!! tip "Reference"

    Find the reference for the `tree.model` module [here](../reference/tree/model.md).

```python
import time

from nextmv_sklearn import tree
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)

start_time = time.time()

options = tree.DecisionTreeRegressorOptions().to_nextmv()
model = tree.DecisionTreeRegressor(options)

fit = model.fit(X, y)
print(fit.predict(X[:1]))
```

Run the script:

```bash
$ python main.py
[151.]
```
