# Proposed first live milestone

Status: planned, not approved or executed. The current implementation is synthetic.
The following is a bounded read-only evaluation, not a claim of interoperability,
Polarion X compatibility, certification or Siemens endorsement.

## Environment and access

Use the [public Test Drive](https://myaccount.polarion.com/) under your own Siemens
account, or an authorized local evaluation installation. Record server URL, exact
installed version, sample project ID and supported API/authentication capabilities.
Browser access alone does not establish external REST/SOAP or PAT availability.
Use that installation's SDK at `/polarion/sdk/index.html` as the target reference.

If Test Drive lacks required API access, use a local evaluation rather than assuming
a separate Siemens demo server will be provisioned. Follow the supplied installer,
license and prerequisites. If trial registration is unavailable, use the Contact
Sales route on the [Polarion trials page](https://www.siemens.com/en-us/products/polarion/trials/).
Keep a local installation private. The exporter and server on the same machine
do not require access to a Siemens internal network.

Use a separate identity with the minimum necessary read permissions. Configure REST
and its documented authentication only when authorized. For SOAP, verify the target's
documented token-login and returned-session flow before implementing it. Keep all
credentials outside configuration tracked in Git, logs, bundles and presentations.

## Expected-results fixture, prepared independently

An administrator or reviewer should prepare a small authorized sample and record
the expected identities, revisions and transitions in a separate review worksheet
using the UI and target-supported source views. Do not generate the expected
results by calling the same extraction/mapping code under test. Agree scope and
check API capability before extending the format beyond its synthetic profile.

| Case | Expected check |
| --- | --- |
| Selected Work Items and opaque revisions | Exact identities and resolved revisions agree with the independent worksheet |
| Incoming and outgoing links | Direction is relative to the exported item; role and suspect value remain explicit |
| Cross-project link | Target project remains distinct; never replace it with the source project |
| Unresolved or inaccessible target | Keep the reference and reason; no fabricated target or complete-coverage claim |
| Approval, reset, disapproval and reapproval | Correct current decision and last supporting transition/revision |
| Actor differs from approver | Separate identities, retained commit timestamp and source |
| Pagination and limited expansions | Follow every page or report truncation and counts explicitly |
| Permission-limited identity | Report denied/missing evidence rather than treating it as absent or complete |
| Historical values and membership | Distinguish values of current selection from sourced membership, including deleted-item gaps |
| Secure comment replacement/removal | Preserve observations by revision without immutable-signature claims |
| Test definition and execution | Distinct records; no execution or acceptance inferred from a definition or approval |

## Deliverables and exit criteria

Deliver a reviewed live-profile contract revision, sanitized completed bundle,
capability inventory, independent expected/actual comparison, gap report and
reproduction instructions. Zero unexplained identity or transition mismatches are
allowed. Every skipped page, denied resource, unresolved target and historical
limitation needs an explicit entry; a limitation may narrow scope but never silently
improve coverage. Classification and acceptance require explicit source evidence.

Only after these results should the project seek further technical review or
discuss reuse/listing. Environment setup instructions do not constitute PoC approval.
