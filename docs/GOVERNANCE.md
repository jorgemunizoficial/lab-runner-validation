# Governança do laboratório público

## Autoridade e separação

Este repositório é uma instalação experimental pública sob controle do proprietário da conta. **Leitura pública não é autorização de escrita ou execução.**

| Atividade | Responsabilidade |
| --- | --- |
| Definir objetivo e escopo | Proprietário / responsável pela autorização |
| Desenvolver fixtures e código sintético | Agente explicitamente autorizado |
| Conferir políticas, isolamento e limites | Revisão técnica independente |
| Aprovar execução, gastos, PR e merge | Proprietário |
| Auditar evidências | Revisor distinto do executor |

## Portões

1. **Fonte:** ref/commit e conteúdo fixados; apenas material publicável.
2. **Admissão:** gatilho, permissões e escopo autorizados separadamente.
3. **Recursos:** host, worker, limites e propriedade demonstráveis.
4. **Execução:** somente após autorização expressa; sem inferir GO de documentação.
5. **Custódia:** provas e hashes têm proveniência e limites claros.
6. **Encerramento:** cleanup restrito e reconciliação de resíduos antes de qualquer próximo ciclo.

## Política de alterações

- Mudanças de apresentação são distintas de mudanças em workflows.
- A branch de documentação não modifica nem dispara Actions.
- Preservar a `main` e os commits históricos até decisão explícita.
- Correções técnicas: análise única consolidada; não repartir defeitos relacionados em ordens sucessivas.
- Usar `PASS / FAIL / NOT_PROVEN / NOT_EXECUTED / BLOCKED` de maneira estrita; `success` do GitHub não equivale a homologação integral.

## Fonte de verdade

Commits e conteúdos do próprio repositório constituem o registro **público**. Não importar ordens, documentos ou dados de outras organizações ou repositórios privados.

[Voltar ao README](../README.md) · [Handover](HANDOVER.md)
