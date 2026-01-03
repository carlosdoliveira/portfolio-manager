# 📊 Status do Projeto — Portfolio Manager v2

**Última atualização**: 03 de Janeiro de 2026  
**Versão**: v2.0.1

> 📖 **Novo?** Comece pelo [INDEX.md](./INDEX.md) para uma visão geral completa.

---

## 🎯 Resumo Executivo

O Portfolio Manager v2 é um **sistema funcional** para gestão de carteira de investimentos com:

### ✅ Implementado
- Import B3 com deduplicação automática
- CRUD completo de ativos e operações
- Renda Fixa com projeções e cálculo de IR
- Consolidação de operações por mercado
- Interface responsiva e profissional

### ⚠️ Em Progresso
- Dashboard principal (placeholder)
- Página de análises (placeholder)
- Testes automatizados (cobertura mínima)

### ❌ Não Implementado
- Cotações de mercado (APIs externas)
- Proventos e dividendos
- Eventos corporativos
- Relatórios de IR

---

## 📋 Índice

1. [Stack Tecnológica](#stack-tecnológica)
2. [Funcionalidades Implementadas](#funcionalidades-implementadas)
3. [Problemas Conhecidos](#problemas-conhecidos)
4. [Modelagem de Dados](#modelagem-de-dados)
5. [Próximos Passos](#próximos-passos)

---

## Stack Tecnológica

| Camada | Tecnologia | Versão | Status |
|--------|-----------|--------|--------|
| Backend | Python + FastAPI | 3.11 | ✅ Estável |
| Banco de Dados | SQLite (WAL mode) | 3.x | ✅ Funcional |
| Frontend | React + TypeScript | 18.x | ✅ Estável |
| Build Tool | Vite | 5.4.x | ✅ Funcional |
| Containerização | Docker Compose | 2.x | ✅ Funcional |

---

## Funcionalidades Implementadas

### ✅ Backend (100% MVP)

| Módulo | Endpoints | Status | Documentação |
|--------|-----------|--------|--------------|
| **Ativos** | `POST/GET/PUT/DELETE /assets` | ✅ Completo | [API](./api/endpoints.md#ativos) |
| | `GET /assets/{id}/operations` | ✅ Completo | |
| **Operações** | `POST/GET/PUT/DELETE /operations` | ✅ Completo | [API](./api/endpoints.md#operações) |
| **Import B3** | `POST /import/b3` | ✅ Completo | [Ref](./REFERENCIA-TECNICA.md#importação-b3) |
| **Renda Fixa** | `POST/GET/PUT/DELETE /fixed-income/assets` | ✅ Completo | [Guia](./renda-fixa.md) |
| | `POST /fixed-income/operations` | ✅ Completo | |
| | `GET /fixed-income/projection/{id}` | ✅ Completo | |

**Principais Features:**
- ✅ Classificação automática de ativos (Ações, FIIs, ETFs, RF)
- ✅ Deduplicação de operações importadas
- ✅ Cálculo de IR regressivo para RF
- ✅ Isenção automática para LCI/LCA
- ✅ Consolidação de operações por mercado
- ✅ Soft delete (status: ACTIVE/DELETED)

---

### ✅ Frontend (70% MVP)

| Página | Rota | Status | Funcionalidades |
|--------|------|--------|-----------------|
| **Import** | `/import` | ✅ **Completo** | Upload drag-and-drop, validação, feedback detalhado |
| **Carteira** | `/portfolio` | ✅ **Completo** | CRUD ativos, tabela agregada, estatísticas, navegação |
| **Detalhes** | `/portfolio/:id` | ✅ **Completo** | Operações por ativo, resumo por mercado, CRUD operações |
| **Renda Fixa** | `/fixed-income` | ✅ **Completo** | CRUD RF, projeções, operações, edição inline |
| **Dashboard** | `/` | ⚠️ **Placeholder** | Apenas título e descrição |
| **Análises** | `/analysis` | ⚠️ **Placeholder** | Apenas título e descrição |
| **Config** | `/settings` | ⚠️ **Placeholder** | Apenas título e descrição |

**Principais Features:**
- ✅ Drag-and-drop para upload de arquivos
- ✅ Formulários de CRUD completos com validação
- ✅ Tabelas com ações inline (editar, deletar)
- ✅ Confirmação de deleção com modal
- ✅ Mensagens de erro detalhadas
- ✅ Feedback de sucesso com toast
- ✅ Loading states
- ✅ Navegação entre páginas
- ✅ Consolidação visual de mercados

---

## Problemas Conhecidos

### 🔴 Críticos

| ID | Problema | Impacto | Localização |
|----|----------|---------|-------------|
| **C01** | Dashboard vazio | UX incompleta — landing page sem valor | `frontend/src/pages/Dashboard.tsx` |
| **C02** | Análises vazias | Feature prometida não entregue | `frontend/src/pages/Analysis.tsx` |
| **C03** | Sem testes automatizados | Risco de regressão alto | `backend/tests/`, `frontend/` |
| **C04** | Sem cotações de mercado | Posição não reflete valor real | N/A |

### 🟡 Importantes

| ID | Problema | Impacto | Sugestão |
|----|----------|---------|----------|
| **I01** | Sem paginação | Performance com muitos registros | Adicionar `limit/offset` em listagens |
| **I02** | Logs inconsistentes | Dificulta debug | Padronizar idioma (português) |
| **I03** | Sem cache de consultas | Queries repetidas | Redis ou in-memory cache |
| **I04** | SQLite em produção | Limitação de concorrência | Migrar para PostgreSQL |
| **I05** | Configurações estáticas | Deploy manual | Variáveis de ambiente |

### ℹ️ Nice to Have

- Lazy loading de rotas (frontend)
- Dark mode
- PWA com offline support
- Gráficos interativos
- Exportação de relatórios
- Comparação com benchmarks

---

## Modelagem de Dados

### Schema Atual

```sql
-- Ativos (ações, FIIs, ETFs, RF)
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    asset_class TEXT NOT NULL,     -- AÇÕES, FUNDO IMOBILIÁRIO, ETF, RENDA FIXA
    asset_type TEXT NOT NULL,      -- ON, PN, FII, ETF, CDB, LCI, etc.
    product_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE'   -- ACTIVE, DELETED
);

-- Operações de renda variável
CREATE TABLE operations (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL,   -- COMPRA, VENDA
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    value REAL NOT NULL,
    trade_date TEXT NOT NULL,
    market TEXT,                   -- MERCADO A VISTA, MERCADO FRACIONARIO
    institution TEXT,
    source TEXT NOT NULL,          -- B3, MANUAL
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    UNIQUE (trade_date, movement_type, market, institution, asset_id, quantity, price, source)
);

-- Ativos de Renda Fixa (extensão)
CREATE TABLE fixed_income_assets (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER UNIQUE NOT NULL,
    issuer TEXT NOT NULL,
    product_type TEXT NOT NULL,    -- CDB, LCI, LCA, TESOURO_SELIC, etc.
    indexer TEXT NOT NULL,         -- CDI, IPCA, PRE, SELIC
    rate REAL NOT NULL,
    maturity_date TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    custody_fee REAL DEFAULT 0,
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

-- Operações de Renda Fixa
CREATE TABLE fixed_income_operations (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL,  -- APLICACAO, RESGATE, VENCIMENTO
    amount REAL NOT NULL,
    net_amount REAL,
    ir_amount REAL DEFAULT 0,
    trade_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);
```

### Campos Calculados (Runtime)

Campos derivados calculados via SQL, **não armazenados**:

| Campo | Cálculo | Uso |
|-------|---------|-----|
| `total_bought` | `SUM(quantity) WHERE movement_type = 'COMPRA'` | Posição |
| `total_sold` | `SUM(quantity) WHERE movement_type = 'VENDA'` | Posição |
| `current_position` | `total_bought - total_sold` | Carteira |
| `total_bought_value` | `SUM(value) WHERE movement_type = 'COMPRA'` | Investimento |
| `total_sold_value` | `SUM(value) WHERE movement_type = 'VENDA'` | Resgate |
| `average_price` | `total_bought_value / total_bought` | Preço médio |

📖 **Princípio:** Estado é derivado, não armazenado (event sourcing)

---

## Próximos Passos

### 🎯 Prioridade Alta (Sprint 1)

1. **Implementar Dashboard Principal**
   ```
   Endpoint backend: GET /dashboard/summary
   Retorno: {
     total_assets: number,
     total_invested: number,
     current_value: number (sem cotações = invested - sold),
     top_positions: Asset[],
     recent_operations: Operation[]
   }
   
   Frontend: Cards + gráfico de alocação + operações recentes
   Estimativa: 8 horas (4h backend + 4h frontend)
   ```

2. **Implementar Página de Análises**
   ```
   Gráficos:
   - Distribuição por classe de ativo (pizza)
   - Timeline de operações (linha)
   - Top 5 maiores posições (barra)
   
   Estimativa: 6 horas
   ```

3. **Adicionar Testes Básicos**
   ```
   Backend:
   - Testes unitários para repositories (3h)
   - Testes de integração para endpoints (3h)
   
   Frontend:
   - Testes de componentes com React Testing Library (4h)
   
   Estimativa: 10 horas
   ```

### 🔮 Prioridade Média (Sprint 2-3)

4. **Integrar Cotações de Mercado**
   - API: Yahoo Finance ou Alpha Vantage
   - Endpoint: `GET /market/quote/:ticker`
   - Job diário para atualização
   - Estimativa: 12 horas

5. **Implementar Mark-to-Market**
   - Cálculo de valor atual da carteira
   - Ganho/perda não realizado
   - Comparação com benchmarks
   - Estimativa: 8 horas

6. **Adicionar Paginação**
   - Backend: `limit`, `offset`, `total` em listagens
   - Frontend: Componente Pagination
   - Estimativa: 4 horas

### 📅 Backlog (Futuro)

- Proventos e dividendos (Issue #1)
- Eventos corporativos (splits, bonificações)
- Relatórios de IR
- PWA com offline support
- Migração para PostgreSQL
- API externa para mobile

---

## 📚 Documentação Relacionada

- **Visão Geral Completa:** [INDEX.md](./INDEX.md)
- **Referência Técnica:** [REFERENCIA-TECNICA.md](./REFERENCIA-TECNICA.md)
- **Arquitetura:** [architecture/principios-core.md](./architecture/principios-core.md)
- **API:** [api/endpoints.md](./api/endpoints.md)
- **Consolidação de Mercados:** [guides/consolidacao-mercados.md](./guides/consolidacao-mercados.md)
- **Renda Fixa:** [renda-fixa.md](./renda-fixa.md)

---

## 🎉 Conquistas do Projeto

| Milestone | Data | Descrição |
|-----------|------|-----------|
| **MVP Funcional** | Dez/2025 | CRUD + Import B3 |
| **Renda Fixa** | Jan/2026 | Gestão completa de RF |
| **Consolidação Mercados** | Jan/2026 | UI explicativa + docs |
| **v2.0.1** | Jan/2026 | Release estável |

---

**Próxima Revisão:** Sprint planning — 10/01/2026
