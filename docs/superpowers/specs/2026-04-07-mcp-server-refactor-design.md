# MCP Server Refactor: Shared Action Layer

**Date:** 2026-04-07
**Status:** Approved

## Problem

The CLI commands (`cli/cloud/`) and MCP tools (`cli/mcp/tools/`) both wrap the same SDK methods but maintain separate implementations. This duplication means every new feature requires changes in two places, and the MCP tools can't be tested without mocking the MCP framework.

## Goal

Extract shared business logic into a standalone `actions/` module. Both CLI commands and MCP tools become thin wrappers that import from `actions/`. The MCP test file (2163 lines, 14 classes) gets split by domain.

## Architecture

```
cli/
├── actions/              # NEW — shared business logic
│   ├── __init__.py
│   ├── app.py            # list_apps, create_app, get_app, delete_app, ...
│   ├── run.py            # submit_run, submit_run_with_result, run_result, ...
│   ├── version.py        # list_versions, create_version, ...
│   ├── instance.py
│   ├── input_set.py
│   ├── batch.py
│   ├── acceptance.py
│   ├── scenario.py
│   ├── ensemble.py
│   ├── shadow.py
│   ├── switchback.py
│   ├── secrets.py
│   ├── sso.py
│   ├── account.py
│   ├── managed_input.py
│   ├── community.py
│   ├── local.py
│   └── profile.py
├── cloud/                # EXISTING — CLI commands (Typer wrappers)
│   ├── app/
│   │   ├── create.py     # imports actions.app.create_app
│   │   ├── list.py       # imports actions.app.list_apps
│   │   └── ...
│   └── ...
└── mcp/                  # EXISTING — MCP tools (thin registration)
    ├── server.py
    ├── serve.py
    └── tools/
        ├── _helpers.py   # slimmed: ProfileSession, _none_if_empty, cache utils
        ├── app.py        # imports actions.app.*, wraps with @mcp.tool()
        └── ...
```

## Action Function Contract

Each action function:

1. Takes a `Client` or `Application` as its first argument
2. Takes plain-typed business parameters (no Typer annotations, no MCP concerns)
3. Returns data (`dict`, `list[dict]`, `str`, `bool`, `None`)
4. Has no side effects (no printing, no prompts, no file I/O)
5. Raises exceptions on errors (no `typer.Exit`, no string error returns)

### Example: `actions/app.py`

```python
from nextmv.cloud import Application, Client, list_applications


def list_apps(client: Client) -> list[dict]:
    """List all applications in the account."""
    apps = list_applications(client)
    return [a.to_dict() for a in apps]


def create_app(
    client: Client,
    name: str,
    app_id: str | None = None,
    description: str | None = None,
    is_workflow: bool = False,
    exist_ok: bool = False,
    default_instance_id: str | None = None,
    default_experiment_instance: str | None = None,
) -> dict:
    """Create a new application. Returns the app dict."""
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


def get_app(client: Client, app_id: str) -> dict:
    """Get application details."""
    return Application.get(client=client, id=app_id).to_dict()


def delete_app(client: Client, app_id: str) -> None:
    """Delete an application."""
    Application(client=client, id=app_id).delete()


def app_exists(client: Client, app_id: str) -> bool:
    """Check whether an application exists."""
    return Application.exists(client=client, id=app_id)


def update_app(
    client: Client,
    app_id: str,
    name: str | None = None,
    description: str | None = None,
    default_instance_id: str | None = None,
    default_experiment_instance: str | None = None,
) -> dict:
    """Update application attributes. Returns the updated app dict."""
    app = Application(client=client, id=app_id)
    return app.update(
        name=name,
        description=description,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def push_app(client: Client, app_id: str, app_dir: str) -> None:
    """Push local code to a cloud application."""
    app = Application(client=client, id=app_id)
    app.push(app_dir=app_dir)
```

## CLI Wrapper Pattern

Existing CLI commands change minimally. The SDK call moves to the action function; everything else stays.

### Before (current `cli/cloud/app/create.py`):

```python
@app.command()
def create(app_id: ..., name: ..., profile: ProfileOption = None):
    client = Client(profile=profile)
    in_progress("Creating application...")
    cloud_app = Application.new(client=client, name=name, id=app_id, ...)
    print_json(cloud_app.to_dict())
```

### After:

```python
from nextmv.cli.actions.app import create_app

@app.command()
def create(app_id: ..., name: ..., profile: ProfileOption = None):
    client = Client(profile=profile)
    in_progress("Creating application...")
    result = create_app(client, name=name, app_id=app_id, ...)
    print_json(result)
```

