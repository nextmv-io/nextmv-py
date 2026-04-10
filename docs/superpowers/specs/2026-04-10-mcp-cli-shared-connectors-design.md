# CLI / MCP Shared Connectors

**Date:** 2026-04-10
**Branch:** `refactor/mcp-shared-actions`
**Status:** Design approved, pilot not yet started

## Problem

The `refactor/mcp-shared-actions` branch introduced a pure `nextmv/cli/actions/`
layer that encapsulates business logic for every CLI/MCP operation. Both the
Typer CLI and the FastMCP server call these actions. The logic duplication is
gone, but the *metadata* duplication remains: every operation still declares
its parameter list, types, help text, and docstring twice — once in a per-command
Typer file under `nextmv/cli/cloud/<domain>/<verb>.py`, and once inside a
`register()` function under `nextmv/cli/mcp/tools/<domain>.py`.

Concrete example. For `list_apps` — a 3-line action — the CLI wrapper is 60
lines ([nextmv/cli/cloud/app/list.py](../../../nextmv/nextmv/cli/cloud/app/list.py))
and the MCP wrapper is 8 lines
([nextmv/cli/mcp/tools/app.py:22-29](../../../nextmv/nextmv/cli/mcp/tools/app.py)).
Across ~20 domains and ~100+ operations, this is a lot of boilerplate whose
only content is "expose this action to frontend X with these flags/names".

## Goal

Eliminate the metadata duplication between CLI and MCP frontends by making the
action the single source of truth for parameter signatures, types, help text,
and docstrings. The CLI and MCP layers become thin wiring tables that register
actions with their respective frameworks.

## Non-Goals

- No behavior change visible to CLI users (`--help` output, exit codes, file
  outputs, progress messages) or to MCP clients (tool names, schemas,
  responses). This is a pure refactor.
- No changes to `nextmv/cloud/` (the SDK layer) or to the action function
  bodies themselves — only their signatures and docstrings.
- No migration of domains beyond `app` in the pilot PR. Other domains move in
  follow-up PRs.

## Design

### Design Principle: Structured Data → Rendered Markup

Every place the frontend emits Rich-formatted text, the connector declares
**data** and the framework produces the **markup**. No `[bold]...[/bold]`
strings scattered across connector files. Applied to:

- **`examples=`** — tuple of `(description, command)` pairs; framework renders
  the "Examples" block.
- **`on_success=` / `result_message=`** — template string (with `{placeholder}`
  slots) or callable; framework applies the formatting and Rich markup.
- **`output_flag=True` + `saved_noun=`** — framework auto-generates the
  save-to-file success message ("{Noun} saved to [magenta]{path}[/magenta].").

New rendering needs should extend this list rather than hand-writing Rich
markup in domain files. Descriptive prose (the action's multi-paragraph
docstring) stays as prose — only the *repeating* formatted structures move
to data.

### Architecture

Three layers, each with one responsibility:

```
┌─────────────────────────────────────────────────────────────┐
│ nextmv/cli/actions/<domain>.py                              │
│   Pure functions: (client: Client, **kwargs) -> result      │
│   Parameters typed with dual-purpose Annotated aliases      │
│   Multi-paragraph docstring shared by both frontends        │
│   First parameter MUST be `client: Client` (convention)     │
└─────────────────────────────────────────────────────────────┘
              ▲                              ▲
              │                              │
┌──────────────────────────┐  ┌──────────────────────────────┐
│ nextmv/cli/framework/    │  │ nextmv/cli/mcp/framework/    │
│   command()              │  │   tool()                     │
│   progress(), emit()     │  │   client(), clean()          │
│   options.py (aliases)   │  │   (imports shared options)   │
└──────────────────────────┘  └──────────────────────────────┘
              ▲                              ▲
              │                              │
┌──────────────────────────┐  ┌──────────────────────────────┐
│ cli/cloud/<domain>/      │  │ cli/mcp/tools/<domain>.py    │
│   __init__.py            │  │   register() calls           │
│   Typer() instance       │  │   mcp.tool() per operation   │
│   cli.command() per op   │  │                              │
└──────────────────────────┘  └──────────────────────────────┘
```

