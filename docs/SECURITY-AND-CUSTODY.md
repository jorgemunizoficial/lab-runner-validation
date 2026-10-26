# Segurança, privacidade e custódia

## Fronteira de publicação

**Público significa publicável.** Não usar dados de pessoas, organizações, hotéis, clientes, infraestrutura interna, repositórios privados, chaves, identificadores sensíveis ou logs de terceiros. Fixtures devem ser geradas com valores artificiais verificáveis.

## Restrições fundamentais

- `permissions: contents: read` é o máximo necessário para o candidato atual; revisar qualquer aumento.
- Somente gatilho manual no candidato integral; guard `if: ${{ false && ... }}` permanece desabilitado.
- Container sem rede (`--network none`) e sem Docker socket; isso não isola necessariamente o host.
- Não tocar em recursos não identificados como pertencentes ao cenário. Stop, cleanup e recovery devem operar apenas sobre prefixos/ledgers próprios.
- Prova de egress exige observação adequada; erro de requisição HTTP isolado não comprova política eficaz.
- SHA-256 de fixture demonstra integridade dos bytes comparados, **não** autoria, segurança, autenticidade geral nem validade jurídica.
- Logs são públicos; nunca ecoar env, tokens, caminhos confidenciais, dumps, payloads privados ou headers sensíveis.
- Não habilitar cache, upload de artefatos, serviços terceiros ou endpoints externos sem nova revisão e autorização.

## Modelo de evidência

Para cada caso futuro: commit e fixture fixados, expectativa, mecanismo de observação, condição negativa, resultado, limites e cleanup. Classificar fatos por `PASS / FAIL / NOT_PROVEN / NOT_EXECUTED / BLOCKED`.

**Incidentes:** se surgir dado real ou violação de ownership, suspender alterações e solicitar decisão. Não apagar históricos ou evidências indiscriminadamente.

[Arquitetura](ARCHITECTURE.md) · [Governança](GOVERNANCE.md)
