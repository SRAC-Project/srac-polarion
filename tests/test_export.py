"""CLI and consumer validation against isolated copies of the repository."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from exporter.bundle import validate_bundle, validate_current
from exporter.contract import validate_documents
from exporter.export import generate, read_config

ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        for name in ("exporter", "schemas"):
            shutil.copytree(ROOT / name, self.root / name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "export.py", self.root / "export.py")
        self.config_path = self.root / "exporter" / "config.json"

    def run_export(self, script="exporter/export.py", cwd=None, args=()):
        return subprocess.run([sys.executable, str(self.root / script), *args],
                              cwd=cwd or self.temp.name, capture_output=True, text=True)

    def test_launch_commands_and_validation_from_different_directories(self):
        run_ids = set()
        for script, cwd in (("exporter/export.py", self.temp.name),
                            ("export.py", self.root),
                            ("exporter/export.py", self.root / "exporter")):
            result = self.run_export(script, cwd)
            self.assertEqual(result.returncode, 0, result.stderr)
            checked = validate_current(self.root / "examples")
            run_ids.add(checked["manifest"]["runId"])
            validation = self.run_export(script, cwd, ("--validate",))
            self.assertEqual(validation.returncode, 0, validation.stderr)
        self.assertEqual(len(run_ids), 3)
        self.assertFalse((self.root / "examples" / "generated-export.json").exists())

    def test_metadata_and_config_validation(self):
        config = {"sourceInstance": "test", "projectId": "OTHER",
                  "exportTime": "2026-11-27T09:00:00+02:00"}
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        documents = generate(read_config(self.config_path))
        for document in documents.values():
            self.assertEqual(document["sourceInstance"], "test")
            self.assertEqual(document["projectId"], "OTHER")
            self.assertEqual(document["extractionTime"], config["exportTime"])
            self.assertFalse(document["liveExtractionPerformed"])
        self.assertEqual(documents["generated-export.json"]["links"][0]["targetProject"], "OTHER")
        for invalid in ("{", "[]", "{}", json.dumps({**config, "exportTime": "2026-11-27"}),
                        json.dumps({**config, "exportTime": "2026-11-27T09:00:00"}),
                        json.dumps({**config, "projectId": None})):
            self.config_path.write_text(invalid, encoding="utf-8")
            result = self.run_export()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Export failed:", result.stderr)
            self.assertFalse((self.root / "examples").exists())

    def test_contract_rejects_unknown_versions_extra_fields_and_overclaims(self):
        documents = generate(read_config(ROOT / "exporter" / "config.json"))
        mutations = [
            ("generated-export.json", "formatVersion", "99.0"),
            ("generated-export.json", "sracVersion", "0.1"),
            ("generated-provenance.json", "retrievalMethod", "REST + SOAP"),
            ("generated-coverage.json", "runId", "wrong-run"),
        ]
        for name, key, value in mutations:
            changed = copy.deepcopy(documents)
            changed[name][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_documents(changed)
        changed = copy.deepcopy(documents)
        changed["generated-coverage.json"]["coverage"]["history"] = "complete"
        with self.assertRaisesRegex(ValueError, "overstates"):
            validate_documents(changed)

    def test_reference_artifact_is_not_modified(self):
        examples = self.root / "examples"
        examples.mkdir()
        reference = examples / "sample-export.json"
        reference.write_bytes(b"reference\n")
        self.assertEqual(self.run_export().returncode, 0)
        self.assertEqual(reference.read_bytes(), b"reference\n")
        previous = (examples / "current-run.json").read_bytes()
        self.config_path.unlink()
        self.assertNotEqual(self.run_export().returncode, 0)
        self.assertEqual(previous, (examples / "current-run.json").read_bytes())

    def test_checked_in_bundle_and_reference_examples_match_contract(self):
        validate_current(ROOT / "examples")
        aliases = {"sample-export.json": "generated-export.json",
                   "coverage-report.json": "generated-coverage.json",
                   "provenance-report.json": "generated-provenance.json"}
        documents = {generated: json.loads((ROOT / "examples" / alias).read_bytes())
                     for alias, generated in aliases.items()}
        validate_documents(documents)
        reference_run = documents["generated-export.json"]["runId"]
        checked = validate_bundle(ROOT / "examples" / "runs" / reference_run)
        self.assertEqual(documents, checked["documents"])


if __name__ == "__main__":
    unittest.main()
