# Tasks: Limpeza da Documentação com Foco em Conteúdo Vigente

**Input**: Design documents from `/specs/002-docs-limpeza-atualizada/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/documentation-governance.md`, `quickstart.md`

**Tests**: Não há solicitação explícita de TDD/testes automatizados nesta feature; validações serão manuais via checklist de links e consistência documental.

**Organization**: Tarefas agrupadas por user story para permitir implementação e validação independentes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar artefatos de trabalho para inventário e execução da limpeza.

- [ ] T001 Criar diretório de artefatos em specs/002-docs-limpeza-atualizada/artifacts/
- [ ] T002 Criar template de inventário em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T003 [P] Criar template de mapa canônico em specs/002-docs-limpeza-atualizada/artifacts/canonical-topics.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Definir regras-base obrigatórias para classificar, arquivar e manter documentos.

**⚠️ CRITICAL**: Nenhuma execução de user story deve começar sem esta fase concluída.

- [ ] T004 Definir critérios de classificação (vigente/histórico/obsoleto/duplicado) em docs/development/documentation-governance.md
- [ ] T005 Definir política de canonicidade por domínio em docs/development/documentation-governance.md
- [ ] T006 [P] Definir política de revisão periódica e checklist de PR em docs/development/documentation-governance.md

**Checkpoint**: Regras fundacionais prontas; execução por user story pode iniciar.

---

## Phase 3: User Story 1 - Inventário e Classificação da Documentação (Priority: P1) 🎯 MVP

**Goal**: Classificar 100% dos arquivos de documentação com decisão explícita e justificativa.

**Independent Test**: Conferir que todos os arquivos de docs/ aparecem em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md com status e ação.

### Implementation for User Story 1

- [ ] T007 [US1] Levantar lista completa de arquivos em docs/ e registrar em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T008 [US1] Classificar cada documento (vigente/histórico/obsoleto/duplicado) em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T009 [P] [US1] Definir documento canônico por domínio em specs/002-docs-limpeza-atualizada/artifacts/canonical-topics.md
- [ ] T010 [US1] Marcar ação por arquivo (manter/atualizar/arquivar/remover) em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T011 [US1] Registrar justificativas de classificação para casos limítrofes em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md

**Checkpoint**: Inventário e classificação completos, permitindo limpeza segura.

---

## Phase 4: User Story 2 - Estrutura Enxuta e Navegável (Priority: P2)

**Goal**: Deixar a navegação principal apontando apenas para documentação vigente (ou histórica explicitamente identificada).

**Independent Test**: Validar manualmente que docs/INDEX.md, README.md e mkdocs.yml não possuem links quebrados nem referências conflitantes.

### Implementation for User Story 2

- [ ] T012 [US2] Aplicar movimentações de arquivo→arquivo para docs/archive/ conforme inventário em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T013 [US2] Remover arquivos marcados como obsoletos/duplicados conforme inventário em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T014 [P] [US2] Atualizar índice principal de documentação em docs/INDEX.md
- [ ] T015 [P] [US2] Atualizar links de entrada da raiz em README.md
- [ ] T016 [US2] Atualizar navegação do site de docs em mkdocs.yml
- [ ] T017 [US2] Adicionar notas de migração/depreciação para conteúdos arquivados em docs/archive/README-ARCHIVE.md
- [ ] T018 [US2] Executar validação manual de links críticos e registrar resultado em specs/002-docs-limpeza-atualizada/artifacts/link-validation.md

**Checkpoint**: Navegação limpa e consistente, sem links quebrados nos pontos de entrada.

---

## Phase 5: User Story 3 - Governança para Evitar Nova Degradação (Priority: P3)

**Goal**: Estabelecer processo contínuo para manter documentação atualizada após a limpeza inicial.

**Independent Test**: Aplicar checklist de governança em uma mudança de docs e confirmar aderência sem ambiguidade.

### Implementation for User Story 3

