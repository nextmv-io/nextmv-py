"""Shared business logic for CLI commands and MCP tools.

Each submodule contains pure functions that:
- Take a Client or Application as their first argument
- Take plain-typed business parameters
- Return data (dict, list, str, bool, None)
- Have no side effects (no printing, no file I/O)
"""
