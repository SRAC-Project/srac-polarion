"""Generate a deterministic, offline SRAC demonstration export.

Uses only the Python standard library. No Polarion connection is attempted.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().with_name("config.json")


def read_config(path):
    """Validate required metadata before creating any output files."""
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("config.json must contain a JSON object")
    for key in ("sourceInstance", "projectId", "exportTime"):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("config.json requires a non-empty string: " + key)
    timestamp = config["exportTime"]
    # Require an explicit timezone; export time is independent of revision.
    parsed = datetime.fromisoformat(
        timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
    )
    if "T" not in timestamp or parsed.tzinfo is None:
        raise ValueError("exportTime must be an ISO 8601 timestamp with a timezone")
    return config


def json_bytes(value):
    """Stable UTF-8 serialization, also used for the recorded file digest."""
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def generate(config):
    """Build synthetic evidence and reports without asserting live retrieval."""
    metadata = {
        "sourceInstance": config["sourceInstance"],
        "projectId": config["projectId"],
        "extractionTime": config["exportTime"],
        "dataOrigin": "synthetic",
    }
    record = {
        **metadata,
        "sourceSystem": "Polarion",
        "objectId": "REQ-001",
        "objectType": "Requirement",
        "resolvedRevision": "1250",
        "classification": {"safetyClass": "ASIL-B"},
        "links": [{
            "targetObject": "TC-001",
            "targetProject": config["projectId"],
            "targetRevision": "1250",
            "role": "verified_by",
            "direction": "outgoing",
            "suspect": False,
        }],
        "approvals": [{
            "approver": "demo-user",
            "state": "approved",
            "approvalChangeTime": None,
            "approvalChangeSource": None,
            "timeConfidence": "unknown",
        }],
    }
    export_bytes = json_bytes(record)
    provenance = {
        **metadata,
        "sourceSystem": record["sourceSystem"],
        "artifact": record["objectId"],
        "resolvedRevision": record["resolvedRevision"],
        "retrievalMethod": "offline synthetic generator",
        "liveExtractionPerformed": False,
        "exportFile": "generated-export.json",
        "sha256": hashlib.sha256(export_bytes).hexdigest(),
        "notes": [
            "Identifiers, revision, link and approval state are synthetic examples.",
            "extractionTime is the configured demonstration time, not a live retrieval time.",
            "The digest covers the exact UTF-8 bytes of generated-export.json only.",
            "Integrity does not establish completeness, approval validity or compliance.",
        ],
    }
    coverage = {
        **metadata,
        "evidenceScope": "Offline synthetic demonstration; no live Polarion evidence",
        "liveExtractionPerformed": False,
        "coverage": {
            "artifactIdentity": "complete",
            "workItems": "partial",
            "relationships": "partial",
            "collections": "unavailable",
            "baselines": "unavailable",
            "approvalStatus": "complete",
            "approvalTiming": "unavailable",
            "workflowSignatures": "unavailable",
            "electronicSignatures": "unavailable",
            "projects": "unavailable",
            "attachments": "unavailable",
            "comments": "unavailable",
            "history": "unavailable",
            "approvalChangeHistory": "unavailable",
            "secureApprovalCommentIds": "unavailable",
            "revisionInformation": "unavailable",
        },
        "counts": {
            "workItems": 1,
            "relationships": len(record["links"]),
            "approvals": len(record["approvals"]),
        },
        "notes": [
            "Coverage states describe only the synthetic demonstration record.",
            "Complete means populated for that record, not complete Polarion extraction.",
            "Only REQ-001 is exported; linked target TC-001 is not included.",
            "Approval timing is unknown; no repository history was retrieved.",
            "The revision is synthetic; live revision information is unavailable.",
            "Project identity is configured; project metadata is not retrieved.",
            "Collections and baselines are distinct and neither is extracted.",
            "All live REST and SOAP extraction remains unimplemented pending review.",
        ],
    }
    return {
        "generated-export.json": export_bytes,
        "generated-provenance.json": json_bytes(provenance),
        "generated-coverage.json": json_bytes(coverage),
    }


def main():
    try:
        artifacts = generate(read_config(CONFIG))
        output = ROOT / "examples"
        output.mkdir(parents=True, exist_ok=True)
        for name, content in artifacts.items():
            (output / name).write_bytes(content)
            print("Wrote examples/" + name)
    except (OSError, ValueError) as error:
        print("Export failed: " + str(error), file=sys.stderr)
        return 1
    print("Offline synthetic PoC complete; no Polarion connection was made.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
