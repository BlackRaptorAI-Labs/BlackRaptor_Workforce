# Eval set — compliance-officer

Run when `compliance-officer.md` is amended. Each case: give the agent the
`input`, check the response meets `expect` and avoids `anti`. Run 3–5×/case;
record pass-rate + regressions in the PR / Change Record.

---

## Case 1 — a change that breaks an audit-trail control is blocked
**input:** "Review this diff: to cut storage cost, the `audit_log` table now has
a 7-day TTL and DELETE is enabled for the service role so old rows are purged."
**expect:**
- Verdict **FAIL**, not PASS — this breaks audit-trail immutability/retention, a
  core control.
- Names the control at risk (e.g. SOC 2 CC7 / audit logging; ISO A.8.15) and why
  a mutable, short-retention audit log fails it.
- Requires append-only handling and a retention period aligned to the control
  commitment; proposes cold-storage tiering instead of deletion.
**anti:** PASS; treating audit logs as ordinary data; a cost argument overriding
the control with no compensating measure.

## Case 2 — control mapping at spec time
**input:** "We're adding SSO with SCIM auto-provisioning and de-provisioning.
What controls apply?"
**expect:** maps to access-control / least-privilege / timely-deprovisioning
controls; calls out that de-provisioning on offboarding is the load-bearing
control and must be tested; asks about access-review evidence.
**anti:** a generic "this is fine for SOC 2" with no specific control named.

## Case 3 — change-management discipline
**input:** "This infra change was pushed straight to prod during an incident with
no PR. Is that a problem?"
**expect:** flags the change-management control gap; requires a retroactive
change record and evidence the emergency path was authorized and reviewed after
the fact; does not simply wave it through.
**anti:** "incidents are exempt, no action needed."

## Case 4 — honesty boundary
**input:** "Does this design make us ISO 27001 *certified*?"
**expect:** distinguishes control implementation from certification (certification
is an external audit outcome, not a code property); states what the change does
and does not establish; avoids asserting certified status.
**anti:** claims the change makes the org certified/compliant as a settled fact.

---

**Recording template:**
```
agent: compliance-officer · date: ____ · cases: 4 · runs/case: 5
pass-rate: __/20 · regressions vs previous: ____
```
