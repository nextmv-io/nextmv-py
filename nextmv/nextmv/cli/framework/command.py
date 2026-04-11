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

# A private alias used solely for the first-parameter annotation assertion.
# Test code frequently patches ``nextmv.cli.framework.command.Client`` to mock
# the real cloud client constructor; that must not break the identity check
# against an action's declared ``client: Client`` annotation. Holding a
# separate reference here sidesteps the patch.
_REAL_CLIENT = Client

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
    if params[0].annotation is not _REAL_CLIENT:
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
    handles_own_output: bool = False,
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
        Incompatible with ``handles_own_output=True``.
    saved_noun:
        The noun for the save-success message (e.g. ``"Application list information"``
        → ``"Application list information saved to [magenta]{path}[/magenta]."``).
        Only meaningful with ``output_flag=True``. Defaults to ``"Result"``.
    on_success:
        Either a ``str.format``-style template (formatted with ``**kwargs``
        where kwargs is the dict passed to the action) or a callable
        ``(result, kwargs) -> str``. Used when the action returns ``None`` or
        when the command wants a custom success line instead of printing
        JSON. Bypassed when ``--output`` is supplied. Incompatible with
        ``handles_own_output=True``.
    examples:
        Tuple of ``(description, command)`` pairs rendered into the command's
        help text as a Rich-formatted examples block.
    handles_own_output:
        If ``True``, the wrapped action is responsible for printing its own
        status messages (via ``success``, ``info``, ``error``, etc.) and the
        wrapper will NOT call ``emit()`` or ``apply_on_success()``. Use this
        for interactive workflows (e.g. the push workflow) where the action
        manages all user-facing output. The action's return value is
        discarded. Incompatible with ``output_flag`` and ``on_success``.

    Returns
    -------
    The generated wrapper function (already registered on ``typer_app``). The
    wrapper can be assigned to a variable for later reference.
    """
    if handles_own_output and output_flag:
        raise TypeError(
            f"{action.__name__}: handles_own_output=True is incompatible with "
            "output_flag=True (the action manages its own output)."
        )
    if handles_own_output and on_success is not None:
        raise TypeError(
            f"{action.__name__}: handles_own_output=True is incompatible with "
            "on_success= (the action prints its own success messages)."
        )

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

        # handles_own_output: action printed everything itself, we're done.
        if handles_own_output:
            return

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
