## MCP Server Refactor: Shared Action Layer

### Problem

The CLI commands (`cli/cloud/`) and MCP tools (`cli/mcp/tools/`) both wrapped the same SDK methods with separate implementations. Every new feature required changes in two places, and MCP tools couldn't be tested without the MCP framework.

### What we did

Extracted shared business logic into a new `cli/actions/` module -- 19 files of pure functions that both CLI and MCP import from. Each function takes a `Client` or `Application`, accepts plain parameters, returns data, and has no side effects.

**Before:**
```
CLI command -> SDK call -> print output
MCP tool    -> SDK call -> return/cache output
```

**After:**
```
CLI command -> actions function -> print output
MCP tool    -> actions function -> return/cache output
```

### Scope

- **18 action modules** covering all domains: app, version, instance, run, batch, acceptance, scenario, ensemble, shadow, switchback, input_set, secrets, account, sso, managed_input, community, local, plus a shared `config.py`
- **~60 CLI command files** updated to import from actions
- **18 MCP tool files** slimmed to thin wrappers
- **Monolithic test file split** -- `test_mcp.py` (2163 lines, 14 classes) split into 9 domain files under `tests/cli/mcp/`
- **147 new action tests** across 18 test files under `tests/cli/actions/`
- **282 total tests passing**, up from 135

### What stayed where

| Layer | Responsibility |
|-------|---------------|
| `cli/actions/` | Pure SDK calls, data transformation (`build_scenario`, `parse_evaluation_rule`) |
| CLI commands | Typer options, Rich formatting, stdin/tar handling, interactive prompts, `--output` file writes |
| MCP tools | `@mcp.tool()` registration, LLM docstrings, `_none_if_empty()` normalization, result caching to `~/.nextmv/runs/` |

### Branch

All work is on `refactor/mcp-shared-actions` (22 commits). `develop` is clean.

### Known follow-ups

- `profile.py` action module not implemented (MCP-only, no CLI counterpart)
- `local_sync` and `clone_app` actions pass `verbose`/`rich_print` through to SDK (pragmatic exception to purity contract)
- Some `run.py` action functions lack return type annotations
- Action tests don't cover error/negative paths
