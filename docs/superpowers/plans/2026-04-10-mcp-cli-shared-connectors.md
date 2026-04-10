# CLI / MCP Shared Connectors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace hand-written Typer CLI command files and FastMCP tool wrappers in the `app` domain with introspection-based connectors that derive parameter signatures, types, help text, and docstrings from pure action functions. Pilot only — framework plus `app` domain.

**Architecture:** Add a `nextmv/cli/framework/` package with `cli.command()` that generates Typer commands from pure action functions using `inspect.signature` and dual-purpose `Annotated` type aliases (Typer `Option` + Pydantic `Field` in one alias). Add `nextmv/cli/mcp/framework/` with `mcp_fw.tool()` doing the same for FastMCP. Migrate the `app` domain action to carry dual-purpose options on its signature, replace 7 per-command Typer files with a single connector file of ~10 `cli.command()` calls, and replace the MCP `app.py` tool file with `mcp_fw.tool()` calls. Pure refactor — no observable contract changes.

**Tech Stack:**
- Python 3.10+ (project requires-python ≥ 3.10)
- Typer ≥ 0.20.1, Pydantic ≥ 2.5.2, MCP `mcp[cli]` ≥ 1.0
- Test framework: `unittest` + `pytest` runner via `uv run pytest` from the `nextmv/` package directory
- Design reference: `docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md`

**Local only:** This branch (`refactor/mcp-shared-actions`) stays local. **No `git push`, no PR creation** anywhere in this plan. The final task stops at "tests pass locally, ready for review."

---

## File Structure

### Created
- `nextmv/nextmv/cli/framework/__init__.py` — public API re-exports for `cli.command`, `cli.progress`, `cli.emit`, and option aliases
- `nextmv/nextmv/cli/framework/options.py` — dual-purpose `Annotated` type aliases used by the `app` domain action
- `nextmv/nextmv/cli/framework/result.py` — `emit()`, save-message formatter, `on_success` template/callable handling
- `nextmv/nextmv/cli/framework/command.py` — `cli.command()` implementation + `_render_examples()`
- `nextmv/nextmv/cli/mcp/framework/__init__.py` — re-exports for `mcp_fw.tool`, `mcp_fw.client`, `mcp_fw.clean`
- `nextmv/nextmv/cli/mcp/framework/tool.py` — `mcp_fw.tool()` implementation
- `nextmv/tests/cli/framework/__init__.py` — empty
- `nextmv/tests/cli/framework/test_spike.py` — feasibility spike (deleted in Task 20)
- `nextmv/tests/cli/framework/test_options.py` — permanent regression guard
- `nextmv/tests/cli/framework/test_command.py` — unit tests for `cli.command()`
- `nextmv/tests/cli/framework/test_tool.py` — unit tests for `mcp_fw.tool()`
- `nextmv/tests/cli/cloud/__init__.py` — empty
- `nextmv/tests/cli/cloud/app/__init__.py` — empty
- `nextmv/tests/cli/cloud/app/fixtures/list_help.txt` — golden snapshot of current `list --help` output
- `nextmv/tests/cli/cloud/app/fixtures/create_help.txt` — golden snapshot of current `create --help` output
- `nextmv/tests/cli/cloud/app/test_help_output.py` — CLI help snapshot tests
- `nextmv/tests/cli/mcp/test_app_schemas.py` — MCP tool schema assertions for the `app` domain

### Modified
- `nextmv/nextmv/cli/actions/app.py` — swap bare parameter types for dual-purpose aliases; expand docstrings
- `nextmv/nextmv/cli/cloud/app/__init__.py` — rewrite as the connector table (holds all 7 commands)
- `nextmv/nextmv/cli/mcp/tools/app.py` — rewrite as `mcp_fw.tool()` calls

### Deleted
- `nextmv/nextmv/cli/cloud/app/create.py`
- `nextmv/nextmv/cli/cloud/app/delete.py`
- `nextmv/nextmv/cli/cloud/app/exists.py`
- `nextmv/nextmv/cli/cloud/app/get.py`
- `nextmv/nextmv/cli/cloud/app/list.py`
- `nextmv/nextmv/cli/cloud/app/push.py`
- `nextmv/nextmv/cli/cloud/app/update.py`
- `nextmv/tests/cli/framework/test_spike.py` (in Task 20, after `test_options.py` supersedes it)

---

## Phase 0: Feasibility Spike

The spec's biggest open risk is: does Pydantic v2 (used by FastMCP) tolerate a `typer.OptionInfo` in the same `Annotated[...]` metadata list where it is also looking for `FieldInfo`? Validate this before writing any framework code.

### Task 1: Feasibility spike — dual-purpose Annotated alias

**Files:**
- Create: `nextmv/tests/cli/framework/__init__.py`
- Create: `nextmv/tests/cli/framework/test_spike.py`

- [ ] **Step 1: Create the empty package init**

Create `nextmv/tests/cli/framework/__init__.py` with no content:

```python
```

- [ ] **Step 2: Write the spike test**

Create `nextmv/tests/cli/framework/test_spike.py`:

```python
"""Feasibility spike: does Annotated carry both typer.Option and pydantic.Field?

This file is deleted once ``test_options.py`` supersedes it as the permanent
regression guard. Its only purpose is to confirm that a single Annotated alias
can drive both Typer and FastMCP without either library choking on the other's
metadata marker.
"""

import unittest
from typing import Annotated, TypeAlias

import typer
from mcp.server.fastmcp import FastMCP
from pydantic import Field, TypeAdapter
from typer.testing import CliRunner

_HELP = "An optional test value."

TestOption: TypeAlias = Annotated[
    str | None,
    typer.Option("--value", "-v", help=_HELP, metavar="VALUE"),
    Field(description=_HELP),
]


class TestDualPurposeAnnotated(unittest.TestCase):
    def test_typer_consumes_option_metadata(self) -> None:
        app = typer.Typer()

        @app.command()
        def echo(value: TestOption = None) -> None:
            typer.echo(f"value={value}")

        runner = CliRunner()
        result = runner.invoke(app, ["--value", "hello"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("value=hello", result.stdout)

        # Short flag still works
        result = runner.invoke(app, ["-v", "short"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("value=short", result.stdout)

    def test_pydantic_type_adapter_accepts_alias(self) -> None:
        # Pydantic must ignore the typer.OptionInfo and still build a schema
        # that picks up the Field(description=...).
        adapter = TypeAdapter(TestOption)
        schema = adapter.json_schema()
        # The description should come from the Field(...) metadata.
        # The alias is `str | None`, so Pydantic renders it as anyOf.
        self.assertIn("description", schema)
        self.assertEqual(schema["description"], _HELP)

    def test_fastmcp_registers_tool_with_alias(self) -> None:
        server = FastMCP("spike-test")

        @server.tool(name="spike_echo")
        def spike_echo(value: TestOption = None) -> str:
            """Echo the value back."""
            return f"value={value}"

        # Tool is registered and its input schema carries the description.
        tool = server._tool_manager._tools["spike_echo"]
        self.assertIsNotNone(tool)
        schema = tool.parameters
        # FastMCP builds a JSON schema with a `properties` dict keyed by
        # parameter name.
        self.assertIn("value", schema["properties"])
        self.assertEqual(schema["properties"]["value"].get("description"), _HELP)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the spike**

Run from `nextmv/` directory:

```bash
cd nextmv && uv run pytest tests/cli/framework/test_spike.py -v
```

Expected: all three tests PASS.

- [ ] **Step 4: If the spike fails, STOP**

If any test fails:
- If `test_pydantic_type_adapter_accepts_alias` fails with a Pydantic error about `typer.OptionInfo`, the single-alias approach is infeasible. **STOP and escalate to the human.** The fallback is sibling aliases (`AppIdCli` / `AppIdMcp` sharing `_APP_ID_HELP`), which requires changes to the plan's downstream tasks. Do not proceed silently.
- If `test_fastmcp_registers_tool_with_alias` fails because `tool.parameters` has a different structure, investigate the actual structure via `print(tool.parameters)` and update the assertion. This is a test-shape issue, not a blocker.

If all three pass, proceed.

- [ ] **Step 5: Commit the spike**

```bash
git add nextmv/tests/cli/framework/__init__.py nextmv/tests/cli/framework/test_spike.py
git commit -m "test: feasibility spike for dual-purpose Annotated aliases"
```

---

## Phase 1: Framework Options Module

### Task 2: Create framework package skeleton

**Files:**
- Create: `nextmv/nextmv/cli/framework/__init__.py`
- Create: `nextmv/nextmv/cli/framework/options.py`

- [ ] **Step 1: Create the framework package init (temporarily empty)**

Create `nextmv/nextmv/cli/framework/__init__.py`:

```python
"""Helpers for building Typer CLI commands and options from pure action functions.

This package is the CLI-side half of the shared-connectors framework. It
pairs with ``nextmv.cli.mcp.framework`` which provides the MCP-side helpers.
Both consume pure action functions from ``nextmv.cli.actions`` and generate
frontend wrappers with matching signatures.

Import at call sites as::

    from nextmv.cli import framework as cli

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""
```

- [ ] **Step 2: Create the options module with the aliases the app domain needs**

Create `nextmv/nextmv/cli/framework/options.py`:

```python
"""Dual-purpose ``Annotated`` option aliases shared by CLI and MCP frontends.

Each alias carries two metadata entries:

* ``typer.Option(...)`` — consumed by Typer when building CLI commands.
* ``pydantic.Field(description=...)`` — consumed by FastMCP's Pydantic layer
  when building MCP tool schemas.

Python's ``Annotated`` accepts multiple metadata entries; Typer walks them
looking for ``ParameterInfo`` and Pydantic walks them looking for
``FieldInfo``. They coexist without conflict. See the feasibility spike
(historical) and ``tests/cli/framework/test_options.py`` for the permanent
regression guard.

The help text for each option is defined once as a module-level constant and
referenced twice inside the alias (once by ``typer.Option(help=...)`` and once
by ``Field(description=...)``) so it stays in sync.

