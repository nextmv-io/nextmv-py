"""Tests for nextmv.cli.framework.command helpers.

Phase 2 of the framework implementation. This file grows across tasks —
first ``_render_examples``, then ``cli.command()`` proper.
"""

import unittest
from typing import Annotated
from unittest.mock import patch

import typer
from pydantic import Field
from typer.testing import CliRunner

from nextmv.cli.framework.options import AppDirOption, AppIdRequiredOption
from nextmv.cloud.client import Client


_NAME_HELP = "A name."
_NameOpt = Annotated[
    str | None,
    typer.Option("--name", "-n", help=_NAME_HELP),
    Field(description=_NAME_HELP),
]


class TestRenderExamples(unittest.TestCase):
    def test_empty_tuple_renders_empty_block(self) -> None:
        from nextmv.cli.framework.command import _render_examples

        result = _render_examples(())
        # An empty examples tuple still emits the header but no bullets.
        self.assertIn("[bold][underline]Examples[/underline][/bold]", result)

    def test_single_example(self) -> None:
        from nextmv.cli.framework.command import _render_examples

        result = _render_examples(
            (("List all applications.", "nextmv cloud app list"),)
        )
        self.assertIn("[bold][underline]Examples[/underline][/bold]", result)
        self.assertIn("- List all applications.", result)
        self.assertIn("    $ [dim]nextmv cloud app list[/dim]", result)

    def test_multiple_examples_preserve_order(self) -> None:
        from nextmv.cli.framework.command import _render_examples

        examples = (
            ("First.", "cmd first"),
            ("Second.", "cmd second"),
            ("Third.", "cmd third"),
        )
        result = _render_examples(examples)
        first = result.find("First.")
        second = result.find("Second.")
        third = result.find("Third.")
        self.assertNotEqual(first, -1)
        self.assertNotEqual(second, -1)
        self.assertNotEqual(third, -1)
        self.assertLess(first, second)
        self.assertLess(second, third)

    def test_rich_markup_in_description_passed_through(self) -> None:
        from nextmv.cli.framework.command import _render_examples

        result = _render_examples(
            (
                (
                    "List all applications using the profile named [magenta]hare[/magenta].",
                    "nextmv cloud app list --profile hare",
                ),
            )
        )
        self.assertIn("[magenta]hare[/magenta]", result)

    def test_multi_line_command_preserved(self) -> None:
        from nextmv.cli.framework.command import _render_examples

        cmd = 'nextmv cloud app create --name "Hare" \\\n    --app-id hare'
        result = _render_examples(
            (("Create with continuation.", cmd),)
        )
        self.assertIn(cmd, result)


class TestCommandWrapperShape(unittest.TestCase):
    """cli.command() builds a Typer-registered wrapper with the right signature."""

    def test_rejects_action_without_client_first_param(self) -> None:
        from nextmv.cli.framework.command import command

        def bad_action(name: str) -> dict:
            return {"name": name}

        app = typer.Typer()
        with self.assertRaises(TypeError) as ctx:
            command(app, bad_action)
        self.assertIn("client", str(ctx.exception))

    def test_rejects_action_with_wrong_client_annotation(self) -> None:
        from nextmv.cli.framework.command import command

        def bad_action(client: str, name: str) -> dict:  # type: ignore[override]
            return {"name": name}

        app = typer.Typer()
        with self.assertRaises(TypeError):
            command(app, bad_action)

    def test_wrapper_docstring_concatenates_action_doc_and_examples(self) -> None:
        from nextmv.cli.framework.command import command

        def list_things(client: Client) -> list[dict]:
            """List all things.

            Returns a list of thing dicts.
            """
            return []

        app = typer.Typer()
        wrapper = command(
            app,
            list_things,
            examples=(("List all things.", "cmd list"),),
        )
        self.assertIn("List all things.", wrapper.__doc__)
        self.assertIn("Returns a list of thing dicts.", wrapper.__doc__)
        self.assertIn("[bold][underline]Examples[/underline][/bold]", wrapper.__doc__)
        self.assertIn("$ [dim]cmd list[/dim]", wrapper.__doc__)

    def test_wrapper_has_qualname_pointing_to_action(self) -> None:
        from nextmv.cli.framework.command import command

        def list_things(client: Client) -> list[dict]:
            """List things."""
            return []

        app = typer.Typer()
        wrapper = command(app, list_things)
        self.assertEqual(
            wrapper.__qualname__,
            f"{list_things.__module__}.{list_things.__name__}",
        )
        self.assertEqual(wrapper.__name__, "list_things")