- [ ] T019 [US3] Publicar guia oficial de governança documental em docs/development/documentation-governance.md
- [ ] T020 [US3] Incluir processo de atualização documental por feature em docs/development/setup.md
- [ ] T021 [P] [US3] Criar checklist de PR para atualização de documentação em .github/PULL_REQUEST_TEMPLATE.md
- [ ] T022 [US3] Atualizar referência de governança no índice de docs em docs/INDEX.md
- [ ] T023 [US3] Documentar periodicidade de revisão e responsáveis em docs/STATUS-PROJETO.md

**Checkpoint**: Governança ativa para prevenir regressão documental.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Fechar qualidade, consistência e rastreabilidade da entrega.

- [ ] T024 [P] Revisar padronização de linguagem PT-BR nos documentos atualizados em docs/
- [ ] T025 Verificar coerência entre inventário, mapa canônico e navegação em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T026 Atualizar quickstart da feature com resultados reais da execução em specs/002-docs-limpeza-atualizada/quickstart.md
- [ ] T027 Registrar resumo final da limpeza e métricas SC-001..SC-005 em specs/002-docs-limpeza-atualizada/artifacts/cleanup-report.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: inicia imediatamente.
- **Phase 2 (Foundational)**: depende da Phase 1 e bloqueia todas as user stories.
- **Phase 3 (US1)**: depende da Phase 2.
- **Phase 4 (US2)**: depende da conclusão da US1 (inventário e mapa canônico aprovados).
- **Phase 5 (US3)**: pode iniciar após Phase 2, mas ideal após US2 para refletir estrutura final.
- **Phase 6 (Polish)**: depende de todas as user stories selecionadas.

### User Story Dependencies

- **US1 (P1)**: sem dependência de outras stories; base para limpeza segura.
- **US2 (P2)**: depende de US1 para executar movimentações/remoções com rastreabilidade.
- **US3 (P3)**: depende da estrutura definida em US1 e preferencialmente da navegação final de US2.

### Within Each User Story

- Inventário/classificação antes de mover/remover arquivos.
- Atualização de índices antes da validação de links.
- Governança antes do fechamento final de métricas.

---

## Parallel Opportunities

- **Setup**: T003 pode ocorrer em paralelo com T001/T002.
- **Foundational**: T006 pode ocorrer em paralelo com T004/T005.
- **US1**: T009 pode ocorrer em paralelo com T008 após T007.
- **US2**: T014 e T015 podem ocorrer em paralelo após T012/T013.
- **US3**: T021 pode ocorrer em paralelo com T019/T020.
- **Polish**: T024 pode ocorrer em paralelo com T025.

---

## Parallel Example: User Story 1

```bash
# Após concluir T007:
Task: "T008 [US1] Classificar cada documento em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md"
Task: "T009 [P] [US1] Definir documento canônico por domínio em specs/002-docs-limpeza-atualizada/artifacts/canonical-topics.md"
```

## Parallel Example: User Story 2

```bash
# Após concluir T012 e T013:
Task: "T014 [P] [US2] Atualizar índice principal em docs/INDEX.md"
Task: "T015 [P] [US2] Atualizar links da raiz em README.md"
```

## Parallel Example: User Story 3

```bash
# Com governança em edição:
Task: "T019 [US3] Publicar guia de governança em docs/development/documentation-governance.md"
Task: "T021 [P] [US3] Criar checklist em .github/PULL_REQUEST_TEMPLATE.md"
```

---

## Implementation Strategy

### MVP First (US1)

1. Concluir Phase 1 + Phase 2.
2. Entregar US1 completa (inventário/classificação/canonicidade).
3. Validar SC-001 antes de seguir.

### Incremental Delivery

1. US1: garante base de decisão.
2. US2: executa limpeza estrutural e navegação.
3. US3: consolida governança para continuidade.
4. Polish: fecha qualidade e métricas.

### Suggested MVP Scope

- **MVP recomendado**: concluir até o fim da **US1 (Phase 3)** para obter rastreabilidade completa da limpeza.
