Polarion to SRAC Mapping Specification v0.1
Purpose
This document defines a reference mapping between Polarion engineering artifacts and SRAC evidence records.

The exporter is read-only and uses Polarion REST and SOAP interfaces.

Artifact Identity
Polarion	SRAC
Polarion Instance	sourceInstance
Project ID	projectId
Work Item ID	objectId
Revision	resolvedRevision
Extraction Time	extractionTime
Notes:

Resolved revision and extraction time are separate values.
Object identity is preserved from the source system.
Work Items
Polarion	SRAC
Requirement	Assertion Subject
Hazard	Assertion Subject
Test Case	Verification Evidence
Change Request	Evidence Artifact
Links
The exporter preserves:

Source artifact
Target artifact
Link role
Link direction
Suspect status
Target project
Target revision
Collections
Collections are exported separately from Baselines.

The exporter preserves:

Collection identifier
Member artifacts
Member revisions
Baselines
Baseline exports include:

Baseline identifier
Baseline revision
Referenced artifacts
Collections and Baselines are not treated as equivalent objects.

Approvals
The exporter records:

Approver identity
Approval state
Evidence source
Ordinary approval state is not treated as a workflow signature or electronic signature.

Approval Timing
Approval timing may be derived from historical repository evidence.

When available:

Repository commit timestamp is recorded.
Provenance source is documented.
When unavailable:

Approval timing is reported as Unknown.
Historical Retrieval Limitations
When historical evidence is retrieved using SOAP queryWorkItemsInRevision:

Historical field values may be available.
Historical collection membership may not be reconstructable.
Subsequently deleted work items may not be returned.
Provenance
Every exported record includes:

Source system
Project
Revision
Extraction timestamp
Evidence Coverage
Coverage is reported independently from exported evidence.

States:

Complete
Partial
Unavailable
Missing evidence is reported explicitly.

Evidence Integrity
SHA-256 digests provide integrity verification only.

They do not establish:

Evidence completeness
Approval validity
Safety compliance
Regulatory compliance
