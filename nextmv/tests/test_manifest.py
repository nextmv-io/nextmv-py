import unittest

from nextmv.manifest import (
    Manifest,
    ManifestContent,
    ManifestContentMultiFile,
    ManifestContentMultiFileInput,
    ManifestContentMultiFileOutput,
    ManifestOption,
    ManifestOptions,
    ManifestOptionUI,
    ManifestPython,
    ManifestRuntime,
    ManifestType,
    ManifestValidation,
)
from nextmv.model import ModelConfiguration
from nextmv.options import Option, Options, OptionsEnforcement


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

    def test_from_model_configuration_with_validation(self):
        options = Options(
            Option("param1", str, "default_value", "A description", True),
            Option("param2", bool, True, "A description", True),
        )

        validation_config = OptionsEnforcement(
            strict=True,
            validation_enforce=True,
        )

        model_configuration = ModelConfiguration(
            name="super_cool_model",
            requirements=[
                "one_requirement",
                "another_requirement",
            ],
            options=options,
            options_enforcement=validation_config,
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
        self.assertEqual(manifest.configuration.options.strict, validation_config.strict)
        self.assertEqual(manifest.configuration.options.validation.enforce, "all")
        self.assertEqual(manifest.configuration.options.items, ManifestOptions.from_options(options).items)

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
        self.assertEqual(manifest.configuration.options.format, ["-{{name}}", "{{value}}"])

        self.assertDictEqual(
            manifest.configuration.content.to_dict(),
            {
                "format": "multi-file",
                "multi-file": {
                    "input": {
                        "path": "my-inputs",
                    },
                    "output": {
                        "statistics": "my-outputs/statistics.json",
                        "assets": "my-outputs/assets.json",
                        "solutions": "my-outputs/solutions",
                    },
                },
            },
        )

    def test_extract_options(self):
        manifest = Manifest.from_yaml("tests/cloud")
        options = manifest.extract_options()
        self.assertEqual(len(options.options), 5)

        found = {
            "string": False,
            "bool": False,
            "int": False,
            "float": False,
        }

        for option in options.options:
            if option.option_type is str:
                found["string"] = True
            elif option.option_type is bool:
                found["bool"] = True
            elif option.option_type is int:
                found["int"] = True
            elif option.option_type is float:
                found["float"] = True

        self.assertTrue(found["string"])
        self.assertTrue(found["bool"])
        self.assertTrue(found["int"])
        self.assertTrue(found["float"])

        self.assertEqual(options.options[3].display_name, "a float parameter")

        self.assertEqual(options.options[4].control_type, "select")
        self.assertEqual(options.options[4].hidden_from, ["operator"])

        manifest2 = Manifest(
            files=["main.py"],
        )
        options2 = manifest2.extract_options()
        self.assertIsNone(options2)

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
        self.assertEqual(manifest.configuration.options.strict, False)
        self.assertEqual(manifest.configuration.options.validation, ManifestValidation(enforce="none"))
        self.assertListEqual(
            manifest.configuration.options.items,
            [
                ManifestOption(
                    name="param1",
                    option_type="string",
                    default="default",
                    description="A description",
                    required=True,
                    ui=None,
                ),
                ManifestOption(
                    name="param2", option_type="bool", default=True, description="A description", required=True, ui=None
                ),
                ManifestOption(
                    name="param3", option_type="int", default=42, description="A description", required=True, ui=None
                ),
                ManifestOption(
                    name="param4",
                    option_type="float",
                    default=3.14,
                    description="A description",
                    required=True,
                    ui=None,
                ),
            ],
        )

    def test_manifest_options_from_options(self):
        options = Options(
            Option("param1", str, "default", "A description", True),
        )
        manifest_options = ManifestOptions.from_options(options, format=["-{{name}}", "{{value}}"])
        self.assertEqual(manifest_options.format, ["-{{name}}", "{{value}}"])
        self.assertEqual(manifest_options.strict, False)

    def test_manifest_content_from_dict(self):
        manifest_content_dict = {
            "format": "multi-file",
            "multi-file": {
                "input": {
                    "path": "data/input_data",
                },
                "output": {
                    "statistics": "data/output/stats.json",
                    "assets": "data/output/assets.json",
                    "solutions": "data/output/solutions",
                },
            },
        }

        manifest_content = ManifestContent.from_dict(manifest_content_dict)

        self.assertEqual(manifest_content.format, "multi-file")
        self.assertIsInstance(manifest_content.multi_file, ManifestContentMultiFile)
        self.assertIsInstance(manifest_content.multi_file.input, ManifestContentMultiFileInput)
        self.assertIsInstance(manifest_content.multi_file.output, ManifestContentMultiFileOutput)
        self.assertEqual(manifest_content.multi_file.input.path, "data/input_data")
        self.assertEqual(manifest_content.multi_file.output.statistics, "data/output/stats.json")
        self.assertEqual(manifest_content.multi_file.output.assets, "data/output/assets.json")
        self.assertEqual(manifest_content.multi_file.output.solutions, "data/output/solutions")

    def test_from_options_with_validation(self):
        options = Options(
            Option(
                "param1",
                str,
                "default",
                "A description",
                True,
                additional_attributes={"max_length": 100},
                control_type="input",
            ),
            Option("param2", bool, True, "A description", True),
            Option("param3", int, 42, "A description", True, additional_attributes={"min": 0, "max": 100, "step": 1}),
            Option("param4", float, 3.14, "A description", True, display_name="a float parameter"),
            Option(
                "param5",
                str,
                "default",
                "A description",
                True,
                additional_attributes={"values": ["option1", "option2"]},
                control_type="select",
                hidden_from=["operator"],
            ),
        )
        manifest = Manifest.from_options(options, OptionsEnforcement(strict=True, validation_enforce=True))

        self.assertListEqual(manifest.files, ["main.py"])
        self.assertEqual(manifest.runtime, ManifestRuntime.PYTHON)
        self.assertEqual(manifest.type, ManifestType.PYTHON)
        self.assertEqual(manifest.python.pip_requirements, "requirements.txt")
        self.assertEqual(manifest.configuration.options.strict, True)
        self.assertEqual(manifest.configuration.options.validation, ManifestValidation(enforce="all"))
        self.assertListEqual(
            manifest.configuration.options.items,
            [
                ManifestOption(
                    name="param1",
                    option_type="string",
                    default="default",
                    description="A description",
                    required=True,
                    additional_attributes={"max_length": 100},
                    ui=ManifestOptionUI(control_type="input"),
                ),
                ManifestOption(
                    name="param2",
                    option_type="bool",
                    default=True,
                    description="A description",
                    required=True,
                ),
                ManifestOption(
                    name="param3",
                    option_type="int",
                    default=42,
                    description="A description",
                    required=True,
                    additional_attributes={"min": 0, "max": 100, "step": 1},
                    ui=None,
                ),
                ManifestOption(
                    name="param4",
                    option_type="float",
                    default=3.14,
                    description="A description",
                    required=True,
                    ui=ManifestOptionUI(display_name="a float parameter"),
                ),
                ManifestOption(
                    name="param5",
                    option_type="string",
                    default="default",
                    description="A description",
                    required=True,
                    additional_attributes={"values": ["option1", "option2"]},
                    ui=ManifestOptionUI(control_type="select", hidden_from=["operator"]),
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
                "expected_option_type": "bool",
            },
            {
                "name": "int option",
                "option": Option("param3", int, 42, "A description", True),
                "expected_option_type": "int",
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
                    option_type="bool",
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
                    option_type="int",
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
