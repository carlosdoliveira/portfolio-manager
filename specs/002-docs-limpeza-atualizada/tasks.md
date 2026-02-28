# Tasks: Limpeza da Documentação com Foco em Conteúdo Vigente

**Input**: Design documents from `/specs/002-docs-limpeza-atualizada/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/documentation-governance.md`, `quickstart.md`

**Tests**: Não há solicitação explícita de TDD/testes automatizados; validação será manual conforme `quickstart.md`.

**Organization**: Tarefas agrupadas por user story para permitir implementação e validação independentes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar artefatos e estrutura de trabalho da limpeza documental.

- [ ] T001 Criar diretório de artefatos da feature em specs/002-docs-limpeza-atualizada/artifacts/
- [ ] T002 Criar template de inventário documental em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T003 [P] Criar template de mapa canônico por domínio em specs/002-docs-limpeza-atualizada/artifacts/canonical-topics.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Definir regras-base obrigatórias para classificação, canonicidade e governança.

**⚠️ CRITICAL**: Nenhuma user story deve iniciar antes da conclusão desta fase.

- [ ] T004 Definir critérios formais de classificação (vigente/histórico/obsoleto/duplicado) em docs/development/documentation-governance.md
- [ ] T005 Definir política de documento canônico por domínio em docs/development/documentation-governance.md
- [ ] T006 [P] Definir política de revisão periódica e checklist de PR em docs/development/documentation-governance.md

**Checkpoint**: Regras fundacionais prontas; user stories liberadas.

---

## Phase 3: User Story 1 - Inventário e Classificação da Documentação (Priority: P1) 🎯 MVP

**Goal**: Classificar 100% dos arquivos de `docs/` com status, ação e justificativa.

**Independent Test**: Validar que todos os arquivos de `docs/` constam em `documentation-inventory.md` com classificação completa.

### Implementation for User Story 1

- [ ] T007 [US1] Levantar lista completa de arquivos de docs/ em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T008 [US1] Classificar cada arquivo em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T009 [P] [US1] Definir canônico por domínio em specs/002-docs-limpeza-atualizada/artifacts/canonical-topics.md
- [ ] T010 [US1] Definir ação por arquivo (manter/atualizar/arquivar/remover) em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T011 [US1] Registrar justificativas para casos limítrofes em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md

**Checkpoint**: Inventário completo e auditável (SC-001).

---

## Phase 4: User Story 2 - Estrutura Enxuta e Navegável (Priority: P2)

**Goal**: Limpar navegação principal para apontar somente para conteúdo vigente (ou histórico explicitamente marcado).

**Independent Test**: Validar manualmente `docs/INDEX.md`, `README.md` e `mkdocs.yml` sem links quebrados e sem referências conflitantes.

### Implementation for User Story 2

- [ ] T012 [US2] Executar movimentações para docs/archive/ conforme inventário em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T013 [US2] Remover arquivos obsoletos/duplicados conforme inventário em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md
- [ ] T014 [US2] Criar mapa de redirecionamento/depreciação de documentos removidos em docs/archive/README-ARCHIVE.md
- [ ] T015 [P] [US2] Atualizar índice principal em docs/INDEX.md
- [ ] T016 [P] [US2] Atualizar links de entrada na raiz em README.md
- [ ] T017 [US2] Atualizar navegação de documentação em mkdocs.yml
- [ ] T018 [US2] Validar links críticos e registrar evidência em specs/002-docs-limpeza-atualizada/artifacts/link-validation.md
- [ ] T019 [US2] Registrar medição de findability (<60s) com protocolo manual em specs/002-docs-limpeza-atualizada/artifacts/findability-validation.md

**Checkpoint**: Navegação limpa, sem links quebrados e com validação de descoberta (SC-002, SC-003).

---

## Phase 5: User Story 3 - Governança para Evitar Nova Degradação (Priority: P3)

**Goal**: Formalizar governança de atualização para manter consistência da documentação no tempo.

**Independent Test**: Aplicar checklist de PR em uma mudança simulada e confirmar aderência sem ambiguidade.

### Implementation for User Story 3

- [ ] T020 [US3] Publicar guia oficial de governança documental em docs/development/documentation-governance.md
- [ ] T021 [US3] Incluir processo de atualização de docs por feature em docs/development/setup.md
- [ ] T022 [P] [US3] Criar checklist de PR com item de documentação canônica em .github/PULL_REQUEST_TEMPLATE.md
- [ ] T023 [US3] Atualizar referências de governança no índice de documentação em docs/INDEX.md
- [ ] T024 [US3] Registrar periodicidade de revisão e responsáveis em docs/STATUS-PROJETO.md

**Checkpoint**: Governança implantada e pronta para uso contínuo (SC-004).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Fechamento de qualidade, consistência e rastreabilidade final.

- [ ] T025 [P] Revisar padronização de linguagem PT-BR nos documentos alterados em docs/
- [ ] T026 Verificar coerência com princípios arquiteturais em docs/architecture/principios-core.md
- [ ] T027 Consolidar relatório final com SC-001..SC-004 em specs/002-docs-limpeza-atualizada/artifacts/cleanup-report.md
- [ ] T028 Atualizar orientação de execução final em specs/002-docs-limpeza-atualizada/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: sem dependências.
- **Phase 2 (Foundational)**: depende da Phase 1 e bloqueia user stories.
- **Phase 3 (US1)**: depende da Phase 2.
- **Phase 4 (US2)**: depende da conclusão da US1.
- **Phase 5 (US3)**: depende da conclusão da US2 para refletir navegação final.
- **Phase 6 (Polish)**: depende das user stories concluídas.

### User Story Dependencies

- **US1 (P1)**: inicia após fundação, sem dependência de outras stories.
- **US2 (P2)**: depende do inventário e mapa canônico da US1.
- **US3 (P3)**: depende da estrutura final da US2.

### Within Each User Story

- Inventário/classificação antes de mover/remover.
- Atualização de índices antes de validação de links.
- Governança antes do relatório final.

---

## Parallel Opportunities

- T003 em paralelo com T001/T002.
- T006 em paralelo com T004/T005.
- T009 em paralelo com T008 após T007.
- T015 e T016 em paralelo após T012/T014.
- T022 em paralelo com T020/T021.
- T025 em paralelo com T026.

---

## Parallel Example: User Story 1

```bash
Task: "T008 [US1] Classificar cada arquivo em specs/002-docs-limpeza-atualizada/artifacts/documentation-inventory.md"
Task: "T009 [P] [US1] Definir canônico por domínio em specs/002-docs-limpeza-atualizada/artifacts/canonical-topics.md"
```

## Parallel Example: User Story 2

```bash
Task: "T015 [P] [US2] Atualizar índice principal em docs/INDEX.md"
Task: "T016 [P] [US2] Atualizar links da raiz em README.md"
```

## Parallel Example: User Story 3

```bash
Task: "T020 [US3] Publicar guia de governança em docs/development/documentation-governance.md"
Task: "T022 [P] [US3] Criar checklist em .github/PULL_REQUEST_TEMPLATE.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1 e Phase 2.
2. Completar US1 integralmente.
3. Validar SC-001 antes de avançar.

### Incremental Delivery

1. US1: inventário e decisão.
2. US2: limpeza estrutural e navegação.
3. US3: governança contínua.
4. Polish: validação final e relatório.

### Suggested MVP Scope

- **MVP recomendado**: concluir até o fim da **US1 (Phase 3)**.