Key shift on the CLI side: **one file per domain**, not one file per command.
The existing `cli/cloud/app/{list,create,get,delete,exists,update,push}.py`
(7 files) collapses into `cli/cloud/app/__init__.py`. The MCP side already
uses a single file per domain and keeps that layout.

### Dual-Purpose `Annotated` Options

Each reusable option is declared **once** in
`nextmv/cli/framework/options.py` and consumed by both frontends. Python's
`Annotated` accepts multiple metadata entries; Typer walks them for
`ParameterInfo` and Pydantic walks them for `FieldInfo`. They coexist.

```python
# nextmv/cli/framework/options.py
from typing import Annotated, TypeAlias
import typer
from pydantic import Field

_APP_ID_HELP = "An optional ID for the application. If not provided, one is generated."

AppIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option("--app-id", "-a", help=_APP_ID_HELP,
                 metavar="APP_ID", envvar="NEXTMV_APP_ID"),
    Field(description=_APP_ID_HELP),
]
```

Each frontend reads the metadata it cares about:

| Metadata              | Typer reads                              | FastMCP reads               |
|-----------------------|------------------------------------------|-----------------------------|
| `str \| None` (type)  | parameter type                           | JSON schema type            |
| `typer.Option(...)`   | flag name, short, help, envvar, metavar  | ignored                     |
| `Field(description=)` | ignored                                  | JSON schema description     |
| Default value         | default                                  | optional vs required        |

Help text is defined once (`_APP_ID_HELP`) and referenced inside the single
alias for both frontends.

**Fallback if Pydantic v2 rejects `typer.OptionInfo` in `Annotated`:** sibling
aliases per option (`AppIdCli`, `AppIdMcp`) sharing the same help constant.
This possibility is tested in the feasibility spike before any framework
code is written.

**CLI-only options** — some options have no MCP counterpart (e.g., the
`--output/-o` save-to-file flag). These aliases omit the `Field(...)` metadata
and are framework-internal: they are injected automatically by
`cli.command()` when flags like `output_flag=True` are set, not imported by
domain connector files. MCP code never sees them.

### Options Live on the Action

The action function is the declaration site. Dual-purpose aliases appear in
its signature, and its docstring is the shared description.

```python
# nextmv/cli/actions/app.py
from nextmv.cli.framework.options import (
    AppIdOption, NameOption, DescriptionOption,
    DefaultInstanceIdOption, DefaultExperimentInstanceOption,
    IsWorkflowOption, ExistOkOption,
)

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

    Creates an application with the given name and optional metadata.
    If `exist_ok` is set, returns the existing application when the ID
    is already taken instead of raising.

    Returns the created (or existing) application as a dict.
    """
    return Application.new(
        client=client, name=name, id=app_id,
        description=description, is_workflow=is_workflow,
        exist_ok=exist_ok,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()
```

**Convention:** the first parameter is always `client: Client`. Both frontends
assert this at decoration time and inject the client themselves. Actions that
do not need a client (e.g., local-only operations) are wired through a
different mechanism not covered by this refactor.

**Dependency note:** `nextmv/cli/actions/` now imports `typer` and `pydantic`
transitively via `nextmv.cli.framework.options`. Acceptable because actions
live under the `cli` namespace, not at `nextmv/` top level.

### Connector Files

With options on the action, the connector files become pure wiring. Examples
are supplied as structured data (tuples of `(description, command)` pairs)
and rendered to the Rich-formatted help block by the framework.

