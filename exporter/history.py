"""Conservative rules for normalized historical evidence, exercised by fixtures.

These helpers do not retrieve Polarion history or establish signature validity.
Callers must supply a complete, correctly scoped and ordered transition sequence.
"""

from datetime import datetime


def unknown_timing(reason):
    return {"approvalChangeTime": None, "timeConfidence": "unknown",
            "timingEvidence": None, "reason": reason}


def derive_approval_timing(approver, state, transitions, history_complete=False):
    """Associate a decision with its last supported transition, never its actor.

    Input is already scoped to one artifact. Filter by approver, retain supplied
    order, and reject gaps or ambiguous sequences rather than guessing a time.
    Revisions are opaque identifiers, not sortable timestamps.
    """
    if not isinstance(approver, str) or not approver.strip():
        return unknown_timing("Approver identity is unavailable")
    if history_complete is not True:
        return unknown_timing("Complete approval history is unavailable")
    if state not in ("approved", "disapproved"):
        return unknown_timing("There is no current approval decision after reset")
    relevant = [e for e in transitions if e.get("approver") == approver]
    previous_state = None
    previous_time = None
    seen = set()
    decision = None
    try:
        for event in relevant:
            required = ("transitionId", "revision", "commitTime", "commitActor",
                        "fromState", "toState", "source")
            if any(not isinstance(event.get(k), str) or not event[k].strip()
                   for k in required):
                return unknown_timing("Transition provenance is incomplete")
            timestamp = datetime.fromisoformat(event["commitTime"].replace("Z", "+00:00"))
            if timestamp.tzinfo is None or event["transitionId"] in seen:
                return unknown_timing("Transition order or identity is ambiguous")
            if previous_time is not None and timestamp < previous_time:
                return unknown_timing("Transition sequence is out of order")
            if previous_state is not None and event["fromState"] != previous_state:
                return unknown_timing("Approval transition chain has a gap")
            if event["fromState"] not in ("pending", "approved", "disapproved") or event["toState"] not in ("pending", "approved", "disapproved"):
                return unknown_timing("Approval transition state is unsupported")
            seen.add(event["transitionId"])
            previous_time = timestamp
            previous_state = event["toState"]
            if event["fromState"] != event["toState"]:
                decision = event
    except (ValueError, TypeError):
        return unknown_timing("Transition timestamp is invalid")
    if decision is None or previous_state != state or decision["toState"] != state:
        return unknown_timing("Current decision has no matching transition")
    return {
        "approvalChangeTime": decision["commitTime"],
        "timeConfidence": "repository_commit_timestamp",
        "timingEvidence": {k: decision[k] for k in (
            "transitionId", "revision", "commitTime", "commitActor", "approver",
            "fromState", "toState", "source")},
        "reason": "Persisted transition time; the user action time is not established",
    }


def historical_membership(current_items, historical_values, snapshot=None):
    """Current selection and historical field reads cannot establish membership."""
    if snapshot is None:
        return {"status": "unknown", "members": None,
                "reason": "No explicit historical membership snapshot"}
    required = ("sourceInstance", "projectId", "configurationId", "revision", "source")
    if (snapshot.get("kind") not in ("collection", "baseline")
            or any(not isinstance(snapshot.get(key), str) or not snapshot[key].strip()
                   for key in required)
            or not isinstance(snapshot.get("members"), list)):
        raise ValueError("Membership requires a sourced collection or baseline snapshot")
    for member in snapshot["members"]:
        if (not isinstance(member, dict)
                or any(not isinstance(member.get(key), str) or not member[key].strip()
                       for key in ("projectId", "objectId", "resolvedRevision"))):
            raise ValueError("Membership requires explicit member identities and revisions")
    return {"status": "known", "kind": snapshot["kind"],
            **{key: snapshot[key] for key in required},
            "members": [dict(member) for member in snapshot["members"]]}


def secure_comment_reference(comment_id, revision):
    """An observed comment reference can later be replaced or removed."""
    return {"commentId": comment_id, "observedRevision": revision,
            "evidenceKind": "mutable_comment_reference",
            "immutableSignatureEvidence": False}


def work_item_evidence_kind(object_type):
    """A test-case Work Item describes a test, not an execution result."""
    return {"Requirement": "requirement", "Hazard": "hazard",
            "TestCase": "test_definition"}.get(object_type, "work_item")
