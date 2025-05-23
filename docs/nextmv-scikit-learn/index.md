# Overview

The [Nextmv & scikit-learn Python SDK][nextmv-scikit-learn],
`nextmv-scikit-learn`, is a package to interact programmatically with Nextmv
and the scikit-learn machine library, from Python. A great way to get started
is to check out the [community apps][community-apps-get-started]. The following
apps are a non-exhaustive list of concrete examples for using this SDK:

* [`python-nextmv-scikit-learn-diabetes`][python-nextmv-scikit-learn-diabetes]

The `nextmv-scikit-learn` package is a wrapper around the `scikit-learn`
library to make it easy to use with Nextmv. It provides support for these
models:

* `dummy`:
  * [`DummyRegressor`][dummy-regressor]
* `ensemble`:
  * [`GradientBoostingRegressor`][gradient-boosting-regressor]
  * [`RandomForestRegressor`][random-forest-regressor]
* `linear_model`:
  * [`LinearRegression`][linear-regression]
* `neural_network`:
  * [`MLPRegressor`][mlp-regressor]
* `tree`:
  * [`DecisionTreeRegressor`][decision-tree-regressor]

## Installation

The package is hosted on [PyPI][nextmv-scikit-learn-pypi]. Python `>=3.9` is
required.

Install via `pip`:

```bash
pip install nextmv-scikit-learn
```

!!! tip

    Note that `nextmv-scikit-learn` installs the `nextmv_sklearn` package, which 
    is the importable name for the SDK.

[nextmv-scikit-learn-pypi]: https://pypi.org/project/nextmv-scikit-learn/
[nextmv-scikit-learn]: https://github.com/nextmv-io/nextmv-py/tree/develop/nextmv-scikit-learn
[community-apps-get-started]: https://docs.nextmv.io/docs/use-cases/community-apps/get-started
[python-nextmv-scikit-learn-diabetes]: https://github.com/nextmv-io/community-apps/blob/develop/python-nextmv-scikit-learn-diabetes
[dummy-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyRegressor.html
[linear-regression]: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
[gradient-boosting-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html
[random-forest-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
[mlp-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html
[decision-tree-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html
