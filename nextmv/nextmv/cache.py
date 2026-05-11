"""
Module with the cache interface and operations for working with dependencies.

Functions
---------
create_cache
    Create the cache directories if they do not already exist.
cache_key
    Return a SHA-256 hex digest that uniquely identifies a dependency set.
get_cached_deps
    Return the path to the cached `deps` directory on a hit.
store_deps
    Copy an installed dependency tree into the cache and run LRU eviction.
evict_lru
    Remove the least-recently-used cache entries until both caps are satisfied.
clear_cache
    Delete the entire cache directory and recreate it empty.
"""

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_CACHE_DIR = Path.home() / ".nextmv" / "cache"
_DEPS_CACHE_DIR = _CACHE_DIR / "deps"
_CACHE_INFO_FILE = "cache_info.json"

_DEFAULT_MAX_ENTRIES = 200
"""Maximum number of dependency sets to keep in the cache."""

_DEFAULT_MAX_BYTES = 1 * 1024**3
"""Maximum total cache size in bytes (1 GiB)."""


def clear_cache() -> None:
    """
    Delete the entire cache directory and recreate it empty.
    """

    if _CACHE_DIR.exists():
        shutil.rmtree(str(_CACHE_DIR))

    _create_cache()


def cache_key(lockfile_content: str, python_version: str, platform: str) -> str:
    """
    Return a SHA-256 hex digest that uniquely identifies a dependency set.

    The key is derived from the fully-pinned lockfile content combined with the
    target Python version and platform.  Any change to resolved packages or the
    target environment produces a different key.

    Parameters
    ----------
    lockfile_content : str
        The fully-pinned lockfile produced by `uv pip compile`.
    python_version : str
        The target Python version string (e.g. `"3.11"`).
    platform : str
        The target platform string (e.g. `"aarch64-unknown-linux-gnu"`).

    Returns
    -------
    str
        A 64-character lowercase hex SHA-256 digest.
    """

    raw = f"{lockfile_content}|{python_version}|{platform}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_deps(key: str) -> Path | None:
    """
    Return the path to the cached `deps` directory on a hit.

    On a cache hit, `last_used_at` in the entry's `cache_info.json` is
    updated to the current UTC time so that the LRU eviction order reflects
    actual recency of use.  The caller is responsible for placing the returned
    directory wherever the consuming logic expects it.

    Parameters
    ----------
    key : str
        The cache key returned by `cache_key`.

    Returns
    -------
    Path or None
        Path to the `deps` directory for the cached entry, or `None` when
        no entry exists for the given key.
    """

    entry_dir = _DEPS_CACHE_DIR / key
    deps_dir = entry_dir / "deps"
    info_file = entry_dir / _CACHE_INFO_FILE

    if not deps_dir.is_dir() or not info_file.is_file():
        return None

    # Update last_used_at for true LRU tracking.
    try:
        with open(info_file) as f:
            info = json.load(f)

        info["last_used_at"] = _now_iso()
        _write_json_atomic(path=info_file, data=info)
    except Exception:
        # A failure to update the timestamp is non-fatal; still serve the hit.
        pass

    return deps_dir


