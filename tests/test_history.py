"""Synthetic expected results, not a claim of successful API retrieval."""

import copy
import unittest

from exporter.history import (derive_approval_timing, historical_membership,
                              secure_comment_reference, work_item_evidence_kind)


def transition(number, before, after, actor="repository-writer", approver="reviewer"):
    return {"transitionId": "transition-" + str(number), "revision": "r" + str(number),
            "commitTime": "2026-11-0" + str(number) + "T10:00:00Z",
            "commitActor": actor, "approver": approver, "fromState": before,
            "toState": after, "source": "synthetic normalized history fixture"}


class HistoricalEvidenceTests(unittest.TestCase):
    def test_actor_is_distinct_from_approver_and_timing_has_support(self):
        event = transition(1, "pending", "approved")
        result = derive_approval_timing("reviewer", "approved", [event], True)
        self.assertEqual(result["approvalChangeTime"], "2026-11-01T10:00:00Z")
        support = result["timingEvidence"]
        self.assertEqual(support["approver"], "reviewer")
        self.assertEqual(support["commitActor"], "repository-writer")
        self.assertEqual(support["revision"], "r1")
        self.assertEqual(support["transitionId"], "transition-1")
        self.assertEqual(support["fromState"], "pending")
        self.assertEqual(support["toState"], "approved")
        self.assertEqual(result["timeConfidence"], "repository_commit_timestamp")

    def test_reset_invalidates_previous_decision_and_reapproval_uses_latest_transition(self):
        events = [transition(1, "pending", "approved"), transition(2, "approved", "pending")]
        reset = derive_approval_timing("reviewer", "pending", events, True)
        self.assertIsNone(reset["approvalChangeTime"])
        events += [transition(3, "pending", "disapproved"), transition(4, "disapproved", "approved")]
        result = derive_approval_timing("reviewer", "approved", events, True)
        self.assertEqual(result["approvalChangeTime"], "2026-11-04T10:00:00Z")
        self.assertEqual(result["timingEvidence"]["revision"], "r4")

    def test_noop_history_does_not_replace_decision_time(self):
        events = [transition(1, "pending", "approved"), transition(2, "approved", "approved")]
        self.assertEqual(derive_approval_timing("reviewer", "approved", events, True)["timingEvidence"]["revision"], "r1")

    def test_missing_incomplete_ambiguous_or_mismatching_history_stays_unknown(self):
        first = transition(1, "pending", "approved")
        cases = [([], True), ([first], False), ([transition(1, "pending", "disapproved")], True),
                 ([transition(1, "pending", "approved", approver="someone-else")], True),
                 ([first, transition(2, "pending", "approved")], True),
                 ([first, first], True),
                 ([transition(2, "pending", "approved"), transition(1, "approved", "approved")], True)]
        for field in ("revision", "commitTime", "commitActor", "transitionId", "source"):
            broken = copy.deepcopy(first)
            broken.pop(field)
            cases.append(([broken], True))
        for invalid_time in ("invalid", "2026-11-01T10:00:00"):
            broken = {**first, "commitTime": invalid_time}
            cases.append(([broken], True))
        for events, complete in cases:
            with self.subTest(events=events, complete=complete):
                result = derive_approval_timing("reviewer", "approved", events, complete)
                self.assertIsNone(result["approvalChangeTime"])
                self.assertIsNone(result["timingEvidence"])
        self.assertIsNone(derive_approval_timing("", "approved", [first], True)["approvalChangeTime"])

    def test_historical_field_values_cannot_establish_membership_or_deleted_items(self):
        result = historical_membership(["REQ-001"], [{"objectId": "REQ-001", "revision": "r1"}])
        self.assertEqual(result["status"], "unknown")
        self.assertIsNone(result["members"])
        members = [{"projectId": "DEMO", "objectId": "REQ-001", "resolvedRevision": "r1"},
                   {"projectId": "OTHER", "objectId": "DELETED-002", "resolvedRevision": "r0"}]
        snapshot = {"sourceInstance": "synthetic-demo", "projectId": "DEMO",
                    "configurationId": "configuration-1", "kind": "baseline", "revision": "r1",
                    "source": "explicit synthetic snapshot", "members": members}
        known = historical_membership(["REQ-001"], [], snapshot)
        self.assertEqual(known["members"], members)
        self.assertEqual(known["members"][1]["resolvedRevision"], "r0")
        self.assertEqual(known["configurationId"], "configuration-1")
        self.assertEqual(known["kind"], "baseline")
        snapshot["kind"] = "collection"
        self.assertEqual(historical_membership([], [], snapshot)["kind"], "collection")
        for missing in ("configurationId", "source", "revision"):
            broken = {key: value for key, value in snapshot.items() if key != missing}
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                historical_membership([], [], broken)
        with self.assertRaises(ValueError):
            historical_membership([], [], {**snapshot, "members": ["REQ-001"]})

    def test_replaced_or_removed_secure_comments_never_establish_signature_evidence(self):
        references = [secure_comment_reference("comment-1", "r1"),
                      secure_comment_reference("comment-2", "r2"),
                      secure_comment_reference(None, "r3")]
        self.assertEqual([r["commentId"] for r in references], ["comment-1", "comment-2", None])
        self.assertTrue(all(not r["immutableSignatureEvidence"] for r in references))
        self.assertEqual(references[1]["observedRevision"], "r2")

    def test_test_definition_and_ordinary_approval_cannot_become_execution_or_acceptance(self):
        self.assertEqual(work_item_evidence_kind("TestCase"), "test_definition")
        self.assertNotEqual(work_item_evidence_kind("TestCase"), "test_execution")
        from exporter.export import generate
        documents = generate({"sourceInstance": "demo", "projectId": "DEMO", "exportTime": "2026-11-20T12:00:00Z"})
        record = documents["generated-export.json"]
        self.assertEqual(record["approvals"][0]["state"], "approved")
        self.assertIsNone(record["classification"]["safetyClass"])
        self.assertIsNone(record["acceptance"]["value"])
        self.assertEqual(documents["generated-coverage.json"]["counts"]["testExecutions"], 0)
