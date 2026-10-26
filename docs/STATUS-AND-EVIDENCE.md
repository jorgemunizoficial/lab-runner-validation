# Estado e evidências — verificáveis e delimitados

**Estado atual nesta documentação:** `EXPERIMENTAL_SYNTHETIC / CANDIDATE_INERT / NO_GO_OPERATIONAL`.

## Campanha E01–E07: resultados de workflow

| Experiência | Run público | Limite da evidência |
| --- | --- | --- |
| E01 | [40152605636](https://github.com/jorgemunizoficial/lab-runner-validation/actions/runs/40152605636) | Inventário observado em runner efêmero |
| E02 | [40153095163](https://github.com/jorgemunizoficial/lab-runner-validation/actions/runs/40153095163) | Worker Docker sintético |
| E03 | [40153350108](https://github.com/jorgemunizoficial/lab-runner-validation/actions/runs/40153350108) | Restrições e interrupção sintéticas |
| E04 | [40159327555](https://github.com/jorgemunizoficial/lab-runner-validation/actions/runs/40159327555) | Watchdog local não independente |
| E05 | [40172457827](https://github.com/jorgemunizoficial/lab-runner-validation/actions/runs/40172457827) | T1–T4 sintéticos |
| E06 | [40173168955](https://github.com/jorgemunizoficial/lab-runner-validation/actions/runs/40173168955) | T5–T8 sintéticos |
| E07 | [40173447134](https://github.com/jorgemunizoficial/lab-runner-validation/actions/runs/40173447134) | T9–T12 sintéticos |

Os sete runs foram observados com conclusão `success`. Eles **não constituem execução N1–N8** nem provam isolamento completo do host. O executor candidato ainda não foi rodado.

## Candidato integral

- [Workflow candidato fixado](https://github.com/jorgemunizoficial/lab-runner-validation/blob/3a2054467c741138531a95104fee351ade614d48/.github/workflows/lab-batch-validation.yml)
- Commit: `3a2054467c741138531a95104fee351ade614d48`.
- Blob Git: `14d7c2f1ea3238377a8f2a593dcb91777b9d3e80`.
- `workflow_dispatch` e guard literal `false`; sem execução do candidato nessa baseline.

## NÃO COMPROVADO

N1–N8 íntegros em uma campanha; independência de supervisor diante de falha do host; proibição de egress do host; quotas end-to-end declaradas versus impostas; custo zero em todas as situações; cadeia de custódia operacional. Não converter `success` dos smokes em aprovação operacional.

[Voltar ao README](../README.md) · [Roadmap](ROADMAP.md)
