"""Shared configuration building utilities."""

from nextmv.input import InputFormat
from nextmv.run import Format, FormatInput, RunConfiguration

_VALID_CONTENT_FORMATS = {f.value for f in InputFormat}


def validate_content_format(content_format: str) -> None:
    """Raise ValueError if content_format is not a recognised value."""
    if content_format not in _VALID_CONTENT_FORMATS:
        raise ValueError(
            f"Invalid content_format '{content_format}'. "
            f"Allowed values: {sorted(_VALID_CONTENT_FORMATS)}"
        )


def build_run_configuration(content_format: str | None) -> RunConfiguration | None:
    """Build a RunConfiguration for the given content format string, or None."""
    if content_format is None:
        return None
    validate_content_format(content_format)
    config = RunConfiguration()
    config.format = Format(
        format_input=FormatInput(input_type=InputFormat(content_format)),
    )
    return config
