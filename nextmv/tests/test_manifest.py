import os
import tempfile
import unittest

from nextmv.content_format import ContentFormat
from nextmv.manifest import (
    MANIFEST_FILE_NAME,
    Manifest,
    ManifestContent,
    ManifestContentMultiFile,
    ManifestContentMultiFileInput,
    ManifestContentMultiFileOutput,
    ManifestOption,
    ManifestOptions,
    ManifestOptionUI,
    ManifestPython,
    ManifestPythonArch,
    ManifestRuntime,
    ManifestType,
    ManifestValidation,
    ModelConfiguration,
    initialize_manifest,
)
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
            "version": 3.11,
            "arch": "amd64",
            "model": {
                "name": "foo_model",
            },
        }

        manifest_python = ManifestPython.from_dict(manifest_python_dict)

        self.assertEqual(manifest_python.pip_requirements, "foo_requirements.txt")
        self.assertEqual(manifest_python.version, "3.11")
        self.assertEqual(manifest_python.arch, ManifestPythonArch.AMD64)
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
                        "metrics": "my-outputs/metrics.json",
                    },
                },
            },
        )

    def test_extract_options(self):
        manifest = Manifest.from_yaml("tests/cloud")
        options = manifest.extract_options(should_parse=False)
        self.assertEqual(len(options.options), 6)

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

    def test_manifest_from_dict(self):
        manifest_dict = {
            "type": "go",
            "runtime": "ghcr.io/nextmv-io/runtime/default:latest",
            "files": ["./build/binary"],
            "execution": {
                "entrypoint": "./binary",
                "cwd": "./build/",
            },
        }

        manifest = Manifest.from_dict(manifest_dict)

        self.assertEqual(manifest.type, ManifestType.GO)
        self.assertEqual(manifest.runtime, ManifestRuntime.DEFAULT)
        self.assertListEqual(manifest.files, ["./build/binary"])
        self.assertEqual(manifest.execution.entrypoint, "./binary")
        self.assertEqual(manifest.execution.cwd, "./build/")

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
                    "metrics": "data/output/metrics.json",
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
        self.assertEqual(manifest_content.multi_file.output.metrics, "data/output/metrics.json")

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


class TestManifestOptionLocalOnly(unittest.TestCase):
    def test_local_only_defaults_to_false(self):
        option = ManifestOption(name="my_option", option_type="string", default="val")
        self.assertFalse(option.local_only)

    def test_local_only_can_be_set_to_true(self):
        option = ManifestOption(name="my_option", option_type="int", default=0, local_only=True)
        self.assertTrue(option.local_only)

    def test_required_and_local_only_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="my_option", option_type="string", default="val", required=True, local_only=True)
        self.assertIn("my_option", str(ctx.exception))
        self.assertIn("required", str(ctx.exception).lower())
        self.assertIn("local only", str(ctx.exception).lower())

    def test_local_only_round_trips_through_dict(self):
        original = ManifestOption(name="my_option", option_type="float", default=1.5, local_only=True)
        as_dict = original.to_dict()
        self.assertTrue(as_dict["local_only"])
        restored = ManifestOption.from_dict(as_dict)
        self.assertTrue(restored.local_only)

    def test_non_local_only_round_trips_through_dict(self):
        original = ManifestOption(name="my_option", option_type="bool", default=False, local_only=False)
        as_dict = original.to_dict()
        self.assertFalse(as_dict["local_only"])
        restored = ManifestOption.from_dict(as_dict)
        self.assertFalse(restored.local_only)

    def test_local_only_loaded_from_yaml(self):
        manifest = Manifest.from_yaml("tests/cloud")
        items = manifest.configuration.options.items
        local_only_items = [item for item in items if item.local_only]
        self.assertEqual(len(local_only_items), 1)
        item = local_only_items[0]
        self.assertEqual(item.name, "a local only parameter")
        self.assertEqual(item.option_type, "string")
        self.assertEqual(item.default, "local_default")
        self.assertFalse(item.required)
        self.assertTrue(item.local_only)

    def test_other_options_are_not_local_only(self):
        manifest = Manifest.from_yaml("tests/cloud")
        items = manifest.configuration.options.items
        non_local_only_items = [item for item in items if not item.local_only]
        # All items except the one explicitly marked local_only should have local_only=False.
        for item in non_local_only_items:
            self.assertFalse(item.local_only, msg=f"Option '{item.name}' should not be local_only")


