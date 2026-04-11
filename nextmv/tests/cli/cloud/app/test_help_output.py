"""Snapshot tests comparing generated help output against captured fixtures.

The fixtures in ``fixtures/`` reflect the post-refactor state of the CLI.
They were captured after Task 11 (the cli/cloud/app connector table
rewrite) and lock in the forward-compatible contract: CLI users and
scripts rely on this exact help text, and any future accidental change
should be caught here.

If any of these tests fail after a framework change, either:
  (a) the help output has legitimately regressed, and the framework must be
      fixed, or
  (b) the fixture needs a deliberate refresh. In (b), the maintainer must
      manually review the diff, explain the change in a commit message, and
      update the fixture — don't auto-regenerate it.
"""

import os
import re
import unittest

from typer.testing import CliRunner

from nextmv.cli.cloud.app import app

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _normalize(text: str) -> str:
    """Normalize help output for comparison.

    Strips trailing whitespace on each line, collapses runs of blank lines to
    a single blank line, and removes ANSI escape codes. This handles the
    common variability in Rich's rendering without masking real changes.
    """
    # Strip ANSI
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    # Strip trailing whitespace per line
    lines = [ln.rstrip() for ln in text.splitlines()]
    # Collapse multiple blank lines
    collapsed: list[str] = []
    prev_blank = False
    for ln in lines:
        if ln == "":
            if not prev_blank:
                collapsed.append(ln)
            prev_blank = True
        else:
            collapsed.append(ln)
            prev_blank = False
    return "\n".join(collapsed).strip()


def _load_fixture(name: str) -> str:
    path = os.path.join(FIXTURES_DIR, name)
    with open(path) as fh:
        return _normalize(fh.read())


class TestHelpOutputSnapshots(unittest.TestCase):
    """Compare generated help output against captured fixtures."""

    def _capture(self, argv: list[str]) -> str:
        result = CliRunner().invoke(app, argv)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return _normalize(result.output)

    def test_list_help_matches_fixture(self) -> None:
        actual = self._capture(["list", "--help"])
        expected = _load_fixture("list_help.txt")
        self.assertEqual(
            actual,
            expected,
            msg=(
                "list --help output diverged from fixture. "
                "Review the diff carefully — update the fixture only if the "
                "change is intentional."
            ),
        )

    def test_create_help_matches_fixture(self) -> None:
        actual = self._capture(["create", "--help"])
        expected = _load_fixture("create_help.txt")
        self.assertEqual(
            actual,
            expected,
            msg=(
                "create --help output diverged from fixture. "
                "Review the diff carefully — update the fixture only if the "
                "change is intentional."
            ),
        )


class TestHelpOutputStructure(unittest.TestCase):
    """Structural assertions that don't depend on exact fixture bytes."""

    def _capture(self, argv: list[str]) -> str:
        result = CliRunner().invoke(app, argv)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return _normalize(result.output)

    def test_list_help_has_examples_section(self) -> None:
        output = self._capture(["list", "--help"])
        self.assertIn("Examples", output)

    def test_list_help_mentions_profile_example_with_hare(self) -> None:
        output = self._capture(["list", "--help"])
        self.assertIn("hare", output)

    def test_create_help_has_examples_section(self) -> None:
        output = self._capture(["create", "--help"])
        self.assertIn("Examples", output)

    def test_create_help_has_is_workflow_flag(self) -> None:
        output = self._capture(["create", "--help"])
        self.assertIn("--is-workflow", output)
        self.assertIn("-w", output)

    def test_create_help_has_app_id_short_flag(self) -> None:
        output = self._capture(["create", "--help"])
        self.assertIn("--app-id", output)
        self.assertIn("-a", output)

    def test_create_help_has_envvar_hint_for_app_id(self) -> None:
        output = self._capture(["create", "--help"])
        self.assertIn("NEXTMV_APP_ID", output)

    def test_exists_help_shows_command(self) -> None:
        output = self._capture(["exists", "--help"])
        self.assertIn("exists", output.lower())

    def test_delete_help_has_app_id_option(self) -> None:
        output = self._capture(["delete", "--help"])
        self.assertIn("--app-id", output)

    def test_push_help_has_app_dir_option(self) -> None:
        output = self._capture(["push", "--help"])
        self.assertIn("--app-dir", output)

    def test_push_help_has_rich_help_panels(self) -> None:
        """push --help preserves the rich_help_panel groupings from the
        interactive workflow (Version control, Instance control)."""
        output = self._capture(["push", "--help"])
        self.assertIn("Version control", output)
        self.assertIn("Instance control", output)


if __name__ == "__main__":
    unittest.main()
