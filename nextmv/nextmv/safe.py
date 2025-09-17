"""

The safe module contains utilities for generating “safe” IDs and human-readable
names.

Functions
---------
safe_name_and_id
    Generate a safe ID and human-readable name from a prefix and user-supplied
    identifier.
safe_id
    Generate a safe ID from a prefix.
"""

import re
import secrets
import string

ENTITY_ID_CHAR_COUNT_MAX: int = 40
INDEX_TAG_CHAR_COUNT: int = 3  # room reserved for “-001”, “-xyz”, etc.
RE_NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")


def _kebab_case(value: str) -> str:
    """Convert arbitrary text to `kebab-case` (lower-case, hyphen-separated)."""

    cleaned = RE_NON_ALNUM.sub(" ", value).strip()
    return "-".join(word.lower() for word in cleaned.split())


def _start_case(value: str) -> str:
    """Convert `kebab-case` (or any hyphen/underscore string) to `Start Case`."""

    cleaned = re.sub(r"[-_]+", " ", value)
    return " ".join(word.capitalize() for word in cleaned.split())


def _nanoid(size: int = 8, alphabet: str = string.ascii_lowercase + string.digits) -> str:
    """Simple nanoid clone using the std-lib `secrets` module."""

    return "".join(secrets.choice(alphabet) for _ in range(size))


def safe_name_and_id(prefix: str, entity_id: str) -> tuple[str, str]:
    """
    Generate a safe ID and human-readable name from a prefix and user-supplied
    identifier.

    You can import the `safe_name_and_id` function directly from `nextmv`:

    ```python
    from nextmv import safe_name_and_id
    ```

    Parameters
    ----------
    prefix : str
        Prefix to use for the ID.
    entity_id : str
        User-supplied identifier. This will be converted to `kebab-case` and
        truncated to fit within the safe ID length.

    Returns
    -------
    tuple[str, str]
        A tuple containing the human-readable name and the safe ID.

    Examples
    --------
    >>> safe_name_and_id("app", "My Application 123!")
    ('App My Application 123', 'app-my-application-123-4f5g6h7j')
    """

    if not prefix or not entity_id:
        return "", ""

    safe_user_defined_id = _kebab_case(entity_id)
    random_slug = _nanoid(8)

    # Space available for user text once prefix, random slug and separator "-"
    # are accounted for
    safe_id_max = (
        ENTITY_ID_CHAR_COUNT_MAX
        - INDEX_TAG_CHAR_COUNT
        - len(prefix)
        - (len(random_slug) + 1)  # +1 for the hyphen before the slug
    )

    safe_id_parts: list[str] = [prefix]

    for word in safe_user_defined_id.split("-"):
        # Trim individual word if it alone would overflow
        safe_slug = word[: safe_id_max - 1] if len(word) > safe_id_max else word

        # Will the combined ID (so far) overflow if we add this slug?
        prospective_len = len("-".join(safe_id_parts + [safe_slug]))
        if prospective_len >= safe_id_max:
            break
        safe_id_parts.append(safe_slug)

    safe_id = "-".join(filter(None, safe_id_parts)) + f"-{random_slug}"
    safe_name = _start_case(safe_id)

    return safe_name, safe_id


def safe_id(prefix: str) -> str:
    """
    Generate a safe ID from a prefix.

    You can import the `safe_id` function directly from `nextmv`:

    ```python
    from nextmv import safe_id
    ```

    Parameters
    ----------
    prefix : str
        Prefix to use for the ID.

    Returns
    -------
    str
        A safe ID.

    Examples
    --------
    >>> safe_id("app")
    'app-4f5g6h7j'
    """

    random_slug = _nanoid(8)
    # Space available for user text once prefix, random slug and separator "-"
    # are accounted for
    safe_id_max = (
        ENTITY_ID_CHAR_COUNT_MAX - INDEX_TAG_CHAR_COUNT - (len(random_slug) + 1)  # +1 for the hyphen before the slug
    )

    if len(prefix) > safe_id_max:
        return prefix[: safe_id_max - 1] + f"-{random_slug}"

    safe_id = f"{prefix}-{random_slug}"

    return safe_id
