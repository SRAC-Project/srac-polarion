# Synthetic examples

Every JSON evidence example independently identifies itself as synthetic,
project-specific proposed evidence format 0.2.0. None records a live extraction.

- `sample-export.json`, `coverage-report.json` and `provenance-report.json` are
  illustrative copies of the checked-in representative run. They are reference
  documents, not a mutable publication mechanism. Their individual notices and
  coverage scope remain visible when opened separately.
- `extraction-report.md` describes only the offline demonstration.
- `current-run.json` selects the completed bundle under `runs/<runId>/`.

Generate and validate using `python exporter/export.py` and the same command with
`--validate`. Consumers must use `exporter.bundle.validate_current()` and the checked
snapshot it returns. Do not search for the latest directory or combine files from
different runs. A run contains the three `generated-*.json` files and `manifest.json`.

The old top-level `generated-*.json` aliases were removed in 0.2.0 to avoid mismatched
evidence after failures. A new invocation creates a new UUID and leaves existing
reference copies unchanged. The checked-in reference copies intentionally continue
to describe their original representative run after subsequent local invocations.
