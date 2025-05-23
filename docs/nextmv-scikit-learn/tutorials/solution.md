# Solution

`<Model>Solution` allows access to the solution of an `sklearn.<Model>`. The
fitted model is considered a "solution". You may create a solution object from
a model and export it to a file. At any moment, the solution (fitted model) can
be loaded from a file that holds the correct information.

Consider the same scripts shown in the [model section][model] and [statistics
section][statistics], which fit, predict and obtain statistics with the
diabetes dataset. You may use the `<Model>Solution` to obtain and write the
solution of the model. After it has been exported, you can load the solution,
create a fitted model from it, and make a basic prediction.

## Dummy

!!! tip "Reference"

    Find the reference for the `dummy.solution` module [here](../reference/dummy.solution.md).

Write the solution.

```python
from nextmv_sklearn import dummy

import nextmv

# Model and statistics code here.

# Create the solution object from the model and construct an output.
solution = dummy.DummyRegressorSolution.from_model(fit)
output = nextmv.Output(
    options=options,
    solution=solution.to_dict(),
    statistics=statistics,
)

# Export the output, with the solution, to a file.
file_path = "regressor.json"
nextmv.write(output, file_path)
```

After running the script, inspect the output:

```bash
cat regressor.json
{
  "options": {
    "strategy": null,
    "constant": null,
    "quantile": null
  },
  "solution": {
    "class": {
      "module": "nextmv_sklearn.dummy.solution",
      "name": "DummyRegressorSolution"
    },
    "attributes": {
      "constant_": [
        [
          152.13348416289594
        ]
      ],
      "n_features_in_": 10,
      "n_outputs_": 1
    }
  },
  "statistics": {
    "run": {
      "duration": 0.0009088516235351562
    },
    "result": {
      "custom": {
        "score": 0.0
      }
    },
    "series_data": {},
    "schema": "v1"
  },
  "assets": []
}
```

Load the solution and make a prediction.

```python
import nextmv


# Load the solution from the file.
input = nextmv.load(path=file_path)
loaded_solution = nextmv.from_dict(input.data["solution"])

# Convert the solution to a model and make a prediction.
loaded_fit = loaded_solution.to_model()
print(loaded_fit.predict(X[:1]))
```

Run the script:

```bash
python main.py
[152.13348416]
```

## Ensemble

!!! tip "Reference"

    Find the reference for the `ensemble.solution` module [here](../reference/ensemble.solution.md).

### Gradient boosting

Write the solution.

```python
from nextmv_sklearn import ensemble

import nextmv

# Model and statistics code here.

# Create the solution object from the model and construct an output.
solution = ensemble.GradientBoostingRegressorSolution.from_model(fit)
output = nextmv.Output(
    options=options,
    solution=solution.to_dict(),
    statistics=statistics,
)

# Export the output, with the solution, to a file.
file_path = "regressor.json"
nextmv.write(output, file_path)
```

After running the script, inspect the output:

