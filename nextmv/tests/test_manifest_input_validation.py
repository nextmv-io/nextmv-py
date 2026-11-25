import os
import tempfile
import unittest

from nextmv.cloud.application import _convert_manifest_to_payload
from nextmv.manifest import (
    MANIFEST_FILE_NAME,
    Manifest,
    ManifestContent,
    ManifestInputValidation,
    ManifestInputValidationEnforce,
)
from pydantic import ValidationError

APP_YAML = """\
type: python
runtime: ghcr.io/nextmv-io/runtime/python:3.11
files:
  - main.py
configuration:
  content:
    format: multi-file
    validation:
      enforce: block
      max_findings: 50
      sources:
        stops:
          file: input.xlsx
          sheet: stops
          columns:
            lon: { required: true, type: number, range: [-180, 180] }
        starting-locations:
          file: input.xlsx
          sheet: starting-locations
      rules:
        - name: vehicle-has-start-location
          in: stops
          column: vehicle id
          where: { column: status, not_equals: unassigned }
          exists_in: { in: starting-locations, column: 1 }
"""


class TestManifestInputValidation(unittest.TestCase):
    def test_defaults(self):
        validation = ManifestInputValidation()
        self.assertEqual(validation.enforce, ManifestInputValidationEnforce.WARN)
        self.assertIsNone(validation.max_findings)
        self.assertIsNone(validation.sources)
        self.assertIsNone(validation.rules)

    def test_content_without_validation(self):
        content = ManifestContent.from_dict({"format": "json"})
        self.assertIsNone(content.validation)
        self.assertNotIn("validation", content.to_dict())

    def test_from_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, MANIFEST_FILE_NAME), "w") as f:
                f.write(APP_YAML)
            manifest = Manifest.from_yaml(tmp)

        validation = manifest.configuration.content.validation
        self.assertIsInstance(validation, ManifestInputValidation)
        self.assertEqual(validation.enforce, ManifestInputValidationEnforce.BLOCK)
        self.assertEqual(validation.max_findings, 50)
        self.assertEqual(validation.sources["stops"]["columns"]["lon"]["range"], [-180, 180])
        self.assertEqual(validation.rules[0]["exists_in"], {"in": "starting-locations", "column": 1})

    def test_yaml_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, MANIFEST_FILE_NAME), "w") as f:
                f.write(APP_YAML)
            original = Manifest.from_yaml(tmp)

            out = os.path.join(tmp, "out")
            os.makedirs(out)
            original.to_yaml(out)
            reloaded = Manifest.from_yaml(out)

        self.assertEqual(
            original.configuration.content.validation.to_dict(),
            reloaded.configuration.content.validation.to_dict(),
        )

    def test_unknown_keys_are_kept(self):
        validation = ManifestInputValidation.from_dict(
            {"enforce": "warn", "future_key": {"a": 1}, "rules": [{"name": "r", "future_check": True}]}
        )
        data = validation.to_dict()
        self.assertEqual(data["future_key"], {"a": 1})
        self.assertTrue(data["rules"][0]["future_check"])

    def test_invalid_enforce(self):
        with self.assertRaises(ValidationError):
            ManifestInputValidation.from_dict({"enforce": "all"})

    def test_invalid_max_findings(self):
        with self.assertRaises(ValidationError):
            ManifestInputValidation.from_dict({"max_findings": 0})

    def test_rule_without_name(self):
        with self.assertRaises(ValidationError) as ctx:
            ManifestInputValidation.from_dict({"rules": [{"path": ".a", "required": True}]})
        self.assertIn("index 0", str(ctx.exception))

    def test_rule_with_empty_name(self):
        with self.assertRaises(ValidationError):
            ManifestInputValidation.from_dict({"rules": [{"name": "  ", "required": True}]})

    def test_duplicate_rule_names(self):
        with self.assertRaises(ValidationError) as ctx:
            ManifestInputValidation.from_dict({"rules": [{"name": "a"}, {"name": "a"}]})
        self.assertIn("Duplicate", str(ctx.exception))


class TestInputValidationPayload(unittest.TestCase):
    def test_payload_contains_input_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, MANIFEST_FILE_NAME), "w") as f:
                f.write(APP_YAML)
            manifest = Manifest.from_yaml(tmp)

        payload = _convert_manifest_to_payload(manifest=manifest)
        input_validation = payload["requirements"]["io_configuration"]["input_validation"]

        self.assertEqual(input_validation["enforce"], "block")
        self.assertEqual(input_validation["max_findings"], 50)
        self.assertIn("stops", input_validation["sources"])
        self.assertEqual(input_validation["rules"][0]["name"], "vehicle-has-start-location")

    def test_payload_without_input_validation(self):
        manifest = Manifest.from_dict(
            {
                "type": "python",
                "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
                "files": ["main.py"],
                "configuration": {"content": {"format": "json"}},
            }
        )
        payload = _convert_manifest_to_payload(manifest=manifest)
        self.assertNotIn("input_validation", payload["requirements"]["io_configuration"])


if __name__ == "__main__":
    unittest.main()
