"""
Unit tests for the `nextmv manifest init` CLI command.
"""

import tempfile
import unittest
from unittest.mock import patch

from nextmv.cli.main import app
from nextmv.content_format import ContentFormat
from nextmv.manifest import ManifestType
from typer.testing import CliRunner


class TestManifestInitNonInteractive(unittest.TestCase):
    """Tests for the non-interactive (all flags provided) path of `manifest init`."""

    def setUp(self):
        self.runner = CliRunner()

    def _invoke(self, args):
        return self.runner.invoke(app, ["manifest", "init"] + args)

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_python_json_with_options(self, mock_init):
        """All flags provided: python, json, options-yes."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--content-format", "json", "--dirpath", d, "--options-yes"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.PYTHON,
                content_format=ContentFormat.JSON,
                dirpath=d,
                with_options=True,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_python_json_without_options(self, mock_init):
        """All flags provided: python, json, options-no."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--content-format", "json", "--dirpath", d, "--options-no"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.PYTHON,
                content_format=ContentFormat.JSON,
                dirpath=d,
                with_options=False,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_go_json_with_options(self, mock_init):
        """All flags provided: go, json, options-yes."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "go", "--content-format", "json", "--dirpath", d, "--options-yes"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.GO,
                content_format=ContentFormat.JSON,
                dirpath=d,
                with_options=True,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_go_multi_file_without_options(self, mock_init):
        """All flags provided: go, multi-file, options-no."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "go", "--content-format", "multi-file", "--dirpath", d, "--options-no"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.GO,
                content_format=ContentFormat.MULTI_FILE,
                dirpath=d,
                with_options=False,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_java_json_with_options(self, mock_init):
        """All flags provided: java, json, options-yes."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "java", "--content-format", "json", "--dirpath", d, "--options-yes"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.JAVA,
                content_format=ContentFormat.JSON,
                dirpath=d,
                with_options=True,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_binary_json_without_options(self, mock_init):
        """All flags provided: binary, json, options-no."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "binary", "--content-format", "json", "--dirpath", d, "--options-no"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.BINARY,
                content_format=ContentFormat.JSON,
                dirpath=d,
                with_options=False,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_short_flags(self, mock_init):
        """Short flags -t, -c, -d, -y should work identically to long flags."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["-t", "python", "-c", "json", "-d", d, "-y"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.PYTHON,
                content_format=ContentFormat.JSON,
                dirpath=d,
                with_options=True,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_short_flags_no_options(self, mock_init):
        """-n short flag should set with_options=False."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["-t", "python", "-c", "json", "-d", d, "-n"])
            self.assertEqual(result.exit_code, 0)
            mock_init.assert_called_once_with(
                manifest_type=ManifestType.PYTHON,
                content_format=ContentFormat.JSON,
                dirpath=d,
                with_options=False,
            )

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_success_message_contains_type_and_format(self, mock_init):
        """Success output should mention the manifest type and content format."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--content-format", "json", "--dirpath", d, "--options-yes"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("python", result.output)
            self.assertIn("json", result.output)

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_success_message_with_options(self, mock_init):
        """Success output should say 'with' when options-yes is used."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--content-format", "json", "--dirpath", d, "--options-yes"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("with", result.output)

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_success_message_without_options(self, mock_init):
        """Success output should say 'without' when options-no is used."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--content-format", "json", "--dirpath", d, "--options-no"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("without", result.output)


class TestManifestInitErrors(unittest.TestCase):
    """Tests for error cases of `manifest init`."""

    def setUp(self):
        self.runner = CliRunner()

    def _invoke(self, args):
        return self.runner.invoke(app, ["manifest", "init"] + args)

    def test_both_options_yes_and_no_exits_with_error(self):
        """Specifying both --options-yes and --options-no must exit with code 1."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(
                ["--type", "python", "--content-format", "json", "--dirpath", d, "--options-yes", "--options-no"]
            )
            self.assertEqual(result.exit_code, 1)

    def test_invalid_type_exits_with_error(self):
        """An unrecognised --type value must cause a non-zero exit."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "not-a-language", "--content-format", "json", "--dirpath", d, "-y"])
            self.assertNotEqual(result.exit_code, 0)

    def test_invalid_content_format_exits_with_error(self):
        """An unrecognised --content-format value must cause a non-zero exit."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--content-format", "xml", "--dirpath", d, "-y"])
            self.assertNotEqual(result.exit_code, 0)


