"""Tests for the nextmv.cache module."""

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
    _DEP_TARBALL_NAME,
    _MAX_DEP_BYTES,
    _MAX_DEPS,
    _evict_lru,
    clear_cache,
    dep_cache_key,
    get_cached_dep,
    store_dep,
)


class TestClearCache(unittest.TestCase):
    def setUp(self):
        self._cache_root = Path(tempfile.mkdtemp())
        self._pkg_tars_dir = self._cache_root / "pkg_tars"
        self._patcher_cache = patch("nextmv.cache._CACHE_DIR", self._cache_root)
        self._patcher_pkg = patch("nextmv.cache._DEPS_CACHE_DIR", self._pkg_tars_dir)
        self._patcher_cache.start()
        self._patcher_pkg.start()

    def tearDown(self):
        self._patcher_cache.stop()
        self._patcher_pkg.stop()
        shutil.rmtree(str(self._cache_root), ignore_errors=True)

    def test_wipes_and_recreates(self):
        from nextmv import cache as cache_mod

        # Populate the cache dir with some content.
        leftover = self._cache_root / "somedata.txt"
        leftover.write_text("data")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir),
        ):
            clear_cache()

        self.assertTrue(self._cache_root.exists())
        self.assertFalse(leftover.exists())
        self.assertTrue(self._pkg_tars_dir.exists())  # recreated by _create_cache()

    def test_idempotent_when_already_empty(self):
        from nextmv import cache as cache_mod

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir),
        ):
            clear_cache()
            clear_cache()  # second call should not raise

        self.assertTrue(self._cache_root.exists())


class TestPackageCacheKey(unittest.TestCase):
    def test_stable(self):
        k1 = dep_cache_key("pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        k2 = dep_cache_key("pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        self.assertEqual(k1, k2)

    def test_normalises_hyphens_and_underscores(self):
        k1 = dep_cache_key("pydantic-core", "2.23.4", "3.11", "aarch64-unknown-linux-gnu")
        k2 = dep_cache_key("pydantic_core", "2.23.4", "3.11", "aarch64-unknown-linux-gnu")
        self.assertEqual(k1, k2)

    def test_normalises_dots(self):
        k1 = dep_cache_key("some.pkg", "1.0.0", "3.11", "aarch64-unknown-linux-gnu")
        k2 = dep_cache_key("some_pkg", "1.0.0", "3.11", "aarch64-unknown-linux-gnu")
        self.assertEqual(k1, k2)

    def test_case_insensitive(self):
        k1 = dep_cache_key("Pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        k2 = dep_cache_key("pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        self.assertEqual(k1, k2)

    def test_differs_on_version(self):
        k1 = dep_cache_key("pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        k2 = dep_cache_key("pydantic", "2.9.3", "3.11", "aarch64-unknown-linux-gnu")
        self.assertNotEqual(k1, k2)

    def test_differs_on_python_version(self):
        k1 = dep_cache_key("pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        k2 = dep_cache_key("pydantic", "2.9.2", "3.12", "aarch64-unknown-linux-gnu")
        self.assertNotEqual(k1, k2)

    def test_differs_on_platform(self):
        k1 = dep_cache_key("pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        k2 = dep_cache_key("pydantic", "2.9.2", "3.11", "x86_64-unknown-linux-gnu")
        self.assertNotEqual(k1, k2)

    def test_returns_hex_string(self):
        k = dep_cache_key("pydantic", "2.9.2", "3.11", "aarch64-unknown-linux-gnu")
        self.assertEqual(len(k), 64)
        int(k, 16)


class TestGetCachedPackageTar(unittest.TestCase):
    def setUp(self):
        self._tmpdir = Path(tempfile.mkdtemp())
        self._patch = patch("nextmv.cache._DEPS_CACHE_DIR", self._tmpdir)
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        shutil.rmtree(str(self._tmpdir), ignore_errors=True)

    def _make_pkg_tar_entry(self, key: str) -> Path:
        entry_dir = self._tmpdir / key
        entry_dir.mkdir(parents=True, exist_ok=True)
        installed_tar = entry_dir / _DEP_TARBALL_NAME
        with tarfile.open(str(installed_tar), "w:gz"):
            pass  # empty tar
        now = datetime.now(tz=timezone.utc).isoformat()
        info = {
            "created_at": now,
            "last_used_at": now,
            "python_version": "3.11",
            "platform": "aarch64-unknown-linux-gnu",
        }
        with open(entry_dir / _CACHE_INFO_FILE, "w") as f:
            json.dump(info, f)
        return installed_tar

    def test_miss_returns_none(self):
        from nextmv import cache as cache_mod

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._tmpdir):
            result = get_cached_dep("nonexistent-key")
        self.assertIsNone(result)

    def test_hit_returns_path(self):
        from nextmv import cache as cache_mod

        key = "abc123"
        self._make_pkg_tar_entry(key)

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._tmpdir):
            result = get_cached_dep(key)

        self.assertIsNotNone(result)
        self.assertTrue(str(result).endswith(_DEP_TARBALL_NAME))

    def test_hit_updates_last_used_at(self):
        from nextmv import cache as cache_mod

        key = "upd456"
        installed_tar = self._make_pkg_tar_entry(key)
        info_file = installed_tar.parent / _CACHE_INFO_FILE
        old_time = "2020-01-01T00:00:00+00:00"
        with open(info_file) as f:
            info = json.load(f)
        info["last_used_at"] = old_time
        with open(info_file, "w") as f:
            json.dump(info, f)

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._tmpdir):
            get_cached_dep(key)

        with open(info_file) as f:
            updated = json.load(f)

        self.assertNotEqual(updated["last_used_at"], old_time)
        self.assertEqual(updated["created_at"], info["created_at"])

    def test_missing_info_file_returns_none(self):
        from nextmv import cache as cache_mod

        key = "noinfo"
        entry_dir = self._tmpdir / key
        entry_dir.mkdir(parents=True)
        with tarfile.open(str(entry_dir / _DEP_TARBALL_NAME), "w:gz"):
            pass  # no cache_info.json written

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._tmpdir):
            result = get_cached_dep(key)

        self.assertIsNone(result)

    def test_missing_installed_tar_returns_none(self):
        from nextmv import cache as cache_mod

        key = "notar"
        entry_dir = self._tmpdir / key
        entry_dir.mkdir(parents=True)
        now = datetime.now(tz=timezone.utc).isoformat()
        with open(entry_dir / _CACHE_INFO_FILE, "w") as f:
            json.dump({"created_at": now, "last_used_at": now, "python_version": "3.11", "platform": "p"}, f)
        # No installed.tar.gz written.

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._tmpdir):
            result = get_cached_dep(key)

        self.assertIsNone(result)