```bash
cat regressor.json
{
  "options": {
    "loss": null,
    "learning_rate": null,
    "n_estimators": null,
    "subsample": null,
    "criterion": null,
    "min_samples_split": null,
    "min_samples_leaf": null,
    "min_weight_fraction_leaf": null,
    "max_depth": null,
    "min_impurity_decrease": null,
    "random_state": null,
    "max_features": null,
    "alpha": null,
    "max_leaf_nodes": null,
    "warm_start": null,
    "validation_fraction": null,
    "n_iter_no_change": null,
    "tol": null,
    "ccp_alpha": null
  },
  "solution": {
    "class": {
      "module": "nextmv_sklearn.ensemble.solution",
      "name": "GradientBoostingRegressorSolution"
    },
    "attributes": {
      "n_estimators_": 100,
      "n_trees_per_iteration_": 1,
      "oob_score_": 0.0,
      "train_score_": [
        5365.788686570168,
        ...
        1195.018648214559,
        1191.6744015438958
      ],
      "init_": {
        "constant_": [
          [
            152.13348416289594
          ]
        ],
        "n_features_in_": 10,
        "n_outputs_": 1
      },
      "estimators_": [
        {
          "max_features_": 10,
          "n_features_in_": 10,
          "n_outputs_": 1,
          "tree_": "gASVqwYAAAAA....QJR0lGJ1Yi4="
        }
      ],
      "n_features_in_": 10,
      "max_features_": 10,
      "loss": "gASVYwEAAAA....AGgZiWgaiXVidWIu"
    }
  },
  "statistics": {
    "run": {
      "duration": 0.06821298599243164
    },
    "result": {
      "custom": {
        "depth": 3,
        "feature_importances_": [
          0.04868904207548975,
          0.013906683009910865,
          ...
          0.041790175253534984
        ],
        "score": 0.7990392018966865
      }
    },
    "series_data": {},
    "schema": "v1"
  },
  "assets": []
}
```

Load the solution and make a prediction.

```python
import nextmv


# Load the solution from the file.
input = nextmv.load(path=file_path)
loaded_solution = nextmv.from_dict(input.data["solution"])

# Convert the solution to a model and make a prediction.
loaded_fit = loaded_solution.to_model()
print(loaded_fit.predict(X[:1]))
```

Run the script:

```bash
python main.py
[200.87337372]
```

### Random forest

Write the solution.

```python
from nextmv_sklearn import ensemble

import nextmv

# Model and statistics code here.

# Create the solution object from the model and construct an output.
solution = ensemble.RandomForestRegressorSolution.from_model(fit)
output = nextmv.Output(
    options=options,
    solution=solution.to_dict(),
    statistics=statistics,
)

# Export the output, with the solution, to a file.
file_path = "regressor.json"
nextmv.write(output, file_path)
```

After running the script, inspect the output:

```bash
cat regressor.json
{
  "options": {
    "n_estimators": null,
    "criterion": null,
    "max_depth": null,
    "min_samples_split": null,
    "min_samples_leaf": null,
    "min_weight_fraction_leaf": null,
    "max_features": null,
    "max_leaf_nodes": null,
    "min_impurity_decrease": null,
    "bootstrap": null,
    "oob_score": null,
    "n_jobs": null,
    "random_state": null,
    "verbose": null,
    "warm_start": null,
    "ccp_alpha": null,
    "max_samples": null,
    "monotonic_cst": null
  },
  "solution": {
    "class": {
      "module": "nextmv_sklearn.ensemble.solution",
      "name": "RandomForestRegressorSolution"
    },
    "attributes": {
      "estimator_": {
        "max_features_": 0,
        "n_features_in_": 0,
        "n_outputs_": 0
      },
      "estimators_": [
        {
          "max_features_": 10,
          "n_features_in_": 10,
          "n_outputs_": 1,
          "tree_": "gASVAHFAAAAAA....BtQJR0lGJ1Yi4="
        }
      ],
      "n_features_in_": 10,
      "n_outputs_": 1,
      "oob_score_": 0.0
    }
  },
  "statistics": {
    "run": {
      "duration": 0.15402698516845703
    },
    "result": {
      "custom": {
        "feature_importances_": [
          0.05862192557250181, 0.012334872517744695, 0.28574949264657873,
          0.09883856630804999, 0.047828611880482576, 0.05744602179282225,
          0.05022167910320828, 0.0236904772411412, 0.2967779353746083,
          0.06849041756286224
        ],
        "score": 0.9184641072754306
      }
    },
    "series_data": {},
    "schema": "v1"
  },
  "assets": []
}
```

Load the solution and make a prediction.

```python
import nextmv


# Load the solution from the file.
input = nextmv.load(path=file_path)
loaded_solution = nextmv.from_dict(input.data["solution"])

# Convert the solution to a model and make a prediction.
loaded_fit = loaded_solution.to_model()
print(loaded_fit.predict(X[:1]))
```

