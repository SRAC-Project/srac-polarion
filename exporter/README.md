# Exporter

Run `python exporter/export.py` from the repository root, or `python export.py`
from this directory. Python 3.9+ and its standard library are sufficient.

`config.json` supplies `sourceInstance`, `projectId`, and `exportTime`.
The generator writes `generated-export.json`, `generated-provenance.json`, and
`generated-coverage.json` to the repository's `examples/` directory regardless
of the working directory. These are deterministic synthetic artifacts, not live
Polarion evidence. Coverage reports gaps explicitly and provenance records the
export file's SHA-256 digest.

`rest_client.connect()` and `soap_client.connect()` only print a placeholder.
They make no connection and are not invoked by the offline generator.
Live REST/SOAP integration and a sanitized real demo export await Petr's review.

See the [main README](../README.md) for configuration, output semantics, planned
integration scope, and verification instructions.
