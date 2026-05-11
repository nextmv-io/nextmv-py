"""Tests for the nextmv.cache module."""

import io
import json
import os
import shutil
import tarfile
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from nextmv.cache import (
    _CACHE_INFO_FILE,
    _DEFAULT_MAX_BYTES,
    _DEPS_CACHE_DIR,
    _evict_lru,
    cache_key,
    clear_cache,
    get_cached_deps,
    store_deps,
)


def _write_fake_entry(key: str, last_used_at: str, size_bytes: int = 0) -> None:
    """Write a minimal cache entry for use in tests."""
    entry_dir = _DEPS_CACHE_DIR / key
    entry_dir.mkdir(parents=True, exist_ok=True)

    deps_tar = entry_dir / "deps.tar.gz"
    with tarfile.open(str(deps_tar), "w:gz") as tar:
        if size_bytes > 0:
            data = b"x" * size_bytes
            info = tarfile.TarInfo(name=".nextmv/python/deps/dummy.pth")
            info.size = size_bytes
            tar.addfile(info, io.BytesIO(data))

    info = {
        "created_at": last_used_at,
        "last_used_at": last_used_at,
        "python_version": "3.11",
        "platform": "aarch64-unknown-linux-gnu",
        "lockfile": "# pinned\nnextmv==1.0.0\n",
    }
    with open(entry_dir / _CACHE_INFO_FILE, "w") as f:
        json.dump(info, f)


class TestCacheKey(unittest.TestCase):
    def test_stable(self):
        k1 = cache_key("lock\nnextmv==1.0.0", "3.11", "aarch64-unknown-linux-gnu")
        k2 = cache_key("lock\nnextmv==1.0.0", "3.11", "aarch64-unknown-linux-gnu")
        self.assertEqual(k1, k2)

    def test_differs_on_lockfile(self):
        k1 = cache_key("nextmv==1.0.0", "3.11", "aarch64-unknown-linux-gnu")
        k2 = cache_key("nextmv==2.0.0", "3.11", "aarch64-unknown-linux-gnu")
        self.assertNotEqual(k1, k2)

    def test_differs_on_python_version(self):
        k1 = cache_key("nextmv==1.0.0", "3.11", "aarch64-unknown-linux-gnu")
        k2 = cache_key("nextmv==1.0.0", "3.12", "aarch64-unknown-linux-gnu")
        self.assertNotEqual(k1, k2)

    def test_differs_on_platform(self):
        k1 = cache_key("nextmv==1.0.0", "3.11", "aarch64-unknown-linux-gnu")
        k2 = cache_key("nextmv==1.0.0", "3.11", "x86_64-unknown-linux-gnu")
        self.assertNotEqual(k1, k2)

    def test_returns_hex_string(self):
        k = cache_key("lock", "3.11", "aarch64-unknown-linux-gnu")
        self.assertEqual(len(k), 64)
        int(k, 16)  # raises if not valid hex


class TestGetCachedDeps(unittest.TestCase):
    def setUp(self):
        self._original_deps_dir = _DEPS_CACHE_DIR
        self._tmpdir = tempfile.mkdtemp()
        self._patch = patch("nextmv.cache._DEPS_CACHE_DIR", Path(self._tmpdir))
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_miss_returns_none(self):
        result = get_cached_deps("nonexistent-key")
        self.assertIsNone(result)

    def test_hit_returns_path(self):
        from nextmv import cache as cache_mod

        key = "abc123"
        deps_tar = Path(self._tmpdir) / key / "deps.tar.gz"
        deps_tar.parent.mkdir(parents=True)
        with tarfile.open(str(deps_tar), "w:gz"):
            pass  # empty tar
        info_file = Path(self._tmpdir) / key / _CACHE_INFO_FILE
        now = datetime.now(tz=timezone.utc).isoformat()
        with open(info_file, "w") as f:
            json.dump(
                {"created_at": now, "last_used_at": now, "python_version": "3.11", "platform": "p", "lockfile": ""}, f
            )

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", Path(self._tmpdir)):
            result = get_cached_deps(key)

        self.assertIsNotNone(result)
        self.assertTrue(str(result).endswith("deps.tar.gz"))

    def test_hit_updates_last_used_at(self):
        from nextmv import cache as cache_mod

        key = "upd456"
        deps_tar = Path(self._tmpdir) / key / "deps.tar.gz"
        deps_tar.parent.mkdir(parents=True)
        with tarfile.open(str(deps_tar), "w:gz"):
            pass  # empty tar
        info_file = Path(self._tmpdir) / key / _CACHE_INFO_FILE
        old_time = "2020-01-01T00:00:00+00:00"
        with open(info_file, "w") as f:
            json.dump(
                {
                    "created_at": old_time,
                    "last_used_at": old_time,
                    "python_version": "3.11",
                    "platform": "p",
                    "lockfile": "",
                },
                f,
            )

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", Path(self._tmpdir)):
            get_cached_deps(key)

        with open(info_file) as f:
            updated = json.load(f)

        self.assertNotEqual(updated["last_used_at"], old_time)
        self.assertEqual(updated["created_at"], old_time)  # created_at unchanged

    def test_missing_info_file_returns_none(self):
        from nextmv import cache as cache_mod

        key = "noinfo"
        deps_tar = Path(self._tmpdir) / key / "deps.tar.gz"
        deps_tar.parent.mkdir(parents=True)
        with tarfile.open(str(deps_tar), "w:gz"):
            pass  # empty tar, no cache_info.json written

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", Path(self._tmpdir)):
            result = get_cached_deps(key)

        self.assertIsNone(result)


