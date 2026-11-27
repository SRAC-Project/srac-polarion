"""Generate project-specific proposed evidence v0.2.0 using synthetic data only."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
from uuid import uuid4

if __package__:
    from .bundle import publish_bundle, validate_current
    from .contract import FORMAT, VERSION, json_bytes, validate_documents
    from .history import derive_approval_timing
else:
    from bundle import publish_bundle, validate_current
    from contract import FORMAT, VERSION, json_bytes, validate_documents
    from history import derive_approval_timing

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path(__file__).resolve().with_name("config.json")


def read_config(path):
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("config.json must contain an object")
    for key in ("sourceInstance", "projectId", "exportTime"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError("config.json requires a non-empty string: " + key)
    timestamp = config["exportTime"]
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if "T" not in timestamp or parsed.tzinfo is None:
        raise ValueError("exportTime requires an ISO 8601 timestamp with a timezone")
    return config


def generate(config, run_id=None):
    """Produce documents with shared identity; coverage is scoped to one fixture."""
    metadata = {
        "format": FORMAT, "formatVersion": VERSION,
        "runId": run_id or str(uuid4()), "sourceSystem": "Polarion",
        "sourceInstance": config["sourceInstance"], "projectId": config["projectId"],
        "extractionTime": config["exportTime"], "dataOrigin": "synthetic",
        "liveExtractionPerformed": False,
        "notice": "Illustrative synthetic example; no live extraction or interoperability claim",
    }
    record = {
        **metadata, "artifactKind": "export",
        "objectId": "REQ-001", "objectType": "Requirement",
        "evidenceKind": "requirement", "resolvedRevision": "1250",
        "classification": {"safetyClass": None, "status": "unknown",
                           "source": None},
        "acceptance": {"value": None, "status": "unknown", "source": None},
        "links": [{"targetObject": "TC-001", "targetProject": config["projectId"],
                   "targetRevision": "1250", "role": "verified_by",
                   "direction": "outgoing", "suspect": False,
                   "targetResolution": "not_exported"}],
        "approvals": [{"approver": "demo-user", "state": "approved",
                       **derive_approval_timing("demo-user", "approved", [], False)}],
        "historicalMembership": {"status": "unknown", "members": None,
                                 "reason": "No historical membership evidence was retrieved"},
    }
    coverage = {
        **metadata, "artifactKind": "coverage",
        "evidenceScope": {
            "selection": [{"projectId": config["projectId"], "objectId": "REQ-001",
                           "resolvedRevision": "1250"}],
            "basis": "one synthetic fixture, not a project inventory",
        },
        "coverage": {
            "artifactIdentity": "complete", "workItems": "complete",
            "relationships": "partial", "approvalStatus": "complete",
            **{k: "unavailable" for k in (
                "approvalTiming", "collections", "baselines", "historicalMembership",
                "workflowSignatures", "electronicSignatures", "projects", "attachments",
                "comments", "history", "approvalChangeHistory", "secureApprovalCommentIds",
                "revisionInformation", "testExecutions")},
        },
        "counts": {"workItems": 1, "relationships": 1, "approvals": 1, "testExecutions": 0},
        "retrievalGaps": {"pagination": "not_attempted", "permissions": "not_attempted",
                          "history": "not_attempted"},
        "notes": [
            "Complete applies only to required fields of the single declared synthetic fixture.",
            "TC-001 is not exported; incoming and cross-project link coverage is untested.",
            "No live pagination, permissions, history or project completeness was evaluated.",
            "Historical values of current items do not prove historical membership.",
            "Approval state does not establish classification, acceptance or signature validity.",
        ],
    }
    provenance = {
        **metadata, "artifactKind": "provenance",
        "artifact": record["objectId"], "resolvedRevision": record["resolvedRevision"],
        "retrievalMethod": "offline synthetic generator",
        "exportFile": "generated-export.json",
        "sha256": hashlib.sha256(json_bytes(record)).hexdigest(),
        "notes": [
            "Identity, revision, links and approval state are invented fixture values.",
            "extractionTime is the configured demonstration timestamp, not a server retrieval time.",
            "SHA-256 checks bytes only; it establishes neither authenticity nor completeness.",
        ],
    }
    documents = {"generated-export.json": record, "generated-provenance.json": provenance,
                 "generated-coverage.json": coverage}
    validate_documents(documents)
    return documents


def main():
    try:
        if sys.argv[1:] == ["--validate"]:
            result = validate_current(ROOT / "examples")
            print("Validated completed run " + result["manifest"]["runId"])
        elif sys.argv[1:]:
            raise ValueError("Usage: python exporter/export.py [--validate]")
        else:
            directory = publish_bundle(ROOT / "examples", generate(read_config(CONFIG)))
            print("Published examples/runs/" + directory.name)
            print("Resolve examples/current-run.json with --validate before consumption.")
            print("Synthetic demonstration only; no Polarion connection was made.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("Export failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