```python
# nextmv/cli/cloud/app/__init__.py
import typer
from nextmv.cli import framework as cli
from nextmv.cli.actions.app import (
    list_apps, create_app, get_app, delete_app,
    app_exists, update_app, push_app,
)

app = typer.Typer()

LIST_EXAMPLES = (
    ("List all applications.",
        "nextmv cloud app list"),
    ("List all applications using the profile named [magenta]hare[/magenta].",
        "nextmv cloud app list --profile hare"),
    ("List all applications and save the information to an [magenta]apps.json[/magenta] file.",
        "nextmv cloud app list --output apps.json"),
)

CREATE_EXAMPLES = (
    ("Create an application with the name [magenta]Hare App[/magenta]. A random ID will be generated.",
        'nextmv cloud app create --name "Hare App"'),
    ("Create an application with the specific ID [magenta]hare-app[/magenta].",
        'nextmv cloud app create --name "Hare App" --app-id hare-app'),
    ("Create an application, or get it if it already exists.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app --exist-ok'),
    ("Create a [magenta]workflow[/magenta] application.",
        'nextmv cloud app create --name "Hare Workflow" --app-id hare-workflow --is-workflow'),
)

list   = cli.command(app, list_apps,
                     progress="Listing applications...",
                     output_flag=True,
                     saved_noun="Application list information",
                     examples=LIST_EXAMPLES)
create = cli.command(app, create_app,
                     progress="Creating application...",
                     examples=CREATE_EXAMPLES)
get    = cli.command(app, get_app,    progress="Getting application...")
delete = cli.command(app, delete_app, progress="Deleting application...",
                     on_success="Deleted application [magenta]{app_id}[/magenta].")
exists = cli.command(app, app_exists)
update = cli.command(app, update_app, progress="Updating application...")
push   = cli.command(app, push_app,   progress="Pushing application...",
                     on_success="Pushed {app_dir} to application [magenta]{app_id}[/magenta].")
```

**Descriptive body text** (e.g., the guidance about `--exist-ok` and
`--is-workflow` on the current `create` command) lives in the action's
multi-paragraph docstring, phrased neutrally so it reads naturally in both
CLI `--help` output and MCP tool descriptions. The action docstring is
appended to the description automatically; the `examples` tuple renders
below it.

```python
# nextmv/cli/mcp/tools/app.py
from mcp.server.fastmcp import FastMCP
from nextmv.cli.mcp import framework as mcp_fw
from nextmv.cli.actions.app import (
    list_apps, create_app, get_app, delete_app,
    app_exists, update_app, push_app,
)

def register(server: FastMCP) -> None:
    mcp_fw.tool(server, list_apps,   name="cloud_list_apps")
    mcp_fw.tool(server, create_app,  name="cloud_create_app",
                normalize_empty=["app_id", "description"])
    mcp_fw.tool(server, get_app,     name="cloud_get_app")
    mcp_fw.tool(server, delete_app,  name="cloud_delete_app",
                result_message="Deleted application {app_id}")
    mcp_fw.tool(server, app_exists,  name="cloud_app_exists")
    mcp_fw.tool(server, update_app,  name="cloud_update_app",
                normalize_empty=["name", "description", "default_instance_id"])
    mcp_fw.tool(server, push_app,    name="cloud_push_app",
                result_message="Pushed {app_dir} to application {app_id}")
```

### `cli.command()` Internals

```python
Example = tuple[str, str]  # (description, command)

def command(
    typer_app: typer.Typer,
    action: Callable,
    *,
    name: str | None = None,
    progress: str | None = None,
    output_flag: bool = False,
    saved_noun: str | None = None,
    on_success: str | Callable | None = None,
    examples: tuple[Example, ...] | None = None,
) -> Callable: ...
```

Behavior:

1. `sig = inspect.signature(action)`. Assert
   `sig.parameters["client"].annotation is Client`, else raise
   `TypeError(f"{action.__name__} must take `client: Client` as first parameter")`
   at import time.
2. Build a new parameter list: all action parameters *except* `client`, with
   their `Annotated[...]` metadata preserved so Typer can read the
   `typer.Option` markers unchanged. **Parameter kinds are preserved**:
   positional-only (`/`), keyword-only (`*`), `var_keyword`, and `var_positional`
   markers on the action's signature are carried through to the wrapper. The
   reconstructed `inspect.Signature` uses `Parameter.replace()` so kinds stay
   intact.
3. Append `profile: ProfileOption = None` as a keyword-only parameter at the
   end. If `output_flag=True`, also append `output: OutputOption = None`
   (keyword-only). Both are framework-owned aliases defined inside
   `framework/options.py` and never imported by domain code.
4. Define a wrapper function that:
   - Pops `profile` and `output` from kwargs.
   - Builds `Client(profile=profile)`.
   - If `progress` is set, calls `in_progress(msg=progress)`.
   - Calls `action(client=client, **kwargs)`.
   - If `output_flag=True` and `output` is truthy, writes JSON to the file
     and prints the save-message:
     `"{saved_noun or 'Result'} saved to [magenta]{output}[/magenta]."`
     (first-letter capitalized). Bypasses `on_success`.
   - Otherwise applies `on_success` handling (see "Result Handling").
