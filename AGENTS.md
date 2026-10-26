# Regras para agentes — Public Synthetic Runner LAB

> Repositório **público**, exclusivo para código e provas **100% sintéticos**. Não confundir com ambientes institucionais, infraestrutura compartilhada ou qualquer sistema real.

## Antes de atuar

1. Ler `README.md`, `docs/GOVERNANCE.md`, `docs/SECURITY-AND-CUSTODY.md`, `docs/STATUS-AND-EVIDENCE.md` e a autorização expressa da missão.
2. Conferir o SHA completo e a branch autorizada. Não assumir que `main` ou o último commit substitui um candidato fixado.
3. Registrar qual workflow, ação, arquivo e resultado estão realmente cobertos. Separar **FACT**, **INFERENCE**, **NOT_PROVEN** e **NOT_EXECUTED**. Um resultado de teste sintético não comprova implantação, proteção do host ou sistema real.
4. **Nenhum agente se autoautoriza** a executar Actions, testes, dispatch, despesas, PR, merge, deploy, modificação de permissions/secrets ou workflows. Solicitar aprovação específica ao responsável pelo repositório.
5. Nunca adicionar dados reais, credenciais, endereços internos, código privado, documentos internos, imagens de sistemas privados ou evidência restrita ao repositório público. Inspecionar o diff antes de cada push.
6. Manter recursos e cenários de outros agentes intocados. Cleanup estritamente de recursos próprios identificados; não executar recuperação ou correções sobre a fundação de terceiros.
7. Para mudanças de escopo técnico: analisar todos os achados, entregar **uma correção consolidada**, não microcorreções parceladas. Reutilizar PASS válidos quando a mudança não os afeta.
8. A branch `lab/hsinf01-integral-executor-candidate-20261025` contém um candidato **inerte**; preservar literalmente `if: ${{ false && ... }}` e `workflow_dispatch` exclusivo até autorização separada, independentemente da branch de documentação.
9. Não repetir E01–E07 / T1–T12 só para reproduzir números. N1–N8 permanecem **NOT_EXECUTED** como campanha integral.
10. A documentação pode ser revista estaticamente; nenhum arquivo Markdown representa autorização de execução.

**HOLD** quando faltar autorização, acesso, prova, contenção ou clareza de propriedade.
