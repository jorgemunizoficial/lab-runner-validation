# Roadmap — laboratório sintético público

| Marco | Escopo | Estado |
| --- | --- | --- |
| E01 | Inventário básico do runner efêmero | SUCCESS sintético |
| E02 | Worker Docker e isolamento inicial | SUCCESS sintético |
| E03 | Restrições do container e parada | SUCCESS sintético |
| E04 | Watchdog local e limpeza | SUCCESS sintético |
| E05 | T1–T4, quotas e preservação de outro cenário | SUCCESS sintético |
| E06 | T5–T8, revogação e integridade artificial | SUCCESS sintético |
| E07 | T9–T12, egress artificial e falha/cleanup | SUCCESS sintético |
| Candidato | Arquivo único de matriz integral em branch isolada | Criado / INERTE |
| Revisão integrada | Cobrir deficiências F1–F4, L2, N1–N8 | Pendente |
| Campanha N1–N8 | Testes nativos e evidência independente | **NOT_EXECUTED** |
| Decisão operacional | Aceite fundamentado pelo proprietário | **NO_GO** |

## Etapas seguintes

**M1 — prontidão estática:** completar revisão única de código, limites efetivos e matriz de provas. Não repetir E01–E07 sem alteração relevante.

**M2 — gate humano:** revisar custos, segurança e permissões; só então decidir se é aceitável habilitar futuramente o fluxo.

**M3 — campanha nativa integral:** se houver autorização explícita, executar uma campanha única com N1–N8, propriedades e evidência por cenário. Nenhum PASS por analogia.

**M4 — revisão independente:** conferir resultados, resíduos e cadeias de custódia antes de qualquer mudança de estado.

O roadmap não representa ordem de execução.

[Voltar ao README](../README.md)
