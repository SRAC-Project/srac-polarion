# Provenance and coherent publication 0.2.0

All checked-in reports are illustrative synthetic examples. Current retrieval
method is `offline synthetic generator`, and `liveExtractionPerformed` is false.
No report may identify REST/SOAP as performed retrieval merely because those
adapters are planned. Revision labels are invented and `extractionTime` is the
configured demonstration time. Source attribution does not establish source truth.

## Provenance fields

The export, coverage, provenance and manifest share the contract's format, version,
run ID, source identity, project, extraction time and data-origin metadata.
Provenance additionally identifies the exported artifact and resolved revision,
`exportFile: generated-export.json`, and `sha256` of its **exact UTF-8 file bytes**.
Every report independently includes a synthetic notice. Hashes validate integrity,
not authenticity, completeness, approval validity, compliance or endorsement.

## Publication transaction

1. Validate config and all three documents before touching the current pointer.
2. Assign a fresh UUID and create a private `.staging-*` directory under `examples/`.
3. Write and flush each evidence file, then write `manifest.json`. The manifest's
   state is `complete`; it records SHA-256 and byte length for exactly three files.
4. Validate the staged bundle, including schema, common metadata, run ID, export
   hash in provenance, coverage selection and counts, and every manifest hash.
5. Rename the staged directory to `examples/runs/<runId>/`. Never overwrite an
   existing run. The run is complete but is not selected for consumers yet.
6. Write a temporary pointer containing the run ID, relative bundle path and
   exact manifest hash. Atomically replace `examples/current-run.json` **last**.

The atomic pointer replacement is the bundle-level completion boundary. Failures
before it leave the previous pointer and run intact. A first-run failure leaves
no current pointer. A failure after directory publication may leave an unreferenced
complete run. Interrupted staging directories and unreferenced runs are ignored.
Concurrent writers have different UUIDs; the last successful pointer swap wins.

Files use LF line endings, including in Git checkouts, so exact-byte digests stay
stable. File flushes and atomic local renames address write/process failures;
they do not guarantee recovery from power loss on every filesystem or atomicity
on arbitrary network filesystems. Old runs are retained and no automatic cleanup
can remove a run while a reader still uses it.

## Consumer protocol

Use `exporter.bundle.validate_current(base)` to read the pointer once. It validates
its schema and relative path, pins its manifest hash, reads the referenced immutable
bundle, and checks all file hashes, lengths, run identities and document semantics.
It rejects missing files, unknown versions, path traversal, mixed runs, tampering,
invalid coverage claims and provenance that names a different artifact/revision.

Consume only the returned `documents` or `bytes` snapshot. Reopening the pointer
or individual files after validation would introduce a new read outside the checked
snapshot. For an intentionally selected older run, `validate_bundle(directory)`
checks internal coherence; callers must separately establish why that run is the
desired one. CLI `python exporter/export.py --validate` validates the current run.

The pointer is the local publication authority, not a digital signature. An attacker
who can replace all files and recompute hashes can fabricate a coherent bundle.
Replay protection, external trust and authenticated distribution are out of scope.

## Future historical provenance

Derived approval timing must retain approver, distinct commit actor, exact
transition ID, from/to states, supporting revision, commit timestamp and retrieval
source. It is persisted change time, not verified user action time. Unknown timing
retains null evidence and a reason. Never substitute latest modification time.
Historical values do not establish historical membership; secure comment references
may change or disappear. See the [mapping contract](mapping-specification.md).
