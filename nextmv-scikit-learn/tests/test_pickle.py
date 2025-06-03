import os
import unittest

from nextmv_sklearn.linear_model import LinearRegression, LinearRegressionOptions

import nextmv


class MLRegressorModel(nextmv.Model):
    def solve(self, input: nextmv.Input) -> nextmv.Output:
        if input.options.mode == "linear":
            model = LinearRegression(input.options)
            _ = model
            return nextmv.Output(solution={}, options=input.options)
        else:
            raise ValueError(f"Unsupported mode: {input.options.mode}")


class TestPickle(unittest.TestCase):
    def tearDown(self):
        """Removes the mlflow elements created during the test."""
        model_configuration = nextmv.ModelConfiguration(
            name="reg",
        )
        nextmv.model._cleanup_python_model(model_dir="export", model_configuration=model_configuration)

    def test_options(self):
        model = MLRegressorModel()
        # Define options (custom and sklearn).
        sklearn_opts = LinearRegressionOptions().to_nextmv()
        custom_options = nextmv.Options(
            nextmv.Option(
                name="mode",
                option_type=str,
                default="linear",
                description="ML mode (linear or xgboost).",
                required=False,
            )
        )
        options = custom_options.merge(sklearn_opts)
        # Create a model configuration so that we can pickle the model.
        model_configuration = nextmv.ModelConfiguration(
            name="reg",
            requirements=[
                "nextmv",
                "nextmv-scikit-learn",
            ],
            options=options,
        )

        # Run the model with some input data.
        input = nextmv.Input(data={}, options=options)
        output = model.solve(input)
        self.assertIsInstance(output, nextmv.Output)

        # Save (pickle) the model to a directory.
        os.makedirs("export", exist_ok=True)
        model.save("export", model_configuration)
        # Assert that the "export" directory is not empty
        self.assertTrue(len(os.listdir("export")) > 0)
