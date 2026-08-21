# Seat list — Hardware Engineering (role → agent)
The change-record template (core) names gate ROLES; hardware runs its own PDR/CDR/MRR gates. Mapping:
- security: N/A: no software auth surface (see rf-connectivity for radio security where relevant)
- privacy: N/A
- compliance: compliance-cert (regulatory/safety certification)
- domain: compliance-cert
- schema: N/A: no data schema
- operational-readiness: reliability-dfr (design-for-reliability / field readiness)
- ux: N/A
- quality: manufacturing-dfm (DFM/test/acceptance)
- review: hw-design-reviewer (adversarial gate before any board spin / firmware release)