class TestWriteSampleManifest(unittest.TestCase):
    def test_writes_python_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.PYTHON, ContentFormat.JSON, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            self.assertEqual(manifest.type, ManifestType.PYTHON)

    def test_writes_go_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.GO, ContentFormat.JSON, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            # Go is just a binary app, so, we use the binary manifest type.
            self.assertEqual(manifest.type, ManifestType.BINARY)

    def test_writes_java_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.JAVA, ContentFormat.JSON, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            self.assertEqual(manifest.type, ManifestType.JAVA)

    def test_writes_binary_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.BINARY, ContentFormat.JSON, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            self.assertEqual(manifest.type, ManifestType.BINARY)

    def test_writes_python_multi_file_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.PYTHON, ContentFormat.MULTI_FILE, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            self.assertEqual(manifest.type, ManifestType.PYTHON)
            self.assertEqual(manifest.configuration.content.format.value, ContentFormat.MULTI_FILE.value)

    def test_writes_go_multi_file_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.GO, ContentFormat.MULTI_FILE, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            # Go is just a binary app, so, we use the binary manifest type.
            self.assertEqual(manifest.type, ManifestType.BINARY)
            self.assertEqual(manifest.configuration.content.format.value, ContentFormat.MULTI_FILE.value)

    def test_writes_java_multi_file_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.JAVA, ContentFormat.MULTI_FILE, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            self.assertEqual(manifest.type, ManifestType.JAVA)
            self.assertEqual(manifest.configuration.content.format.value, ContentFormat.MULTI_FILE.value)

    def test_writes_binary_multi_file_manifest(self):
        with tempfile.TemporaryDirectory() as dirpath:
            initialize_manifest(ManifestType.BINARY, ContentFormat.MULTI_FILE, dirpath)
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertTrue(os.path.isfile(dest))
            manifest = Manifest.from_yaml(dirpath)
            self.assertEqual(manifest.type, ManifestType.BINARY)
            self.assertEqual(manifest.configuration.content.format.value, ContentFormat.MULTI_FILE.value)

    def test_creates_directory_if_not_exists(self):
        with tempfile.TemporaryDirectory() as base:
            dirpath = os.path.join(base, "new_subdir")
            self.assertFalse(os.path.exists(dirpath))
            initialize_manifest(ManifestType.PYTHON, ContentFormat.JSON, dirpath)
            self.assertTrue(os.path.isfile(os.path.join(dirpath, MANIFEST_FILE_NAME)))

    def test_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as dirpath:
            dest = os.path.join(dirpath, MANIFEST_FILE_NAME)
            with open(dest, "w") as f:
                f.write("placeholder: true\n")
            initialize_manifest(ManifestType.PYTHON, ContentFormat.JSON, dirpath)
            manifest = Manifest.from_yaml(dirpath)
            self.assertEqual(manifest.type, ManifestType.PYTHON)

    def test_returns_normalized_path(self):
        with tempfile.TemporaryDirectory() as base:
            # Pass a path with a trailing slash; normpath should remove it.
            dirpath = base + os.sep
            dst = initialize_manifest(ManifestType.PYTHON, ContentFormat.JSON, dirpath)
            expected = os.path.join(os.path.normpath(dirpath), MANIFEST_FILE_NAME)
            self.assertEqual(dst, expected)
            self.assertTrue(os.path.isfile(dst))

    def test_expands_user_home_in_path(self):
        home = os.path.expanduser("~")
        with tempfile.TemporaryDirectory(dir=home) as dirpath:
            # Replace the home prefix with ~ so expanduser must be applied.
            tilde_path = os.path.join("~", os.path.relpath(dirpath, home))
            dst = initialize_manifest(ManifestType.PYTHON, ContentFormat.JSON, tilde_path)
            expected = os.path.join(dirpath, MANIFEST_FILE_NAME)
            self.assertEqual(dst, expected)
            self.assertTrue(os.path.isfile(dst))

    def test_normalized_path_used_for_subdirectory_creation(self):
        with tempfile.TemporaryDirectory() as base:
            # Path with redundant separators that normpath will clean up.
            dirpath = os.path.join(base, "sub" + os.sep + os.sep + "dir")
            dst = initialize_manifest(ManifestType.PYTHON, ContentFormat.JSON, dirpath)
            normalized = os.path.normpath(dirpath)
            expected = os.path.join(normalized, MANIFEST_FILE_NAME)
            self.assertEqual(dst, expected)
            self.assertTrue(os.path.isfile(dst))


