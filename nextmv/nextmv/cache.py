"""
Module with the cache interface and operations for working with dependencies.

Functions
---------
dep_cache_key
    Return a SHA-256 hex digest that uniquely identifies a single package.
get_cached_dep
    Return the path to the cached per-package `installed.tar.gz` on a hit.
store_dep
    Store a per-package `installed.tar.gz` into the cache and run LRU eviction.
clear_cache
    Delete the entire cache directory and recreate it empty.
"""

import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_CACHE_DIR = Path.home() / ".nextmv" / "cache"
"""Root directory for all Nextmv cache data."""
_DEPS_CACHE_DIR = _CACHE_DIR / "deps"
"""Directory storing per-package dependency tarballs."""
_CACHE_INFO_FILE = "cache_info.json"
"""Name of the metadata file stored alongside each cached entry."""
_MAX_DEPS = 2000
"""Maximum number of individual package tarballs to keep in the cache."""
_MAX_DEP_BYTES = 5 * 1024**3
"""Maximum total cache size in bytes (5 GiB)."""


def clear_cache() -> None:
    """
    Delete the entire cache directory and recreate it empty.
    """

    if _CACHE_DIR.exists():
        shutil.rmtree(str(_CACHE_DIR))

    _create_cache()


def dep_cache_key(name: str, version: str, python_version: str, platform: str) -> str:
    """
    Return a SHA-256 hex digest that uniquely identifies a single package wheel.

    The key is derived from the normalised package name, version, target Python
    version, and platform.  Name normalisation follows PEP 503 so that
    `pydantic-core` and `pydantic_core` map to the same key.

    Parameters
    ----------
    name : str
        The package name as it appears in the lockfile or wheel filename.
    version : str
        The pinned version string (e.g. `"2.23.4"`).
    python_version : str
        The target Python version string (e.g. `"3.11"`).
    platform : str
        The target platform string (e.g. `"aarch64-unknown-linux-gnu"`).

    Returns
    -------
    str
        A 64-character lowercase hex SHA-256 digest.
    """

    normalized = re.sub(r"[-_.]+", "_", name.lower())
    raw = f"{normalized}=={version}|{python_version}|{platform}"

    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_dep(pkg_key: str) -> Path | None:
    """
    Return the path to the cached `installed.tar.gz` for *pkg_key*, or `None`
    on a miss.

    The tarball contains the installed files for a single package archived under
    `.nextmv/python/deps/`, ready to be concatenated with other per-package
    tarballs to form the final `deps.tar.gz` (valid per RFC 1952).

    On a cache hit `last_used_at` in the entry's `cache_info.json` is
    updated to the current UTC time for LRU tracking.

    Parameters
    ----------
    pkg_key : str
        The cache key returned by :func:`dep_cache_key`.

    Returns
    -------
    Path or None
        Path to the `installed.tar.gz` file, or `None` when no entry exists.
    """

    entry_dir = _DEPS_CACHE_DIR / pkg_key
    info_file = entry_dir / _CACHE_INFO_FILE
    installed_tar = entry_dir / "installed.tar.gz"

    if not installed_tar.is_file() or not info_file.is_file():
        return None

    # Update last_used_at for true LRU tracking.
    try:
        with open(info_file) as f:
            info = json.load(f)
        info["last_used_at"] = _now_iso()
        _write_json_atomic(path=info_file, data=info)
    except Exception:
        pass

    return installed_tar


def store_dep(
    pkg_key: str,
    tar_path: Path,
    python_version: str,
    platform: str,
    max_entries: int = _MAX_DEPS,
    max_bytes: int = _MAX_DEP_BYTES,
) -> None:
    """
    Store a per-package `installed.tar.gz` in the cache and run LRU eviction.

    The tarball must contain the installed files for a single package archived
    under `.nextmv/python/deps/`.  The copy is performed atomically via a
    sibling temporary directory followed by a rename.

    Parameters
    ----------
    pkg_key : str
        The cache key returned by :func:`dep_cache_key`.
    tar_path : Path
        Path to the `installed.tar.gz` to cache.
    python_version : str
        The target Python version string (e.g. `"3.11"`).
    platform : str
        The target platform string (e.g. `"aarch64-unknown-linux-gnu"`).
    max_entries : int, optional
        Maximum number of package tarball entries to retain.
    max_bytes : int, optional
        Maximum total cache size in bytes.
    """

    _create_cache()
    entry_dir = _DEPS_CACHE_DIR / pkg_key

    with tempfile.TemporaryDirectory(dir=_DEPS_CACHE_DIR, prefix=f"{pkg_key}-tmp-", ignore_cleanup_errors=True) as _tmp:
        tmp_entry = Path(_tmp)
        shutil.copy2(str(tar_path), tmp_entry / "installed.tar.gz")
        now = _now_iso()
        info = {
            "created_at": now,
            "last_used_at": now,
            "python_version": python_version,
            "platform": platform,
        }
        _write_json_atomic(path=tmp_entry / _CACHE_INFO_FILE, data=info)

        # Rename into place; if the key already exists (race), keep existing.
        if not entry_dir.exists():
            tmp_entry.rename(entry_dir)

    _evict_lru(max_entries=max_entries, max_bytes=max_bytes)


def _create_cache() -> None:
    """
    Create the cache directories if they do not already exist.
    """

    _DEPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _evict_lru(max_entries: int = _MAX_DEPS, max_bytes: int = _MAX_DEP_BYTES) -> int:
    """
    Remove the least-recently-used per-package tarball cache entries until both
    caps are satisfied.

    Parameters
    ----------
    max_entries : int, optional
        Maximum number of package tarball entries to retain.
    max_bytes : int, optional
        Maximum total cache size in bytes.

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
        # If the info file has problems, treat the entry as very old.
        try:
            with open(info_file) as f:
                info = json.load(f)
            last_used = datetime.fromisoformat(info["last_used_at"])
        except Exception:
            last_used = datetime.min.replace(tzinfo=timezone.utc)

        entries.append(
            {
                "last_used": last_used,
                "dir": entry_dir,
                "size": _dir_size(entry_dir),
            }
        )

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

    Returns
    -------
    str
        Current UTC time as an ISO-8601 string.
    """

    return datetime.now(tz=timezone.utc).isoformat()


def _dir_size(path: Path) -> int:
    """
    Return the total size in bytes of all files under path.

    Parameters
    ----------
    path : Path
        The directory path to calculate the size of.

    Returns
    -------
    int
        Total size in bytes of all files under path.
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

    Parameters
    ----------
    path : Path
        The path to write the JSON data to.
    data : dict
        The data to write as JSON.
    """

    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".tmp-", delete=False) as f:
        json.dump(data, f, indent=2)
        tmp = Path(f.name)

    try:
        tmp.rename(path)
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise e
