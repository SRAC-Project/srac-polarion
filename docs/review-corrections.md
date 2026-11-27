# Technical review corrections

This change addresses the supplied review without claiming reviewer approval.

| Requested correction | Implementation and verification |
| --- | --- |
| Individually label older examples and qualify mapping | Every evidence JSON has required synthetic origin/notice, offline retrieval method and explicit version; extraction report and mapping identify proposed behavior |
| Explicit versioned format | Project-specific proposed format 0.2.0, strict JSON Schema, runtime contract checks, populated coverage/provenance documents and aligned slide example |
| Historical evidence rules | Normalized-fixture helpers and tests for distinct actors, resets/reapprovals, supported transition/revision, historical membership limits, mutable comments and test definitions |
| Coherent run publication | Immutable run directory, manifest hashes and shared run ID, atomic pointer publication, checked consumer snapshot, injected write/rename failures and tamper tests |
| Bounded first live milestone | Target capability checks and independent expected-results plan covering directional/cross-project links, unresolved targets, permissions, pagination and history |
| Reuse terms and positioning | Apache-2.0 license, independent project disclosure and explicit limits on interoperability, compatibility, certification and endorsement claims |

The output change from top-level generated files to `current-run.json` plus immutable
run directories is intentional and documented in the README. The presentation's
filename remains unchanged for existing links; its content identifies contract 0.2.0.

Remaining work: choose and access an authorized target, verify supported APIs,
implement a reviewed live profile and adapters, and execute the independent pilot.
Passing local synthetic tests does not establish those capabilities.