Run the script:

```bash
python main.py
[176.1]
```

## Linear model

!!! tip "Reference"

    Find the reference for the `linear_model.solution` module [here](../reference/linear_model.solution.md).

Write the solution.

```python
from nextmv_sklearn import linear_model

import nextmv

# Model and statistics code here.

# Create the solution object from the model and construct an output.
solution = linear_model.LinearRegressionSolution.from_model(fit)
output = nextmv.Output(
    options=options,
    solution=solution.to_dict(),
    statistics=statistics,
)

# Export the output, with the solution, to a file.
file_path = "regressor.json"
nextmv.write(output, file_path)
```

After running the script, inspect the output:

```bash
cat regressor.json
{
  "options": {
    "fit_intercept": null,
    "copy_X": null,
    "n_jobs": null,
    "positive": null
  },
  "solution": {
    "class": {
      "module": "nextmv_sklearn.linear_model.solution",
      "name": "LinearRegressionSolution"
    },
    "attributes": {
      "coef_": [
        -10.009866299810263,
        -239.81564367242262,
        519.8459200544598,
        324.38464550232345,
        -792.1756385522301,
        476.7390210052578,
        101.04326793803399,
        177.0632376713463,
        751.273699557104,
        67.62669218370486
      ],
      "rank_": 10,
      "singular_": [
        2.006043556394722,
        1.2216053690118982,
        1.0981649507815319,
        0.9774847330082032,
        0.8137452864786221,
        0.7763485529194514,
        0.7325064179373295,
        0.6585453943089912,
        0.2798571500982059,
        0.092524212112576
      ],
      "intercept_": 152.13348416289597,
      "n_features_in_": 10
    }
  },
  "statistics": {
    "run": {
      "duration": 0.0015370845794677734
    },
    "result": {
      "custom": {
        "score": 0.5177484222203499
      }
    },
    "series_data": {},
    "schema": "v1"
  },
  "assets": []
}
```

Load the solution and make a prediction.

```python
import nextmv


# Load the solution from the file.
input = nextmv.load(path=file_path)
loaded_solution = nextmv.from_dict(input.data["solution"])

# Convert the solution to a model and make a prediction.
loaded_fit = loaded_solution.to_model()
print(loaded_fit.predict(X[:1]))
```

Run the script:

```bash
python main.py
[206.11667725]
```

## Neural network

!!! tip "Reference"

    Find the reference for the `neural_network.solution` module [here](../reference/neural_network.solution.md).

Write the solution.

```python
from nextmv_sklearn import neural_network

import nextmv

# Model and statistics code here.

# Create the solution object from the model and construct an output.
solution = neural_network.MLPRegressorSolution.from_model(fit)
output = nextmv.Output(
    options=options,
    solution=solution.to_dict(),
    statistics=statistics,
)

# Export the output, with the solution, to a file.
file_path = "regressor.json"
nextmv.write(output, file_path)
```

After running the script, inspect the output:

