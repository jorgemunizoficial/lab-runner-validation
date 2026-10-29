# Public Synthetic Post-run Receipt Template

Complete only after an explicitly authorized run; keep all fields public-safe.

| Field | Recorded value |
|---|---|
| Public repository | |
| Workflow path | |
| Immutable commit SHA | |
| Run ID and attempt | |
| Start/completion timestamps | |
| Runner class and approved budget | |
| Workflow conclusion | |
| Planned / attempted / passed / failed / not-executed checks | |
| Observed resource limits and timings | |
| Independent observer evidence reference | |
| Owned resource cleanup result and known residuals | |
| Sanitized public run URL | |
| Reviewer and custody reference (non-sensitive) | |
| Evidence completeness | PASS / FAIL / NOT_PROVEN |

Do not copy credentials, private records, private source paths, confidential URLs, raw sensitive logs or protected artifacts into this receipt.

A public synthetic PASS does not certify private, production, host/provider-independent, or end-to-end controls. If evidence is incomplete or guardian observation is absent, record **NOT_PROVEN** and block the next run.