Framework-internal aliases (e.g. ``_OutputOption``) omit the ``Field(...)``
entry because they have no MCP counterpart. They are injected automatically
by ``cli.command(output_flag=True, ...)`` and are not imported by domain
connector files.
"""

from typing import Annotated, TypeAlias

import typer
from pydantic import Field

# ---------------------------------------------------------------------------
# App domain — dual-purpose aliases used by cli/actions/app.py
# ---------------------------------------------------------------------------

_APP_ID_HELP = (
    "An optional ID for the Nextmv Cloud application. "
    "If not provided, a random ID will be generated."
)
AppIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--app-id",
        "-a",
        help=_APP_ID_HELP,
        metavar="APP_ID",
        envvar="NEXTMV_APP_ID",
    ),
    Field(description=_APP_ID_HELP),
]

_APP_ID_REQUIRED_HELP = "The Nextmv Cloud application ID."
AppIdRequiredOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--app-id",
        "-a",
        help=_APP_ID_REQUIRED_HELP,
        metavar="APP_ID",
        envvar="NEXTMV_APP_ID",
    ),
    Field(description=_APP_ID_REQUIRED_HELP),
]

_NAME_HELP = (
    "A name for the application. If not provided, the application ID will be "
    "used as the name."
)
NameOption: TypeAlias = Annotated[
    str | None,
    typer.Option("--name", "-n", help=_NAME_HELP, metavar="NAME"),
    Field(description=_NAME_HELP),
]

_DESCRIPTION_HELP = "An optional description for the application."
DescriptionOption: TypeAlias = Annotated[
    str | None,
    typer.Option("--description", "-d", help=_DESCRIPTION_HELP, metavar="DESCRIPTION"),
    Field(description=_DESCRIPTION_HELP),
]

_DEFAULT_INSTANCE_ID_HELP = "An optional default instance ID for the application."
DefaultInstanceIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--default-instance-id",
        "-i",
        help=_DEFAULT_INSTANCE_ID_HELP,
        metavar="DEFAULT_INSTANCE_ID",
    ),
    Field(description=_DEFAULT_INSTANCE_ID_HELP),
]

_DEFAULT_EXPERIMENT_INSTANCE_HELP = (
    "An optional default experiment instance ID for the application."
)
DefaultExperimentInstanceOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--default-experiment-instance",
        "-x",
        help=_DEFAULT_EXPERIMENT_INSTANCE_HELP,
        metavar="DEFAULT_EXPERIMENT_INSTANCE",
    ),
    Field(description=_DEFAULT_EXPERIMENT_INSTANCE_HELP),
]

_IS_WORKFLOW_HELP = "Whether the application is a workflow."
IsWorkflowOption: TypeAlias = Annotated[
    bool,
    typer.Option("--is-workflow", "-w", help=_IS_WORKFLOW_HELP),
    Field(description=_IS_WORKFLOW_HELP),
]

_EXIST_OK_HELP = (
    "If an application with the given ID already exists, do not raise an "
    "error, and simply return it."
)
ExistOkOption: TypeAlias = Annotated[
    bool,
    typer.Option("--exist-ok", "-e", help=_EXIST_OK_HELP),
    Field(description=_EXIST_OK_HELP),
]

_APP_DIR_HELP = (
    "Absolute path to the local directory containing the application code "
    "and ``app.yaml`` manifest."
)
AppDirOption: TypeAlias = Annotated[
    str,
    typer.Option("--app-dir", "-D", help=_APP_DIR_HELP, metavar="APP_DIR"),
    Field(description=_APP_DIR_HELP),
]


# ---------------------------------------------------------------------------
# Framework-internal CLI-only aliases — NOT imported by domain connector files.
# These are injected automatically by ``cli.command()`` when flags like
# ``output_flag=True`` are set.
# ---------------------------------------------------------------------------

_OUTPUT_HELP = "Save the result as JSON to this file path."
_OutputOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--output",
        "-o",
        help=_OUTPUT_HELP,
        metavar="OUTPUT_PATH",
    ),
]
```

- [ ] **Step 3: Run pytest to confirm nothing is broken by the new files**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_spike.py -v
```

Expected: spike tests still PASS (the new package files don't import anything unusual).

- [ ] **Step 4: Commit**

```bash
git add nextmv/nextmv/cli/framework/__init__.py nextmv/nextmv/cli/framework/options.py
git commit -m "feat(framework): add dual-purpose option aliases for app domain"
```

### Task 3: Options regression guard

**Files:**
- Create: `nextmv/tests/cli/framework/test_options.py`

- [ ] **Step 1: Write the permanent regression guard**

Create `nextmv/tests/cli/framework/test_options.py`:

```python
"""Permanent regression guard for dual-purpose Annotated option aliases.

Supersedes the feasibility spike. For every dual-purpose alias in
``nextmv.cli.framework.options``, assert both frontends consume it
correctly:

* Typer: the alias can be used as a CLI parameter and the short flag, long
  flag, and envvar all work through ``CliRunner``.
* Pydantic: ``TypeAdapter(alias).json_schema()`` picks up the description
  from the ``Field(...)`` metadata.

If this file ever fails, the dual-alias assumption has broken — either a
library version bump changed behavior, or one of the aliases was edited
incorrectly. Either way, stop and investigate.
"""

import unittest
from typing import Annotated

import typer
from pydantic import TypeAdapter
from typer.testing import CliRunner

from nextmv.cli.framework import options as fopts


class TestDualPurposeAliases(unittest.TestCase):
    """Assert every public dual-purpose alias works in both frontends."""

    def _assert_pydantic_description(self, alias, expected_substring: str) -> None:
        """The alias must carry a ``Field(description=...)`` marker that
        Pydantic surfaces in the JSON schema."""
        schema = TypeAdapter(alias).json_schema()
        description = schema.get("description", "")
        self.assertIn(
            expected_substring,
            description,
            f"Expected Pydantic schema description to contain {expected_substring!r}, "
            f"got {description!r}",
        )

    def _assert_typer_consumes(self, alias, long_flag: str, short_flag: str, sample: str) -> None:
        """The alias must be usable as a ``typer.Option(...)`` and the flags
        must work via ``CliRunner``."""
        app = typer.Typer()

        @app.command()
        def cmd(value: alias = None) -> None:  # type: ignore[valid-type]
            typer.echo(f"value={value}")

        runner = CliRunner()

        result = runner.invoke(app, [long_flag, sample])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(f"value={sample}", result.stdout)

        result = runner.invoke(app, [short_flag, sample])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(f"value={sample}", result.stdout)

    def test_app_id_option(self) -> None:
        self._assert_typer_consumes(fopts.AppIdOption, "--app-id", "-a", "my-app")
        self._assert_pydantic_description(fopts.AppIdOption, "optional ID")

    def test_name_option(self) -> None:
        self._assert_typer_consumes(fopts.NameOption, "--name", "-n", "MyName")
        self._assert_pydantic_description(fopts.NameOption, "name for the application")

    def test_description_option(self) -> None:
        self._assert_typer_consumes(
            fopts.DescriptionOption, "--description", "-d", "Does stuff"
        )
        self._assert_pydantic_description(fopts.DescriptionOption, "description")

    def test_default_instance_id_option(self) -> None:
        self._assert_typer_consumes(
            fopts.DefaultInstanceIdOption, "--default-instance-id", "-i", "inst-1"
        )
        self._assert_pydantic_description(
            fopts.DefaultInstanceIdOption, "default instance ID"
        )

    def test_default_experiment_instance_option(self) -> None:
        self._assert_typer_consumes(
            fopts.DefaultExperimentInstanceOption,
            "--default-experiment-instance",
            "-x",
            "exp-1",
        )
        self._assert_pydantic_description(
            fopts.DefaultExperimentInstanceOption, "default experiment instance"
        )

    def test_bool_aliases_have_pydantic_descriptions(self) -> None:
        # Bool aliases can't easily be exercised via CliRunner with a value
        # argument (they're flags), so only assert the Pydantic side.
        self._assert_pydantic_description(fopts.IsWorkflowOption, "workflow")
        self._assert_pydantic_description(fopts.ExistOkOption, "already exists")

    def test_bool_flag_works_via_typer(self) -> None:
        """Smoke-test that an IsWorkflowOption flag is settable via Typer."""
        app = typer.Typer()

        @app.command()
        def cmd(flag: fopts.IsWorkflowOption = False) -> None:  # type: ignore[valid-type]
            typer.echo(f"flag={flag}")

        runner = CliRunner()
        result = runner.invoke(app, ["--is-workflow"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("flag=True", result.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the regression guard**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_options.py -v
```

Expected: all tests PASS.

- [ ] **Step 3: Commit**

```bash
git add nextmv/tests/cli/framework/test_options.py
git commit -m "test(framework): permanent regression guard for dual-purpose options"
```

---

## Phase 2: `cli.command()` Builder

The builder is the most complex piece — it does signature introspection, wrapper generation, and result handling. Build it in small TDD increments.

### Task 4: `result.py` — save-message formatting and emit()

**Files:**
- Create: `nextmv/nextmv/cli/framework/result.py`

- [ ] **Step 1: Write the test first**

Create `nextmv/tests/cli/framework/test_result.py`:

```python
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
```

- [ ] **Step 2: Run the test — expect it to fail**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_result.py -v
```

Expected: FAIL (module doesn't exist yet). Example error: `ModuleNotFoundError: No module named 'nextmv.cli.framework.result'`.

- [ ] **Step 3: Implement `result.py`**

Create `nextmv/nextmv/cli/framework/result.py`:

```python
"""Result rendering helpers for CLI commands.

``emit()`` is the default output branch for ``cli.command()``: prints the
action's return value as JSON, or saves it to a file with a success message
when ``--output`` was supplied.