5. Sets `wrapper.__signature__`, `wrapper.__annotations__`,
   `wrapper.__name__ = name or action.__name__`,
   `wrapper.__qualname__ = f"{action.__module__}.{action.__name__}"` (clean
   tracebacks). Builds `wrapper.__doc__` by concatenating:
   (a) the action's docstring (shared description + any body text), then
   (b) a Rich-formatted examples block rendered from the `examples` tuple
   (see "Examples Rendering" below), if provided.
6. Registers via `typer_app.command(name=name)(wrapper)` and returns the
   wrapper.

The returned wrapper supports `list = cli.command(...)` assignment style.

### Examples Rendering

The `examples` parameter accepts a tuple of `(description, command)` pairs.
A helper in `nextmv/cli/framework/command.py` renders them into the same
Rich-formatted block that today's per-command files hand-write:

```python
def _render_examples(examples: tuple[Example, ...]) -> str:
    lines = ["", "[bold][underline]Examples[/underline][/bold]", ""]
    for description, command in examples:
        lines.append(f"- {description}")
        lines.append(f"    $ [dim]{command}[/dim]")
        lines.append("")
    return "\n".join(lines)
```

**Rich markup inside descriptions is preserved.** The renderer adds only the
surrounding structure — header, bullet prefix, `$ [dim]...[/dim]` wrapper,
blank lines. Any `[magenta]...[/magenta]`, `[bold]...[/bold]`, `[link=...]`,
etc. inside the description string is passed through verbatim. This gives
per-example inline highlighting identical to the hand-written blocks on
`develop`:

- Hand-written today:
  `- List all applications using the profile named [magenta]hare[/magenta].`
- Produced by `_render_examples`:
  `- List all applications using the profile named [magenta]hare[/magenta].`

The **command** string is wrapped in `[dim]...[/dim]` so its entire contents
render dimmed. Markup inside the command string is legal but unnecessary —
everything is already dim.

**Multi-line commands** (e.g., `create` with many flags) are handled by
letting the `command` string contain embedded newlines and continuation
backslashes — the renderer passes them through verbatim so Rich displays
them as-is.

**Why a tuple, not a list:** tuples signal immutability and read as data
literals in module-level constants. No behavior depends on the choice.

### `mcp.tool()` Internals

```python
def tool(
    server: FastMCP,
    action: Callable,
    *,
    name: str,
    description: str | None = None,
    normalize_empty: list[str] | None = None,
    result_message: str | Callable | None = None,
) -> None: ...
```

Behavior:

1. Same signature inspection and `client` assertion as `cli.command()`.
2. Build a wrapper whose parameters are the action's non-client parameters
   with `Annotated` metadata preserved (FastMCP's Pydantic reads
   `Field(description=...)`).
3. Wrapper body:
   - Calls `mcp.session.get_client()` to build the client.
   - For each name listed in `normalize_empty`, wraps the corresponding kwarg
     with `none_if_empty(...)` before passing to the action.
   - Calls `action(client, **kwargs)`.
   - If `result_message` is set, formats it (`str.format(**kwargs)` for a
     string template, `(result, kwargs) -> str` for a callable) and returns
     the formatted string. Otherwise returns the action's result as-is for
     FastMCP to serialize.
4. Sets `__signature__`, `__name__ = name`, `__qualname__`, and
   `__doc__ = description or action.__doc__`.
5. Registers via `server.tool(name=name)(wrapper)`.

MCP's `result_message` is the equivalent of CLI's `on_success` but must stay
plain text — no Rich markup.

### Result Handling

| Action returns | CLI default                   | MCP default                       | Override mechanism           |
|----------------|-------------------------------|-----------------------------------|------------------------------|
| `dict`         | `print_json(result)`          | return raw                        | `on_success` / `result_message` |
| `list[dict]`   | `print_json(result)`          | return raw                        | `on_success` / `result_message` |
| `bool`         | `print_json(result)`          | return raw                        | `on_success` / `result_message` |
| `None`         | `success("Done.")` (generic)  | return `"Done."` string (generic) | **must** provide explicit override |

