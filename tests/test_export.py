"""Exercise the CLI in isolated repository copies using the standard library."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
NAMES = {"generated-export.json", "generated-provenance.json",
         "generated-coverage.json"}


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        shutil.copytree(ROOT / "exporter", self.root / "exporter",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "export.py", self.root / "export.py")
        self.config_path = self.root / "exporter" / "config.json"

    def run_export(self, script, cwd=None):
        return subprocess.run(
            [sys.executable, str(self.root / script)],
            cwd=cwd or self.temp.name, capture_output=True, text=True,
        )

    def read_outputs(self):
        return {path.name: path.read_bytes()
                for path in (self.root / "examples").iterdir()}

    def test_entry_points_repeatability_and_integrity(self):
        result = self.run_export("exporter/export.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        first = self.read_outputs()
        self.assertEqual(set(first), NAMES)
        provenance = json.loads(first["generated-provenance.json"])
        self.assertEqual(provenance["sha256"], hashlib.sha256(
            first["generated-export.json"]).hexdigest())
        self.assertFalse(provenance["liveExtractionPerformed"])
        coverage = json.loads(first["generated-coverage.json"])
        record = json.loads(first["generated-export.json"])
        self.assertEqual(coverage["counts"]["relationships"], len(record["links"]))
        self.assertIsNone(record["approvals"][0]["approvalChangeTime"])
        self.assertEqual(coverage["coverage"]["approvalTiming"], "unavailable")
        for script, cwd in (("export.py", self.root),
                            ("exporter/export.py", self.root / "exporter")):
            with self.subTest(script=script):
                result = self.run_export(script, cwd)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(first, self.read_outputs())

    def test_configuration_propagates(self):
        config = {"sourceInstance": "test-instance", "projectId": "OTHER",
                  "exportTime": "2026-11-27T09:00:00+02:00"}
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        result = self.run_export("exporter/export.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        outputs = self.read_outputs()
        for name, content in outputs.items():
            with self.subTest(name=name):
                artifact = json.loads(content)
                self.assertEqual(artifact["sourceInstance"], config["sourceInstance"])
                self.assertEqual(artifact["projectId"], config["projectId"])
                self.assertEqual(artifact["extractionTime"], config["exportTime"])
                self.assertEqual(artifact["dataOrigin"], "synthetic")
        record = json.loads(outputs["generated-export.json"])
        self.assertEqual(record["links"][0]["targetProject"], "OTHER")

    def test_invalid_config_fails_before_writing(self):
        valid = json.loads(self.config_path.read_text(encoding="utf-8"))
        invalid = ["{", "[]", "{}"]
        for key in valid:
            for value in (None, "", "   ", 123):
                invalid.append(json.dumps({**valid, key: value}))
        for timestamp in ("yesterday", "2026-11-27", "2026-11-27T09:00:00"):
            invalid.append(json.dumps({**valid, "exportTime": timestamp}))
        for content in invalid:
            with self.subTest(content=content):
                self.config_path.write_text(content, encoding="utf-8")
                result = self.run_export("exporter/export.py")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Export failed:", result.stderr)
                self.assertFalse((self.root / "examples").exists())

    def test_preserves_reference_and_previous_outputs(self):
        examples = self.root / "examples"
        examples.mkdir()
        reference = examples / "sample-export.json"
        reference.write_bytes(b"reference sample\n")
        result = self.run_export("exporter/export.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(reference.read_bytes(), b"reference sample\n")
        self.config_path.unlink()
        before = self.read_outputs()
        result = self.run_export("exporter/export.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, self.read_outputs())


if __name__ == "__main__":
    unittest.main()
