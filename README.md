# SRAC Polarion Exporter

An executable, offline proof of concept for representing Polarion engineering
evidence as SRAC-compatible records, with provenance and coverage reports.

## Usage

Requires Python 3.9 or newer. No packages, credentials, or Polarion server are needed.
From the repository root:

```bat
python exporter\export.py
```

On other platforms, use `python exporter/export.py` (or `python3`).
The root shortcut `python export.py` also works. From the `exporter` directory,
`python export.py` runs the same exporter. Paths are relative to the script.

Expected outputs:

```text
examples/generated-export.json
examples/generated-provenance.json
examples/generated-coverage.json
```

Edit `exporter/config.json` to set the demonstration metadata:

```json
{
  "sourceInstance": "polarion-demo",
  "projectId": "SAFETY-DEMO",
  "exportTime": "2026-11-20T12:00:00Z"
}
```

`exportTime` must be an ISO 8601 timestamp with a timezone. It becomes
`extractionTime` in each artifact, separate from the synthetic revision.
The same configuration produces byte-identical files. Each run overwrites only
the three generated files. Original sample reports remain reference examples.
Invalid configuration produces an error and a nonzero exit code before writing;
any existing generated files remain from the preceding successful run.

The generated export contains one synthetic requirement, an outgoing test-case
link, and an ordinary approval state. The linked test case is not exported.
All generated artifacts identify the data as synthetic. Approval timing is unknown.
Coverage describes the demonstration record, not live extraction completeness.
Provenance includes a SHA-256 digest of the exact export file bytes; this verifies
integrity only, not completeness, approval validity, or compliance.

## Repository structure

- `docs/`: mapping specification and evidence model documents.
- `examples/`: original reference samples and generated demonstration artifacts.
- `exporter/`: configuration, offline generator, and REST/SOAP placeholders.
- `presentations/`: project presentation.
- `tests/`: verification using the Python standard library.

Run verification from the repository root:

```bat
python -m unittest discover -s tests -v
```

## Integration status

The executable PoC makes no network calls. `exporter/rest_client.py` and
`exporter/soap_client.py` expose placeholder `connect()` functions and are not
called by the offline generator. They establish the intended adapter boundaries.

Live integration is deferred until Petr reviews:

- REST: work items, links, projects, attachments, comments, and approvals.
- SOAP: history, baselines, approval change history, secure approval comment IDs,
  and revision information.

After review and live integration, a sanitized export from a Polarion Demo Project
can be produced as `real-export.json`. It is not part of this milestone.
See [the mapping specification](docs/mapping-specification.md) for the proposed model.
Existing reference samples illustrate that model and are not proof of live extraction.

## Disclaimer

This project is independently maintained. It is not affiliated with, endorsed by,
certified by, or maintained by Siemens. Polarion is a trademark of Siemens
Digital Industries Software. The exporter does not provide safety or compliance
certification.
