# Implementation Plan: Recomendações de Rebalanceamento de Carteiras

**Branch**: `001-wallet-rebalancing-recommendations` | **Date**: 2026-02-28 | **Spec**: `/specs/001-wallet-rebalancing-recommendations/spec.md`
**Input**: Feature specification from `/specs/001-wallet-rebalancing-recommendations/spec.md`

## Summary

Implementar módulo de carteiras com CRUD, atribuição N:M de ativos, configuração de alocação-alvo e geração sob demanda de recomendações de rebalanceamento com simulação de custos. A solução preserva arquitetura event-based do projeto: operações seguem imutáveis, valores derivados são calculados em runtime, e recomendações não são persistidas.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x + React 18 (frontend)  
**Primary Dependencies**: FastAPI, sqlite3, pandas, openpyxl, yfinance, React, axios, react-router-dom, recharts  
**Storage**: SQLite (`backend/data/portfolio.db`)  
**Testing**: pytest (backend), testes manuais de UI/integração frontend, scripts de teste existentes em `tests/` e `backend/tests/`  
**Target Platform**: Linux com Docker Compose (backend + frontend), navegador desktop/mobile  
**Project Type**: Aplicação web full-stack (FastAPI + React)  
**Performance Goals**: gerar recomendação de rebalanceamento em < 3s para carteira com até 20 ativos (SC-002)  
**Constraints**: interface 100% PT-BR, precisão financeira em 2 casas decimais, sem persistir estado derivado, preservação de imutabilidade e auditabilidade  
**Scale/Scope**: usuários individuais (micro-SaaS), múltiplas carteiras por usuário, foco MVP com evolução incremental

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [Portfolio Manager v2 Constitution](../.specify/memory/constitution.md):

- [x] **Principle I: Immutability** — Feature só cria novas operações para execução de rebalanceamento; sem mutação histórica.
- [x] **Principle II: Idempotency** — Operações críticas usam constraints e regras explícitas para evitar duplicação em atribuições/configurações.
- [x] **Principle III: Clarity** — Estrutura explícita em repositórios/serviços/componentes sem abstrações prematuras.
- [x] **Principle IV: Event-Based** — Métricas de carteira e recomendações derivadas de operações + cotações, sem estado financeiro persistido.
- [x] **Principle V: Simplicity** — Algoritmo threshold-based e modelo relacional simples no SQLite.
- [x] **Code Quality** — Tipagem explícita, validações de entrada, tratamento de erros em API e estados de UI.
- [x] **Testing** — Plano inclui testes de endpoint, cálculo e fluxo frontend.
- [x] **Documentation** — Entregáveis incluem `research.md`, `data-model.md`, `contracts/` e `quickstart.md`.

**Constitution Compliance**: ✅ Full

## Project Structure

### Documentation (this feature)

```text
specs/001-wallet-rebalancing-recommendations/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py
│   ├── db/
│   ├── repositories/
│   └── services/
└── tests/

frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   └── styles/
└── package.json

docs/
├── architecture/
├── api/
├── guides/
├── development/
└── deployment/

tests/
```

**Structure Decision**: Manter arquitetura web existente (backend + frontend + docs) e evoluir com módulos de carteira/rebalanceamento sem reorganização estrutural ampla.

## Phase 0: Research Output

Pesquisa consolidada em `/specs/001-wallet-rebalancing-recommendations/research.md` cobrindo:
- design de schema de carteiras e alocação-alvo;
- abordagem do algoritmo de rebalanceamento;
- padrão de UX frontend e cobertura PT-BR;
- estratégia de integração com cálculo de posições existente;
- modelagem de custos e tratamento de ativos de baixa liquidez.

Todas as decisões possuem rationale e alternativas consideradas.

## Phase 1: Design & Contracts Output

- Modelo de dados detalhado: `/specs/001-wallet-rebalancing-recommendations/data-model.md`
- Contratos de API: `/specs/001-wallet-rebalancing-recommendations/contracts/api.md`
- Guia de execução e validação: `/specs/001-wallet-rebalancing-recommendations/quickstart.md`

## Post-Design Constitution Check

- [x] Imutabilidade preservada na execução guiada (operações novas, sem overwrite)
- [x] Idempotência preservada em vínculos e configurações com constraints/regras
- [x] Cálculos derivados em runtime (sem persistir métricas financeiras)
- [x] Solução permanece simples e auditável para MVP
- [x] Documentação técnica em PT-BR e alinhada à estrutura `docs/`

**Post-Design Compliance**: ✅ Full

## Complexity Tracking

Sem exceções constitucionais necessárias nesta fase.