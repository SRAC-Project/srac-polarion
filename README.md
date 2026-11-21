SRAC Polarion Exporter
Reference implementation for exporting Polarion engineering evidence into SRAC-compatible evidence records.

Overview
This project demonstrates how engineering evidence can be extracted from Polarion using supported REST and SOAP interfaces and represented as interoperable SRAC evidence records.

The implementation is intended as a proof of concept and focuses on:

Artifact identity
Requirements and work items
Traceability relationships
Collections and baselines
Approval evidence
Provenance reporting
Evidence coverage reporting
Objectives
Preserve source-system provenance
Preserve revisions and traceability context
Report evidence gaps explicitly
Avoid overstating evidence completeness
Enable interoperable evidence exchange
Repository Structure
docs/
    Mapping specifications
    Coverage model
    Provenance model

examples/
    Sample exports
    Coverage reports
    Provenance reports

exporter/
    Exporter implementation
Current Status
Proof of Concept

Planned Deliverables:

Mapping Specification
Sample Evidence Export
Coverage Report
Provenance Report
Disclaimer
This project is independently maintained.

This project is not affiliated with, endorsed by, certified by, or maintained by Siemens.

Polarion is a trademark of Siemens Digital Industries Software.
