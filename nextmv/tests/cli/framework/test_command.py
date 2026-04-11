"""Tests for nextmv.cli.framework.command helpers.

Phase 2 of the framework implementation. This file grows across tasks —
first ``_render_examples``, then ``cli.command()`` proper.
"""

import unittest


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


if __name__ == "__main__":
    unittest.main()