class TestManifestOptionUIValidation(unittest.TestCase):
    def test_valid_control_types_accepted(self):
        for ct in ("input", "select", "multiselect", "slider", "toggle"):
            with self.subTest(control_type=ct):
                ui = ManifestOptionUI(control_type=ct)
                self.assertEqual(ui.control_type, ct)

    def test_none_control_type_accepted(self):
        ui = ManifestOptionUI(control_type=None)
        self.assertIsNone(ui.control_type)

    def test_invalid_control_type_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOptionUI(control_type="checkbox")
        self.assertIn("checkbox", str(ctx.exception))
        self.assertIn("control_type", str(ctx.exception))


class TestManifestOptionControlTypeValidation(unittest.TestCase):
    """Tests that control_type must be compatible with option_type."""

    def test_string_valid_control_types(self):
        for ct in ("input", "select", "multiselect"):
            with self.subTest(control_type=ct):
                extra = {"values": ["a"]} if ct in ("select", "multiselect") else None
                ManifestOption(
                    name="opt", option_type="string", ui=ManifestOptionUI(control_type=ct), additional_attributes=extra
                )

    def test_bool_valid_control_type(self):
        ManifestOption(name="opt", option_type="bool", ui=ManifestOptionUI(control_type="toggle"))

    def test_int_valid_control_types(self):
        for ct, attrs in (
            ("input", None),
            ("slider", {"min": 0, "max": 10, "step": 1}),
            ("select", {"values": [1, 2]}),
        ):
            with self.subTest(control_type=ct):
                ManifestOption(
                    name="opt", option_type="int", ui=ManifestOptionUI(control_type=ct), additional_attributes=attrs
                )

    def test_float_valid_control_types(self):
        for ct, attrs in (
            ("input", None),
            ("slider", {"min": 0.0, "max": 1.0, "step": 0.1}),
            ("select", {"values": [1.0]}),
        ):
            with self.subTest(control_type=ct):
                ManifestOption(
                    name="opt", option_type="float", ui=ManifestOptionUI(control_type=ct), additional_attributes=attrs
                )

    def test_string_with_slider_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="string", ui=ManifestOptionUI(control_type="slider"))
        self.assertIn("slider", str(ctx.exception))
        self.assertIn("string", str(ctx.exception))

    def test_string_with_toggle_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="string", ui=ManifestOptionUI(control_type="toggle"))
        self.assertIn("toggle", str(ctx.exception))

    def test_bool_with_input_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="bool", ui=ManifestOptionUI(control_type="input"))
        self.assertIn("input", str(ctx.exception))
        self.assertIn("bool", str(ctx.exception))

    def test_bool_with_select_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="bool", ui=ManifestOptionUI(control_type="select"))
        self.assertIn("select", str(ctx.exception))

    def test_int_with_toggle_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="int", ui=ManifestOptionUI(control_type="toggle"))
        self.assertIn("toggle", str(ctx.exception))
        self.assertIn("int", str(ctx.exception))

    def test_float_with_toggle_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="float", ui=ManifestOptionUI(control_type="toggle"))
        self.assertIn("toggle", str(ctx.exception))
        self.assertIn("float", str(ctx.exception))

    def test_error_message_contains_option_name(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="my_special_opt", option_type="bool", ui=ManifestOptionUI(control_type="slider"))
        self.assertIn("my_special_opt", str(ctx.exception))


