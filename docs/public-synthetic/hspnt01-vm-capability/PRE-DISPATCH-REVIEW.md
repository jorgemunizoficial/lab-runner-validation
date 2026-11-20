# HSPNT01 | Pre-dispatch review record

Status: **NOT_APPROVED_TO_DISPATCH**. This is a preparation checklist, not a record of passing any gate.

| ID | Required precondition | Current evidence |
|---|---|---|
| G0 | exact source commit, branch and workflow reviewed | branch prepared, final SHA to cite from publication |
| G1 | PO explicit permission for **one specific workflow_dispatch** | NOT_GRANTED (preparation permission only) |
| G2 | HSPVD01 independent review of the public workflow and risks | PENDING |
| G3 | GitHub-hosted runner and billing/minutes eligibility confirmed | NOT_PROVEN |
| G4 | no secrets, private checkout, private inputs, artifacts, third-party actions or network tests | STATIC_DECLARED; independent verification pending |
| G5 | independent observation and evidence custody/retention | NOT_DEFINED |
| G6 | cost/network STOP conditions and cleanup responsibility | NOT_DEFINED |
| G7 | repository branch protections/review requirements effective | NOT_PROVEN |
| G8 | P01-P08 criteria not confused with host inventory | DOCUMENTED; actual VM remains NOT_PROVEN |

Each unmet criterion blocks dispatch. No administrative settings changes, writes to `main`, Actions dispatch, artifact upload or chargeable resources authorized by this file.

See `docs/public-synthetic/PRE-DISPATCH-STATIC-GATE.md` and `PUBLIC-SYNTHETIC-SCENARIO-CONTRACT.md`.
