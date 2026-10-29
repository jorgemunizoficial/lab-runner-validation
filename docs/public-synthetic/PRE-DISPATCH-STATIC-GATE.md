# Public Synthetic Pre-dispatch Gate

This is a fail-closed, manually recorded checklist, **not** execution authorization.

For each proposed run, independently verify:

- [ ] Repository and exact immutable source commit recorded; intended workflow contents reviewed.
- [ ] Explicit approval exists for this precise public synthetic run and its resource budget.
- [ ] Runner is a standard public hosted runner; free-plan eligibility or an approved zero-billable path is confirmed for this run.
- [ ] Workflow is manual-only with `contents: read` and no privileged token, secret usage, private checkout, hidden trigger, artifact upload or cache.
- [ ] No private or personally identifying material in repository content, workflow names, inputs, logs or destinations.
- [ ] All images are digest-pinned; any external action is pinned to a reviewed full commit.
- [ ] Worker ownership, bounds, network isolation, stop condition and recovery responsibilities are documented.
- [ ] An observer outside the worker failure domain, evidence custodian and independent reviewer are designated and the observation method is accepted.
- [ ] A sanitized receipt destination and retention policy exist; costs and unexpected network use have explicit STOP conditions.
- [ ] Repository protection and review requirements are effective, and any remaining limitations are documented.

**Any missing, failed or unverifiable essential gate: STOP. Do not dispatch.**
The existence of this file is not proof that any listed gate has passed.