`on_success` (CLI) and `result_message` (MCP) accept:

- **String template**: formatted with `str.format(**kwargs)` where kwargs is
  the dict passed to the action. CLI templates may contain Rich markup; MCP
  templates stay plain text.
- **Callable**: `(result, kwargs) -> str` for cases requiring logic.

When `output_flag=True` and the user passes `--output <path>`, the CLI
wrapper writes JSON to the file and prints the save-message, bypassing
`on_success`. Format:

```text
{saved_noun or "Result"} saved to [magenta]{output}[/magenta].
```

The noun is capitalized before formatting (so `saved_noun="run list"`
produces `"Run list saved to ..."`). This replaces ~30 hand-written
`success(msg=f"... saved to [magenta]{output}[/magenta].")` strings across
the full CLI — see "Design Principle" at the top of this section.

### Framework Module Layout

```text
nextmv/cli/framework/
    __init__.py          # re-exports:
                         #   command          (from command.py)
                         #   progress         (= nextmv.cli.message.in_progress)
                         #   emit             (from result.py)
                         #   option aliases   (from options.py)
    command.py           # cli.command() implementation + _render_examples()
    options.py           # dual-purpose Annotated aliases,
                         #             shared help constants,
                         #             framework-internal CLI-only aliases
    result.py            # emit(), on_success template/callable handling,
                         #             save-message formatting

nextmv/cli/mcp/framework/
    __init__.py          # re-exports:
                         #   tool             (from tool.py)
                         #   client           (= session.get_client)
                         #   clean            (= nextmv.cli.mcp.tools._helpers._none_if_empty)
    tool.py              # mcp_fw.tool() implementation
```

`cli.progress(...)` is a re-export of the existing
`nextmv.cli.message.in_progress(...)` under a shorter name — no new
implementation. Same for `mcp_fw.client()` (re-exports the session helper)
and `mcp_fw.clean()` (re-exports the string normalizer).

**Import pattern at call sites:**

```python
from nextmv.cli import framework as cli
from nextmv.cli.mcp import framework as mcp_fw
# Usage: cli.command(...), cli.progress(...), cli.AppIdOption
#        mcp_fw.tool(...), mcp_fw.client(), mcp_fw.clean(...)
```

The `mcp_fw` alias avoids shadowing the top-level `mcp` package from the MCP
Python SDK. `mcp_fw.client()` replaces the current `_helpers._get_client()`;
`mcp_fw.clean()` replaces `_helpers._none_if_empty()`. The old `_helpers`
names remain as thin aliases until all MCP domains have migrated.

**`normalize_empty` vs `mcp_fw.clean()`:** the `normalize_empty=[...]`
parameter on `mcp_fw.tool()` is the **declarative** form — list the kwargs
that should be piped through `none_if_empty()` before the action is invoked.
This covers nearly all cases. `mcp_fw.clean()` is the **imperative** form,
exported for ad-hoc sanitization inside custom action bodies or helper
functions. Prefer the declarative form in connector files.

## Pilot Scope

**In scope for the pilot PR (stays on `refactor/mcp-shared-actions` branch,
local only):**

1. **Feasibility spike** — ~20-line standalone test confirming that
   `Annotated[str | None, typer.Option(...), Field(description=...)]` is
   accepted by both Typer's `CliRunner` and FastMCP's tool registration.
   If Pydantic rejects `typer.OptionInfo`, fall back to sibling aliases
   before writing any framework code.
2. **Framework implementation**:
   - `nextmv/cli/framework/{__init__.py, command.py, options.py, result.py}`
     with every alias the `app` domain needs.
   - `nextmv/cli/mcp/framework/{__init__.py, tool.py}`.
3. **Framework unit tests** under `tests/cli/framework/`:
   - `test_command.py`, `test_tool.py`, `test_options.py`
     (see "Testing" section).
4. **`app` domain migration**:
   - Rewrite `nextmv/cli/actions/app.py` to use dual-purpose aliases and
     multi-paragraph docstrings.
   - Delete the 7 per-command files under `nextmv/cli/cloud/app/`.
   - Rewrite `nextmv/cli/cloud/app/__init__.py` as the connector table.
   - Rewrite `nextmv/cli/mcp/tools/app.py` as `mcp.tool()` calls.