class TestCommandInvocation(unittest.TestCase):
    """Running generated commands via Typer's CliRunner."""

    def _build_app_with_action(self, action, **command_kwargs):
        from nextmv.cli.framework.command import command

        app = typer.Typer()
        wrapper = command(app, action, **command_kwargs)
        return app, wrapper

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.emit")
    def test_simple_list_action_invokes_action_and_emits(
        self, mock_emit, mock_client_cls
    ) -> None:
        mock_client = mock_client_cls.return_value

        def list_things(client: Client) -> list[dict]:
            """List things."""
            return [{"id": "a"}, {"id": "b"}]

        app, _ = self._build_app_with_action(list_things)
        result = CliRunner().invoke(app, [])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_client_cls.assert_called_once_with(profile=None)
        mock_emit.assert_called_once_with(
            [{"id": "a"}, {"id": "b"}], output=None, saved_noun=None
        )

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.emit")
    def test_profile_option_passed_to_client(
        self, mock_emit, mock_client_cls
    ) -> None:
        def list_things(client: Client) -> list[dict]:
            """List things."""
            return []

        app, _ = self._build_app_with_action(list_things)
        result = CliRunner().invoke(app, ["--profile", "hare"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_client_cls.assert_called_once_with(profile="hare")

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.emit")
    def test_action_with_params_forwarded(self, mock_emit, mock_client_cls) -> None:
        captured: dict = {}

        def create_thing(client: Client, name: _NameOpt = None) -> dict:
            """Create a thing."""
            captured["name"] = name
            return {"name": name}

        app, _ = self._build_app_with_action(create_thing)
        result = CliRunner().invoke(app, ["--name", "foo"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(captured["name"], "foo")

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.in_progress")
    @patch("nextmv.cli.framework.command.emit")
    def test_progress_message_printed_when_set(
        self, mock_emit, mock_in_progress, mock_client_cls
    ) -> None:
        def list_things(client: Client) -> list[dict]:
            """List things."""
            return []

        app, _ = self._build_app_with_action(list_things, progress="Listing...")
        result = CliRunner().invoke(app, [])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_in_progress.assert_called_once_with(msg="Listing...")

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.emit")
    def test_output_flag_injects_output_option_and_forwards(
        self, mock_emit, mock_client_cls
    ) -> None:
        def list_things(client: Client) -> list[dict]:
            """List things."""
            return [{"id": "a"}]

        app, _ = self._build_app_with_action(
            list_things, output_flag=True, saved_noun="Thing list"
        )
        result = CliRunner().invoke(app, ["--output", "/tmp/x.json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_emit.assert_called_once_with(
            [{"id": "a"}], output="/tmp/x.json", saved_noun="Thing list"
        )

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.success")
    def test_none_returning_action_uses_on_success_template(
        self, mock_success, mock_client_cls
    ) -> None:
        def delete_thing(client: Client, app_id: AppIdRequiredOption) -> None:
            """Delete a thing."""

        app, _ = self._build_app_with_action(
            delete_thing,
            on_success="Deleted thing [magenta]{app_id}[/magenta].",
        )
        result = CliRunner().invoke(app, ["--app-id", "foo"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_success.assert_called_once_with(
            "Deleted thing [magenta]foo[/magenta]."
        )

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.success")
    def test_none_returning_action_uses_on_success_callable(
        self, mock_success, mock_client_cls
    ) -> None:
        def push_thing(
            client: Client, app_id: AppIdRequiredOption, app_dir: AppDirOption
        ) -> None:
            """Push a thing."""

        app, _ = self._build_app_with_action(
            push_thing,
            on_success=lambda result, kwargs: (
                f"Pushed {kwargs['app_dir']} to {kwargs['app_id']}."
            ),
        )
        result = CliRunner().invoke(
            app, ["--app-id", "foo", "--app-dir", "/path"]
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_success.assert_called_once_with("Pushed /path to foo.")

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.success")
    @patch("nextmv.cli.framework.command.emit")
    def test_output_flag_with_on_success_falls_through_when_output_omitted(
        self, mock_emit, mock_success, mock_client_cls
    ) -> None:
        """When output_flag=True but --output is omitted, on_success still
        runs. This documents the ``conditional bypass'' wording in the
        output_flag docstring: the bypass only fires when --output is
        actually supplied at invocation time.
        """
        def delete_thing(client: Client, app_id: AppIdRequiredOption) -> None:
            """Delete a thing."""

        app, _ = self._build_app_with_action(
            delete_thing,
            output_flag=True,
            saved_noun="Thing",
            on_success="Deleted thing [magenta]{app_id}[/magenta].",
        )
        result = CliRunner().invoke(app, ["--app-id", "foo"])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        # --output not supplied → emit NOT called, on_success fires.
        mock_emit.assert_not_called()
        mock_success.assert_called_once_with("Deleted thing [magenta]foo[/magenta].")


class TestHandlesOwnOutput(unittest.TestCase):
    """cli.command(handles_own_output=True) mode for interactive workflows
    like the push workflow that manage their own messaging."""

    def test_rejects_combo_with_output_flag(self) -> None:
        """handles_own_output=True and output_flag=True are incompatible."""
        from nextmv.cli.framework.command import command

        def workflow(client: Client) -> None:
            """A workflow."""

        app = typer.Typer()
        with self.assertRaises(TypeError) as ctx:
            command(app, workflow, handles_own_output=True, output_flag=True)
        self.assertIn("handles_own_output", str(ctx.exception))

    def test_rejects_combo_with_on_success(self) -> None:
        """handles_own_output=True and on_success are incompatible — the
        workflow is expected to print its own success messages."""
        from nextmv.cli.framework.command import command

        def workflow(client: Client) -> None:
            """A workflow."""

        app = typer.Typer()
        with self.assertRaises(TypeError) as ctx:
            command(
                app,
                workflow,
                handles_own_output=True,
                on_success="Done.",
            )
        self.assertIn("handles_own_output", str(ctx.exception))

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.emit")
    @patch("nextmv.cli.framework.command.success")
    def test_handles_own_output_skips_emit_and_success(
        self, mock_success, mock_emit, mock_client_cls
    ) -> None:
        """In handles_own_output mode, neither emit nor success is called
        by the wrapper — the action is responsible for all output."""
        from nextmv.cli.framework.command import command

        captured = {"called": False}

        def workflow(client: Client, app_id: AppIdRequiredOption) -> None:
            """A workflow that manages its own output."""
            captured["called"] = True
            captured["client"] = client
            captured["app_id"] = app_id

        app = typer.Typer()
        command(app, workflow, handles_own_output=True)

        result = CliRunner().invoke(app, ["--app-id", "foo"])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        self.assertTrue(captured["called"])
        self.assertEqual(captured["app_id"], "foo")
        mock_emit.assert_not_called()
        mock_success.assert_not_called()

    @patch("nextmv.cli.framework.command.Client")
    @patch("nextmv.cli.framework.command.in_progress")
    def test_handles_own_output_still_runs_progress(
        self, mock_in_progress, mock_client_cls
    ) -> None:
        """Progress messages are still printed before the workflow runs."""
        from nextmv.cli.framework.command import command

        def workflow(client: Client) -> None:
            """A workflow."""

        app = typer.Typer()
        command(app, workflow, handles_own_output=True, progress="Working...")

        result = CliRunner().invoke(app, [])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_in_progress.assert_called_once_with(msg="Working...")

    @patch("nextmv.cli.framework.command.Client")
    def test_handles_own_output_still_injects_profile(
        self, mock_client_cls
    ) -> None:
        """--profile still drives Client construction in handles_own_output mode."""
        from nextmv.cli.framework.command import command

        def workflow(client: Client) -> None:
            """A workflow."""

        app = typer.Typer()
        command(app, workflow, handles_own_output=True)

        result = CliRunner().invoke(app, ["--profile", "hare"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_client_cls.assert_called_once_with(profile="hare")


if __name__ == "__main__":
    unittest.main()