```bash
cat regressor.json
{
  "options": {
    "hidden_layer_sizes": null,
    "activation": null,
    "solver": null,
    "alpha": null,
    "batch_size": null,
    "learning_rate": null,
    "learning_rate_init": null,
    "power_t": null,
    "max_iter": 2500,
    "shuffle": null,
    "random_state": null,
    "tol": null,
    "verbose": null,
    "warm_start": null,
    "momentum": null,
    "nesterovs_momentum": null,
    "early_stopping": null,
    "validation_fraction": null,
    "beta_1": null,
    "beta_2": null,
    "epsilon": null,
    "n_iter_no_change": null,
    "max_fun": null
  },
  "solution": {
    "class": {
      "module": "nextmv_sklearn.neural_network.solution",
      "name": "MLPRegressorSolution"
    },
    "attributes": {
      "loss_": 1446.176859835485,
      "best_loss_": 1445.790195444945,
      "loss_curve_": [
        14531.186602180687,
        ...
        1446.024979302395,
        1446.176859835485
      ],
      "t_": 893724,
      "coefs_": [
        [
          [
            -0.017255350152175514,
            ...
            0.04931994332298196
          ],
          ...
        ],
        [
          [
            -0.021388414548190945
          ],
          ...
        ]
      ],
      "intercepts_": [
        [
          -0.03335657429574056,
          ...
          -0.03597971253262282
        ],
        ...
      ],
      "n_features_in_": 10,
      "n_iter_": 2022,
      "n_layers_": 3,
      "n_outputs_": 1,
      "out_activation_": "identity"
    }
  },
  "statistics": {
    "run": {
      "duration": 0.9377310276031494
    },
    "result": {
      "custom": {
        "score": 0.5123771786534843
      }
    },
    "series_data": {},
    "schema": "v1"
  },
  "assets": []
}
```

Load the solution and make a prediction.

```python
import nextmv


# Load the solution from the file.
input = nextmv.load(path=file_path)
loaded_solution = nextmv.from_dict(input.data["solution"])

# Convert the solution to a model and make a prediction.
loaded_fit = loaded_solution.to_model()
print(loaded_fit.predict(X[:1]))
```

Run the script:

```bash
python main.py -max_iter 2500
[199.38432603]
```

## Tree

!!! tip "Reference"

    Find the reference for the `tree.solution` module [here](../reference/tree.solution.md).

Write the solution.

```python
from nextmv_sklearn import tree

import nextmv

# Model and statistics code here.

# Create the solution object from the model and construct an output.
solution = tree.DecisionTreeRegressorSolution.from_model(fit)
output = nextmv.Output(
    options=options,
    solution=solution.to_dict(),
    statistics=statistics,
)

# Export the output, with the solution, to a file.
file_path = "regressor.json"
nextmv.write(output, file_path)
```

After running the script, inspect the output:

```bash
cat regressor.json
{
  "options": {
    "criterion": "squared_error",
    "splitter": "best",
    "max_depth": null,
    "min_samples_split": null,
    "min_samples_leaf": null,
    "min_weight_fraction_leaf": null,
    "max_features": null,
    "random_state": null,
    "max_leaf_nodes": null,
    "min_impurity_decrease": null,
    "ccp_alpha": null
  },
  "solution": {
    "class": {
      "module": "nextmv_sklearn.tree.solution",
      "name": "DecisionTreeRegressorSolution"
    },
    "attributes": {
      "max_features_": 10,
      "n_features_in_": 10,
      "n_outputs_": 1,
      "tree_": "gASVMfUAAAAAAACMEnNrbGVhcm4udH...R0lGJ1Yi4="
    }
  },
  "statistics": {
    "run": {
      "duration": 0.0044820308685302734
    },
    "result": {
      "custom": {
        "depth": 20,
        "feature_importances_": [
          0.03869204610835461,
          0.010414593479079177,
          0.23623009367609873,
          0.08523716847272961,
          0.06178429111080888,
          0.07221426644525238,
          0.07449166752232912,
          0.012499198167788545,
          0.3394458949538394,
          0.06899078006371957
        ],
        "n_leaves": 432,
        "score": 1.0
      }
    },
    "series_data": {},
    "schema": "v1"
  },
  "assets": []
}
```

Load the solution and make a prediction.

```python
import nextmv


# Load the solution from the file.
input = nextmv.load(path=file_path)
loaded_solution = nextmv.from_dict(input.data["solution"])

# Convert the solution to a model and make a prediction.
loaded_fit = loaded_solution.to_model()
print(loaded_fit.predict(X[:1]))
```

Run the script:

```bash
python main.py
[151.]
```

[model]: ./model.md
[statistics]: ./statistics.md
