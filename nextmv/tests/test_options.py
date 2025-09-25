import os
import shutil
import subprocess
import unittest

import nextmv


class TestOptions(unittest.TestCase):
    """
    Tests for the `Options` class.

    This test suite will first copy the `optionsX.py` scripts one level
    up: to the root directory. This happens in the `setUp` method. This is
    necessary because those scripts contain an `import nextmv` statement. If
    the path to `nextmv` is not in the same path as the test scripts, the
    `import nextmv` statement will fail.

    After the test suite is executed, the `tearDown` method will remove the
    `optionsX.py` scripts from the root directory.

    All the test methods that rely on a `optionsX.py` script, need to
    assume that the script is one level up.
    """

    test_scripts = ["1", "2", "3", "4", "5", "6", "7", "_deprecated"]
    """These are auxiliary scripts that are used to test different scenarios of
    instantiating an `Options` object."""

    def setUp(self):
        """Copies the options scripts to the root directory before the
        tests are executed."""

        for file in self.test_scripts:
            name = f"options{file}.py"
            src = self._file_name(name, "./scripts")
            dst = self._file_name(name, "..")
            shutil.copy(src, dst)

    def tearDown(self):
        """Removes the options scripts from the root directory after the
        tests are executed."""

        for file in self.test_scripts:
            name = f"options{file}.py"
            filename = self._file_name(name, "..")
            os.remove(filename)

    def test_defaults(self):
        file = self._file_name("options1.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "{'duration': '30s', 'threads': 4}\n")

    def test_env_vars(self):
        file = self._file_name("options1.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "DURATION": "60s", "THREADS": "8"},
        )

        self.assertEqual(result.returncode, 0, str(result.stderr))
        self.assertEqual(result.stdout, "{'duration': '60s', 'threads': 8}\n")

    def test_command_line_args_two_dashes(self):
        file = self._file_name("options1.py", "..")
        result = subprocess.run(
            ["python3", file, "--duration", "90s", "--threads", "12"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "{'duration': '90s', 'threads': 12}\n")

    def test_command_line_args_one_dash(self):
        file = self._file_name("options1.py", "..")
        result = subprocess.run(
            ["python3", file, "-duration", "120s", "-threads", "16"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "{'duration': '120s', 'threads': 16}\n")

    def test_command_line_args_precede_env_vars(self):
        file = self._file_name("options1.py", "..")
        result = subprocess.run(
            ["python3", file, "--duration", "90s", "--threads", "12"],
            capture_output=True,
            text=True,
            env={**os.environ, "DURATION": "60s", "THREADS": "8"},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "{'duration': '90s', 'threads': 12}\n")

    def test_no_values(self):
        file = self._file_name("options2.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn('option "duration" is required', result.stderr)

    def test_no_options(self):
        # The test passes if no exception is raised.
        opt = nextmv.Options()
        self.assertTrue(opt)

    def test_bad_option_type(self):
        with self.assertRaises(TypeError):
            opt = nextmv.Options("I am not a valid option")
            opt.parse()

    def test_bad_type_command_line_arg(self):
        file = self._file_name("options2.py", "..")
        result = subprocess.run(
            ["python3", file, "--duration", "30s", "--threads", "four"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid int value", result.stderr)

    def test_bad_type_env_var(self):
        file = self._file_name("options2.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "DURATION": "30s", "THREADS": "four"},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("not of type <class 'int'>", result.stderr)

    def test_full_help_message(self):
        file = self._file_name("options1.py", "..")
        result = subprocess.run(
            ["python3", file, "-h"],
            capture_output=True,
            text=True,
        )

        self.maxDiff = None
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[env var: DURATION] (default: 30s)", result.stdout)

    def test_minimal_help_message(self):
        file = self._file_name("options3.py", "..")
        result = subprocess.run(
            ["python3", file, "-h"],
            capture_output=True,
            text=True,
        )

        self.maxDiff = None
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("[env var: DURATION] (default: 30s)", result.stdout)

    def test_bool_option(self):
        file = self._file_name("options4.py", "..")

        result1 = subprocess.run(
            ["python3", file, "-bool_opt", "false"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result1.returncode, 0, result1.stderr)
        self.assertEqual(result1.stdout, "{'bool_opt': False}\n")

        result2 = subprocess.run(
            ["python3", file, "-bool_opt", "f"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result2.returncode, 0, result2.stderr)
        self.assertEqual(result2.stdout, "{'bool_opt': False}\n")

        result3 = subprocess.run(
            ["python3", file, "-bool_opt", "False"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result3.returncode, 0, result3.stderr)
        self.assertEqual(result3.stdout, "{'bool_opt': False}\n")

        result4 = subprocess.run(
            ["python3", file, "-bool_opt", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result4.returncode, 0, result4.stderr)
        self.assertEqual(result4.stdout, "{'bool_opt': False}\n")

        result5 = subprocess.run(
            ["python3", file, "-bool_opt", "true"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result5.returncode, 0, result5.stderr)
        self.assertEqual(result5.stdout, "{'bool_opt': True}\n")

        result6 = subprocess.run(
            ["python3", file, "-bool_opt", "t"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result6.returncode, 0, result6.stderr)
        self.assertEqual(result6.stdout, "{'bool_opt': True}\n")

        result7 = subprocess.run(
            ["python3", file, "-bool_opt", "True"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result7.returncode, 0, result7.stderr)
        self.assertEqual(result7.stdout, "{'bool_opt': True}\n")

        result8 = subprocess.run(
            ["python3", file, "-bool_opt", "1"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result8.returncode, 0, result8.stderr)
        self.assertEqual(result8.stdout, "{'bool_opt': True}\n")

        result9 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "f"},
        )
        self.assertEqual(result9.returncode, 0, result9.stderr)
        self.assertEqual(result9.stdout, "{'bool_opt': False}\n")

        result10 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "false"},
        )
        self.assertEqual(result10.returncode, 0, result10.stderr)
        self.assertEqual(result10.stdout, "{'bool_opt': False}\n")

        result11 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "False"},
        )
        self.assertEqual(result11.returncode, 0, result11.stderr)
        self.assertEqual(result11.stdout, "{'bool_opt': False}\n")

        result12 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "0"},
        )
        self.assertEqual(result12.returncode, 0, result12.stderr)
        self.assertEqual(result12.stdout, "{'bool_opt': False}\n")

        result13 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "t"},
        )
        self.assertEqual(result13.returncode, 0, result13.stderr)
        self.assertEqual(result13.stdout, "{'bool_opt': True}\n")

        result14 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "true"},
        )
        self.assertEqual(result14.returncode, 0, result14.stderr)
        self.assertEqual(result14.stdout, "{'bool_opt': True}\n")

        result14 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "True"},
        )
        self.assertEqual(result14.returncode, 0, result14.stderr)
        self.assertEqual(result14.stdout, "{'bool_opt': True}\n")

        result14 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "1"},
        )
        self.assertEqual(result14.returncode, 0, result14.stderr)
        self.assertEqual(result14.stdout, "{'bool_opt': True}\n")

        # Default case: nothing is specified.
        result15 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result15.returncode, 0, result15.stderr)
        self.assertEqual(result15.stdout, "{'bool_opt': True}\n")

        # Bad arg produces False.
        result16 = subprocess.run(
            ["python3", file, "-bool_opt", "Frue"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result16.returncode, 0, result16.stderr)
        self.assertEqual(result16.stdout, "{'bool_opt': False}\n")

        # Bad env var produces False.
        result17 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "BOOL_OPT": "Frue"},
        )
        self.assertEqual(result17.returncode, 0, result17.stderr)
        self.assertEqual(result17.stdout, "{'bool_opt': False}\n")

    def test_none_default(self):
        file = self._file_name("options5.py", "..")

        result1 = subprocess.run(
            ["python3", file, "-str_opt", ""],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result1.returncode, 0, result1.stderr)
        self.assertEqual(result1.stdout, "str_opt: \n")

        result2 = subprocess.run(
            ["python3", file, "-str_opt", "empanadas"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result2.returncode, 0, result2.stderr)
        self.assertEqual(result2.stdout, "str_opt: empanadas\n")

        result3 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result3.returncode, 0, result3.stderr)
        self.assertEqual(result3.stdout, "str_opt: None\n")

    def test_name_handling(self):
        file = self._file_name("options6.py", "..")

        result1 = subprocess.run(
            [
                "python3",
                file,
                "-dash-opt",
                "empanadas",
                "-underscore_opt",
                "is",
                "-camelCaseOpt",
                "life",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result1.returncode, 0, result1.stderr)
        self.assertEqual(result1.stdout, "{'dash_opt': 'empanadas', 'underscore_opt': 'is', 'camelCaseOpt': 'life'}\n")

    def test_choices(self):
        file = self._file_name("options7.py", "..")

        result1 = subprocess.run(
            ["python3", file, "-choice_opt", "choice2"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result1.returncode, 0, result1.stderr)
        self.assertEqual(result1.stdout, "{'choice_opt': 'choice2'}\n")

        result2 = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result2.returncode, 0, result2.stderr)
        self.assertEqual(result2.stdout, "{'choice_opt': 'choice1'}\n")

    def test_deprecated_parameter(self):
        """Test that nextmv.Parameter can co-exist with nextmv.Option."""
        file = self._file_name("options_deprecated.py", "..")
        result = subprocess.run(
            ["python3", file, "--duration", "30s", "--threads", "4"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "{'duration': '30s', 'threads': 4}\n")

    @staticmethod
    def _file_name(name: str, relative_location: str = ".") -> str:
        """
        Returns the full path to a file in the current testing directory.

        Parameters
        ----------
        name : str
            The name of the file.
        relative_location : str, optional
            The relative location of the file. The default is ".".

        Returns
        -------
        str
            The full path to the file.
        """

        return os.path.join(os.path.dirname(__file__), relative_location, name)


class TestParameter(unittest.TestCase):
    def test_from_dict_str(self):
        data = {
            "name": "i_am_a_fish",
            "param_type": "<class 'str'>",
            "default": "salmon",
            "description": "I am a fish",
            "required": False,
        }
        param = nextmv.Parameter.from_dict(data)

        self.assertEqual(param.name, data["name"])
        self.assertEqual(param.param_type, str)
        self.assertEqual(param.default, data["default"])
        self.assertEqual(param.description, data["description"])
        self.assertEqual(param.required, data["required"])

    def test_from_dict_float(self):
        data = {
            "name": "i_am_a_fish",
            "param_type": "<class 'float'>",
            "default": 3.14,
            "description": "I am a fish",
            "required": False,
        }
        param = nextmv.Parameter.from_dict(data)

        self.assertEqual(param.name, data["name"])
        self.assertEqual(param.param_type, float)
        self.assertEqual(param.default, data["default"])
        self.assertEqual(param.description, data["description"])
        self.assertEqual(param.required, data["required"])

    def test_from_dict_int(self):
        data = {
            "name": "i_am_a_fish",
            "param_type": "<class 'int'>",
            "default": 42,
            "description": "I am a fish",
            "required": False,
        }
        param = nextmv.Parameter.from_dict(data)

        self.assertEqual(param.name, data["name"])
        self.assertEqual(param.param_type, int)
        self.assertEqual(param.default, data["default"])
        self.assertEqual(param.description, data["description"])
        self.assertEqual(param.required, data["required"])

    def test_from_dict_bool(self):
        data = {
            "name": "i_am_a_fish",
            "param_type": "<class 'bool'>",
            "default": False,
            "description": "I am a fish",
            "required": False,
        }
        param = nextmv.Parameter.from_dict(data)

        self.assertEqual(param.name, data["name"])
        self.assertEqual(param.param_type, bool)
        self.assertEqual(param.default, data["default"])
        self.assertEqual(param.description, data["description"])
        self.assertEqual(param.required, data["required"])

    def test_to_dict_str(self):
        param = nextmv.Parameter(
            name="i_am_a_fish",
            param_type=str,
            default="salmon",
            description="I am a fish",
            required=False,
        )
        data = param.to_dict()

        self.assertEqual(data["name"], param.name)
        self.assertEqual(data["param_type"], "<class 'str'>")
        self.assertEqual(data["default"], param.default)
        self.assertEqual(data["description"], param.description)
        self.assertEqual(data["required"], param.required)

    def test_to_dict_float(self):
        param = nextmv.Parameter(
            name="i_am_a_fish",
            param_type=float,
            default=3.14,
            description="I am a fish",
            required=False,
        )
        data = param.to_dict()

        self.assertEqual(data["name"], param.name)
        self.assertEqual(data["param_type"], "<class 'float'>")
        self.assertEqual(data["default"], param.default)
        self.assertEqual(data["description"], param.description)
        self.assertEqual(data["required"], param.required)

    def test_to_dict_int(self):
        param = nextmv.Parameter(
            name="i_am_a_fish",
            param_type=int,
            default=42,
            description="I am a fish",
            required=False,
        )
        data = param.to_dict()

        self.assertEqual(data["name"], param.name)
        self.assertEqual(data["param_type"], "<class 'int'>")
        self.assertEqual(data["default"], param.default)
        self.assertEqual(data["description"], param.description)
        self.assertEqual(data["required"], param.required)

    def test_to_dict_bool(self):
        param = nextmv.Parameter(
            name="i_am_a_fish",
            param_type=bool,
            default=False,
            description="I am a fish",
            required=False,
        )
        data = param.to_dict()

        self.assertEqual(data["name"], param.name)
        self.assertEqual(data["param_type"], "<class 'bool'>")
        self.assertEqual(data["default"], param.default)
        self.assertEqual(data["description"], param.description)
        self.assertEqual(data["required"], param.required)

    def test_merge(self):
        opt1 = nextmv.Options(
            nextmv.Parameter("foo1", int, default=1),
            nextmv.Parameter("bar1", int, default=2),
        )
        self.assertFalse(opt1.PARSED)

        opt2 = nextmv.Options(
            nextmv.Parameter("foo2", int, default=3),
            nextmv.Parameter("bar2", int, default=4),
        )
        self.assertFalse(opt2.PARSED)

        opt = opt1.merge(opt2)
        self.assertTrue(opt.PARSED)

        self.assertEqual(opt.foo1, 1)
        self.assertEqual(opt.bar1, 2)
        self.assertEqual(opt.foo2, 3)
        self.assertEqual(opt.bar2, 4)

    def test_merge_lazy(self):
        opt1 = nextmv.Options(
            nextmv.Parameter("foo1", int, default=1),
            nextmv.Parameter("bar1", int, default=2),
        )
        self.assertFalse(opt1.PARSED)

        opt2 = nextmv.Options(
            nextmv.Parameter("foo2", int, default=3),
            nextmv.Parameter("bar2", int, default=4),
        )
        self.assertFalse(opt2.PARSED)

        opt3 = nextmv.Options(
            nextmv.Parameter("foo3", int, default=5),
            nextmv.Parameter("bar3", int, default=6),
        )
        self.assertFalse(opt3.PARSED)

        opt = opt1.merge(opt2, skip_parse=True)
        self.assertFalse(opt.PARSED)

        opt = opt.merge(opt3, skip_parse=True)
        self.assertFalse(opt.PARSED)

        opt.parse()
        self.assertTrue(opt.PARSED)

        self.assertEqual(opt.foo1, 1)
        self.assertEqual(opt.bar1, 2)
        self.assertEqual(opt.foo2, 3)
        self.assertEqual(opt.bar2, 4)
        self.assertEqual(opt.foo3, 5)
        self.assertEqual(opt.bar3, 6)

    def test_merge_multi(self):
        opt1 = nextmv.Options(
            nextmv.Parameter("foo1", int, default=1),
            nextmv.Parameter("bar1", int, default=2),
        )
        self.assertFalse(opt1.PARSED)

        opt2 = nextmv.Options(
            nextmv.Parameter("foo2", int, default=3),
            nextmv.Parameter("bar2", int, default=4),
        )
        self.assertFalse(opt2.PARSED)

        opt3 = nextmv.Options(
            nextmv.Parameter("foo3", int, default=5),
            nextmv.Parameter("bar3", int, default=6),
        )
        self.assertFalse(opt3.PARSED)

        opt1.merge(opt2, opt3)
        self.assertTrue(opt1.PARSED)
        self.assertEqual(opt1.foo1, 1)
        self.assertEqual(opt1.bar1, 2)
        self.assertEqual(opt1.foo2, 3)
        self.assertEqual(opt1.bar2, 4)
        self.assertEqual(opt1.foo3, 5)
        self.assertEqual(opt1.bar3, 6)

    def test_cant_merge(self):
        opt1 = nextmv.Options(
            nextmv.Parameter("foo1", int, default=1),
            nextmv.Parameter("bar1", int, default=2),
        )
        opt1.parse()

        opt2 = nextmv.Options(
            nextmv.Parameter("foo2", int, default=3),
            nextmv.Parameter("bar2", int, default=4),
        )

        with self.assertRaises(RuntimeError):
            opt1.merge(opt2)

    def test_parse(self):
        opt = nextmv.Options(
            nextmv.Parameter("foo", int, default=1),
            nextmv.Parameter("bar", int, default=2),
        )

        self.assertFalse(opt.PARSED)
        opt.parse()
        self.assertTrue(opt.PARSED)


class TestOption(unittest.TestCase):
    def test_from_dict_str(self):
        data = {
            "name": "i_am_a_fish",
            "option_type": "<class 'str'>",
            "default": "salmon",
            "description": "I am a fish",
            "required": False,
        }
        opt = nextmv.Option.from_dict(data)

        self.assertEqual(opt.name, data["name"])
        self.assertEqual(opt.option_type, str)
        self.assertEqual(opt.default, data["default"])
        self.assertEqual(opt.description, data["description"])
        self.assertEqual(opt.required, data["required"])

    def test_from_dict_float(self):
        data = {
            "name": "i_am_a_fish",
            "option_type": "<class 'float'>",
            "default": 3.14,
            "description": "I am a fish",
            "required": False,
        }
        opt = nextmv.Option.from_dict(data)

        self.assertEqual(opt.name, data["name"])
        self.assertEqual(opt.option_type, float)
        self.assertEqual(opt.default, data["default"])
        self.assertEqual(opt.description, data["description"])
        self.assertEqual(opt.required, data["required"])

    def test_from_dict_int(self):
        data = {
            "name": "i_am_a_fish",
            "option_type": "<class 'int'>",
            "default": 42,
            "description": "I am a fish",
            "required": False,
        }
        opt = nextmv.Option.from_dict(data)

        self.assertEqual(opt.name, data["name"])
        self.assertEqual(opt.option_type, int)
        self.assertEqual(opt.default, data["default"])
        self.assertEqual(opt.description, data["description"])
        self.assertEqual(opt.required, data["required"])

    def test_from_dict_bool(self):
        data = {
            "name": "i_am_a_fish",
            "option_type": "<class 'bool'>",
            "default": False,
            "description": "I am a fish",
            "required": False,
        }
        opt = nextmv.Option.from_dict(data)

        self.assertEqual(opt.name, data["name"])
        self.assertEqual(opt.option_type, bool)
        self.assertEqual(opt.default, data["default"])
        self.assertEqual(opt.description, data["description"])
        self.assertEqual(opt.required, data["required"])

    def test_to_dict_str(self):
        opt = nextmv.Option(
            name="i_am_a_fish",
            option_type=str,
            default="salmon",
            description="I am a fish",
            required=False,
        )
        data = opt.to_dict()

        self.assertEqual(data["name"], opt.name)
        self.assertEqual(data["option_type"], "<class 'str'>")
        self.assertEqual(data["default"], opt.default)
        self.assertEqual(data["description"], opt.description)
        self.assertEqual(data["required"], opt.required)

    def test_to_dict_float(self):
        opt = nextmv.Option(
            name="i_am_a_fish",
            option_type=float,
            default=3.14,
            description="I am a fish",
            required=False,
        )
        data = opt.to_dict()

        self.assertEqual(data["name"], opt.name)
        self.assertEqual(data["option_type"], "<class 'float'>")
        self.assertEqual(data["default"], opt.default)
        self.assertEqual(data["description"], opt.description)
        self.assertEqual(data["required"], opt.required)

    def test_to_dict_int(self):
        opt = nextmv.Option(
            name="i_am_a_fish",
            option_type=int,
            default=42,
            description="I am a fish",
            required=False,
        )
        data = opt.to_dict()

        self.assertEqual(data["name"], opt.name)
        self.assertEqual(data["option_type"], "<class 'int'>")
        self.assertEqual(data["default"], opt.default)
        self.assertEqual(data["description"], opt.description)
        self.assertEqual(data["required"], opt.required)

    def test_to_dict_bool(self):
        opt = nextmv.Option(
            name="i_am_a_fish",
            option_type=bool,
            default=False,
            description="I am a fish",
            required=False,
        )
        data = opt.to_dict()

        self.assertEqual(data["name"], opt.name)
        self.assertEqual(data["option_type"], "<class 'bool'>")
        self.assertEqual(data["default"], opt.default)
        self.assertEqual(data["description"], opt.description)
        self.assertEqual(data["required"], opt.required)

    def test_merge(self):
        opt1 = nextmv.Options(
            nextmv.Option("foo1", int, default=1),
            nextmv.Option("bar1", int, default=2),
        )
        self.assertFalse(opt1.PARSED)

        opt2 = nextmv.Options(
            nextmv.Option("foo2", int, default=3),
            nextmv.Option("bar2", int, default=4),
        )
        self.assertFalse(opt2.PARSED)

        opt = opt1.merge(opt2)
        self.assertTrue(opt.PARSED)

        self.assertEqual(opt.foo1, 1)
        self.assertEqual(opt.bar1, 2)
        self.assertEqual(opt.foo2, 3)
        self.assertEqual(opt.bar2, 4)

    def test_cant_merge(self):
        opt1 = nextmv.Options(
            nextmv.Option("foo1", int, default=1),
            nextmv.Option("bar1", int, default=2),
        )
        opt1.parse()

        opt2 = nextmv.Options(
            nextmv.Option("foo2", int, default=3),
            nextmv.Option("bar2", int, default=4),
        )

        with self.assertRaises(RuntimeError):
            opt1.merge(opt2)

    def test_parse(self):
        opt = nextmv.Options(
            nextmv.Option("foo", int, default=1),
            nextmv.Option("bar", int, default=2),
        )

        self.assertFalse(opt.PARSED)
        opt.parse()
        self.assertTrue(opt.PARSED)
