# Change Record — PR #77

## 3. Gate analyses

```verdict
{"gate": "review", "agent": "code-reviewer", "artifact": "PR #77 / src/auth/session.ts", "verdict": "PASS", "confidence": 7, "falsifier": "a session that survives logout", "evidence": "MEASURED `npm test` 120 passed; diff read at src/auth/session.ts:1-80", "standards": ["none: practice applied: session review"]}
```

```verdict
{"gate": "security", "agent": "security-architect", "artifact": "PR #77 / src/auth/session.ts", "verdict": "FAIL", "confidence": 7, "falsifier": "a session that survives logout", "evidence": "CITED src/auth/session.ts:40 refresh token not revoked on logout", "standards": ["none: practice applied: session review"], "conditions": ["revoke the refresh token on logout"]}
```

## 5. Deviations & risk acceptance

| What | Agent said | I decided | Why acceptable | Revisit by |
|---|---|---|---|---|
| privacy: unrelated note | PASS | ACCEPT | n/a | n/a |

## 6. Emergency addendum

- n/a
