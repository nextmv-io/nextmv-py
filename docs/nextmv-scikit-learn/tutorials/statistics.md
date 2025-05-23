# Statistics

`<Model>Statistics` allows access to the statistics of an `sklearn.<Model>`. It
is a convenience function that will collect a simple set of statistics.

Consider the same scripts shown in the [model section][model], which fit and
predict with the diabetes dataset. You may use the `<Model>Statistics` to
obtain the statistics of the model. This convenience functionality is provided
out of the box, but we recommend that you customize how the model is
interpreted to extract statistics.

## Dummy

!!! tip "Reference"

    Find the reference for the `dummy.statistics` module [here](../reference/dummy.statistics.md).

```python
import json

from nextmv_sklearn import dummy

# Model code here.

statistics = dummy.DummyRegressorStatistics(fit, X, y, run_duration_start=start_time)
print(json.dumps(statistics.to_dict(), indent=2))
```

Run the script:

```bash
python main.py
{
  "run": {
    "duration": 0.0009911060333251953
  },
  "result": {
    "custom": {
      "score": 0.0
    }
  },
  "series_data": {},
  "schema": "v1"
}
```

## Ensemble

!!! tip "Reference"

    Find the reference for the `ensemble.statistics` module [here](../reference/ensemble.statistics.md).

```python
import json

from nextmv_sklearn import ensemble

# Model code here.

statistics = ensemble.GradientBoostingRegressorStatistics(fit, X, y, run_duration_start=start_time)
print(json.dumps(statistics.to_dict(), indent=2))

```

Run the script:

```bash
python main.py
{
  "run": {
    "duration": 0.06733989715576172
  },
  "result": {
    "custom": {
      "depth": 3,
      "feature_importances_": [
        0.04838302190078237,
        0.013922652165423995,
        0.261283146271802,
        0.10170455309660177,
        0.028599216988454114,
        0.04562385785680753,
        0.040315277921146336,
        0.01589286353541712,
        0.402315668430028,
        0.04195974183353675
      ],
      "score": 0.7990392018966865
    }
  },
  "series_data": {},
  "schema": "v1"
}
```

```python
import json

from nextmv_sklearn import ensemble

# Model code here.

statistics = ensemble.RandomForestRegressorStatistics(fit, X, y, run_duration_start=start_time)
print(json.dumps(statistics.to_dict(), indent=2))

```

Run the script:

```bash
python main.py
{
  "run": {
    "duration": 0.15362906455993652
  },
  "result": {
    "custom": {
      "feature_importances_": [
        0.05804547555574568,
        0.011942445816542004,
        0.26046692216365497,
        0.09831628970586574,
        0.04414312280601346,
        0.05823550762545449,
        0.05163041383919266,
        0.024326122944217127,
        0.323262101101696,
        0.06963159844161786
      ],
      "score": 0.9180285142096314
    }
  },
  "series_data": {},
  "schema": "v1"
}
```

## Linear model

!!! tip "Reference"

    Find the reference for the `linear_model.statistics` module [here](../reference/linear_model.statistics.md).

```python
import json

from nextmv_sklearn import linear_model

# Model code here.

statistics = linear_model.LinearRegressionStatistics(fit, X, y, run_duration_start=start_time)
print(json.dumps(statistics.to_dict(), indent=2))
```

Run the script:

```bash
python main.py
{
  "run": {
    "duration": 0.0011751651763916016
  },
  "result": {
    "custom": {
      "score": 0.5177484222203499
    }
  },
  "series_data": {},
  "schema": "v1"
}
```

## Neural network

!!! tip "Reference"

    Find the reference for the `neural_network.statistics` module [here](../reference/neural_network.statistics.md).

```python
import json

from nextmv_sklearn import neural_network

# Model code here.

statistics = neural_network.MLPRegressorStatistics(fit, X, y, run_duration_start=start_time)
print(json.dumps(statistics.to_dict(), indent=2))
```

Run the script:

```bash
$ python main.py -max_iter 2500
{
  "run": {
    "duration": 0.9213109016418457
  },
  "result": {
    "custom": {
      "score": 0.5105739729721858
    }
  },
  "series_data": {},
  "schema": "v1"
}
```

## Tree

!!! tip "Reference"

    Find the reference for the `tree.statistics` module [here](../reference/tree.statistics.md).

```python
import json

from nextmv_sklearn import tree

# Model code here.

statistics = tree.DecisionTreeRegressorStatistics(fit, X, y, run_duration_start=start_time)
print(json.dumps(statistics.to_dict(), indent=2))
```

Run the script:

```bash
$ python main.py
{
  "run": {
    "duration": 0.0031609535217285156
  },
  "result": {
    "custom": {
      "depth": 20,
      "feature_importances_": [
        0.03648268541156411,
        0.008967396431459116,
        0.23191566128391577,
        0.082693316388564,
        0.07347510143597435,
        0.056688846730468985,
        0.07264156168631583,
        0.013709115567881148,
        0.3487799461424682,
        0.07464636892138855
      ],
      "n_leaves": 433,
      "score": 1.0
    }
  },
  "series_data": {},
  "schema": "v1"
}
```

[model]: ./model.md
