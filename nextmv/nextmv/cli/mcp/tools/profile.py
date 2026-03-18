"""MCP tools for profile management."""

from mcp.server.fastmcp import FastMCP

from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register profile management tools."""

    @mcp.tool()
    def cloud_list_profiles() -> list[dict[str, str | None]]:
        """List available Nextmv Cloud profiles.

        Reads profiles from ``~/.nextmv/config.yaml``. Each returned
        profile contains a name, endpoint URL, and a masked API key
        (only the last 4 characters are visible). The ``"default"``
        profile corresponds to the top-level configuration keys.
        """

        from nextmv.cli.configuration.config import (
            API_KEY_KEY,
            ENDPOINT_KEY,
            load_config,
            non_profile_keys,
        )

        config = load_config()
        profiles: list[dict[str, str | None]] = []

        # Add the default profile (top-level keys).
        if config:
            profiles.append(
                {
                    "name": "default",
                    "endpoint": config.get(ENDPOINT_KEY),
                    "api_key": _helpers._mask_key(config.get(API_KEY_KEY)),
                }
            )

        # Add named profiles.
        reserved = non_profile_keys()
        for key, value in config.items():
            if key in reserved:
                continue
            if isinstance(value, dict):
                profiles.append(
                    {
                        "name": key,
                        "endpoint": value.get(ENDPOINT_KEY),
                        "api_key": _helpers._mask_key(value.get(API_KEY_KEY)),
                    }
                )

        return profiles

    @mcp.tool()
    def cloud_set_profile(profile: str) -> str:
        """Set the active Nextmv Cloud profile for this session.

        All subsequent cloud tool calls will use this profile's API
        key and endpoint unless explicitly overridden. Use
        ``"default"`` to switch back to the top-level configuration.

        Args:
            profile: Profile name as defined in
                ``~/.nextmv/config.yaml``, or ``"default"`` for the
                top-level configuration keys.
        """

        _helpers._current_profile = None if profile == "default" else profile
        return f"Active profile set to \"{profile}\"."

    @mcp.tool()
    def cloud_get_profile() -> str:
        """Get the name of the currently active Nextmv Cloud profile.

        Returns ``"default"`` if no named profile has been set.
        """

        return _helpers._current_profile or "default"