class TestStoreDeps(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._cache_root = Path(tempfile.mkdtemp())
        self._patcher_cache = patch("nextmv.cache._CACHE_DIR", self._cache_root)
        self._patcher_deps = patch("nextmv.cache._DEPS_CACHE_DIR", self._cache_root / "deps")
        self._patcher_cache.start()
        self._patcher_deps.start()

    def tearDown(self):
        self._patcher_cache.stop()
        self._patcher_deps.stop()
        shutil.rmtree(self._tmpdir, ignore_errors=True)
        shutil.rmtree(str(self._cache_root), ignore_errors=True)

    def _make_installed_dir(self) -> Path:
        installed = Path(self._tmpdir) / "installed" / "deps"
        installed.mkdir(parents=True)
        (installed / "somepackage.py").write_text("# package")
        return installed

    def test_creates_entry_directory(self):
        from nextmv import cache as cache_mod

        installed = self._make_installed_dir()
        key = cache_key("lockfile", "3.11", "aarch64-unknown-linux-gnu")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._cache_root / "deps"),
        ):
            store_deps(
                key,
                installed,
                "3.11",
                "aarch64-unknown-linux-gnu",
                "lockfile",
                max_entries=200,
                max_bytes=_DEFAULT_MAX_BYTES,
            )

        entry_dir = self._cache_root / "deps" / key
        self.assertTrue(entry_dir.is_dir())

    def test_cache_info_has_required_fields(self):
        from nextmv import cache as cache_mod

        installed = self._make_installed_dir()
        key = cache_key("lockfile", "3.11", "aarch64-unknown-linux-gnu")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._cache_root / "deps"),
        ):
            store_deps(
                key,
                installed,
                "3.11",
                "aarch64-unknown-linux-gnu",
                "lockfile",
                max_entries=200,
                max_bytes=_DEFAULT_MAX_BYTES,
            )

        info_file = self._cache_root / "deps" / key / _CACHE_INFO_FILE
        with open(info_file) as f:
            info = json.load(f)

        self.assertIn("created_at", info)
        self.assertIn("last_used_at", info)
        self.assertEqual(info["created_at"], info["last_used_at"])
        self.assertEqual(info["python_version"], "3.11")
        self.assertEqual(info["platform"], "aarch64-unknown-linux-gnu")
        self.assertEqual(info["lockfile"], "lockfile")

    def test_deps_are_copied(self):
        from nextmv import cache as cache_mod

        installed = self._make_installed_dir()
        key = cache_key("lockfile2", "3.11", "aarch64-unknown-linux-gnu")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._cache_root / "deps"),
        ):
            store_deps(
                key,
                installed,
                "3.11",
                "aarch64-unknown-linux-gnu",
                "lockfile2",
                max_entries=200,
                max_bytes=_DEFAULT_MAX_BYTES,
            )

        deps_tar = self._cache_root / "deps" / key / "deps.tar.gz"
        self.assertTrue(deps_tar.is_file())
        with tarfile.open(str(deps_tar), "r:gz") as tar:
            names = tar.getnames()
        self.assertIn(".nextmv/python/deps/somepackage.py", names)