def store_deps(
    key: str,
    installed_deps_dir: str | Path,
    python_version: str,
    platform: str,
    lockfile_content: str,
    max_entries: int = _DEFAULT_MAX_ENTRIES,
    max_bytes: int = _DEFAULT_MAX_BYTES,
) -> None:
    """
    Copy an installed dependency tree into the cache and run LRU eviction.

    The `installed_deps_dir` must be the `.nextmv/python/deps` directory
    produced by `uv pip install`.  The copy is performed atomically via a
    sibling temporary directory followed by a rename, so concurrent readers
    never observe a partial write.

    Parameters
    ----------
    key : str
        The cache key returned by `cache_key`.
    installed_deps_dir : str or Path
        Path to the directory of installed packages produced by
        `uv pip install`.
    python_version : str
        The target Python version string (e.g. `"3.11"`).
    platform : str
        The target platform string (e.g. `"aarch64-unknown-linux-gnu"`).
    lockfile_content : str
        The fully-pinned lockfile stored in `cache_info.json` for
        informational purposes.
    max_entries : int, optional
        Maximum number of entries allowed in the cache.  Defaults to
        `DEFAULT_MAX_ENTRIES`.
    max_bytes : int, optional
        Maximum total cache size in bytes.  Defaults to `DEFAULT_MAX_BYTES`.
    """

    _create_cache()
    entry_dir = _DEPS_CACHE_DIR / key

    # Write to a sibling temp directory first, then rename for atomicity.
    # ignore_cleanup_errors=True handles the case where rename succeeded and
    # the directory no longer exists when the context manager tries to clean up.
    with tempfile.TemporaryDirectory(dir=_DEPS_CACHE_DIR, prefix=f"{key}-tmp-", ignore_cleanup_errors=True) as _tmp:
        tmp_entry = Path(_tmp)
        tmp_deps = tmp_entry / "deps"
        shutil.copytree(str(installed_deps_dir), str(tmp_deps))
        now = _now_iso()
        info = {
            "created_at": now,
            "last_used_at": now,
            "python_version": python_version,
            "platform": platform,
            "lockfile": lockfile_content,
        }
        metadata_path = tmp_entry / _CACHE_INFO_FILE
        _write_json_atomic(path=metadata_path, data=info)

        # Rename into place; if the key already exists (race), keep existing.
        if not entry_dir.exists():
            tmp_entry.rename(entry_dir)

    _evict_lru(max_entries=max_entries, max_bytes=max_bytes)


def _create_cache() -> None:
    """
    Create the cache directories if they do not already exist.
    """

    _DEPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _evict_lru(
    max_entries: int = _DEFAULT_MAX_ENTRIES,
    max_bytes: int = _DEFAULT_MAX_BYTES,
) -> int:
    """
    Remove the least-recently-used (LRU) cache entries until both caps are satisfied.

    Entries are sorted by `last_used_at` ascending (oldest first) and deleted
    one by one until the total entry count is at most `max_entries` AND the
    total disk usage is at most `max_bytes`.

    Parameters
    ----------
    max_entries : int, optional
        Maximum number of entries to retain.  Defaults to
        `DEFAULT_MAX_ENTRIES`.
    max_bytes : int, optional
        Maximum total cache size in bytes to retain.  Defaults to
        `DEFAULT_MAX_BYTES`.

    Returns
    -------
    int
        The number of entries that were removed.
    """

    if not _DEPS_CACHE_DIR.is_dir():
        return 0

    entries = []
    for entry_dir in _DEPS_CACHE_DIR.iterdir():
        if not entry_dir.is_dir():
            continue

        info_file = entry_dir / _CACHE_INFO_FILE
        try:
            with open(info_file) as f:
                info = json.load(f)

            last_used = datetime.fromisoformat(info["last_used_at"])
        except Exception:
            # Treat unreadable entries as very old so they are evicted first.
            last_used = datetime.min.replace(tzinfo=timezone.utc)

        entry = {
            "last_used": last_used,
            "dir": entry_dir,
            "size": _dir_size(entry_dir),
        }
        entries.append(entry)

    # Sort oldest to newest by last_used_at.
    entries.sort(key=lambda e: e["last_used"])

    total = sum(e["size"] for e in entries)
    evicted = 0
    while entries and (len(entries) > max_entries or total > max_bytes):
        oldest = entries.pop(0)
        shutil.rmtree(str(oldest["dir"]), ignore_errors=True)
        total -= oldest["size"]
        evicted += 1

    return evicted


def _now_iso() -> str:
    """
    Return the current UTC time as an ISO-8601 string.
    """

    return datetime.now(tz=timezone.utc).isoformat()


def _dir_size(path: Path) -> int:
    """
    Return the total size in bytes of all files under path.
    """
    total = 0
    for root, _, files in os.walk(path):
        for fname in files:
            try:
                total += os.path.getsize(os.path.join(root, fname))
            except OSError:
                pass
    return total


def _write_json_atomic(path: Path, data: dict) -> None:
    """
    Write data as JSON to path atomically via a sibling temporary file.
    """

    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=path.parent,
        prefix=".tmp-",
        delete=False,
    ) as f:
        json.dump(data, f, indent=2)
        tmp = Path(f.name)

    try:
        tmp.rename(path)
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise e