class TestManifestInitInteractiveFallback(unittest.TestCase):
    """
    Tests for the interactive-fallback path.

    The CLI helpers in `message.py` detect whether stdin is a tty and return
    the default value when it is not (non-interactive context). The
    CliRunner from Typer provides a non-tty stdin by default, so all
    interactive prompts fall back to their defaults automatically.
    """

    def setUp(self):
        self.runner = CliRunner()

    def _invoke(self, args):
        return self.runner.invoke(app, ["manifest", "init"] + args)

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_no_type_flag_uses_default_python(self, mock_init):
        """Without --type, the default 'python' is used."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--content-format", "json", "--dirpath", d, "-y"])
            self.assertEqual(result.exit_code, 0)
            call_kwargs = mock_init.call_args.kwargs
            self.assertEqual(call_kwargs["manifest_type"], ManifestType.PYTHON)

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_no_content_format_flag_uses_default_json(self, mock_init):
        """Without --content-format, the default 'json' is used."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--dirpath", d, "-y"])
            self.assertEqual(result.exit_code, 0)
            call_kwargs = mock_init.call_args.kwargs
            self.assertEqual(call_kwargs["content_format"], ContentFormat.JSON)

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_no_dirpath_flag_uses_current_directory(self, mock_init):
        """Without --dirpath, the current directory ('.') is used."""
        result = self._invoke(["--type", "python", "--content-format", "json", "-y"])
        self.assertEqual(result.exit_code, 0)
        call_kwargs = mock_init.call_args.kwargs
        self.assertEqual(call_kwargs["dirpath"], ".")

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_no_options_flags_uses_default_with_options_true(self, mock_init):
        """Without --options-yes/-no, the default (True) is used in non-interactive mode."""
        with tempfile.TemporaryDirectory() as d:
            result = self._invoke(["--type", "python", "--content-format", "json", "--dirpath", d])
            self.assertEqual(result.exit_code, 0)
            call_kwargs = mock_init.call_args.kwargs
            # In non-tty context `confirmation()` returns its default (True).
            self.assertEqual(call_kwargs["with_options"], True)

    @patch("nextmv.cli.manifest.init.initialize_manifest", return_value="/tmp/app.yaml")
    def test_all_defaults_no_flags(self, mock_init):
        """Invoking with no flags at all should succeed using all defaults."""
        result = self._invoke([])
        self.assertEqual(result.exit_code, 0)
        mock_init.assert_called_once_with(
            manifest_type=ManifestType.PYTHON,
            content_format=ContentFormat.JSON,
            dirpath=".",
            with_options=True,
        )


class TestManifestInitHelp(unittest.TestCase):
    """Sanity checks on the --help output of `manifest init`."""

    def setUp(self):
        self.runner = CliRunner()

    def test_help_exits_zero(self):
        result = self.runner.invoke(app, ["manifest", "init", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_help_documents_content_format_option(self):
        result = self.runner.invoke(app, ["manifest", "init", "--help"])
        self.assertIn("--content-format", result.output)

    def test_help_documents_type_option(self):
        result = self.runner.invoke(app, ["manifest", "init", "--help"])
        self.assertIn("--type", result.output)

    def test_help_documents_dirpath_option(self):
        result = self.runner.invoke(app, ["manifest", "init", "--help"])
        self.assertIn("--dirpath", result.output)

    def test_help_documents_options_yes(self):
        result = self.runner.invoke(app, ["manifest", "init", "--help"])
        self.assertIn("--options-yes", result.output)

    def test_help_documents_options_no(self):
        result = self.runner.invoke(app, ["manifest", "init", "--help"])
        self.assertIn("--options-no", result.output)


if __name__ == "__main__":
    unittest.main()