class TestEvictLru(unittest.TestCase):
    def setUp(self):
        self._cache_root = Path(tempfile.mkdtemp())
        self._deps_dir = self._cache_root / "deps"
        self._deps_dir.mkdir(parents=True)
        self._patcher = patch("nextmv.cache._DEPS_CACHE_DIR", self._deps_dir)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        shutil.rmtree(str(self._cache_root), ignore_errors=True)

    def _add_entry(self, key: str, last_used: str, size_bytes: int = 0):
        entry_dir = self._deps_dir / key
        entry_dir.mkdir(parents=True, exist_ok=True)
        deps_tar = entry_dir / "deps.tar.gz"
        with tarfile.open(str(deps_tar), "w:gz") as tar:
            if size_bytes > 0:
                # Use incompressible random data so gzip cannot shrink it.
                data = os.urandom(size_bytes)
                info = tarfile.TarInfo(name=".nextmv/python/deps/dummy.bin")
                info.size = size_bytes
                tar.addfile(info, io.BytesIO(data))
        info = {
            "created_at": last_used,
            "last_used_at": last_used,
            "python_version": "3.11",
            "platform": "p",
            "lockfile": "",
        }
        with open(entry_dir / _CACHE_INFO_FILE, "w") as f:
            json.dump(info, f)

    def test_no_eviction_under_caps(self):
        from nextmv import cache as cache_mod

        self._add_entry("k1", "2026-01-01T00:00:00+00:00")
        self._add_entry("k2", "2026-01-02T00:00:00+00:00")

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._deps_dir):
            evicted = _evict_lru(max_entries=10, max_bytes=_DEFAULT_MAX_BYTES)

        self.assertEqual(evicted, 0)
        self.assertTrue((self._deps_dir / "k1").exists())
        self.assertTrue((self._deps_dir / "k2").exists())

    def test_evicts_oldest_by_last_used(self):
        from nextmv import cache as cache_mod

        self._add_entry("oldest", "2025-01-01T00:00:00+00:00")
        self._add_entry("middle", "2025-06-01T00:00:00+00:00")
        self._add_entry("newest", "2026-01-01T00:00:00+00:00")

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._deps_dir):
            evicted = _evict_lru(max_entries=2, max_bytes=_DEFAULT_MAX_BYTES)

        self.assertEqual(evicted, 1)
        self.assertFalse((self._deps_dir / "oldest").exists())
        self.assertTrue((self._deps_dir / "middle").exists())
        self.assertTrue((self._deps_dir / "newest").exists())

    def test_evicts_by_size_cap(self):
        from nextmv import cache as cache_mod

        # Each deps.tar.gz holds ~10 KiB of random (incompressible) data.
        # Use a cap that sits between one and two entries so exactly the oldest
        # is evicted.
        self._add_entry("big_old", "2025-01-01T00:00:00+00:00", size_bytes=10 * 1024)
        self._add_entry("big_new", "2026-01-01T00:00:00+00:00", size_bytes=10 * 1024)

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._deps_dir):
            evicted = _evict_lru(max_entries=200, max_bytes=15 * 1024)

        self.assertEqual(evicted, 1)
        self.assertFalse((self._deps_dir / "big_old").exists())
        self.assertTrue((self._deps_dir / "big_new").exists())

    def test_returns_zero_when_cache_missing(self):
        from nextmv import cache as cache_mod

        missing = self._cache_root / "nonexistent"
        with patch.object(cache_mod, "_DEPS_CACHE_DIR", missing):
            evicted = _evict_lru(max_entries=10, max_bytes=_DEFAULT_MAX_BYTES)

        self.assertEqual(evicted, 0)


class TestClearCache(unittest.TestCase):
    def setUp(self):
        self._cache_root = Path(tempfile.mkdtemp())
        self._deps_dir = self._cache_root / "deps"
        self._patcher_cache = patch("nextmv.cache._CACHE_DIR", self._cache_root)
        self._patcher_deps = patch("nextmv.cache._DEPS_CACHE_DIR", self._deps_dir)
        self._patcher_cache.start()
        self._patcher_deps.start()

    def tearDown(self):
        self._patcher_cache.stop()
        self._patcher_deps.stop()
        shutil.rmtree(str(self._cache_root), ignore_errors=True)

    def test_wipes_and_recreates(self):
        from nextmv import cache as cache_mod

        # Populate the cache dir with some content.
        leftover = self._cache_root / "somedata.txt"
        leftover.write_text("data")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._deps_dir),
        ):
            clear_cache()

        self.assertTrue(self._cache_root.exists())
        self.assertFalse(leftover.exists())
        self.assertTrue(self._deps_dir.exists())  # recreated by create_cache()

    def test_idempotent_when_already_empty(self):
        from nextmv import cache as cache_mod

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._deps_dir),
        ):
            clear_cache()
            clear_cache()  # second call should not raise

        self.assertTrue(self._cache_root.exists())


if __name__ == "__main__":
    unittest.main()