5. **Integration assertions for `app`**:
   - New: CLI `--help` output check for each command (flag names, short forms,
     envvar hints, example blocks present).
   - New: MCP `server.list_tools()` schema check for each tool (name,
     description, input schema shape).
   - Existing: `tests/cli/actions/app.py`, `tests/cli/cloud/app/*`,
     `tests/cli/mcp/tools/test_app.py` — all pass unchanged.

**Local-only constraint:**

- **No `git push` on the pilot branch.** Work stays local through the
  feasibility spike, framework implementation, and `app` domain migration.
- Verification is done via `uv run pytest` from `nextmv/` and manual
  `nextmv cloud app --help` / MCP tool-list inspection.
- Decision to push or create a PR is deferred until explicit user approval
  after reviewing the working pilot. The final checkpoint of the
  implementation plan stops at "tests pass locally, ready for review" —
  no push, no PR step.

**Out of scope** (deferred to follow-up PRs):

- Migrating the other ~19 domains (`secrets`, `instance`, `version`,
  `input_set`, `managed_input`, `batch`, `switchback`, `shadow`, `ensemble`,
  `acceptance`, `scenario`, `community`, `run`, `local`, `account`, `sso`,
  `guide`, `profile`, `upload`). Suggested rollout order after pilot:
  1. Simple CRUD domains first (`secrets`, `instance`, `version`,
     `input_set`, `managed_input`).
  2. Medium-complexity domains next (`batch`, `switchback`, `shadow`,
     `ensemble`, `acceptance`, `scenario`, `community`).
  3. Complex domains last (`run`, `local`).
  4. MCP-only tools (`guide`, `profile`) — wired with `mcp.tool()` only,
     no `cli.command()`.
- Retiring `_helpers._none_if_empty` and `_helpers._get_client` in full
  (they remain as thin aliases until all domains have migrated).
- Any changes to the actions layer's public API beyond the `app` domain.

## Testing

### Feasibility Spike (first)

A standalone ~20-line test in `tests/cli/framework/test_spike.py`, deleted
once `test_options.py` subsumes it as the permanent regression guard:

- Define one dual-purpose alias
  `Annotated[str | None, typer.Option(...), Field(description=...)]`.
- Define one dummy action using it.
- Register with a `typer.Typer()` via `typer.Option`-style introspection,
  run via `CliRunner`, assert the command executes with the right
  parameter binding.
- Register with a `FastMCP()` instance, call `server.list_tools()`, assert
  the JSON schema contains the `description` from `Field(...)`.
- If Pydantic raises on the `typer.OptionInfo`: stop, adjust the design to
  sibling aliases, re-run the spike, then proceed.

### Framework Unit Tests

`tests/cli/framework/test_command.py`:
- Pass fake actions to `cli.command()` with varying signatures
  (no params, one param, multiple params, `None`-returning,
  positional-only params, keyword-only params).
- Assert the wrapper has the expected `__signature__`, `__annotations__`,
  and parameter kinds (positional-only/keyword-only preserved).
- Run via Typer's `CliRunner` and assert:
  - Correct `Client` construction from `--profile`.
  - `in_progress()` called when `progress=` is set.
  - `--output <path>` writes JSON to file when `output_flag=True`.
  - Save-message uses `saved_noun` when provided, defaults to "Result"
    otherwise, and is capitalized and markup-formatted correctly.
  - `on_success` string templates and callables format correctly.
  - Missing `client` first parameter raises `TypeError` at decoration time.

`tests/cli/framework/test_tool.py`:
- Pass fake actions to `mcp.tool()`.
- Register on a real `FastMCP()` instance.
- Introspect via `server.list_tools()` and assert the input schema matches
  the expected JSON schema (types, descriptions, required vs optional).
- Invoke the tool and assert:
  - `none_if_empty` applied to every name in `normalize_empty`.
  - `result_message` string templates and callables format correctly.
  - Missing `client` first parameter raises at decoration time.

`tests/cli/framework/test_options.py`:
- For each dual-purpose alias in `options.py`, assert it is consumable by:
  - Typer: a dummy Typer command using the alias runs via `CliRunner`.
  - Pydantic: `TypeAdapter(alias).json_schema()` returns the expected
    schema with the description from `Field(...)`.
