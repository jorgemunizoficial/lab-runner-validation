# Continuidade — passagem entre agentes

Este material permite que qualquer agente autorizado compreenda o laboratório sem conhecer conversas ou ambientes privados.

## Ordem de leitura

1. [README](../README.md) — objetivo, estado e histórico.
2. [Governança](GOVERNANCE.md) e [Regras para agentes](../AGENTS.md).
3. [Arquitetura](ARCHITECTURE.md) e [Segurança e custódia](SECURITY-AND-CUSTODY.md).
4. [Estado e evidências](STATUS-AND-EVIDENCE.md) — o que foi observado versus não provado.
5. [Roadmap](ROADMAP.md) — sequência futura.

## Bases públicas fixadas

- Base `main` da revisão documental: `05c938340ed29f05ca5684ad5ecde7c068d89123`.
- Candidato integral inerte: `3a2054467c741138531a95104fee351ade614d48`.
- Arquivo do candidato: `.github/workflows/lab-batch-validation.yml`; blob Git `14d7c2f1ea3238377a8f2a593dcb91777b9d3e80`.
- Branch documental isolada: `docs/public-lab-repository-presentation-20261026`.

## Protocolo de retomada

Conferir novamente ref, branch e diff antes de escrever, porque versões podem mudar. Não restaurar `main` por conveniência nem reexecutar PASS antigos. Se o candidato divergiu, **HOLD / CONFLICT** com as duas versões identificadas.

Transferir apenas o escopo da nova missão, com ledger de arquivos, commit, hash e resultados verificados. A documentação deste repositório **não concede permissão** para rodar o executor ou publicar dados reais.

## Limites de sucessão

O nome de qualquer agente, seu ambiente de provisionamento e sua conta são externos ao Git; acesso de outro agente deve ser demonstrado naquele ambiente. Manter o histórico técnico, não identidade ou credenciais de terceiros.
