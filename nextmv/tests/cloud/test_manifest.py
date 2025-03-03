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
        self.assertEqual(manifest_python.pip_requirements, "model_requirements.txt")

    def test_manifest_python_from_dict(self):
        manifest_python_dict = {
            "pip-requirements": "foo_requirements.txt",
            "model": {
                "name": "foo_model",
            },
        }

        manifest_python = ManifestPython.from_dict(manifest_python_dict)

        self.assertEqual(manifest_python.pip_requirements, "foo_requirements.txt")
        self.assertEqual(manifest_python.model.name, "foo_model")

    def test_manifest_python_direct_instantiation(self):
        manifest_python = ManifestPython(
            pip_requirements="foo_requirements.txt",
            model={"name": "foo_model"},
        )

        self.assertEqual(manifest_python.pip_requirements, "foo_requirements.txt")
        self.assertEqual(manifest_python.model.name, "foo_model")

    def test_manifest_from_yaml(self):
        manifest = Manifest.from_yaml("tests/cloud")

        self.assertListEqual(
            manifest.files,
            ["main.py", "super_cool_model/**"],
        )

        self.assertEqual(manifest.runtime, ManifestRuntime.PYTHON)

        self.assertEqual(manifest.type, ManifestType.PYTHON)

        self.assertEqual(manifest.python.pip_requirements, "model_requirements.txt")
        self.assertEqual(manifest.python.model.name, "super_cool_model")
        self.assertListEqual(
            manifest.python.model.options,
            [
                {
                    "choices": None,
                    "default": 30,
                    "description": "Max runtime duration (in seconds).",
                    "name": "duration",
                    "param_type": "<class 'int'>",
                    "required": False,
                },
            ],
        )

        self.assertEqual(manifest.pre_push, "echo 'hello world - pre-push'")

        self.assertEqual(manifest.build.command, "echo 'hello world - build'")
        self.assertDictEqual(
            manifest.build.environment,
            {
                "SUPER": "COOL",
                "EXTRA": "AWESOME",
            },
        )
