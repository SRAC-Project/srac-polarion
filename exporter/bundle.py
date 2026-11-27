"""Publish immutable evidence runs and atomically switch a validated pointer."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

if __package__:
    from .contract import ARTIFACTS, IDENTITY, json_bytes, validate_documents, validate_schema
else:
    from contract import ARTIFACTS, IDENTITY, json_bytes, validate_documents, validate_schema


def _digest(content):
    return hashlib.sha256(content).hexdigest()


def _write(path, content):
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def validate_bundle(directory, expected_run=None, manifest_sha256=None):
    """Read and return checked bytes/documents; consumers must use this snapshot."""
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("Bundle directory must not be a symbolic link")
    raw = {}
    for name in (*ARTIFACTS, "manifest.json"):
        path = directory / name
        if path.is_symlink():
            raise ValueError("Bundle files must not be symbolic links")
        raw[name] = path.read_bytes()
    manifest = json.loads(raw["manifest.json"])
    validate_schema(manifest, "manifest")
    if expected_run is not None and manifest["runId"] != expected_run:
        raise ValueError("Manifest run identity mismatch")
    if manifest_sha256 is not None and _digest(raw["manifest.json"]) != manifest_sha256:
        raise ValueError("Manifest hash mismatch")
    for name in ARTIFACTS:
        if _digest(raw[name]) != manifest["files"][name]["sha256"]:
            raise ValueError("Artifact hash mismatch: " + name)
        if len(raw[name]) != manifest["files"][name]["bytes"]:
            raise ValueError("Artifact byte count mismatch: " + name)
    documents = {name: json.loads(raw[name]) for name in ARTIFACTS}
    validate_documents(documents, export_bytes=raw["generated-export.json"])
    for document in documents.values():
        if any(document[key] != manifest[key] for key in IDENTITY):
            raise ValueError("Manifest metadata does not match its evidence files")
    return {"manifest": manifest, "documents": documents, "bytes": raw}


def validate_current(base):
    """Resolve the pointer once and validate all referenced files before use."""
    base = Path(base).resolve()
    pointer = json.loads((base / "current-run.json").read_bytes())
    validate_schema(pointer, "pointer")
    expected_path = "runs/" + pointer["runId"]
    if pointer["bundlePath"] != expected_path:
        raise ValueError("Pointer path and run identity disagree")
    directory = base / pointer["bundlePath"]
    if not directory.resolve().is_relative_to(base) or (base / "runs").is_symlink():
        raise ValueError("Bundle path escapes output directory")
    return validate_bundle(directory, pointer["runId"], pointer["manifestSha256"])


def publish_bundle(base, documents):
    """Publish pointer last. Failed writes leave the previous pointer untouched.

    Concurrent writers use distinct run IDs. The last successful pointer swap
    wins; each published pointer still refers to one complete immutable run.
    """
    validate_documents(documents)
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".staging-", dir=base))
    run_id = documents["generated-export.json"]["runId"]
    pointer_temp = base / (".current-" + stage.name + ".json")
    try:
        payloads = {name: json_bytes(doc) for name, doc in documents.items()}
        for name, content in payloads.items():
            _write(stage / name, content)
        record = documents["generated-export.json"]
        manifest = {key: record[key] for key in IDENTITY}
        manifest.update({"artifactKind": "manifest", "state": "complete",
                         "notice": record["notice"],
                         "files": {name: {"sha256": _digest(content), "bytes": len(content)}
                                   for name, content in payloads.items()}})
        manifest_bytes = json_bytes(manifest)
        _write(stage / "manifest.json", manifest_bytes)
        validate_bundle(stage, expected_run=run_id)
        runs = base / "runs"
        runs.mkdir(exist_ok=True)
        final = runs / run_id
        if final.exists():
            raise ValueError("Run already exists; immutable runs cannot be overwritten")
        os.rename(stage, final)
        pointer = {key: record[key] for key in ("format", "formatVersion", "runId")}
        pointer.update({"artifactKind": "pointer", "bundlePath": "runs/" + run_id,
                        "manifestSha256": _digest(manifest_bytes)})
        validate_schema(pointer, "pointer")
        _write(pointer_temp, json_bytes(pointer))
        os.replace(pointer_temp, base / "current-run.json")
        return final
    finally:
        if stage.exists():
            shutil.rmtree(stage)
        pointer_temp.unlink(missing_ok=True)