- This is the permanent regression guard for the "`typer.Option` +
  `Field` in one `Annotated`" contract.

### Action Tests (Existing, Unchanged)

`tests/cli/actions/test_app.py` and other action tests must pass
unchanged. The dual-purpose aliases reduce to the same runtime types the
actions had before (`str | None`, `bool`, etc.), so no test updates
are expected.

### Pilot-Domain Integration Tests

Existing tests under `tests/cli/cloud/app/` (if any) and
`tests/cli/mcp/tools/test_app.py`:
- Tests that assert on the **observable contract** (flags, help output,
  exit codes, printed output, tool names, tool input schemas, tool return
  values) must pass unchanged — this refactor preserves the contract exactly.
- Tests that assert on **implementation details** (specific mock call
  sequences against `Client`, internal function call order, the exact
  location of a particular code path) will likely need updates. These
  should be rewritten as observable-contract assertions rather than patched
  to match the new internals. If a test cannot be converted without losing
  coverage, flag it on the pilot review — the migration may have exposed a
  missing seam in the action layer.

New tests added for the pilot:
- `tests/cli/cloud/app/test_help_output.py`:
  - Run `nextmv cloud app <verb> --help` via `CliRunner` for each verb.
  - Assert the help text contains expected flag names, short forms,
    envvar hints, and the rendered examples block (with every
    `(description, command)` pair from the tuple appearing in order).
  - Assert the "Examples" header is present when `examples=` is set and
    absent when it is not.
  - **Snapshot comparison against the current hand-written help output**
    for at least one example-rich command (`create`) and one simple
    command (`list`). This confirms the rendered examples block matches
    today's presentation byte-for-byte, including inline Rich markup
    like `[magenta]hare[/magenta]` inside descriptions. Captured once at
    the start of the pilot from the current `develop` output, stored
    under `tests/cli/cloud/app/fixtures/`, and compared in the test.
- `tests/cli/mcp/tools/test_app_schemas.py`:
  - Register the `app` MCP tools on a `FastMCP()` instance.
  - Call `server.list_tools()`.
  - Assert each tool's name, description (first line of action docstring),
    and input schema shape.

## Risks

- **Pydantic v2 rejects `typer.OptionInfo` in `Annotated`.** *Mitigation:*
  feasibility spike runs before any framework code is written. If it
  rejects, fall back to sibling aliases (`AppIdCli`, `AppIdMcp`) sharing a
  help constant — still one source of truth for help text, two aliases
  instead of one.
- **Typer version coupling.** The design relies on Typer walking `Annotated`
  metadata for `OptionInfo`, which is Typer's documented contract.
  *Mitigation:* pin Typer's major version; the `test_options.py` regression
  guard catches breakage if it happens.
- **Stack traces point at anonymous wrappers.** *Mitigation:* set
  `wrapper.__qualname__ = f"{action.__module__}.{action.__name__}"` and
  use `functools.wraps` so tracebacks point at the action.
- **Rich markup leakage.** CLI `on_success` may contain Rich markup
  (`[magenta]...[/magenta]`); MCP `result_message` must not. *Mitigation:*
  documented in both `command.py` and `tool.py` docstrings; reviewers
  check it during domain migrations.
- **Action layer transitively imports `typer` and `pydantic`.** The actions
  module is no longer framework-free. *Mitigation:* documented in the
  `nextmv/cli/actions/` package docstring; acceptable because actions live
  under the `cli` namespace.

## References

- Current CLI command example (pre-refactor):
  [nextmv/cli/cloud/app/list.py](../../../nextmv/nextmv/cli/cloud/app/list.py)
- Current MCP tool example (pre-refactor):
  [nextmv/cli/mcp/tools/app.py](../../../nextmv/nextmv/cli/mcp/tools/app.py)
- Current action example:
  [nextmv/cli/actions/app.py](../../../nextmv/nextmv/cli/actions/app.py)
- MCP helpers targeted for retirement:
  [nextmv/cli/mcp/tools/_helpers.py](../../../nextmv/nextmv/cli/mcp/tools/_helpers.py)
