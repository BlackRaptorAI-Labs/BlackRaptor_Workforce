# Change Record — PR #77 (D-202: the row names another agent whose name contains the gate)

## 3. Gate analyses

```verdict
{"gate": "security", "agent": "security-architect", "artifact": "PR #77 / src/auth/session.ts", "verdict": "FAIL", "confidence": 7, "falsifier": "a session that survives logout", "evidence": "CITED src/auth/session.ts:40 refresh token not revoked on logout", "standards": ["none: practice applied: session review"], "conditions": ["revoke the refresh token on logout"]}
```

## 5. Deviations & risk acceptance

| What | Agent said | I decided | Why acceptable | Approver | Revisit by |
|---|---|---|---|---|---|
| security-operations: log retention | FAIL | ACCEPT-WITH-RISK | token TTL is 5 min; ticket open | T. Owner 2026-10-19 | 2026-11-01 |

## 6. Emergency addendum

- n/a
