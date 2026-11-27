# Evidence coverage model 0.2.0

This document describes the **synthetic project-specific proposed evidence
profile**, not a completed Polarion extraction or a completeness certification.

## Declared scope

`evidenceScope.selection` identifies exactly one fixture by project ID, object ID
and resolved revision. Its `basis` is `one synthetic fixture, not a project inventory`.
The executable generates only REQ-001, one outgoing relationship to TC-001 and one
ordinary approval record. TC-001 itself is not exported. No live query was attempted.

## Coverage states

| State in JSON | Exact interpretation |
| --- | --- |
| `complete` | All category fields required for the explicitly declared synthetic selection are populated and pass the contract's checks. No claim about project-wide evidence, historical authority or real source truth. |
| `partial` | Some evidence is represented but the category has a disclosed gap in the declared demonstration. |
| `unavailable` | This run supplies no supported evidence for this category. It does not assert that the source system has no such evidence. |

## Current category decisions

| Category | State | Scope and reason |
| --- | --- | --- |
| Artifact identity | complete | Instance, project, object ID and synthetic resolved revision of the one fixture |
| Work Items | complete | Required fields of the one selected requirement fixture; no project enumeration |
| Approval status | complete | Approver and ordinary state of the one fixture; no decision time or signature claim |
| Relationships | partial | Only one outgoing fixture link; target is not exported; incoming and cross-project cases untested |
| Approval timing, history and approval-change history | unavailable | No history was retrieved; decision timestamp remains unknown |
| Collections, baselines and historical membership | unavailable | No explicit configuration or membership snapshot |
| Projects, attachments and comments | unavailable | Configured project identity is not retrieved project metadata |
| Revision information | unavailable | Synthetic revision label is not independently retrieved revision evidence |
| Secure approval comment IDs | unavailable | No comment references retrieved; future references remain mutable |
| Test executions | unavailable | No executed test results; a link to a test definition does not prove an execution |
| Workflow and electronic signatures | unavailable | Ordinary approval state provides neither kind of signature evidence |

`counts` describes the actual export arrays: one Work Item, one relationship, one
approval and zero test executions. It is not a count of all source-system entities.
`retrievalGaps` explicitly marks pagination, permissions and history as
`not_attempted`. The validator rejects coverage that overstates this fixture profile.

## Future live scope

Before a live run, specify the target version, project set, selection/query,
resolved revisions, requested categories and exclusions. Track every page,
truncated expansion, denied object and unresolved link target. Cross-project and
incoming links are part of the first pilot, not an implied capability today.

A live Complete claim would require checked expected results and evidence that
the selected category was fully retrieved under the declared scope and permissions.
When permissions prevent proving completeness, report a gap. Historical coverage
must separately address values, membership, deleted objects and decision transitions.
Any live profile requires a new contract revision; current validation only accepts
the synthetic 0.2.0 profile. See [the pilot plan](live-pilot-plan.md).
