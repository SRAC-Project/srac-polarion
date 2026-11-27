# Proposed evidence format contract 0.2.0

## Status and versioning

This is a **project-specific proposed evidence format**, named
`srac-polarion-proposed-evidence`. It does not implement an identified external
SRAC schema and does not establish SRAC interoperability. The executable profile
and every supplied example are synthetic. Live REST/SOAP extraction is proposed
behavior, not implemented behavior.

The normative structural contract is
[`proposed-evidence-0.2.0.schema.json`](../schemas/proposed-evidence-0.2.0.schema.json),
using JSON Schema draft 2020-12. It contains definitions for export, coverage,
provenance, manifest and pointer documents. Required fields and allowed values
are explicit, and additional properties are forbidden. `contract.py` enforces
this vocabulary plus the cross-document rules below. New fields, live profiles
or changed meanings require an explicit contract version and corresponding tests.
Readers reject unknown versions rather than silently accepting incompatible data.

## Required shared metadata

Export, coverage, provenance and manifest must agree on all these values:

| Field | Required value or meaning |
| --- | --- |
| `format` | `srac-polarion-proposed-evidence` |
| `formatVersion` | `0.2.0` |
| `runId` | UUID v4 generated for this invocation |
| `sourceSystem` | `Polarion`, the modeled system, not proof of contact |
| `sourceInstance` | Nonempty configured synthetic instance identifier |
| `projectId` | Nonempty configured synthetic project identifier |
| `extractionTime` | Configured ISO 8601 timestamp with timezone; not actual retrieval time |
| `dataOrigin` | `synthetic` |
| `liveExtractionPerformed` | `false` |

Each evidence document also requires the exact synthetic `notice` from the schema
and the appropriate `artifactKind`. The pointer includes format, version and run ID,
its relative bundle path, and the exact manifest hash. See the provenance model.

## Field mapping and current profile

The Polarion column describes a **proposed future source**, to be checked against
the installed target's supported API and permissions. Current values are invented.

| Proposed source or concept | Output field | Current implementation |
| --- | --- | --- |
| Work Item identity and type | `objectId`, `objectType`, `evidenceKind` | One synthetic `REQ-001`, `Requirement`, `requirement` |
| Explicit resolved repository revision | `resolvedRevision` | Synthetic opaque string `1250`; distinct from time |
| Explicit classification field and source | `classification.safetyClass`, `status`, `source` | `null`, `unknown`, `null` |
| Explicit acceptance evidence and source | `acceptance.value`, `status`, `source` | `null`, `unknown`, `null` |
| Link endpoint identity | `links[].targetObject`, `targetProject`, `targetRevision` | One synthetic target; never silently assume same project in live mode |
| Link semantics | `role`, `direction`, `suspect`, `targetResolution` | Outgoing `verified_by`, false suspect, `not_exported` target |
| Ordinary approval | `approvals[].approver`, `state` | Synthetic `demo-user`, `approved` |
| Supported historical transition | `approvalChangeTime`, `timeConfidence`, `timingEvidence`, `reason` | `null`, `unknown`, `null`, explanation |
| Historical selection membership | `historicalMembership` | Unknown, null members, explanation |
| Test-case Work Item | A future test-definition record | Definition only; not an executed result |
| Test execution | A future, separate execution record | Unavailable; no verdict or execution record generated |
| Collection or baseline configuration | Separate future entities with kind, identity and member revisions | Unavailable; collections and baselines remain distinct |

Current v0.2.0 export permits only its requirement fixture profile. Proposed live
records, histories, membership snapshots and test executions need a versioned
extension. The historical helpers operate on normalized fixtures outside that
export schema; their richer evidence must not be inserted into 0.2.0 documents.

## Unknown, unavailable, empty and false

`unknown` describes a field whose actual value has not been established. Use JSON
`null` and an explicit status/confidence or reason. A null approval timestamp is
not a timestamp of zero, the extraction time or the latest modification time.

`unavailable` is a coverage state: this run cannot supply that evidence category.
For example, approval time is unknown because history is unavailable. Proposed
live failure reasons should distinguish unsupported API, permission denied,
pagination truncation and incomplete history. A missing or inaccessible result is
never an empty, complete result. `false` means an explicitly known boolean, not
unknown. `suspect: null` and `targetRevision: null` are allowed where unestablished.

Classification and acceptance require their own explicit source evidence. They
must never be inferred from Work Item type, workflow state, ordinary approval,
or the existence of a test definition. No data here establishes certification.

## Approval-history interpretation

The proposed live normalizer must bind history to the exact instance, project,
artifact and approver before invoking the local rule. It must establish a complete,
ordered transition sequence and disclose any inaccessible or truncated history.

`derive_approval_timing()` in `exporter/history.py` follows these tested rules:

1. Preserve the approver and commit actor separately. A commit actor may persist
   a change on another person's behalf; actor identity is not approver identity.
2. Derive timing only from an identified status-changing transition supporting
   the current approved/disapproved state. Retain transition ID, revision, source,
   from/to state, commit timestamp, actor and approver together.
3. Follow resets and disapprovals. A reset clears the prior active decision.
   Reapproval uses the later supporting transition, not the original approval.
   Repeated unchanged states do not move the decision time.
4. Treat the commit timestamp as persisted transition time, not the instant of
   clicking Approve, a signature time or proof of historical approver authority.
5. Return unknown for incomplete history, gaps, duplicates, invalid/out-of-order
   times, missing provenance or a current state that disagrees with history.
   Revisions are opaque and must not be sorted numerically to invent chronology.

This helper does not authenticate raw history, prove that the caller supplied a
complete sequence or verify authorization. Those remain live retrieval duties.

## Historical membership and secure comments

Historical field values retrieved for a current selection cannot establish which
items belonged to a historical collection, baseline or project. They cannot reveal
subsequently deleted items merely by being read at an older revision. Membership
requires an explicit sourced snapshot with configuration kind, revision and member
identities. Collection membership must never be presented as baseline membership.

A secure-approval comment ID is an observed reference at a revision. Comments may
be replaced or removed. The reference is mutable evidence, never an immutable
signature, proof of acceptance or a substitute for a supported approval transition.

## Cross-document invariants

The export's identity and revision must match provenance and the exact selection
in coverage. Counts must agree with the actual export arrays. Coverage Complete
is limited to the single declared fixture and required category fields, as defined
in [evidence coverage](evidence-coverage.md). Offline history and timing cannot be
upgraded to Complete. Provenance hashes the exact export bytes. The manifest hashes
all three files, and the pointer pins the manifest hash and run ID. Consumers must
validate the whole bundle before using any evidence.
