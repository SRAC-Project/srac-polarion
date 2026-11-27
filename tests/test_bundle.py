"""Failure injection and tamper checks at the publication/consumption boundary."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from exporter import bundle
from exporter.contract import json_bytes
from exporter.export import generate

CONFIG = {"sourceInstance": "demo", "projectId": "DEMO", "exportTime": "2026-11-20T12:00:00Z"}


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / "examples"

    def test_every_write_failure_keeps_previous_completed_run(self):
        first = bundle.publish_bundle(self.base, generate(CONFIG))
        previous = (self.base / "current-run.json").read_bytes()
        real_write = bundle._write
        # Three evidence writes, manifest, and temporary pointer, including errors
        # after bytes reached disk. No mixed run can cross the pointer boundary.
        for target in range(1, 6):
            calls = 0
            def failing_write(path, content):
                nonlocal calls
                calls += 1
                real_write(path, content)
                if calls == target:
                    raise OSError("injected write failure")
            with self.subTest(target=target), patch.object(bundle, "_write", failing_write):
                with self.assertRaises(OSError):
                    bundle.publish_bundle(self.base, generate(CONFIG))
            self.assertEqual((self.base / "current-run.json").read_bytes(), previous)
            self.assertEqual(bundle.validate_current(self.base)["manifest"]["runId"], first.name)
            self.assertFalse(list(self.base.glob(".staging-*")))
            self.assertFalse(list(self.base.glob(".current-*")))

    def test_rename_failures_keep_previous_run(self):
        bundle.publish_bundle(self.base, generate(CONFIG))
        previous = (self.base / "current-run.json").read_bytes()
        for operation in ("rename", "replace"):
            with self.subTest(operation=operation), patch.object(bundle.os, operation, side_effect=OSError("injected rename failure")):
                with self.assertRaises(OSError):
                    bundle.publish_bundle(self.base, generate(CONFIG))
            self.assertEqual((self.base / "current-run.json").read_bytes(), previous)
            bundle.validate_current(self.base)

    def test_first_run_failure_has_no_completion_pointer(self):
        with patch.object(bundle, "_write", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                bundle.publish_bundle(self.base, generate(CONFIG))
        self.assertFalse((self.base / "current-run.json").exists())
        with self.assertRaises(OSError):
            bundle.validate_current(self.base)

    def test_existing_run_cannot_be_overwritten(self):
        documents = generate(CONFIG)
        directory = bundle.publish_bundle(self.base, documents)
        before = {p.name: p.read_bytes() for p in directory.iterdir()}
        with self.assertRaisesRegex(ValueError, "immutable"):
            bundle.publish_bundle(self.base, documents)
        self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})

    def test_missing_files_and_hash_tampering_are_rejected(self):
        directory = bundle.publish_bundle(self.base, generate(CONFIG))
        for name in ("generated-export.json", "generated-coverage.json", "generated-provenance.json", "manifest.json"):
            path = directory / name
            original = path.read_bytes()
            with self.subTest(name=name):
                path.write_bytes(original + b" ")
                with self.assertRaises(ValueError):
                    bundle.validate_current(self.base)
                path.unlink()
                with self.assertRaises(OSError):
                    bundle.validate_current(self.base)
                path.write_bytes(original)

    def test_mixed_run_rejected_even_when_hashes_are_updated(self):
        directory = bundle.publish_bundle(self.base, generate(CONFIG))
        other = generate(CONFIG)["generated-coverage.json"]
        raw = json_bytes(other)
        (directory / "generated-coverage.json").write_bytes(raw)
        manifest_path = directory / "manifest.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["files"]["generated-coverage.json"] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        manifest_path.write_bytes(json_bytes(manifest))
        pointer_path = self.base / "current-run.json"
        pointer = json.loads(pointer_path.read_bytes())
        pointer["manifestSha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        pointer_path.write_bytes(json_bytes(pointer))
        with self.assertRaisesRegex(ValueError, "identity"):
            bundle.validate_current(self.base)

    def test_pointer_path_traversal_is_rejected(self):
        bundle.publish_bundle(self.base, generate(CONFIG))
        path = self.base / "current-run.json"
        pointer = json.loads(path.read_bytes())
        pointer["bundlePath"] = "../elsewhere"
        path.write_bytes(json_bytes(pointer))
        with self.assertRaisesRegex(ValueError, "path"):
            bundle.validate_current(self.base)

    def test_provenance_checks_exact_bytes_rather_than_reserialized_json(self):
        directory = bundle.publish_bundle(self.base, generate(CONFIG))
        path = directory / "generated-export.json"
        record = json.loads(path.read_bytes())
        compact = (json.dumps(record, separators=(",", ":")) + "\n").encode("utf-8")
        path.write_bytes(compact)
        def refresh_manifest_and_pointer():
            manifest_path = directory / "manifest.json"
            manifest = json.loads(manifest_path.read_bytes())
            for name in manifest["files"]:
                raw = (directory / name).read_bytes()
                manifest["files"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
            manifest_path.write_bytes(json_bytes(manifest))
            pointer_path = self.base / "current-run.json"
            pointer = json.loads(pointer_path.read_bytes())
            pointer["manifestSha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            pointer_path.write_bytes(json_bytes(pointer))
        refresh_manifest_and_pointer()
        with self.assertRaisesRegex(ValueError, "Provenance export hash"):
            bundle.validate_current(self.base)
        provenance_path = directory / "generated-provenance.json"
        provenance = json.loads(provenance_path.read_bytes())
        provenance["sha256"] = hashlib.sha256(compact).hexdigest()
        provenance_path.write_bytes(json_bytes(provenance))
        refresh_manifest_and_pointer()
        checked = bundle.validate_current(self.base)
        self.assertEqual(checked["bytes"]["generated-export.json"], compact)

    def test_concurrent_writers_publish_only_complete_runs(self):
        bundle.publish_bundle(self.base, generate(CONFIG))
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(bundle.publish_bundle, self.base, generate(CONFIG)) for _ in range(4)]
            for _ in futures:
                bundle.validate_current(self.base)
            directories = [future.result() for future in futures]
        current = bundle.validate_current(self.base)
        self.assertIn(current["manifest"]["runId"], [p.name for p in directories])
        for directory in directories:
            bundle.validate_bundle(directory)


if __name__ == "__main__":
    unittest.main()
