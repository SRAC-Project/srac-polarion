"""Validate this project's fixed JSON Schema vocabulary and cross-file rules.

This is not a general-purpose JSON Schema implementation. The checked-in schema
uses only the keywords implemented below; schema changes require matching tests.
"""

import hashlib
import json
from pathlib import Path
import re
from datetime import datetime

FORMAT = "srac-polarion-proposed-evidence"
VERSION = "0.2.0"
SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "proposed-evidence-0.2.0.schema.json"
ARTIFACTS = {"generated-export.json": "export", "generated-coverage.json": "coverage",
             "generated-provenance.json": "provenance"}
IDENTITY = ("format", "formatVersion", "runId", "sourceSystem", "sourceInstance",
            "projectId", "extractionTime", "dataOrigin", "liveExtractionPerformed")


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _validate(value, spec, root, path):
    if "$ref" in spec:
        return _validate(value, root["$defs"][spec["$ref"].split("/")[-1]], root, path)
    if "oneOf" in spec:
        matches = 0
        for option in spec["oneOf"]:
            try:
                _validate(value, option, root, path)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError(path + ": expected exactly one schema variant")
    checks = {"object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
              "string": lambda v: isinstance(v, str), "null": lambda v: v is None,
              "boolean": lambda v: isinstance(v, bool),
              "integer": lambda v: isinstance(v, int) and not isinstance(v, bool)}
    types = spec.get("type")
    if types is not None:
        types = [types] if isinstance(types, str) else types
        if not any(checks[t](value) for t in types):
            raise ValueError(path + ": invalid type")
    if "const" in spec and (type(value) is not type(spec["const"]) or value != spec["const"]):
        raise ValueError(path + ": invalid constant")
    if "enum" in spec and value not in spec["enum"]:
        raise ValueError(path + ": invalid enum value")
    if isinstance(value, str):
        if len(value) < spec.get("minLength", 0) or ("pattern" in spec and re.search(spec["pattern"], value) is None):
            raise ValueError(path + ": invalid string")
    if isinstance(value, int) and "minimum" in spec and value < spec["minimum"]:
        raise ValueError(path + ": below minimum")
    if isinstance(value, dict):
        properties = spec.get("properties", {})
        if set(spec.get("required", [])) - value.keys():
            raise ValueError(path + ": missing required fields")
        if spec.get("additionalProperties") is False and value.keys() - properties.keys():
            raise ValueError(path + ": unexpected fields")
        for key, child in value.items():
            if key in properties:
                _validate(child, properties[key], root, path + "." + key)
    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0):
            raise ValueError(path + ": too few entries")
        for index, child in enumerate(value):
            if "items" in spec:
                _validate(child, spec["items"], root, path + "[" + str(index) + "]")


def validate_schema(document, kind):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    _validate(document, schema["$defs"][kind], schema, kind)


def validate_documents(documents, export_bytes=None):
    if set(documents) != set(ARTIFACTS):
        raise ValueError("Exactly three named evidence artifacts are required")
    for name, kind in ARTIFACTS.items():
        validate_schema(documents[name], kind)
    record = documents["generated-export.json"]
    timestamp = datetime.fromisoformat(record["extractionTime"].replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("Extraction timestamp requires a timezone")
    provenance = documents["generated-provenance.json"]
    coverage = documents["generated-coverage.json"]
    for document in documents.values():
        if any(document[key] != record[key] for key in IDENTITY):
            raise ValueError("Evidence artifacts have inconsistent run identity or metadata")
    if (provenance["artifact"] != record["objectId"]
            or provenance["resolvedRevision"] != record["resolvedRevision"]):
        raise ValueError("Provenance refers to a different artifact or revision")
    if export_bytes is None:
        export_bytes = json_bytes(record)
    if provenance["sha256"] != hashlib.sha256(export_bytes).hexdigest():
        raise ValueError("Provenance export hash mismatch")
    expected_selection = [{k: record[k] for k in ("projectId", "objectId", "resolvedRevision")}]
    if coverage["evidenceScope"]["selection"] != expected_selection:
        raise ValueError("Coverage selection does not match the exported record")
    expected_counts = {"workItems": 1, "relationships": len(record["links"]),
                       "approvals": len(record["approvals"]), "testExecutions": 0}
    if coverage["counts"] != expected_counts:
        raise ValueError("Coverage counts do not match exported evidence")
    expected_states = {key: "unavailable" for key in coverage["coverage"]}
    expected_states.update({"artifactIdentity": "complete", "workItems": "complete",
                            "approvalStatus": "complete", "relationships": "partial"})
    if coverage["coverage"] != expected_states:
        raise ValueError("Coverage overstates the supported synthetic fixture profile")
    for approval in record["approvals"]:
        if (approval["approvalChangeTime"] is not None
                or approval["timeConfidence"] != "unknown"
                or approval["timingEvidence"] is not None):
            raise ValueError("The offline fixture cannot claim retrieved approval timing")
