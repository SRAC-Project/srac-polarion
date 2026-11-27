# SRAC Polarion Exporter

Independent, offline executable PoC for **project-specific proposed evidence
format 0.2.0**. Every supplied example is synthetic. No adopted external SRAC
schema, interoperability, live extraction, Polarion X compatibility, safety
certification, or Siemens endorsement has been established.

## Run and validate

Python 3.9+ and the standard library are sufficient. From the repository root:

```bat
python exporter\export.py
python exporter\export.py --validate
```

Use forward slashes on other platforms, and `python3` where appropriate.
`python export.py` from the repository root or the `exporter` directory also
works. Paths resolve relative to the script, independently of the working directory.

Edit `exporter/config.json` for the synthetic source instance, project ID and
timezone-qualified `exportTime`. This configured time becomes `extractionTime`;
it is separate from the synthetic repository revision. No credentials belong here.

## Completed output bundles

Each successful invocation assigns a new UUID run ID and publishes:

```text
examples/current-run.json
examples/runs/<runId>/manifest.json
examples/runs/<runId>/generated-export.json
examples/runs/<runId>/generated-provenance.json
examples/runs/<runId>/generated-coverage.json
```

The three artifacts form one immutable run. The manifest records their SHA-256
hashes and byte counts. The pointer records the manifest hash and run ID. It
changes atomically only after every staged file has been written and validated.
A failed generation leaves the previous completed run selected. Interrupted
staging directories or unreferenced runs must not be consumed as current output.

Consumers must call `exporter.bundle.validate_current(Path("examples"))` and use
the returned `documents` or `bytes` snapshot. It checks the contract, shared run
identity, metadata, hashes, counts and selection before returning evidence. The
CLI `--validate` performs the same checks. Do not independently reopen files after
validation or resolve the pointer separately for each file.

**Migration from 0.1:** independently overwritten `examples/generated-*.json`
files have been removed. Resolve `current-run.json`; there are deliberately no
mutable top-level aliases. UUIDs change each run even for identical fixture inputs.
These local atomic rename semantics do not promise power-loss durability on every
filesystem, cryptographic authenticity, or protection from a malicious publisher.

## Contract and evidence rules

- [Mapping and format contract](docs/mapping-specification.md)
- [JSON Schema](schemas/proposed-evidence-0.2.0.schema.json)
- [Coverage definitions](docs/evidence-coverage.md)
- [Provenance and publication protocol](docs/provenance-model.md)
- [Live pilot scope and expected-results plan](docs/live-pilot-plan.md)
- [Review corrections](docs/review-corrections.md)

The current contract is a strict **synthetic fixture profile**. The generator
exports one requirement, one outgoing link to an unexported test definition, and
an ordinary approval state. Classification, acceptance, approval timing and
historical membership remain unknown. Live adapters remain placeholders. Future
live records require a reviewed contract revision; changing `dataOrigin` alone
cannot turn this fixture into verified evidence.

Historical helper tests cover reset/reapproval transitions, commit actor versus
approver, membership limitations, mutable secure-comment references and test
definitions versus executions. They verify local rules against invented inputs,
not the correctness or completeness of any Polarion API retrieval.

## Examples and presentation

Each top-level JSON reference example independently declares its synthetic origin,
format version and limitations. These are copies of the checked-in representative
run, not independently consumable live evidence. See [examples](examples/README.md).
The editable presentation in `presentations/` uses the same contract and includes
a clearly labeled literal subset of the generated export with matching field names.

## Verification

```bat
python -m unittest discover -s tests -v
```

Tests include publication failures at each write and rename boundary, concurrent
writers, missing/tampered files, mixed run IDs, contract violations and historical
evidence rules. Runtime validation supports exactly the schema vocabulary used by
the checked-in contract; it is not a general JSON Schema engine.

## License and independence

Licensed under [Apache-2.0](LICENSE). Contributions intentionally submitted for
inclusion follow that license unless separately agreed. Do not submit credentials
or unauthorized source data. Report defects with sanitized reproductions.

This independently maintained project is not affiliated with, endorsed by,
certified by or maintained by Siemens. Polarion is a trademark of Siemens Digital
Industries Software. Ordinary approvals and workflow states do not establish
safety acceptance, signature validity, safety compliance or regulatory compliance.