class TestStorePackageTar(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._cache_root = Path(tempfile.mkdtemp())
        self._pkg_tars_dir = self._cache_root / "pkg_tars"
        self._patcher_cache = patch("nextmv.cache._CACHE_DIR", self._cache_root)
        self._patcher_pkg = patch("nextmv.cache._DEPS_CACHE_DIR", self._pkg_tars_dir)
        self._patcher_cache.start()
        self._patcher_pkg.start()

    def tearDown(self):
        self._patcher_cache.stop()
        self._patcher_pkg.stop()
        shutil.rmtree(self._tmpdir, ignore_errors=True)
        shutil.rmtree(str(self._cache_root), ignore_errors=True)

    def _make_installed_tar(self, name: str = "pkg-1.0.0.tar.gz") -> Path:
        p = Path(self._tmpdir) / name
        with tarfile.open(str(p), "w:gz"):
            pass  # empty tar
        return p

    def test_creates_entry(self):
        from nextmv import cache as cache_mod

        tar = self._make_installed_tar()
        key = dep_cache_key("pkg", "1.0.0", "3.11", "aarch64-unknown-linux-gnu")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir),
        ):
            store_dep(
                key,
                tar,
                "pkg",
                "1.0.0",
                "3.11",
                "aarch64-unknown-linux-gnu",
                max_entries=_MAX_DEPS,
                max_bytes=_MAX_DEP_BYTES,
            )

        entry_dir = self._pkg_tars_dir / key
        self.assertTrue(entry_dir.is_dir())
        self.assertTrue((entry_dir / _DEP_TARBALL_NAME).is_file())

    def test_info_file_has_required_fields(self):
        from nextmv import cache as cache_mod

        tar = self._make_installed_tar()
        key = dep_cache_key("pkg", "1.0.0", "3.11", "aarch64-unknown-linux-gnu")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir),
        ):
            store_dep(
                key,
                tar,
                "pkg",
                "1.0.0",
                "3.11",
                "aarch64-unknown-linux-gnu",
                max_entries=_MAX_DEPS,
                max_bytes=_MAX_DEP_BYTES,
            )

        info_file = self._pkg_tars_dir / key / _CACHE_INFO_FILE
        with open(info_file) as f:
            info = json.load(f)

        self.assertIn("created_at", info)
        self.assertIn("last_used_at", info)
        self.assertEqual(info["python_version"], "3.11")
        self.assertEqual(info["platform"], "aarch64-unknown-linux-gnu")
        self.assertNotIn("wheel_file", info)  # no wheel_file key in new format

    def test_idempotent_on_duplicate_key(self):
        from nextmv import cache as cache_mod

        tar = self._make_installed_tar()
        key = dep_cache_key("pkg", "1.0.0", "3.11", "aarch64-unknown-linux-gnu")

        with (
            patch.object(cache_mod, "_CACHE_DIR", self._cache_root),
            patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir),
        ):
            store_dep(
                key,
                tar,
                "pkg",
                "1.0.0",
                "3.11",
                "aarch64-unknown-linux-gnu",
                max_entries=_MAX_DEPS,
                max_bytes=_MAX_DEP_BYTES,
            )
            store_dep(
                key,
                tar,
                "pkg",
                "1.0.0",
                "3.11",
                "aarch64-unknown-linux-gnu",
                max_entries=_MAX_DEPS,
                max_bytes=_MAX_DEP_BYTES,
            )

        entries = [d for d in self._pkg_tars_dir.iterdir() if d.is_dir()]
        self.assertEqual(len(entries), 1)


