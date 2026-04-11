"""Tests for nextmv.cli.framework.result helpers."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from nextmv.cli.framework import result as fresult


class TestFormatSaveMessage(unittest.TestCase):
    def test_default_noun_is_result(self) -> None:
        msg = fresult.format_save_message(output="/tmp/foo.json", saved_noun=None)
        self.assertEqual(msg, "Result saved to [magenta]/tmp/foo.json[/magenta].")

    def test_custom_noun_is_capitalized(self) -> None:
        msg = fresult.format_save_message(
            output="/tmp/apps.json", saved_noun="application list information"
        )
        self.assertEqual(
            msg, "Application list information saved to [magenta]/tmp/apps.json[/magenta]."
        )

    def test_noun_already_capitalized(self) -> None:
        msg = fresult.format_save_message(output="/tmp/x.json", saved_noun="Run list")
        self.assertEqual(msg, "Run list saved to [magenta]/tmp/x.json[/magenta].")

    def test_whitespace_only_noun_falls_back_to_result(self) -> None:
        msg = fresult.format_save_message(output="/tmp/x.json", saved_noun="   ")
        self.assertEqual(msg, "Result saved to [magenta]/tmp/x.json[/magenta].")


class TestEmit(unittest.TestCase):
    @patch("nextmv.cli.framework.result.print_json")
    def test_emit_without_output_prints_json(self, mock_print_json) -> None:
        data = {"id": "my-app", "name": "My App"}
        fresult.emit(data, output=None)
        mock_print_json.assert_called_once_with(data)

    @patch("nextmv.cli.framework.result.success")
    @patch("nextmv.cli.framework.result.print_json")
    def test_emit_with_output_writes_file_and_prints_success(
        self, mock_print_json, mock_success
    ) -> None:
        data = [{"id": "a"}, {"id": "b"}]
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "out.json")
            fresult.emit(data, output=out_path, saved_noun="Application list information")

            # File was written.
            self.assertTrue(os.path.exists(out_path))
            with open(out_path) as fh:
                self.assertEqual(json.load(fh), data)

            # Success message was printed (not print_json).
            mock_print_json.assert_not_called()
            mock_success.assert_called_once()
            msg = mock_success.call_args[0][0]
            self.assertIn("Application list information", msg)
            self.assertIn(f"[magenta]{out_path}[/magenta]", msg)

    @patch("nextmv.cli.framework.result.success")
    @patch("nextmv.cli.framework.result.print_json")
    def test_emit_with_empty_output_string_prints_json(
        self, mock_print_json, mock_success
    ) -> None:
        # Empty string should be treated as "no --output supplied".
        fresult.emit({"x": 1}, output="")
        mock_print_json.assert_called_once_with({"x": 1})
        mock_success.assert_not_called()


if __name__ == "__main__":
    unittest.main()
