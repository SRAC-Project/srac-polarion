# Illustrative synthetic demonstration report

**No live extraction was performed.** This report describes the offline generator
using project-specific proposed evidence format 0.2.0. It does not demonstrate SRAC
interoperability, Polarion X compatibility, certification or Siemens endorsement.

The generator invents REQ-001 at revision 1250, a link to unexported TC-001, and an
ordinary approval state. It retrieves no data through REST or SOAP. The configured
extraction timestamp is demonstration metadata. Classification, acceptance,
approval timing and historical membership remain unknown.

| Demonstration category | Coverage within the one-fixture scope |
| --- | --- |
| Artifact identity and required Work Item fields | complete |
| Ordinary approval identity/state | complete |
| Relationships | partial; one outgoing link and unexported target |
| History, timing, membership and test executions | unavailable |
| Collections, baselines, projects, attachments and comments | unavailable |
| Live revision information and secure approval comment IDs | unavailable |
| Workflow and electronic signatures | unavailable |

Complete means required category fields for this synthetic fixture only. It does
not mean complete extraction from a Polarion project. Pagination, permissions and
historical retrieval are explicitly not attempted.

Use `current-run.json` and the bundle validator to consume all three generated
artifacts from one completed run. The manifest hashes each file, and the pointer
pins the manifest. The top-level reference JSON files are illustrative copies,
not publication pointers. Hashes establish byte integrity only.
