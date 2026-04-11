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
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools._helpers import _get_client, _none_if_empty
from nextmv.cloud.client import Client

# Module-level alias captured at import time so that @patch("...tool.Client")
# in tests doesn't break the identity check in _assert_first_param_is_client.
# Mirrors the same pattern used by nextmv.cli.framework.command.
_REAL_CLIENT = Client


def _assert_first_param_is_client(action: Callable) -> inspect.Signature:
    """Assert that the action's first parameter is ``client: Client``.

    Raises ``TypeError`` at decoration time if the convention is violated.
    Returns the action's ``inspect.Signature`` for reuse by the builder.
    """
    sig = inspect.signature(action)
    params = list(sig.parameters.values())
    if not params or params[0].name != "client":
        raise TypeError(
            f"{action.__name__} must take `client: Client` as its first parameter "
            f"(got parameters: {[p.name for p in params]})"
        )
    if params[0].annotation is not _REAL_CLIENT:
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
        actions (delete, push). Must stay plain text — no Rich markup.
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

    # functools.update_wrapper contributes __module__, __name__,
    # __type_params__, __wrapped__ (used by inspect.unwrap), and merges
    # __dict__. The manual overrides below replace the metadata that
    # needs wrapper-specific values (__signature__, __annotations__,
    # __qualname__, __doc__).
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
