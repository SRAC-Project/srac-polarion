# Offline exporter

Run `python exporter/export.py` at the repository root, or `python export.py`
from this directory. Run the same command with `--validate` to check the current
completed bundle. Python 3.9+ and its standard library are sufficient.

`config.json` provides synthetic metadata only. `export.py` generates the strict
project-specific proposed evidence fixture profile 0.2.0. `contract.py` checks the
versioned schema and cross-file invariants. `bundle.py` stages all three artifacts,
publishes an immutable run and atomically changes `examples/current-run.json` last.
Consumers must use `validate_current()` and its returned checked snapshot.

`history.py` exercises conservative rules on normalized synthetic transitions.
It performs no retrieval. `rest_client.connect()` and `soap_client.connect()`
remain placeholders. Live extraction requires separate implementation, target
capability checks and independently checked expected results.

See the [main README](../README.md), [contract](../docs/mapping-specification.md)
and [publication protocol](../docs/provenance-model.md).
