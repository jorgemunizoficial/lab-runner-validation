# Public Synthetic Scenario Contract

Status: repository-level policy for public, manually invoked experiments.

## Scope
- Only independently authored, artificial inputs may be committed, supplied as workflow inputs or shown in logs.
- No confidential or private code, personal records, tokens, credentials, private endpoints, private configuration, backups or forensic materials may be uploaded or used.
- Public workflow source, inputs, names, stdout/stderr, caches and artifacts are treated as publicly visible.
- Each scenario needs a unique run-scoped identifier, fixed public source revision, documented owner and narrowly bounded resource use.
- Only `workflow_dispatch` is permitted. The workflow token must default to `contents: read`; no secret-dependent jobs, private checkouts, SSH connections or unreviewed third-party actions.
- Container images must be pinned by digest; third-party actions, if introduced in future, must be pinned to reviewed full commit hashes.
- Containers must operate only on resources positively identified as owned by the current run. Uncertain ownership blocks deletion; never remove resources by broad name prefixes.
- No public artifact upload or cross-run cache by default. Any exception requires separate approval before execution.

## Admission
This document does **not** authorize running workflows. An individually approved execution must pass the pre-dispatch gate and establish observation, retention, cost and cleanup controls. A passing synthetic check does not establish production or private-system readiness.