``format_save_message()`` produces the save-to-file success message using the
structured-data-to-markup pattern described in the spec ("Design Principle:
Structured Data → Rendered Markup").

``apply_on_success()`` handles ``cli.command(on_success=...)`` — either a
``str.format`` template or a callable ``(result, kwargs) -> str``.
"""

import json
from pathlib import Path
from typing import Any, Callable

from nextmv.cli.message import print_json, success


def format_save_message(*, output: str, saved_noun: str | None) -> str:
    """Format the save-to-file success message.

    The default noun is ``"Result"``. A user-supplied ``saved_noun`` is
    capitalized at the first letter (so ``"run list"`` becomes ``"Run list"``)
    and embedded before ``"saved to [magenta]{output}[/magenta]."``.
    """
    noun = (saved_noun or "Result").strip()
    if noun:
        noun = noun[0].upper() + noun[1:]
    return f"{noun} saved to [magenta]{output}[/magenta]."


def emit(
    result: Any,
    *,
    output: str | None = None,
    saved_noun: str | None = None,
) -> None:
    """Render ``result`` to stdout or to a file.

    When ``output`` is an empty or ``None`` value, prints the result as JSON.
    When ``output`` is a non-empty path, writes the result as JSON to that
    path and prints a save-success message instead.
    """
    if output:
        Path(output).write_text(json.dumps(result, indent=2))
        success(format_save_message(output=output, saved_noun=saved_noun))
        return
    print_json(result)


def apply_on_success(
    on_success: str | Callable[[Any, dict[str, Any]], str] | None,
    *,
    result: Any,
    kwargs: dict[str, Any],
) -> str | None:
    """Format the ``on_success`` handler into a display string.

    Returns ``None`` when ``on_success`` is ``None``. Returns the formatted
    string otherwise. The caller is responsible for passing the returned
    string to ``success(...)``.

    Templates are formatted via ``str.format(**kwargs)``. Callables receive
    ``(result, kwargs)`` and must return a string.
    """
    if on_success is None:
        return None
    if callable(on_success):
        return on_success(result, kwargs)
    return on_success.format(**kwargs)
```

- [ ] **Step 4: Run the test — expect it to pass**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_result.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add nextmv/nextmv/cli/framework/result.py nextmv/tests/cli/framework/test_result.py
git commit -m "feat(framework): add result.emit, save-message, on_success helpers"
```

### Task 5: `command.py` — `_render_examples()` helper

**Files:**
- Create: `nextmv/nextmv/cli/framework/command.py` (this task adds `_render_examples` only; the full builder lands in Task 6)

- [ ] **Step 1: Extend the test file to cover `_render_examples`**

Append to `nextmv/tests/cli/framework/test_result.py` a new test class OR create `nextmv/tests/cli/framework/test_command.py` now. Create `nextmv/tests/cli/framework/test_command.py`:

```python
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
```

- [ ] **Step 2: Run the test — expect it to fail**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_command.py -v
```

Expected: FAIL (module doesn't exist). Example: `ModuleNotFoundError: No module named 'nextmv.cli.framework.command'`.

- [ ] **Step 3: Create the initial `command.py` with `_render_examples` only**

Create `nextmv/nextmv/cli/framework/command.py`:

```python
"""``cli.command()`` builder and helpers.

Given a pure action function under ``nextmv.cli.actions``, generates a Typer
command wrapper whose signature mirrors the action's (minus the ``client``
parameter, plus framework-injected flags like ``--profile`` and optionally
``--output``). The wrapper reads metadata from the action's ``Annotated``
parameters so the same aliases drive both CLI and MCP tool registration.

This module is imported at call sites as part of ``cli`` via::

    from nextmv.cli import framework as cli
    list = cli.command(app, list_apps, ...)
"""

from typing import Tuple

Example = Tuple[str, str]  # (description, command)


def _render_examples(examples: tuple[Example, ...]) -> str:
    """Render a tuple of ``(description, command)`` pairs into a Rich-formatted
    examples block suitable for appending to a Typer command docstring.

    The output reproduces the hand-written format used on ``develop``:

    * Header: ``[bold][underline]Examples[/underline][/bold]``
    * Bullet per pair: ``- {description}``
    * Command under each bullet: ``    $ [dim]{command}[/dim]``
    * Blank lines between entries.

    Rich markup inside ``description`` is passed through verbatim so
    inline highlights like ``[magenta]hare[/magenta]`` render correctly.
    """
    lines: list[str] = ["", "[bold][underline]Examples[/underline][/bold]", ""]
    for description, command in examples:
        lines.append(f"- {description}")
        lines.append(f"    $ [dim]{command}[/dim]")
        lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: Run the test — expect it to pass**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_command.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add nextmv/nextmv/cli/framework/command.py nextmv/tests/cli/framework/test_command.py
git commit -m "feat(framework): add _render_examples for structured example blocks"
```

### Task 6: `cli.command()` — signature inspection and wrapper construction

**Files:**
- Modify: `nextmv/nextmv/cli/framework/command.py`
- Modify: `nextmv/tests/cli/framework/test_command.py`

- [ ] **Step 1: Add failing tests for `cli.command()` wrapping a fake action**

Append to `nextmv/tests/cli/framework/test_command.py` (keep existing classes, add below them):

```python
from typing import Annotated
from unittest.mock import patch

import typer
from pydantic import Field
from typer.testing import CliRunner

from nextmv.cloud.client import Client


_NAME_HELP = "A name."
_NameOpt = Annotated[
    str | None,
    typer.Option("--name", "-n", help=_NAME_HELP),
    Field(description=_NAME_HELP),
]


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

    def _build_app_with_action(
        self, action, **command_kwargs
    ) -> tuple[typer.Typer, object]:
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
        def delete_thing(client: Client, app_id: str) -> None:
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
        def push_thing(client: Client, app_id: str, app_dir: str) -> None:
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
```

- [ ] **Step 2: Run the tests — expect them to fail**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_command.py -v
```

Expected: the existing `TestRenderExamples` class still passes; all new tests FAIL because `command` is not yet defined.

- [ ] **Step 3: Implement `cli.command()`**

Replace `nextmv/nextmv/cli/framework/command.py` with:

```python
"""``cli.command()`` builder and helpers.

Given a pure action function under ``nextmv.cli.actions``, generates a Typer
command wrapper whose signature mirrors the action's (minus the ``client``
parameter, plus framework-injected flags like ``--profile`` and optionally
``--output``). The wrapper reads metadata from the action's ``Annotated``
parameters so the same aliases drive both CLI and MCP tool registration.

This module is imported at call sites as part of ``cli`` via::

    from nextmv.cli import framework as cli
    list = cli.command(app, list_apps, ...)
"""

import functools
import inspect
from typing import Any, Callable, Tuple

import typer

from nextmv.cli.framework.options import _OutputOption
from nextmv.cli.framework.result import apply_on_success, emit
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import ProfileOption
from nextmv.cloud.client import Client

Example = Tuple[str, str]  # (description, command)


def _render_examples(examples: tuple[Example, ...]) -> str:
    """Render a tuple of ``(description, command)`` pairs into a Rich-formatted
    examples block suitable for appending to a Typer command docstring.

    The output reproduces the hand-written format used on ``develop``:

    * Header: ``[bold][underline]Examples[/underline][/bold]``
    * Bullet per pair: ``- {description}``
    * Command under each bullet: ``    $ [dim]{command}[/dim]``
    * Blank lines between entries.

    Rich markup inside ``description`` is passed through verbatim so
    inline highlights like ``[magenta]hare[/magenta]`` render correctly.
    """
    lines: list[str] = ["", "[bold][underline]Examples[/underline][/bold]", ""]
    for description, command in examples:
        lines.append(f"- {description}")
        lines.append(f"    $ [dim]{command}[/dim]")
        lines.append("")
    return "\n".join(lines)


def _assert_first_param_is_client(action: Callable) -> inspect.Signature:
    """Assert that the action's first parameter is ``client: Client``.

    Returns the action's ``inspect.Signature`` for further use by the builder.
    Raises ``TypeError`` with a clear message at import time if the
    convention is violated.
    """
    sig = inspect.signature(action)
    params = list(sig.parameters.values())
    if not params or params[0].name != "client":
        raise TypeError(
            f"{action.__name__} must take `client: Client` as its first parameter "
            f"(got parameters: {[p.name for p in params]})"
        )
    if params[0].annotation is not Client:
        raise TypeError(
            f"{action.__name__}'s first parameter must be annotated as "
            f"`client: Client`, got annotation {params[0].annotation!r}"
        )
    return sig


def command(
    typer_app: typer.Typer,
    action: Callable,
    *,
    name: str | None = None,
    progress: str | None = None,
    output_flag: bool = False,
    saved_noun: str | None = None,
    on_success: str | Callable[[Any, dict[str, Any]], str] | None = None,
    examples: tuple[Example, ...] | None = None,
) -> Callable:
    """Build and register a Typer command wrapper around a pure action.

    Parameters
    ----------
    typer_app:
        The ``typer.Typer`` instance to register the command on.
    action:
        The pure action function. Must take ``client: Client`` as its first
        parameter; remaining parameters are exposed as Typer options using
        their existing ``Annotated`` metadata.
    name:
        Optional Typer command name. Defaults to ``action.__name__``.
    progress:
        Optional in-progress message printed before the action is invoked.
    output_flag:
        If ``True``, inject ``--output/-o OUTPUT_PATH`` as a keyword-only
        option on the generated command. When the user supplies it, the
        action's return value is written as JSON to the file and a
        save-success message is printed, bypassing ``on_success``.
    saved_noun:
        The noun for the save-success message (e.g. ``"Application list information"``
        → ``"Application list information saved to [magenta]{path}[/magenta]."``).
        Only meaningful with ``output_flag=True``. Defaults to ``"Result"``.
    on_success:
        Either a ``str.format``-style template (formatted with ``**kwargs``
        where kwargs is the dict passed to the action) or a callable
        ``(result, kwargs) -> str``. Used when the action returns ``None`` or
        when the command wants a custom success line instead of printing
        JSON. Bypassed when ``--output`` is supplied.
    examples:
        Tuple of ``(description, command)`` pairs rendered into the command's
        help text as a Rich-formatted examples block.

    Returns
    -------
    The generated wrapper function (already registered on ``typer_app``). The
    wrapper can be assigned to a variable for later reference.
    """
    sig = _assert_first_param_is_client(action)
    action_params = list(sig.parameters.values())
    user_params = action_params[1:]  # drop `client`

    # Build the wrapper's parameter list: user params (kinds preserved) +
    # framework-injected `profile`, and optionally `output`.
    wrapper_params: list[inspect.Parameter] = []
    for p in user_params:
        # Preserve parameter kind (POSITIONAL_OR_KEYWORD, KEYWORD_ONLY, etc.)
        # by using Parameter.replace() — the annotation and default carry over
        # as-is, which means Annotated[...] metadata flows through to Typer.
        wrapper_params.append(p.replace())

    wrapper_params.append(
        inspect.Parameter(
            "profile",
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=ProfileOption,
        )
    )
    if output_flag:
        wrapper_params.append(
            inspect.Parameter(
                "output",
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=_OutputOption,
            )
        )

    def wrapper(**kwargs: Any) -> None:
        profile = kwargs.pop("profile", None)
        output = kwargs.pop("output", None) if output_flag else None
        client = Client(profile=profile)
        if progress:
            in_progress(msg=progress)

        result = action(client=client, **kwargs)

        # Output-to-file branch: bypasses on_success, uses save-message.
        if output_flag and output:
            emit(result, output=output, saved_noun=saved_noun)
            return

        # on_success override (template or callable). Most commonly used for
        # None-returning actions that need a custom confirmation line.
        success_msg = apply_on_success(on_success, result=result, kwargs=kwargs)
        if success_msg is not None:
            success(success_msg)
            return

        # Default: print JSON via emit() (which handles both dict/list/bool
        # cases — rich.print_json handles non-dict scalars too).
        emit(result, output=None, saved_noun=saved_noun)

    # Make the wrapper look like the action to Typer's introspector and to
    # downstream tracebacks.
    functools.update_wrapper(wrapper, action)
    wrapper.__signature__ = sig.replace(parameters=wrapper_params)  # type: ignore[attr-defined]
    wrapper.__annotations__ = {p.name: p.annotation for p in wrapper_params}
    wrapper.__qualname__ = f"{action.__module__}.{action.__name__}"

    # Build the Typer-visible help text: action docstring + optional examples block.
    doc = inspect.cleandoc(action.__doc__ or "")
    if examples:
        doc = (doc + "\n" + _render_examples(examples)).strip()
    wrapper.__doc__ = doc

    typer_app.command(name=name or action.__name__)(wrapper)
    return wrapper
```

- [ ] **Step 4: Run the tests — expect them to pass**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_command.py -v
```

Expected: all tests PASS.

If any fail, do NOT proceed — diagnose and fix. Common failures:
- `TypeError: Client() takes no arguments` in a patched call → verify the `@patch` decorators target `nextmv.cli.framework.command.Client` (the name Typer's wrapper is actually calling).
- `AttributeError: 'Typer' object has no attribute ...` → verify import order.

- [ ] **Step 5: Update framework `__init__.py` to re-export public helpers**

Replace `nextmv/nextmv/cli/framework/__init__.py`:

```python
"""Helpers for building Typer CLI commands and options from pure action functions.