class TestEvictLruPackages(unittest.TestCase):
    def setUp(self):
        self._cache_root = Path(tempfile.mkdtemp())
        self._pkg_tars_dir = self._cache_root / "pkg_tars"
        self._pkg_tars_dir.mkdir(parents=True)
        self._patcher = patch("nextmv.cache._DEPS_CACHE_DIR", self._pkg_tars_dir)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        shutil.rmtree(str(self._cache_root), ignore_errors=True)

    def _add_entry(self, key: str, last_used: str, size_bytes: int = 0):
        entry_dir = self._pkg_tars_dir / key
        entry_dir.mkdir(parents=True, exist_ok=True)
        installed_tar = entry_dir / _DEP_TARBALL_NAME
        if size_bytes > 0:
            data = os.urandom(size_bytes)
            with tarfile.open(str(installed_tar), "w:gz") as tar:
                info = tarfile.TarInfo(name=".nextmv/python/deps/dummy.bin")
                info.size = size_bytes
                import io as _io

                tar.addfile(info, _io.BytesIO(data))
        else:
            with tarfile.open(str(installed_tar), "w:gz"):
                pass
        info = {
            "created_at": last_used,
            "last_used_at": last_used,
            "python_version": "3.11",
            "platform": "p",
        }
        with open(entry_dir / _CACHE_INFO_FILE, "w") as f:
            json.dump(info, f)

    def test_no_eviction_under_caps(self):
        from nextmv import cache as cache_mod

        self._add_entry("k1", "2026-01-01T00:00:00+00:00")
        self._add_entry("k2", "2026-01-02T00:00:00+00:00")

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir):
            evicted = _evict_lru(max_entries=10, max_bytes=_MAX_DEP_BYTES)

        self.assertEqual(evicted, 0)
        self.assertTrue((self._pkg_tars_dir / "k1").exists())
        self.assertTrue((self._pkg_tars_dir / "k2").exists())

    def test_evicts_oldest_first(self):
        from nextmv import cache as cache_mod

        self._add_entry("oldest", "2025-01-01T00:00:00+00:00")
        self._add_entry("middle", "2025-06-01T00:00:00+00:00")
        self._add_entry("newest", "2026-01-01T00:00:00+00:00")

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir):
            evicted = _evict_lru(max_entries=2, max_bytes=_MAX_DEP_BYTES)

        self.assertEqual(evicted, 1)
        self.assertFalse((self._pkg_tars_dir / "oldest").exists())
        self.assertTrue((self._pkg_tars_dir / "middle").exists())
        self.assertTrue((self._pkg_tars_dir / "newest").exists())

    def test_evicts_by_size_cap(self):
        from nextmv import cache as cache_mod

        self._add_entry("big_old", "2025-01-01T00:00:00+00:00", size_bytes=10 * 1024)
        self._add_entry("big_new", "2026-01-01T00:00:00+00:00", size_bytes=10 * 1024)

        with patch.object(cache_mod, "_DEPS_CACHE_DIR", self._pkg_tars_dir):
            evicted = _evict_lru(max_entries=200, max_bytes=15 * 1024)

        self.assertEqual(evicted, 1)
        self.assertFalse((self._pkg_tars_dir / "big_old").exists())
        self.assertTrue((self._pkg_tars_dir / "big_new").exists())

    def test_returns_zero_when_cache_missing(self):
        from nextmv import cache as cache_mod

        missing = self._cache_root / "nonexistent"
        with patch.object(cache_mod, "_DEPS_CACHE_DIR", missing):
            evicted = _evict_lru(max_entries=10, max_bytes=_MAX_DEP_BYTES)

        self.assertEqual(evicted, 0)


if __name__ == "__main__":
    unittest.main()
