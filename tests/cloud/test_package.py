import os
import shutil
import tempfile
import unittest

from nextmv.cloud.manifest import Manifest, ManifestType
from nextmv.cloud.package import _package


class TestPackage(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
