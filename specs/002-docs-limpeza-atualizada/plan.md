# Implementation Plan: Limpeza da Documentação com Foco em Conteúdo Vigente

**Branch**: `002-docs-limpeza-atualizada` | **Date**: 2026-02-28 | **Spec**: `/specs/002-docs-limpeza-atualizada/spec.md`
**Input**: Feature specification from `/specs/002-docs-limpeza-atualizada/spec.md`

## Summary

Padronizar e enxugar a documentação do projeto para manter no fluxo principal apenas conteúdo vigente, preservando histórico relevante em `docs/archive/`, removendo redundâncias e estabelecendo governança para evitar nova degradação.

## Technical Context

**Language/Version**: Markdown + configuração MkDocs (`mkdocs.yml`) + shell tooling de suporte  
**Primary Dependencies**: Estrutura atual de `docs/`, `README.md`, `mkdocs.yml`, convenções internas do repositório  
**Storage**: Arquivos em repositório Git (sem persistência adicional)  
**Testing**: Validação manual de links críticos + revisão de consistência entre documentos canônicos  
**Target Platform**: Repositório GitHub e leitura web/local via MkDocs  
**Project Type**: Governança e manutenção documental em aplicação web full-stack  
**Performance Goals**: reduzir tempo de descoberta de documentos principais para < 60s a partir do índice  
**Constraints**: português (Brasil), sem apagar histórico relevante, sem quebrar navegação, sem criar ferramentas complexas  
**Scale/Scope**: todo diretório `docs/` e pontos de entrada (`README.md`, `docs/INDEX.md`, `mkdocs.yml`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [Portfolio Manager v2 Constitution](../.specify/memory/constitution.md):

- [x] **Principle I: Immutability** — Não altera operações financeiras nem histórico transacional do produto.
- [x] **Principle II: Idempotency** — Critérios de classificação e limpeza são reproduzíveis; reexecução mantém o mesmo resultado esperado.
- [x] **Principle III: Clarity** — Regras explícitas de canonicidade, arquivamento e remoção.
- [x] **Principle IV: Event-Based** — Não introduz persistência de estado derivado financeiro; escopo restrito à documentação.
- [x] **Principle V: Simplicity** — Solução baseada em inventário + critérios + atualização de índice, sem sobreengenharia.
- [x] **Code Quality** — Alterações em arquivos textuais com estrutura clara e rastreável.
- [x] **Testing** — Inclui validação de links e revisão manual dos pontos de entrada.
- [x] **Documentation** — A própria feature atualiza e governa a documentação em `docs/`.

**Constitution Compliance**: ✅ Full

## Project Structure

### Documentation (this feature)

```text
specs/002-docs-limpeza-atualizada/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── documentation-governance.md
└── tasks.md
```

### Source Code (repository root)

```text
docs/
├── INDEX.md
├── README.md
├── api/
├── architecture/
├── guides/
├── development/
├── deployment/
└── archive/

README.md
mkdocs.yml
```

**Structure Decision**: Operar somente no ecossistema de documentação existente, sem criação de novos subsistemas.

## Phase 0: Research Output

Pesquisa consolidada em `/specs/002-docs-limpeza-atualizada/research.md` cobrindo:
- taxonomia de classificação;
- política de retenção histórica;
- definição de fonte canônica por domínio;
- validação de navegação e links;
- governança para prevenir regressão.

## Phase 1: Design & Contracts Output

- Modelo conceitual da limpeza: `/specs/002-docs-limpeza-atualizada/data-model.md`
- Contrato de governança editorial: `/specs/002-docs-limpeza-atualizada/contracts/documentation-governance.md`
- Guia de execução da limpeza: `/specs/002-docs-limpeza-atualizada/quickstart.md`

## Post-Design Constitution Check

- [x] Escopo não afeta integridade de eventos financeiros
- [x] Processo de classificação reproduzível e auditável
- [x] Diretrizes simples e explícitas para manutenção contínua
- [x] Documentação ativa e histórica claramente separadas
- [x] Política de atualização alinhada ao padrão PT-BR do projeto

**Post-Design Compliance**: ✅ Full

## Complexity Tracking

Sem exceções constitucionais necessárias nesta fase.