This package is the CLI-side half of the shared-connectors framework. It
pairs with ``nextmv.cli.mcp.framework`` which provides the MCP-side helpers.
Both consume pure action functions from ``nextmv.cli.actions`` and generate
frontend wrappers with matching signatures.

Import at call sites as::

    from nextmv.cli import framework as cli

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""

from nextmv.cli.framework.command import Example, command
from nextmv.cli.framework.options import (
    AppDirOption,
    AppIdOption,
    AppIdRequiredOption,
    DefaultExperimentInstanceOption,
    DefaultInstanceIdOption,
    DescriptionOption,
    ExistOkOption,
    IsWorkflowOption,
    NameOption,
)
from nextmv.cli.framework.result import emit, format_save_message
from nextmv.cli.message import in_progress as progress  # short alias

__all__ = [
    "command",
    "emit",
    "format_save_message",
    "progress",
    "Example",
    "AppIdOption",
    "AppIdRequiredOption",
    "NameOption",
    "DescriptionOption",
    "DefaultInstanceIdOption",
    "DefaultExperimentInstanceOption",
    "IsWorkflowOption",
    "ExistOkOption",
    "AppDirOption",
]
```

- [ ] **Step 6: Run the full framework test suite**

```bash
cd nextmv && uv run pytest tests/cli/framework/ -v
```

Expected: all tests PASS (spike, options, result, command).

- [ ] **Step 7: Commit**

```bash
git add nextmv/nextmv/cli/framework/command.py nextmv/nextmv/cli/framework/__init__.py nextmv/tests/cli/framework/test_command.py
git commit -m "feat(framework): implement cli.command() builder"
```

---

## Phase 3: `mcp_fw.tool()` Builder

### Task 7: Scaffold the MCP framework package

**Files:**
- Create: `nextmv/nextmv/cli/mcp/framework/__init__.py`
- Create: `nextmv/nextmv/cli/mcp/framework/tool.py` (empty placeholder)

- [ ] **Step 1: Create the tool.py placeholder and package init**

Create `nextmv/nextmv/cli/mcp/framework/__init__.py`:

```python
"""Helpers for registering MCP tools from pure action functions.

This package is the MCP-side half of the shared-connectors framework. It
pairs with ``nextmv.cli.framework`` which provides the CLI-side helpers.

Import at call sites as::

    from nextmv.cli.mcp import framework as mcp_fw

``mcp_fw.tool()`` registers a FastMCP tool wrapping a pure action function.
``mcp_fw.client()`` returns the current session client (re-export of
``nextmv.cli.mcp.tools._helpers._get_client``).
``mcp_fw.clean()`` normalizes a possibly-empty string to ``None`` (re-export
of ``nextmv.cli.mcp.tools._helpers._none_if_empty``).

The alias ``mcp_fw`` avoids shadowing the top-level ``mcp`` package from the
MCP Python SDK.

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""

from nextmv.cli.mcp.framework.tool import tool
from nextmv.cli.mcp.tools._helpers import _get_client as client
from nextmv.cli.mcp.tools._helpers import _none_if_empty as clean

__all__ = ["tool", "client", "clean"]
```

Create `nextmv/nextmv/cli/mcp/framework/tool.py`:

```python
"""``mcp_fw.tool()`` builder.

Given a pure action function under ``nextmv.cli.actions``, generates a
FastMCP tool wrapper whose signature mirrors the action's (minus the
``client`` parameter; MCP uses session-scoped client injection instead of a
per-call ``--profile`` flag). The wrapper reads metadata from the action's
``Annotated`` parameters so the same aliases drive both CLI and MCP tool
registration.

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""
```

- [ ] **Step 2: Run pytest to ensure the package is importable**

```bash
cd nextmv && uv run python -c "from nextmv.cli.mcp import framework as mcp_fw; print(dir(mcp_fw))"
```

Expected output includes `'client'`, `'clean'`, `'tool'` (though `tool` will be None at this point).

Actually, expect an ImportError because `tool.py` doesn't define `tool`. Move on to Step 3 which fixes it.

- [ ] **Step 3: Stub the `tool` export to make the import clean**

Append to `nextmv/nextmv/cli/mcp/framework/tool.py`:

```python


def tool(*args, **kwargs):  # pragma: no cover - replaced in Task 8
    """Stub — real implementation in Task 8."""
    raise NotImplementedError("mcp_fw.tool() not yet implemented")
```

- [ ] **Step 4: Re-run import check**

```bash
cd nextmv && uv run python -c "from nextmv.cli.mcp import framework as mcp_fw; print(mcp_fw.tool, mcp_fw.client, mcp_fw.clean)"
```

Expected: prints the stub `tool` function reference, the real `client` and `clean` functions. No errors.

- [ ] **Step 5: Commit**

```bash
git add nextmv/nextmv/cli/mcp/framework/__init__.py nextmv/nextmv/cli/mcp/framework/tool.py
git commit -m "feat(framework): scaffold nextmv.cli.mcp.framework package"
```

### Task 8: Implement `mcp_fw.tool()`

**Files:**
- Modify: `nextmv/nextmv/cli/mcp/framework/tool.py`
- Create: `nextmv/tests/cli/framework/test_tool.py`

- [ ] **Step 1: Write the failing tests**

Create `nextmv/tests/cli/framework/test_tool.py`:

```python
"""Tests for nextmv.cli.mcp.framework.tool."""

import unittest
from typing import Annotated
from unittest.mock import MagicMock, patch

import typer
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from nextmv.cloud.client import Client

_NAME_HELP = "A name."
_NameOpt = Annotated[
    str | None,
    typer.Option("--name", "-n", help=_NAME_HELP),
    Field(description=_NAME_HELP),
]