class TestManifestOptionAdditionalAttributesValidation(unittest.TestCase):
    """Tests for required and invalid additional_attributes per (option_type, control_type)."""

    # --- select / multiselect: values is required ---

    def test_string_select_requires_values(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="string", ui=ManifestOptionUI(control_type="select"))
        self.assertIn("values", str(ctx.exception))

    def test_string_multiselect_requires_values(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="string", ui=ManifestOptionUI(control_type="multiselect"))
        self.assertIn("values", str(ctx.exception))

    def test_int_select_requires_values(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="int", ui=ManifestOptionUI(control_type="select"))
        self.assertIn("values", str(ctx.exception))

    def test_float_select_requires_values(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="float", ui=ManifestOptionUI(control_type="select"))
        self.assertIn("values", str(ctx.exception))

    # --- slider: min, max, step are required ---

    def test_int_slider_requires_min_max_step(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="int", ui=ManifestOptionUI(control_type="slider"))
        self.assertIn("min", str(ctx.exception))

    def test_int_slider_with_partial_attrs_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(
                name="opt",
                option_type="int",
                ui=ManifestOptionUI(control_type="slider"),
                additional_attributes={"min": 0, "max": 100},
            )
        self.assertIn("step", str(ctx.exception))

    def test_float_slider_requires_min_max_step(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(name="opt", option_type="float", ui=ManifestOptionUI(control_type="slider"))
        self.assertIn("min", str(ctx.exception))

    def test_float_slider_with_partial_attrs_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(
                name="opt",
                option_type="float",
                ui=ManifestOptionUI(control_type="slider"),
                additional_attributes={"min": 0.0},
            )
        # Both max and step are missing; at least one should appear in the error.
        msg = str(ctx.exception)
        self.assertTrue("max" in msg or "step" in msg)

    # --- invalid attribute keys for a given combination ---

    def test_string_input_rejects_unknown_attr(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(
                name="opt",
                option_type="string",
                ui=ManifestOptionUI(control_type="input"),
                additional_attributes={"max_length": 50, "unknown_key": True},
            )
        self.assertIn("unknown_key", str(ctx.exception))

    def test_int_input_rejects_values_attr(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(
                name="opt",
                option_type="int",
                ui=ManifestOptionUI(control_type="input"),
                additional_attributes={"min": 0, "max": 10, "values": [1, 2]},
            )
        self.assertIn("values", str(ctx.exception))

    def test_float_input_rejects_unknown_attr(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(
                name="opt",
                option_type="float",
                ui=ManifestOptionUI(control_type="input"),
                additional_attributes={"min": 0.0, "bad_key": 99},
            )
        self.assertIn("bad_key", str(ctx.exception))

    # --- additional_attributes without control_type should NOT be validated ---

    def test_additional_attributes_without_control_type_not_validated(self):
        # When no control_type is set, we don't validate additional_attributes keys.
        opt = ManifestOption(
            name="opt",
            option_type="string",
            additional_attributes={"anything": "goes"},
        )
        self.assertEqual(opt.additional_attributes, {"anything": "goes"})

    # --- valid full configurations that should pass ---

    def test_string_input_with_valid_attrs(self):
        opt = ManifestOption(
            name="opt",
            option_type="string",
            ui=ManifestOptionUI(control_type="input"),
            additional_attributes={"max_length": 100, "min_length": 1},
        )
        self.assertEqual(opt.additional_attributes["max_length"], 100)

    def test_string_select_with_values(self):
        opt = ManifestOption(
            name="opt",
            option_type="string",
            ui=ManifestOptionUI(control_type="select"),
            additional_attributes={"values": ["a", "b", "c"]},
        )
        self.assertEqual(opt.additional_attributes["values"], ["a", "b", "c"])

    def test_int_slider_with_all_required_attrs(self):
        opt = ManifestOption(
            name="opt",
            option_type="int",
            ui=ManifestOptionUI(control_type="slider"),
            additional_attributes={"min": 0, "max": 100, "step": 5},
        )
        self.assertEqual(opt.additional_attributes["step"], 5)

    def test_float_slider_with_all_required_attrs(self):
        opt = ManifestOption(
            name="opt",
            option_type="float",
            ui=ManifestOptionUI(control_type="slider"),
            additional_attributes={"min": 0.0, "max": 1.0, "step": 0.1},
        )
        self.assertAlmostEqual(opt.additional_attributes["step"], 0.1)

    def test_error_message_contains_option_name(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestOption(
                name="solver_timeout",
                option_type="string",
                ui=ManifestOptionUI(control_type="select"),
            )
        self.assertIn("solver_timeout", str(ctx.exception))


class TestManifestValidationEnforce(unittest.TestCase):
    def test_valid_enforce_none(self):
        v = ManifestValidation(enforce="none")
        self.assertEqual(v.enforce, "none")

    def test_valid_enforce_all(self):
        v = ManifestValidation(enforce="all")
        self.assertEqual(v.enforce, "all")

    def test_default_enforce_is_none(self):
        v = ManifestValidation()
        self.assertEqual(v.enforce, "none")

    def test_invalid_enforce_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestValidation(enforce="partial")
        self.assertIn("partial", str(ctx.exception))

    def test_invalid_enforce_empty_string_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestValidation(enforce="")
        self.assertIn("enforce", str(ctx.exception).lower())

    def test_invalid_enforce_uppercase_raises(self):
        # Enforce is case-sensitive; "ALL" and "NONE" should not be accepted.
        with self.assertRaises(ValueError):
            ManifestValidation(enforce="ALL")

    def test_invalid_enforce_unknown_raises(self):
        with self.assertRaises(ValueError) as ctx:
            ManifestValidation(enforce="strict")
        self.assertIn("strict", str(ctx.exception))