CLI-specific concerns stay in the CLI: `Annotated` options, `--output` file handling, Rich progress messages, interactive prompts (`build_cloud_app`'s confirmation flow), stdin reading, tar detection.

## MCP Wrapper Pattern

MCP tool files shrink to thin registration. Each still owns its tool names, LLM-facing docstrings, `_none_if_empty()` normalization, and caching.

### Before (current `mcp/tools/app.py`):

```python
@mcp.tool()
def cloud_create_app(name: str, app_id: str | None = None, ...):
    app_id = _helpers._none_if_empty(app_id)
    client = _helpers._get_client()
    app = Application.new(client=client, name=name, id=app_id, ...)
    return app.to_dict()
```

### After:

```python
from nextmv.cli.actions.app import create_app

@mcp.tool()
def cloud_create_app(name: str, app_id: str | None = None, ...):
    """Create a new Nextmv Cloud application. ..."""
    return create_app(
        _helpers._get_client(),
        name=name,
        app_id=_helpers._none_if_empty(app_id),
        ...
    )
```

## Complex Cases

### Run Create

The CLI and MCP diverge most here. The core actions are at a lower level:

```python
# actions/run.py

def submit_run(
    app: Application,
    input: dict | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    instance_id: str | None = None,
    options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> str:
    """Submit a run, return the run ID."""
    return app.new_run(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        instance_id=instance_id,
        options=options or {},
        managed_input_id=managed_input_id,
        name=name,
        description=description,
    )


def submit_run_with_result(
    app: Application,
    input: dict | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    instance_id: str | None = None,
    options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    polling_options: PollingOptions | None = None,
    output_dir_path: str | None = None,
) -> RunResult:
    """Submit a run and poll until complete. Returns the full result."""
    return app.new_run_with_result(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        instance_id=instance_id,
        run_options=options or {},
        polling_options=polling_options or default_polling_options(),
        managed_input_id=managed_input_id,
        output_dir_path=output_dir_path,
    )


def run_result(app: Application, run_id: str, output_dir_path: str | None = None):
    """Fetch the result of a completed run."""
    return app.run_result(run_id=run_id, output_dir_path=output_dir_path)


def run_metadata(app: Application, run_id: str) -> dict:
    """Get run status and metadata."""
    return app.run_metadata(run_id=run_id).to_dict()


def cancel_run(app: Application, run_id: str) -> None:
    """Cancel a queued or running run."""
    app.cancel_run(run_id=run_id)


def list_runs(app: Application, status: str | None = None) -> list[dict]:
    """List runs, optionally filtered by status."""
    status_filter = StatusV2(status) if status else None
    return [r.to_dict() for r in app.list_runs(status=status_filter)]


def run_input(app: Application, run_id: str, output_dir_path: str | None = None):
    """Fetch the input data for a run."""
    return app.run_input(run_id=run_id, output_dir_path=output_dir_path)


def run_logs(app: Application, run_id: str):
    """Fetch log snapshot for a run."""
    return app.run_logs(run_id=run_id)
```

The CLI keeps its stdin/tar/wait/tail logic. The MCP keeps its caching logic. Both call the same action functions.

### Scenario/Ensemble Data Parsing

Functions like `_build_scenario()` and `_parse_evaluation_rule()` move to their respective action modules since they're pure data transformation, not MCP-specific:

```python
# actions/scenario.py
def build_scenario(s: dict) -> Scenario:
    """Convert a plain dict into a Scenario dataclass."""
    ...

def create_scenario_test(app: Application, scenarios: list[dict], ...) -> str:
    scenario_objs = [build_scenario(s) for s in scenarios]
    return app.new_scenario_test(scenarios=scenario_objs, ...)
```

## What Stays in `mcp/tools/_helpers.py`

Only MCP-specific concerns:

- `ProfileSession` — async context isolation for concurrent HTTP requests
- `_get_client()` / `_get_app()` — env var + profile resolution (different from CLI's `Client(profile=...)`)
- `_none_if_empty()` — LLM input normalization
- Cache utilities: `_cloud_run_dir`, `_cloud_run_file_exists`, `_save_cloud_run_file`, `_extract_cloud_run_outputs`, `_save_cloud_run_logs`, `_save_to_file`, `_save_to_json_file`
- `_endpoint_from_app()`

## Test Structure

### Split existing `test_mcp.py` (2163 lines) into `tests/cli/mcp/`:

```
tests/cli/mcp/
├── __init__.py
├── test_serve.py          # TestMCPServeCommand, TestMCPOptionalDependency (~70 lines)
├── test_tools.py          # TestMCPServerTools — registration checks (~280 lines)
├── test_client.py         # TestGetClient, TestProfileSessionIsolation (~120 lines)
├── test_helpers.py        # TestSaveToFile, TestHelperFunctions (~270 lines)
├── test_profiles.py       # TestProfiles (~120 lines)
├── test_run.py            # TestBugFixes, TestMultiFileRunSupport, TestCloudRunCache (~950 lines)
├── test_ensemble.py       # TestEnsembleRunTools (~100 lines)
├── test_visuals.py        # TestVisualGenerationWarning (~40 lines)
└── test_content_type.py   # TestSDKContentType (~70 lines)
```

### New core action tests in `tests/cli/actions/`:

```
tests/cli/actions/
├── __init__.py
├── test_app.py            # Tests list_apps, create_app, etc. with mocked Client
├── test_run.py            # Tests submit_run, run_result, etc.
├── test_version.py
├── test_scenario.py       # Tests build_scenario() parsing logic
└── ...                    # One per action module as needed
```

These test the core functions directly — no Typer runner, no MCP server, just mock the `Client`/`Application` SDK objects.

## Migration Order

Each phase is a self-contained PR:

1. **Phase 1 — Simple CRUD:** app, version, instance, input_set, secrets, managed_input, account, sso, profile
2. **Phase 2 — Experiments:** batch, acceptance, scenario, ensemble, shadow, switchback
3. **Phase 3 — Complex:** run, local, community
4. **Phase 4 — Test split:** move existing test classes to domain files, add action tests

Phases 1-3 each follow the same steps per domain:
1. Create `actions/<domain>.py` with core functions
2. Update CLI command to import and call the action function
3. Update MCP tool to import and call the action function
4. Verify existing tests still pass

Phase 4 can happen in parallel with any other phase.

## Out of Scope

- Changing the MCP server's FastMCP setup, transport, or instructions
- Changing CLI command signatures or help text
- Auto-generating MCP tools from action functions (possible future improvement)
- Changing the SDK layer
