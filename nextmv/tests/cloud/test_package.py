import os
import shutil
import tempfile
import unittest

from nextmv.cloud.package import _package
from nextmv.manifest import Manifest, ManifestType


class TestPackageOneFile(unittest.TestCase):
    def setUp(self):
        self.app_dir = tempfile.mkdtemp()
        self.manifest = Manifest(type=ManifestType.PYTHON, files=["main.py"], python=None)
        with open(os.path.join(self.app_dir, "main.py"), "w") as f:
            f.write("print('Hello, World!')")

    def tearDown(self):
        shutil.rmtree(self.app_dir)

    def test_package_creates_tarball(self):
        tar_file, output_dir = _package(self.app_dir, self.manifest, verbose=False)
        self.assertTrue(os.path.isfile(tar_file))
        self.assertTrue(os.path.isdir(output_dir))

    def test_package_missing_files(self):
        self.manifest.files.append("missing_file.py")
        with self.assertRaises(Exception) as context:
            _package(self.app_dir, self.manifest, verbose=False)
        self.assertIn("could not find files listed in manifest", str(context.exception))

    def test_package_mandatory_files(self):
        self.manifest.type = ManifestType.GO
        with self.assertRaises(Exception) as context:
            _package(self.app_dir, self.manifest, verbose=False)
        self.assertIn("missing mandatory files", str(context.exception))


class TestPackageDir(unittest.TestCase):
    def setUp(self):
        self.app_dir = tempfile.mkdtemp()
        self.manifest = Manifest(type=ManifestType.PYTHON, files=["main.py", "app/"], python=None)
        with open(os.path.join(self.app_dir, "main.py"), "w") as f:
            f.write("print('Hello, World!')")

        os.makedirs(os.path.join(self.app_dir, "app"))
        with open(os.path.join(self.app_dir, "app", "main.py"), "w") as f:
            f.write("print('Hello, World!')")

    def tearDown(self):
        shutil.rmtree(self.app_dir)

    def test_package_creates_tarball(self):
        tar_file, output_dir = _package(self.app_dir, self.manifest, verbose=False)
        self.assertTrue(os.path.isfile(tar_file))
        self.assertTrue(os.path.isdir(output_dir))

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.unpack_archive(tar_file, tmpdir)
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, "main.py")))
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, "app")))
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, "app", "main.py")))

    def test_package_missing_files(self):
        self.manifest.files.append("missing_file.py")
        with self.assertRaises(Exception) as context:
            _package(self.app_dir, self.manifest, verbose=False)
        self.assertIn("could not find files listed in manifest", str(context.exception))

    def test_package_mandatory_files(self):
        self.manifest.type = ManifestType.GO
        with self.assertRaises(Exception) as context:
            _package(self.app_dir, self.manifest, verbose=False)
        self.assertIn("missing mandatory files", str(context.exception))
