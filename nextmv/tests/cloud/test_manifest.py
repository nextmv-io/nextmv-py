import unittest

from nextmv.cloud.manifest import Manifest, ManifestOption, ManifestPython, ManifestRuntime, ManifestType
from nextmv.model import ModelConfiguration
from nextmv.options import Option, Options


class TestManifest(unittest.TestCase):
    def test_from_model_configuration(self):
        options = Options(
            Option("param1", str, ""),
            Option("param2", str, ""),
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
                    "options": model_configuration.options.options_dict(),
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

    def test_extract_options(self):
        manifest = Manifest.from_yaml("tests/cloud")
        options = manifest.extract_options()
        self.assertEqual(len(options.options), 4)

        found = {
            "string": False,
            "boolean": False,
            "integer": False,
            "float": False,
        }

        for option in options.options:
            if option.option_type is str:
                found["string"] = True
            elif option.option_type is bool:
                found["boolean"] = True
            elif option.option_type is int:
                found["integer"] = True
            elif option.option_type is float:
                found["float"] = True

        self.assertTrue(found["string"])
        self.assertTrue(found["boolean"])
        self.assertTrue(found["integer"])
        self.assertTrue(found["float"])

    def test_from_options(self):
        options = Options(
            Option("param1", str, "default", "A description", True),
            Option("param2", bool, True, "A description", True),
            Option("param3", int, 42, "A description", True),
            Option("param4", float, 3.14, "A description", True),
        )
        manifest = Manifest.from_options(options)

        self.assertListEqual(manifest.files, ["main.py"])
        self.assertEqual(manifest.runtime, ManifestRuntime.PYTHON)
        self.assertEqual(manifest.type, ManifestType.PYTHON)
        self.assertEqual(manifest.python.pip_requirements, "requirements.txt")
        self.assertListEqual(
            manifest.options,
            [
                ManifestOption(
                    name="param1",
                    option_type="string",
                    default="default",
                    description="A description",
                    required=True,
                ),
                ManifestOption(
                    name="param2",
                    option_type="boolean",
                    default=True,
                    description="A description",
                    required=True,
                ),
                ManifestOption(
                    name="param3",
                    option_type="integer",
                    default=42,
                    description="A description",
                    required=True,
                ),
                ManifestOption(
                    name="param4",
                    option_type="float",
                    default=3.14,
                    description="A description",
                    required=True,
                ),
            ],
        )


class TestManifestOption(unittest.TestCase):
    def test_from_option(self):
        test_cases = [
            {
                "name": "string option",
                "option": Option("param1", str, "default", "A description", True),
                "expected_option_type": "string",
            },
            {
                "name": "bool option",
                "option": Option("param2", bool, True, "A description", True),
                "expected_option_type": "boolean",
            },
            {
                "name": "int option",
                "option": Option("param3", int, 42, "A description", True),
                "expected_option_type": "integer",
            },
            {
                "name": "float option",
                "option": Option("param4", float, 3.14, "A description", True),
                "expected_option_type": "float",
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case["name"]):
                option = test_case["option"]
                manifest_option = ManifestOption.from_option(option)

                self.assertEqual(manifest_option.name, option.name)
                self.assertEqual(manifest_option.option_type, test_case["expected_option_type"])
                self.assertEqual(manifest_option.default, option.default)
                self.assertEqual(manifest_option.description, option.description)
                self.assertEqual(manifest_option.required, option.required)
                self.assertEqual(manifest_option.choices, option.choices)

    def test_to_option(self):
        test_cases = [
            {
                "name": "string option",
                "manifest_option": ManifestOption(
                    name="param1",
                    option_type="string",
                    default="default",
                    description="A description",
                    required=True,
                ),
                "expected_option_type": str,
            },
            {
                "name": "bool option",
                "manifest_option": ManifestOption(
                    name="param2",
                    option_type="boolean",
                    default=True,
                    description="A description",
                    required=True,
                ),
                "expected_option_type": bool,
            },
            {
                "name": "int option",
                "manifest_option": ManifestOption(
                    name="param3",
                    option_type="integer",
                    default=42,
                    description="A description",
                    required=True,
                ),
                "expected_option_type": int,
            },
            {
                "name": "float option",
                "manifest_option": ManifestOption(
                    name="param4",
                    option_type="float",
                    default=3.14,
                    description="A description",
                    required=True,
                ),
                "expected_option_type": float,
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case["name"]):
                manifest_option = test_case["manifest_option"]
                option = manifest_option.to_option()

                self.assertEqual(option.name, manifest_option.name)
                self.assertIs(option.option_type, test_case["expected_option_type"])
                self.assertEqual(option.default, manifest_option.default)
                self.assertEqual(option.description, manifest_option.description)
                self.assertEqual(option.required, manifest_option.required)
                self.assertEqual(option.choices, manifest_option.choices)
