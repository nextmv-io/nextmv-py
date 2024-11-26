import unittest

from nextmv.cloud.manifest import Manifest, ManifestPython, ManifestRuntime, ManifestType
from nextmv.model import ModelConfiguration
from nextmv.options import Options, Parameter


class TestManifest(unittest.TestCase):
    def test_from_model_configuration(self):
        options = Options(
            Parameter("param1", str, ""),
            Parameter("param2", str, ""),
        )
        model_configuration = ModelConfiguration(
            name="super_cool_model",
            requirements=[
                "one_requirement",
                "another_requirement",
            ],
            options=options,
        )
        manifest = Manifest.from_model_configuration(model_configuration)

        self.assertListEqual(
            manifest.files,
            ["main.py", f"{model_configuration.name}/**"],
        )
        self.assertEqual(manifest.runtime, ManifestRuntime.PYTHON)
        self.assertEqual(manifest.type, ManifestType.PYTHON)

        manifest_python = ManifestPython.from_dict(
            {
                "pip-requirements": "model_requirements.txt",
                "model": {
                    "name": model_configuration.name,
                    "options": model_configuration.options.parameters_dict(),
                },
            }
        )
        self.assertEqual(manifest.python, manifest_python)