class TestMcpToolBuilder(unittest.TestCase):
    def test_rejects_action_without_client_first_param(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def bad_action(name: str) -> dict:
            return {"name": name}

        server = FastMCP("test")
        with self.assertRaises(TypeError) as ctx:
            tool(server, bad_action, name="bad")
        self.assertIn("client", str(ctx.exception))

    def test_registers_tool_with_given_name(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def list_things(client: Client) -> list[dict]:
            """List all things."""
            return []

        server = FastMCP("test")
        tool(server, list_things, name="test_list_things")
        self.assertIn("test_list_things", server._tool_manager._tools)

    def test_tool_description_from_action_docstring(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def list_things(client: Client) -> list[dict]:
            """List all things in the system."""
            return []

        server = FastMCP("test")
        tool(server, list_things, name="t_list")
        t = server._tool_manager._tools["t_list"]
        self.assertIn("List all things in the system.", t.description)

    def test_description_override(self) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        def list_things(client: Client) -> list[dict]:
            """Original docstring."""
            return []

        server = FastMCP("test")
        tool(
            server,
            list_things,
            name="t_list2",
            description="Overridden.",
        )
        t = server._tool_manager._tools["t_list2"]
        self.assertIn("Overridden.", t.description)

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_tool_invocation_forwards_args_and_returns_result(
        self, mock_get_client
    ) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_client = MagicMock(spec=Client)
        mock_get_client.return_value = mock_client
        captured: dict = {}

        def create_thing(client: Client, name: _NameOpt = None) -> dict:
            """Create a thing."""
            captured["client"] = client
            captured["name"] = name
            return {"name": name}

        server = FastMCP("test")
        tool(server, create_thing, name="t_create")

        t = server._tool_manager._tools["t_create"]
        # FastMCP tools are typically invoked via run(); for unit testing we
        # call the underlying function directly.
        result = t.fn(name="hello")
        self.assertEqual(result, {"name": "hello"})
        self.assertIs(captured["client"], mock_client)
        self.assertEqual(captured["name"], "hello")

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_normalize_empty_converts_empty_strings_to_none(
        self, mock_get_client
    ) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_get_client.return_value = MagicMock(spec=Client)
        captured: dict = {}

        def create_thing(
            client: Client,
            name: _NameOpt = None,
            description: _NameOpt = None,
        ) -> dict:
            """Create."""
            captured["name"] = name
            captured["description"] = description
            return {}

        server = FastMCP("test")
        tool(
            server,
            create_thing,
            name="t_create2",
            normalize_empty=["name", "description"],
        )
        t = server._tool_manager._tools["t_create2"]
        t.fn(name="", description="  ")
        self.assertIsNone(captured["name"])
        self.assertIsNone(captured["description"])

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_result_message_string_template(self, mock_get_client) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_get_client.return_value = MagicMock(spec=Client)

        def delete_thing(client: Client, app_id: str) -> None:
            """Delete."""

        server = FastMCP("test")
        tool(
            server,
            delete_thing,
            name="t_delete",
            result_message="Deleted {app_id}",
        )
        t = server._tool_manager._tools["t_delete"]
        result = t.fn(app_id="foo")
        self.assertEqual(result, "Deleted foo")

    @patch("nextmv.cli.mcp.framework.tool._get_client")
    def test_result_message_callable(self, mock_get_client) -> None:
        from nextmv.cli.mcp.framework.tool import tool

        mock_get_client.return_value = MagicMock(spec=Client)

        def push_thing(client: Client, app_id: str, app_dir: str) -> None:
            """Push."""

        server = FastMCP("test")
        tool(
            server,
            push_thing,
            name="t_push",
            result_message=lambda result, kwargs: (
                f"Pushed {kwargs['app_dir']} to {kwargs['app_id']}"
            ),
        )
        t = server._tool_manager._tools["t_push"]
        result = t.fn(app_id="foo", app_dir="/p")
        self.assertEqual(result, "Pushed /p to foo")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests — expect them to fail**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_tool.py -v
```

Expected: tests FAIL because `tool()` is only a stub.

- [ ] **Step 3: Implement `mcp_fw.tool()`**

Replace `nextmv/nextmv/cli/mcp/framework/tool.py`:

```python
"""``mcp_fw.tool()`` builder.

Given a pure action function under ``nextmv.cli.actions``, generates a
FastMCP tool wrapper whose signature mirrors the action's (minus the
``client`` parameter; MCP uses session-scoped client injection instead of a
per-call ``--profile`` flag). The wrapper reads metadata from the action's
``Annotated`` parameters so the same aliases drive both CLI and MCP tool
registration.

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""

import functools
import inspect
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools._helpers import _get_client, _none_if_empty
from nextmv.cloud.client import Client


def _assert_first_param_is_client(action: Callable) -> inspect.Signature:
    """Assert that the action's first parameter is ``client: Client``."""
    sig = inspect.signature(action)
    params = list(sig.parameters.values())
    if not params or params[0].name != "client":
        raise TypeError(
            f"{action.__name__} must take `client: Client` as its first parameter "
            f"(got parameters: {[p.name for p in params]})"
        )
    if params[0].annotation is not Client:
        raise TypeError(
            f"{action.__name__}'s first parameter must be annotated as "
            f"`client: Client`, got annotation {params[0].annotation!r}"
        )
    return sig


def tool(
    server: FastMCP,
    action: Callable,
    *,
    name: str,
    description: str | None = None,
    normalize_empty: list[str] | None = None,
    result_message: str | Callable[[Any, dict[str, Any]], str] | None = None,
) -> None:
    """Register a FastMCP tool wrapping a pure action function.

    Parameters
    ----------
    server:
        The ``FastMCP`` instance to register the tool on.
    action:
        The pure action function. Must take ``client: Client`` as its first
        parameter; remaining parameters are exposed as MCP tool parameters
        using their existing ``Annotated`` metadata (FastMCP's Pydantic
        layer reads ``Field(description=...)`` entries).
    name:
        The MCP tool name (required — e.g. ``"cloud_list_apps"``).
    description:
        Override for the tool description. Defaults to the action's
        docstring.
    normalize_empty:
        List of parameter names that should be piped through
        ``_none_if_empty()`` before the action is invoked. This handles LLMs
        passing ``""`` for optional parameters.
    result_message:
        Either a ``str.format``-style template (formatted with the dict
        passed to the action) or a callable ``(result, kwargs) -> str``.
        When set, the tool returns the formatted string instead of the
        action's raw return value. Most commonly used for ``None``-returning
        actions (delete, push).
    """
    sig = _assert_first_param_is_client(action)
    action_params = list(sig.parameters.values())
    user_params = action_params[1:]  # drop `client`

    normalize_empty_set = set(normalize_empty or [])

    def wrapper(**kwargs: Any) -> Any:
        if normalize_empty_set:
            for key in list(kwargs.keys()):
                if key in normalize_empty_set:
                    kwargs[key] = _none_if_empty(kwargs[key])

        client = _get_client()
        result = action(client=client, **kwargs)

        if result_message is not None:
            if callable(result_message):
                return result_message(result, kwargs)
            return result_message.format(**kwargs)

        return result

    functools.update_wrapper(wrapper, action)
    wrapper.__signature__ = sig.replace(parameters=user_params)  # type: ignore[attr-defined]
    wrapper.__annotations__ = {p.name: p.annotation for p in user_params}
    # Return annotation: keep the action's declared return type unless a
    # result_message override forces a string return.
    if result_message is not None:
        wrapper.__annotations__["return"] = str
    else:
        wrapper.__annotations__["return"] = sig.return_annotation

    wrapper.__name__ = name
    wrapper.__qualname__ = f"{action.__module__}.{action.__name__}"
    wrapper.__doc__ = description or inspect.cleandoc(action.__doc__ or "")

    server.tool(name=name)(wrapper)
```

- [ ] **Step 4: Run the tests — expect them to pass**

```bash
cd nextmv && uv run pytest tests/cli/framework/test_tool.py -v
```

Expected: all tests PASS.

Common failure: `AttributeError: 'FunctionTool' object has no attribute 'fn'`. If this happens, inspect how the current `test_tools.py` retrieves the callable (`server._tool_manager._tools[name]`). The FastMCP version in use may expose the wrapped function via `.fn`, `.handler`, or similar. Print the object and find the right attribute; update the test, not the implementation.

- [ ] **Step 5: Commit**

```bash
git add nextmv/nextmv/cli/mcp/framework/tool.py nextmv/tests/cli/framework/test_tool.py
git commit -m "feat(framework): implement mcp_fw.tool() builder"
```

---

## Phase 4: Migrate the `app` Action

### Task 9: Update `cli/actions/app.py` to use dual-purpose aliases

**Files:**
- Modify: `nextmv/nextmv/cli/actions/app.py`

- [ ] **Step 1: Read the current action file to confirm the starting state**

Read `nextmv/nextmv/cli/actions/app.py`. It should match the version at the start of this plan (77 lines, bare parameter types). Proceed only if the file matches; if it has diverged, diagnose before continuing.

- [ ] **Step 2: Rewrite the action file with dual-purpose aliases and expanded docstrings**

Replace `nextmv/nextmv/cli/actions/app.py`:

```python
"""Core application management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Each action takes ``client: Client`` as its first parameter so the CLI and
MCP frameworks can inject a client at call time. Remaining parameters use
dual-purpose ``Annotated`` aliases from ``nextmv.cli.framework.options`` so
the same metadata drives both Typer's ``--help`` output and FastMCP's tool
input schema.

Docstrings are multi-paragraph: the first line is a short description used
by both frontends as the primary tool/command description, and subsequent
paragraphs provide additional guidance that reads naturally in both
contexts.
"""

from typing import Any

from nextmv.cli.framework.options import (
    AppDirOption,
    AppIdOption,
    AppIdRequiredOption,
    DefaultExperimentInstanceOption,
    DefaultInstanceIdOption,
    DescriptionOption,
    ExistOkOption,
    IsWorkflowOption,
    NameOption,
)
from nextmv.cloud import Application, Client, list_applications


def list_apps(client: Client) -> list[dict[str, Any]]:
    """List all Nextmv Cloud applications in the current account.

    Returns a list of application dictionaries containing each application's
    ID, name, description, and default instance.
    """
    apps = list_applications(client)
    return [a.to_dict() for a in apps]


def create_app(
    client: Client,
    name: NameOption = None,
    app_id: AppIdOption = None,
    description: DescriptionOption = None,
    is_workflow: IsWorkflowOption = False,
    exist_ok: ExistOkOption = False,
    default_instance_id: DefaultInstanceIdOption = None,
    default_experiment_instance: DefaultExperimentInstanceOption = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud application.

    Set ``exist_ok`` to avoid errors when an application with the given ID
    already exists; the existing application is returned instead.

    An application can be marked as a workflow via ``is_workflow``. Workflows
    leverage Nextpipe to orchestrate multiple decision models.

    Returns the created (or existing) application object. A version and
    default instance are automatically provisioned for new applications.
    """
    return Application.new(
        client=client,
        name=name,
        id=app_id,
        description=description,
        is_workflow=is_workflow,
        exist_ok=exist_ok,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def get_app(client: Client, app_id: AppIdRequiredOption) -> dict[str, Any]:
    """Get details of a specific Nextmv Cloud application.

    Returns the full application object including its name, description,
    default instance, and creation timestamp.
    """
    return Application.get(client=client, id=app_id).to_dict()


def delete_app(client: Client, app_id: AppIdRequiredOption) -> None:
    """Delete a Nextmv Cloud application permanently.

    This action cannot be undone. All versions, instances, and run history
    associated with the application will be removed.
    """
    Application(client=client, id=app_id).delete()


def app_exists(client: Client, app_id: AppIdRequiredOption) -> bool:
    """Check whether a Nextmv Cloud application exists.

    Returns ``True`` if an application with the given ID exists in the
    current account, ``False`` otherwise.
    """
    return Application.exists(client=client, id=app_id)


def update_app(
    client: Client,
    app_id: AppIdRequiredOption,
    name: NameOption = None,
    description: DescriptionOption = None,
    default_instance_id: DefaultInstanceIdOption = None,
    default_experiment_instance: DefaultExperimentInstanceOption = None,
) -> dict[str, Any]:
    """Update attributes of a Nextmv Cloud application.

    Only the provided fields are updated; omitted fields remain unchanged.
    Returns the updated application object.
    """
    app = Application(client=client, id=app_id)
    return app.update(
        name=name,
        description=description,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def push_app(
    client: Client,
    app_id: AppIdRequiredOption,
    app_dir: AppDirOption,
) -> None:
    """Push local application code to a Nextmv Cloud application.

    Uploads the contents of a local directory as a new version of the
    application. The directory must contain an ``app.yaml`` manifest.
    """
    app = Application(client=client, id=app_id)
    app.push(app_dir=app_dir)
```

- [ ] **Step 3: Run the existing action tests**

```bash
cd nextmv && uv run pytest tests/cli/actions/test_app.py -v
```

Expected: all tests PASS. The dual-purpose aliases reduce to the same runtime types (`str | None`, `bool`, etc.) so the existing tests that call the actions directly should not notice the change.

If any test fails:
- Check whether the test relies on exact annotation objects (unlikely but possible). If so, update the test to use `typing.get_type_hints()` or inspect the alias's origin. Flag the change in the commit message.
- The test uses `from nextmv.cli.actions.app import ...` — this should still work.

- [ ] **Step 4: Commit**

```bash
git add nextmv/nextmv/cli/actions/app.py
git commit -m "refactor(actions): use dual-purpose aliases and expanded docstrings in app"
```

---

## Phase 5: Migrate the CLI `app` Domain

### Task 10: Capture golden help output snapshots from the current CLI

**Files:**
- Create: `nextmv/tests/cli/cloud/__init__.py`
- Create: `nextmv/tests/cli/cloud/app/__init__.py`
- Create: `nextmv/tests/cli/cloud/app/fixtures/list_help.txt`
- Create: `nextmv/tests/cli/cloud/app/fixtures/create_help.txt`

- [ ] **Step 1: Create the test package skeletons**

Create `nextmv/tests/cli/cloud/__init__.py` (empty):

```python
```

Create `nextmv/tests/cli/cloud/app/__init__.py` (empty):

```python
```

- [ ] **Step 2: Capture the current `list --help` snapshot**

The goal is byte-for-byte fidelity between today's hand-written help and the post-migration generated help for at least one simple command (`list`) and one example-rich command (`create`). Capture the golden outputs now, while the old files still exist.

Run:

```bash
cd nextmv && mkdir -p tests/cli/cloud/app/fixtures && \
  uv run nextmv cloud app list --help > tests/cli/cloud/app/fixtures/list_help.txt
```

Then inspect the captured file to confirm it contains:
- The "Examples" heading
- The `$ nextmv cloud app list` example line
- The `--output` option description
- The `--profile` option description

If any of these are missing, the CLI binary is not what you think — investigate before proceeding.

- [ ] **Step 3: Capture the current `create --help` snapshot**

```bash
cd nextmv && uv run nextmv cloud app create --help > tests/cli/cloud/app/fixtures/create_help.txt
```

Inspect the file for:
- The "Examples" heading
- The magenta-marked `Hare App` example
- The `--app-id` / `-a` flag with its help text
- The `--is-workflow` / `-w` flag

- [ ] **Step 4: Commit the snapshots**

```bash
git add nextmv/tests/cli/cloud/__init__.py nextmv/tests/cli/cloud/app/__init__.py nextmv/tests/cli/cloud/app/fixtures/
git commit -m "test: capture golden CLI help snapshots for app list and create"
```

### Task 11: Rewrite `cli/cloud/app/__init__.py` as the connector table

**Files:**
- Modify: `nextmv/nextmv/cli/cloud/app/__init__.py`

- [ ] **Step 1: Rewrite the `__init__.py` as the connector table**

Replace `nextmv/nextmv/cli/cloud/app/__init__.py`:

```python
"""Cloud app command tree for the Nextmv CLI.

All seven commands are built by ``cli.command()`` from pure action functions
in ``nextmv.cli.actions.app``. Parameter types, help text, and defaults
come from the action signatures — this file carries only the per-command
wiring (Typer registration, progress messages, example blocks, save-noun,
and success-message overrides).
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.app import (
    app_exists,
    create_app,
    delete_app,
    get_app,
    list_apps,
    push_app,
    update_app,
)

# Set up subcommand application.
app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create, manage, and push Nextmv Cloud applications.

    A Nextmv application is an entity that contains a decision model as
    executable code. An application can make a run by taking an input,
    executing the decision model, and producing an output.
    """
    pass


# ---------------------------------------------------------------------------
# Rich example blocks — data tuples rendered to Rich markup by cli.command().
# Inline [magenta]...[/magenta] highlights inside descriptions are preserved.
# ---------------------------------------------------------------------------

LIST_EXAMPLES: tuple[cli.Example, ...] = (
    ("List all applications.",
        "nextmv cloud app list"),
    ("List all applications using the profile named [magenta]hare[/magenta].",
        "nextmv cloud app list --profile hare"),
    ("List all applications and save the information to an [magenta]apps.json[/magenta] file.",
        "nextmv cloud app list --output apps.json"),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Create an application with the name [magenta]Hare App[/magenta]. A random ID will be generated.",
        'nextmv cloud app create --name "Hare App"'),
    ("Create an application with the specific ID [magenta]hare-app[/magenta].",
        'nextmv cloud app create --name "Hare App" --app-id hare-app'),
    ("Create an application with an ID and description.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app \\\n'
        '    --description "An application for routing hares"'),
    ("Create an application, or get it if it already exists.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app --exist-ok'),
    ("Create a workflow application.",
        'nextmv cloud app create --name "Hare Workflow" --app-id hare-workflow --is-workflow'),
    ("Create an application with a default instance ID.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app \\\n'
        '    --default-instance-id burrow'),
    ("Create an application with a default experiment instance.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app \\\n'
        '    --default-experiment-instance experiment-v1'),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    ("Get details for an application.",
        "nextmv cloud app get --app-id hare-app"),
    ("Get details and save them to a file.",
        "nextmv cloud app get --app-id hare-app --output app.json"),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Delete an application.",
        "nextmv cloud app delete --app-id hare-app"),
)

EXISTS_EXAMPLES: tuple[cli.Example, ...] = (
    ("Check whether an application exists.",
        "nextmv cloud app exists --app-id hare-app"),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Update an application's name.",
        'nextmv cloud app update --app-id hare-app --name "New Name"'),
    ("Update an application's default instance.",
        "nextmv cloud app update --app-id hare-app --default-instance-id burrow"),
)

PUSH_EXAMPLES: tuple[cli.Example, ...] = (
    ("Push a local application directory to Nextmv Cloud.",
        "nextmv cloud app push --app-id hare-app --app-dir ./my-app"),
)


# ---------------------------------------------------------------------------
# Command registration — one cli.command() call per operation.
# ---------------------------------------------------------------------------

list = cli.command(  # noqa: A001 — shadows the builtin intentionally; this file is not a general-purpose namespace
    app,
    list_apps,
    progress="Listing applications...",
    output_flag=True,
    saved_noun="Application list information",
    examples=LIST_EXAMPLES,
)

create = cli.command(
    app,
    create_app,
    progress="Creating application...",
    examples=CREATE_EXAMPLES,
)

get = cli.command(
    app,
    get_app,
    progress="Getting application...",
    output_flag=True,
    saved_noun="Application information",
    examples=GET_EXAMPLES,
)

delete = cli.command(
    app,
    delete_app,
    progress="Deleting application...",
    on_success="Deleted application [magenta]{app_id}[/magenta].",
    examples=DELETE_EXAMPLES,
)

exists = cli.command(
    app,
    app_exists,
    examples=EXISTS_EXAMPLES,
)

update = cli.command(
    app,
    update_app,
    progress="Updating application...",
    output_flag=True,
    saved_noun="Updated application information",
    examples=UPDATE_EXAMPLES,
)

push = cli.command(
    app,
    push_app,
    progress="Pushing application...",
    on_success=(
        "Pushed [magenta]{app_dir}[/magenta] to application "
        "[magenta]{app_id}[/magenta]."
    ),
    examples=PUSH_EXAMPLES,
)
```

- [ ] **Step 2: Delete the seven per-command files**

```bash
cd nextmv && rm \
  nextmv/cli/cloud/app/create.py \
  nextmv/cli/cloud/app/delete.py \
  nextmv/cli/cloud/app/exists.py \
  nextmv/cli/cloud/app/get.py \
  nextmv/cli/cloud/app/list.py \
  nextmv/cli/cloud/app/push.py \
  nextmv/cli/cloud/app/update.py
```

- [ ] **Step 3: Smoke-test the CLI can still start**

```bash
cd nextmv && uv run nextmv cloud app --help
```

Expected: shows the callback docstring plus the seven subcommands `create`, `delete`, `exists`, `get`, `list`, `push`, `update` in alphabetical order.

If the command fails to import:
- `ModuleNotFoundError: nextmv.cli.framework` → the framework package isn't on the import path. Verify `nextmv/cli/framework/__init__.py` exists.
- `TypeError: ... must take 'client: Client' as its first parameter` → the action module still has old parameter types. Verify Task 9 completed.

- [ ] **Step 4: Run each command's `--help` to confirm it produces output**

```bash
cd nextmv && for verb in list create get delete exists update push; do
  echo "=== $verb ==="
  uv run nextmv cloud app $verb --help || break
done
```

Expected: each command prints its help text without error. The examples block should appear for `list`, `create`, `get`, `delete`, `exists`, `update`, `push`.

- [ ] **Step 5: Commit**

```bash
git add nextmv/nextmv/cli/cloud/app/
git commit -m "refactor(cli): rewrite cloud app as connector table via cli.command()"
```

### Task 12: Add the help-output snapshot test

**Files:**
- Create: `nextmv/tests/cli/cloud/app/test_help_output.py`

- [ ] **Step 1: Write the snapshot comparison test**

Create `nextmv/tests/cli/cloud/app/test_help_output.py`:

```python
"""Snapshot tests comparing generated help output against captured fixtures.

These fixtures were captured from the pre-refactor CLI (Task 10) and represent
the observable contract: CLI users and scripts rely on this exact help text.
The refactor must preserve it byte-for-byte (except for minor whitespace
differences that we normalize below).

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
    """Compare today's generated help output against captured fixtures."""

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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests**

```bash
cd nextmv && uv run pytest tests/cli/cloud/app/test_help_output.py -v
```

Expected outcomes:
- `TestHelpOutputStructure` tests should all pass — they assert on structural presence, not bytes.
- `TestHelpOutputSnapshots` tests may fail on the first run. **This is expected and diagnostic.** When they fail:
  1. Examine the diff between `actual` and `expected`. Typer's generated formatting may differ slightly from the hand-written version (column widths, how multi-line examples wrap, etc.).
  2. If the only differences are cosmetic (whitespace, panel widths), consider loosening the normalization in `_normalize()` further.
  3. If the differences are substantive (missing text, wrong help, missing example), fix the framework or the connector, not the test.
  4. Once you're confident the output is correct, refresh the fixture via:
     ```bash
     cd nextmv && uv run nextmv cloud app list --help > tests/cli/cloud/app/fixtures/list_help.txt
     cd nextmv && uv run nextmv cloud app create --help > tests/cli/cloud/app/fixtures/create_help.txt
     ```
     Explain the refresh in the commit message.

- [ ] **Step 3: Commit whichever variant of the tests passes**

If both test classes pass without fixture updates:

```bash
git add nextmv/tests/cli/cloud/app/test_help_output.py
git commit -m "test(cli): add help-output snapshot and structural tests for app"
```

If fixtures had to be updated:

```bash
git add nextmv/tests/cli/cloud/app/fixtures/ nextmv/tests/cli/cloud/app/test_help_output.py
git commit -m "test(cli): add help-output tests and refresh fixtures

Fixtures refreshed because [describe the cosmetic difference between the
hand-written and generated output]. Observable contract is preserved."
```

---

## Phase 6: Migrate the MCP `app` Domain

### Task 13: Rewrite `mcp/tools/app.py` as `mcp_fw.tool()` calls

**Files:**
- Modify: `nextmv/nextmv/cli/mcp/tools/app.py`

**⚠️ Intentional MCP schema change — read before implementing:**

The current `cloud_create_app` MCP tool declares `name: str` (required). The underlying action `create_app` has always accepted `name=None` at the Python level — the "required" constraint was only enforced at the MCP tool boundary, not in the action itself. After this task, the action's signature (`name: NameOption = None`) drives the MCP schema, so `name` becomes **optional** in `cloud_create_app`.

This is technically a schema change contrary to the spec's "no schema change" non-goal, but it is a **loosening** — existing MCP clients that always pass `name` continue to work unchanged. New clients that omit `name` no longer get a validation error at the MCP boundary (they may still get a downstream error from the SDK, same as the CLI path).

**Accept this.** Do not add a per-tool override to re-impose `required=True` on `name` — that would reintroduce the metadata duplication this refactor is eliminating. Call it out in the commit message for this task.

- [ ] **Step 1: Rewrite the MCP tool file**

Replace `nextmv/nextmv/cli/mcp/tools/app.py`:

```python
"""MCP tools for cloud application management.

Each tool wraps a pure action function from ``nextmv.cli.actions.app``. The
parameter signatures, types, and descriptions are derived from the action;
per-tool wiring (tool name, empty-string normalization, result-message
formatting) lives here.
"""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.app import (
    app_exists,
    create_app,
    delete_app,
    get_app,
    list_apps,
    push_app,
    update_app,
)
from nextmv.cli.mcp import framework as mcp_fw


def register(server: FastMCP) -> None:
    """Register cloud application management tools."""

    mcp_fw.tool(server, list_apps, name="cloud_list_apps")

    mcp_fw.tool(
        server,
        get_app,
        name="cloud_get_app",
    )

    mcp_fw.tool(
        server,
        create_app,
        name="cloud_create_app",
        normalize_empty=["app_id", "description", "name"],
    )

    mcp_fw.tool(
        server,
        delete_app,
        name="cloud_delete_app",
        result_message="Deleted application {app_id}",
    )

    mcp_fw.tool(
        server,
        app_exists,
        name="cloud_app_exists",
    )

    mcp_fw.tool(
        server,
        update_app,
        name="cloud_update_app",
        normalize_empty=[
            "name",
            "description",
            "default_instance_id",
            "default_experiment_instance",
        ],
    )

    mcp_fw.tool(
        server,
        push_app,
        name="cloud_push_app",
        result_message="Pushed {app_dir} to application {app_id}",
    )
```

- [ ] **Step 2: Smoke-test that the MCP server still creates successfully**

```bash
cd nextmv && uv run python -c "
from nextmv.cli.mcp.server import create_server
server = create_server()
tools = list(server._tool_manager._tools.keys())
expected = [
    'cloud_list_apps', 'cloud_get_app', 'cloud_create_app',
    'cloud_delete_app', 'cloud_app_exists', 'cloud_update_app',
    'cloud_push_app',
]
for name in expected:
    assert name in tools, f'missing: {name}'
print('All app tools registered:', expected)
"
```

Expected: prints the list with no assertion errors.

- [ ] **Step 3: Run the existing MCP tool registration test**

```bash
cd nextmv && uv run pytest tests/cli/mcp/test_tools.py::TestMCPServerTools::test_server_has_all_cloud_app_tools -v
```

Expected: PASS. This existing test checks that all seven `cloud_*_app` tool names are registered.

- [ ] **Step 4: Commit**

```bash
git add nextmv/nextmv/cli/mcp/tools/app.py
git commit -m "$(cat <<'EOF'
refactor(mcp): rewrite app tools using mcp_fw.tool() builder

cloud_create_app now treats `name` as optional (was required in the old
hand-written wrapper). The underlying create_app action has always
accepted name=None — the "required" was enforced only at the MCP tool
boundary. Existing clients that always pass `name` are unaffected;
clients that omit it no longer see a validation error at the MCP layer.
EOF
)"
```

### Task 14: Add MCP tool schema assertions for the `app` domain

**Files:**
- Create: `nextmv/tests/cli/mcp/test_app_schemas.py`

- [ ] **Step 1: Write the schema assertion test**

Create `nextmv/tests/cli/mcp/test_app_schemas.py`:

```python
"""Schema-shape assertions for the cloud app MCP tools.

These tests are the MCP-side equivalent of the CLI help-output tests: they
assert that the tool descriptions and input schemas match what the old
hand-written ``app.py`` produced, so that any LLM or MCP client consuming
these tools sees the same interface.
"""

import unittest

from nextmv.cli.mcp.server import create_server


class TestAppToolSchemas(unittest.TestCase):
    """Assert the tool name, description, and input schema for each app tool."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server()
        cls.tools = cls.server._tool_manager._tools

    def test_cloud_list_apps_has_no_parameters(self) -> None:
        tool = self.tools["cloud_list_apps"]
        self.assertIn("List all Nextmv Cloud applications", tool.description)
        schema = tool.parameters
        properties = schema.get("properties", {})
        self.assertEqual(properties, {})

    def test_cloud_get_app_requires_app_id(self) -> None:
        tool = self.tools["cloud_get_app"]
        self.assertIn("Get details", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("properties", {}))
        self.assertIn("app_id", schema.get("required", []))

    def test_cloud_create_app_has_all_optional_params(self) -> None:
        """cloud_create_app schema covers all seven action params, all optional.

        Note: `name` was previously required in the hand-written MCP wrapper
        (the action always accepted None, but the wrapper declared ``name: str``).
        After the refactor, the action's signature drives the schema, so `name`
        is now optional. See the commit message for Task 13 for context.
        """
        tool = self.tools["cloud_create_app"]
        self.assertIn("Create a new Nextmv Cloud application", tool.description)
        props = tool.parameters.get("properties", {})
        for name in [
            "name",
            "app_id",
            "description",
            "is_workflow",
            "exist_ok",
            "default_instance_id",
            "default_experiment_instance",
        ]:
            self.assertIn(
                name,
                props,
                msg=f"cloud_create_app schema missing parameter: {name}",
            )
        # None of these are required (all have defaults on the action).
        self.assertEqual(tool.parameters.get("required", []), [])

    def test_cloud_create_app_param_descriptions_come_from_field(self) -> None:
        """The dual-purpose Annotated aliases must surface Field(description=)
        into the MCP schema."""
        tool = self.tools["cloud_create_app"]
        props = tool.parameters["properties"]
        # app_id help comes from _APP_ID_HELP
        self.assertIn("description", props["app_id"])
        self.assertIn("optional ID", props["app_id"]["description"])
        # is_workflow help comes from _IS_WORKFLOW_HELP
        self.assertIn("description", props["is_workflow"])
        self.assertIn("workflow", props["is_workflow"]["description"])

    def test_cloud_delete_app_requires_app_id(self) -> None:
        tool = self.tools["cloud_delete_app"]
        self.assertIn("Delete a Nextmv Cloud application", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("required", []))

    def test_cloud_app_exists_requires_app_id(self) -> None:
        tool = self.tools["cloud_app_exists"]
        self.assertIn("Check whether", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("required", []))

    def test_cloud_update_app_requires_app_id_only(self) -> None:
        tool = self.tools["cloud_update_app"]
        self.assertIn("Update attributes", tool.description)
        schema = tool.parameters
        self.assertIn("app_id", schema.get("required", []))
        # All other params are optional.
        for name in [
            "name",
            "description",
            "default_instance_id",
            "default_experiment_instance",
        ]:
            self.assertIn(name, schema.get("properties", {}))
            self.assertNotIn(name, schema.get("required", []))

    def test_cloud_push_app_requires_app_id_and_app_dir(self) -> None:
        tool = self.tools["cloud_push_app"]
        self.assertIn("Push local application code", tool.description)
        schema = tool.parameters
        required = set(schema.get("required", []))
        self.assertEqual(required, {"app_id", "app_dir"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the schema tests**

```bash
cd nextmv && uv run pytest tests/cli/mcp/test_app_schemas.py -v
```

Expected: all tests PASS.

Common failure modes:
- `KeyError: 'properties'` → FastMCP's schema dict has a different shape in this version. Print `tool.parameters` to see the actual structure and adjust assertions.
- Descriptions missing → the dual-purpose alias fallback is needed (sibling aliases). This would mean Task 1's spike should have caught it. If it appears here, escalate.
- `'required' not in schema` when expected → Pydantic may not emit `required` when the list is empty. Use `schema.get("required", [])` (already done in the test).

- [ ] **Step 3: Commit**

```bash
git add nextmv/tests/cli/mcp/test_app_schemas.py
git commit -m "test(mcp): assert app tool schemas derive from action signatures"
```

---

## Phase 7: Cleanup and Full Verification

### Task 15: Run the full test suite and fix any regressions

- [ ] **Step 1: Run the entire CLI test suite**

```bash
cd nextmv && uv run pytest tests/cli/ -v
```

Expected: all tests PASS. Specifically check:
- `tests/cli/actions/test_app.py` — action tests still pass (Task 9 preserved behavior).
- `tests/cli/framework/` — spike, options, result, command, tool all pass.
- `tests/cli/cloud/app/test_help_output.py` — snapshot + structure tests pass.
- `tests/cli/mcp/test_tools.py` — tool registration tests still pass.
- `tests/cli/mcp/test_app_schemas.py` — schema assertions pass.

If any test fails, diagnose one at a time:
- **Action tests failing** → the dual-purpose aliases aren't reducing to expected runtime types. Revisit Task 9 and compare annotations with `typing.get_type_hints(func)`.
- **`test_tools.py::test_server_has_all_cloud_app_tools` failing** → a tool name changed. Check Task 13's names against the old file's names.
- **Snapshot tests failing** → see Task 12's Step 2 failure handling.
- **Schema tests failing** → Pydantic schema structure assumption. Inspect actual schemas.

Do NOT proceed past this step with any failing tests.

- [ ] **Step 2: Run the broader test suite (not just cli/) to catch ripples**

```bash
cd nextmv && uv run pytest -v 2>&1 | tail -60
```

Expected: no new failures compared to the branch starting point. If anything unrelated to CLI fails, check whether this refactor introduced a circular import or similar. The framework imports `nextmv.cloud.client.Client` — if the cloud layer starts failing to import, there may be a cycle.

### Task 16: Manual CLI smoke test

- [ ] **Step 1: Run the app command tree manually**

```bash
cd nextmv && uv run nextmv cloud app --help
```

Inspect the output. The callback docstring should appear, followed by the seven subcommands.

- [ ] **Step 2: Inspect the `list` help output manually**

```bash
cd nextmv && uv run nextmv cloud app list --help
```

Verify visually:
- "Examples" header appears.
- Three example entries appear with descriptions and `$ nextmv cloud app list...` lines.
- `--output` / `-o` option is present with its description.
- `--profile` / `-p` option is present.
- Text colors/formatting render as expected (magenta for "hare" and "apps.json").

- [ ] **Step 3: Inspect the `create` help output manually**

```bash
cd nextmv && uv run nextmv cloud app create --help
```

Verify visually:
- "Examples" header appears.
- Magenta highlights inside descriptions (`Hare App`, `hare-app`).
- `--app-id` / `-a` with its envvar `NEXTMV_APP_ID`.
- `--is-workflow` / `-w`.
- `--name` / `-n`, `--description` / `-d`.
- Multi-line example commands with continuation backslashes display correctly.

- [ ] **Step 4: Inspect the `delete` help output**

```bash
cd nextmv && uv run nextmv cloud app delete --help
```

Verify:
- `--app-id` / `-a` is required.
- The example shows `nextmv cloud app delete --app-id hare-app`.

If any of these manual checks fail, fix the connector call in `nextmv/cli/cloud/app/__init__.py` and re-run. No commit yet.

### Task 17: Manual MCP tool inspection

- [ ] **Step 1: List the MCP tools via a Python one-liner**

```bash
cd nextmv && uv run python -c "
import json
from nextmv.cli.mcp.server import create_server

server = create_server()
tools = server._tool_manager._tools
for name in sorted(n for n in tools if n.endswith('_app') or n == 'cloud_list_apps' or n == 'cloud_app_exists'):
    t = tools[name]
    print(f'== {name} ==')
    print(f'  description: {t.description[:80]}...' if len(t.description) > 80 else f'  description: {t.description}')
    props = t.parameters.get('properties', {})
    required = set(t.parameters.get('required', []))
    for pname in sorted(props):
        req = '*' if pname in required else ' '
        desc = props[pname].get('description', '')[:60]
        print(f'  {req} {pname}: {desc}')
    print()
"
```

Expected: prints each of the seven `cloud_*` app tools with its description and parameters. Verify that:
- `cloud_list_apps` has no parameters.
- `cloud_get_app`, `cloud_delete_app`, `cloud_app_exists` each have `*app_id` (required).
- `cloud_create_app` has `app_id`, `description`, `is_workflow`, `exist_ok`, `name`, `default_instance_id`, `default_experiment_instance` — all optional.
- `cloud_update_app` has `*app_id` plus the same optional params.
- `cloud_push_app` has `*app_id` and `*app_dir`.

If the output diverges from these expectations, fix the MCP connector in `nextmv/cli/mcp/tools/app.py`.

### Task 18: Update framework `__init__.py` re-exports if the smoke test found anything missing

- [ ] **Step 1: Review imports**

Check that any name referenced in `nextmv/cli/cloud/app/__init__.py` from the `cli` namespace is actually re-exported in `nextmv/cli/framework/__init__.py`.

Specifically confirm the following attributes resolve:
- `cli.command` ✓
- `cli.Example` ✓
- `cli.progress` (may or may not be used in the connector file — OK either way)
- None of the option aliases are referenced from the connector file directly since options are used on the action. Verify this.

Run:

```bash
cd nextmv && uv run python -c "
from nextmv.cli import framework as cli
assert hasattr(cli, 'command')
assert hasattr(cli, 'Example')
assert hasattr(cli, 'progress')
assert hasattr(cli, 'emit')
print('Framework exports OK')
"
```

Expected: prints "Framework exports OK".

If any `hasattr` fails, add the missing name to `nextmv/cli/framework/__init__.py`'s `__all__` and imports, then re-run.

- [ ] **Step 2: No commit** — this step is verification only; any fix in Step 1 should be committed separately if one is needed.

### Task 19: Delete the feasibility spike

**Files:**
- Delete: `nextmv/tests/cli/framework/test_spike.py`

- [ ] **Step 1: Delete the spike file**

The spike's job is done — `test_options.py` now serves as the permanent regression guard.

```bash
cd nextmv && rm tests/cli/framework/test_spike.py
```

- [ ] **Step 2: Re-run the framework tests to confirm nothing depended on the spike**

```bash
cd nextmv && uv run pytest tests/cli/framework/ -v
```

Expected: all remaining tests (options, result, command, tool) PASS.

- [ ] **Step 3: Commit the deletion**

```bash
git add -u nextmv/tests/cli/framework/test_spike.py
git commit -m "test: remove feasibility spike (superseded by test_options.py)"
```

### Task 20: Final verification and stop

- [ ] **Step 1: Run the full test suite one more time**

```bash
cd nextmv && uv run pytest tests/cli/ -v 2>&1 | tail -40
```

Expected: all tests PASS with no errors. Summary line should read something like "NN passed".

- [ ] **Step 2: Run the full test suite outside `tests/cli/`**

```bash
cd nextmv && uv run pytest -v 2>&1 | tail -20
```

Expected: no new failures compared to the branch starting point.

- [ ] **Step 3: Show the branch commit log**

```bash
git log --oneline refactor/mcp-shared-actions ^develop | head -30
```

Expected: the commits from this plan (spike, options aliases, regression guard, result.py, render_examples, cli.command, mcp_fw scaffold, mcp_fw.tool, action migration, help snapshots, connector rewrite, help tests, MCP rewrite, schema tests, spike deletion) appear on top of the prior work on this branch.

- [ ] **Step 4: Verify no remote push has happened**

```bash
git status && git log origin/refactor/mcp-shared-actions..HEAD --oneline | head -20
```

Expected: `git status` shows a clean working tree; the second command lists the new pilot commits as local-only (not yet on the remote).

- [ ] **Step 5: STOP HERE**

**This plan ends at "tests pass locally, ready for review." Do not run `git push`. Do not create a PR. Do not trigger CI.**

Report to the human:
- Which tasks completed.
- Any fixture refreshes or test-shape adjustments that were needed.
- The commit count and a quick list of the pilot commits.
- A prompt like: "Pilot migration complete and local-only. Ready for your review when you're ready — want to walk through any piece, inspect help output or tool schemas, or proceed to migrate another domain?"

---

## Notes for the Executor

**Commit discipline:** each task's final step is a commit. Do not batch commits across tasks. If a single task requires mid-task commits (e.g., Task 11 deletes seven files and rewrites one), it is still one logical commit at the end of that task.

**Never skip hooks:** do not use `--no-verify` on any commit. If a pre-commit hook fails, fix the underlying issue rather than bypassing. Expected hooks in this repo: `ruff` formatting/linting and possibly type checks. If a framework file fails ruff, fix the formatting and re-stage.

**Python version:** 3.10+ syntax is expected (`X | Y` union types, `TypeAlias`, `Annotated` without `from __future__ import annotations`). Do not rewrite existing code to an older syntax.

**When in doubt about the observable contract:** re-read the spec at `docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md`. Section "Non-Goals" is the authoritative list of what this refactor must NOT change.

**If a test failure seems to indicate a framework bug:** fix the framework, not the test. Tests are authoritative for the observable contract; the framework is authoritative for the implementation. Revisiting a framework task is cheaper than silently loosening a test.

**If a test failure seems to indicate a test-shape bug:** some FastMCP or Typer internals (e.g., `tool.fn` vs `tool.handler`, schema dict shape) may differ by version. Print the actual object, understand its shape, and adjust the test — but only after confirming with a Python REPL that the implementation is producing the intended output.

**When the spike fails:** STOP. Do not try to silently work around Pydantic rejecting `typer.OptionInfo`. Escalate to the human so we can decide whether to switch to sibling aliases (which would reshape Tasks 2, 3, 9, 11, 13, and 14).
