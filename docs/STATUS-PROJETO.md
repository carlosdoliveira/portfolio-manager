# 📊 Status do Projeto — Portfolio Manager v2

**Última atualização**: 02 de Janeiro de 2026

Este documento apresenta uma visão completa do estado atual do projeto, funcionalidades implementadas, problemas conhecidos e oportunidades de otimização.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura Atual](#arquitetura-atual)
3. [Funcionalidades Implementadas](#funcionalidades-implementadas)
4. [Problemas Conhecidos](#problemas-conhecidos)
5. [Modelagem de Dados](#modelagem-de-dados)
6. [Otimizações para Dashboards](#otimizações-para-dashboards)
7. [Roadmap Sugerido](#roadmap-sugerido)

---

## Visão Geral

O Portfolio Manager v2 é um sistema de gestão de carteira de investimentos com foco inicial em:

- Importação de relatórios oficiais da B3 (Excel)
- Gerenciamento manual de ativos e operações
- Suporte especializado para Renda Fixa
- Projeções de rendimento com cálculo de IR

### Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | Python + FastAPI | 3.11 |
| Banco de Dados | SQLite (WAL mode) | 3.x |
| Frontend | React + TypeScript | 18.x |
| Build Tool | Vite | 5.4.x |
| Containerização | Docker Compose | 2.x |

---

## Arquitetura Atual

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                    React + TypeScript                       │
│  ┌─────────┬─────────┬──────────┬─────────┬──────────┐     │
│  │Dashboard│Portfolio│FixedIncome│ Import │ Analysis │     │
│  │ (vazio) │   ✓     │    ✓     │   ✓    │ (vazio)  │     │
│  └────┬────┴────┬────┴────┬─────┴───┬────┴────┬─────┘     │
│       │         │         │         │         │            │
│       └─────────┴─────────┼─────────┴─────────┘            │
│                           │                                 │
│                    ┌──────▼──────┐                         │
│                    │ API Client  │                         │
│                    │ (client.ts) │                         │
│                    └──────┬──────┘                         │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP REST
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                          BACKEND                              │
│                    FastAPI + Python                           │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                     main.py                           │    │
│  │  • /assets          → CRUD de ativos                 │    │
│  │  • /operations      → CRUD de operações              │    │
│  │  • /import/b3       → Importação Excel B3            │    │
│  │  • /fixed-income/*  → CRUD Renda Fixa + Projeções    │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                     │
│  ┌──────────────────────▼───────────────────────────────┐    │
│  │                  Repositories                         │    │
│  │  • assets_repository.py                              │    │
│  │  • operations_repository.py                          │    │
│  │  • fixed_income_repository.py                        │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                     │
│  ┌──────────────────────▼───────────────────────────────┐    │
│  │                    Services                           │    │
│  │  • importer.py (classificação + importação B3)       │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────┐
│                        DATABASE                               │
│                   SQLite (WAL mode)                           │
│  ┌──────────────┬───────────────┬────────────────────────┐   │
│  │    assets    │  operations   │ fixed_income_assets    │   │
│  └──────────────┴───────────────┴────────────────────────┘   │
│                                  │                            │
│                        ┌─────────▼─────────┐                 │
│                        │ fixed_income_ops  │                 │
│                        └───────────────────┘                 │
└───────────────────────────────────────────────────────────────┘
```

---

## Funcionalidades Implementadas

### ✅ Backend — Completo

| Módulo | Endpoint | Método | Status | Descrição |
|--------|----------|--------|--------|-----------|
| **Ativos** | `/assets` | POST | ✅ | Criar ativo |
| | `/assets` | GET | ✅ | Listar ativos com agregações |
| | `/assets/{id}` | GET | ✅ | Buscar ativo por ID |
| | `/assets/{id}` | PUT | ✅ | Atualizar ativo |
| | `/assets/{id}` | DELETE | ✅ | Deletar ativo (soft delete) |
| | `/assets/{id}/operations` | GET | ✅ | Listar operações do ativo |
| **Operações** | `/operations` | POST | ✅ | Criar operação manual |
| | `/operations` | GET | ✅ | Listar todas operações |
| | `/operations/{id}` | GET | ✅ | Buscar operação por ID |
| | `/operations/{id}` | PUT | ✅ | Atualizar operação |
| | `/operations/{id}` | DELETE | ✅ | Deletar operação |
| **Importação** | `/import/b3` | POST | ✅ | Importar Excel B3 |
| **Renda Fixa** | `/fixed-income/assets` | POST | ✅ | Criar ativo RF |
| | `/fixed-income/assets` | GET | ✅ | Listar ativos RF |
| | `/fixed-income/assets/{id}` | GET | ✅ | Buscar ativo RF |
| | `/fixed-income/assets/{id}` | PUT | ✅ | Atualizar ativo RF |
| | `/fixed-income/assets/{id}` | DELETE | ✅ | Deletar ativo RF |
| | `/fixed-income/operations` | POST | ✅ | Criar operação RF |
| | `/fixed-income/operations/{id}` | GET | ✅ | Listar operações RF |
| | `/fixed-income/projection/{id}` | GET | ✅ | Projeção de rendimento |

### ✅ Frontend — Parcialmente Implementado

| Página | Rota | Status | Funcionalidades |
|--------|------|--------|-----------------|
| **Dashboard** | `/` | ⚠️ Placeholder | Apenas título, sem dados |
| **Importar** | `/import` | ✅ Completo | Upload B3, drag-and-drop, feedback |
| **Carteira** | `/portfolio` | ✅ Completo | CRUD ativos, tabela com agregações monetárias |
| **Detalhe Ativo** | `/portfolio/:id` | ✅ Completo | Operações do ativo, gráficos básicos |
| **Renda Fixa** | `/fixed-income` | ✅ Completo | CRUD RF, projeções, edição |
| **Análises** | `/analysis` | ⚠️ Placeholder | Apenas título, sem dados |
| **Configurações** | `/settings` | ⚠️ Placeholder | Apenas título, sem funcionalidades |

### ✅ Importação B3

| Feature | Status | Descrição |
|---------|--------|-----------|
| Upload de arquivo | ✅ | Suporte a .xlsx via drag-and-drop |
| Validação de colunas | ✅ | Verifica colunas obrigatórias da B3 |
| Classificação automática | ✅ | Detecta Ações (ON/PN), FIIs, ETFs, RF |
| Deduplicação | ✅ | Evita duplicatas via UNIQUE constraint |
| Idempotência | ✅ | Múltiplas importações do mesmo arquivo são seguras |

### ✅ Renda Fixa

| Feature | Status | Descrição |
|---------|--------|-----------|
| Cadastro de ativos | ✅ | CDB, LCI, LCA, Tesouro (Selic, IPCA+, Pré) |
| Operações | ✅ | Aplicação, Resgate, Vencimento |
| Projeção de rendimento | ✅ | Cálculo com CDI, IPCA, Pré, Selic |
| IR regressivo | ✅ | 22.5% → 15% baseado em dias |
| Isenção LCI/LCA | ✅ | Automaticamente isento de IR |
| Taxa de custódia | ✅ | Suporte para Tesouro Direto |
| Edição de ativos | ✅ | Atualização de taxa, indexador, datas |

---

## Problemas Conhecidos

### 🔴 Backend — Críticos

| ID | Problema | Impacto | Arquivo |
|----|----------|---------|---------|
| B01 | Sem suíte de testes | Regressões não detectadas | `backend/tests/` |
| B02 | Sem validação de preços de mercado | Posição não reflete valor real | `assets_repository.py` |
| B03 | Projeção RF usa taxas fixas | CDI/IPCA hardcoded | `fixed_income_repository.py` |

### 🟡 Backend — Melhorias

| ID | Problema | Impacto | Sugestão |
|----|----------|---------|----------|
| B04 | Sem paginação em listagens | Performance com muitos registros | Adicionar limit/offset |
| B05 | Logs em português e inglês | Inconsistência | Padronizar idioma |
| B06 | Migrations manuais | Risco em atualizações | Usar Alembic ou similar |
| B07 | Sem cache de consultas | Queries repetidas | Implementar cache Redis |

### 🔴 Frontend — Críticos

| ID | Problema | Impacto | Arquivo |
|----|----------|---------|---------|
| F01 | Dashboard vazio | UX incompleta | `Dashboard.tsx` |
| F02 | Análises vazias | Feature não entregue | `Analysis.tsx` |
| F03 | Configurações vazias | Sem personalização | `Settings.tsx` |

### 🟡 Frontend — Melhorias

| ID | Problema | Impacto | Sugestão |
|----|----------|---------|----------|
| F04 | Sem loading states globais | UX fragmentada | Criar contexto global |
| F05 | Sem tratamento offline | Erros silenciosos | Service Worker / cache |
| F06 | Sem gráficos na carteira | Visualização limitada | Recharts / Chart.js |
| F07 | Formatação de datas inconsistente | Confusão do usuário | Criar helper de formatação |

---

## Modelagem de Dados

### Schema Atual

```sql
-- Tabela principal de ativos
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL UNIQUE,
    asset_class TEXT NOT NULL,      -- AÇÕES, FUNDO IMOBILIÁRIO, ETF, RENDA FIXA
    asset_type TEXT NOT NULL,       -- ON, PN, FII, ETF, CDB, LCI, LCA, etc.
    product_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

-- Operações de compra/venda (renda variável)
CREATE TABLE operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL,    -- COMPRA, VENDA
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    value REAL NOT NULL,
    trade_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    source TEXT NOT NULL,           -- B3, MANUAL
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    market TEXT,
    institution TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    UNIQUE (trade_date, movement_type, market, institution, asset_id, quantity, price, source)
);

-- Ativos de Renda Fixa (extensão)
CREATE TABLE fixed_income_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    issuer TEXT NOT NULL,           -- Banco XYZ, Tesouro Nacional
    product_type TEXT NOT NULL,     -- CDB, LCI, LCA, TESOURO_SELIC, etc.
    indexer TEXT NOT NULL,          -- CDI, IPCA, PRE, SELIC
    rate REAL NOT NULL,             -- Taxa contratada (%)
    maturity_date TEXT NOT NULL,
    custody_fee REAL DEFAULT 0,
    issue_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    UNIQUE (asset_id)
);

-- Operações de Renda Fixa
CREATE TABLE fixed_income_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL,   -- APLICACAO, RESGATE, VENCIMENTO
    amount REAL NOT NULL,
    net_amount REAL,
    ir_amount REAL DEFAULT 0,
    trade_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);
```

### Campos Calculados em Runtime

| Entidade | Campo | Cálculo |
|----------|-------|---------|
| Asset | `total_bought` | SUM(quantity) WHERE movement_type = 'COMPRA' |
| Asset | `total_sold` | SUM(quantity) WHERE movement_type = 'VENDA' |
| Asset | `current_position` | total_bought - total_sold |
| Asset | `total_bought_value` | SUM(value) WHERE movement_type = 'COMPRA' |
| Asset | `total_sold_value` | SUM(value) WHERE movement_type = 'VENDA' |
| RF Asset | `total_invested` | SUM(amount) WHERE operation_type = 'APLICACAO' |
| RF Asset | `total_redeemed` | SUM(amount) WHERE operation_type IN ('RESGATE', 'VENCIMENTO') |
| RF Asset | `current_balance` | total_invested - total_redeemed |

---

## Otimizações para Dashboards

### 1. Tabelas Materializadas para Performance

Para dashboards com grandes volumes de dados, recomenda-se criar tabelas de resumo:

```sql
-- Resumo diário de posição por ativo
CREATE TABLE daily_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    reference_date TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    avg_price REAL NOT NULL,
    total_value REAL NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (asset_id, reference_date),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

-- Resumo mensal de performance
CREATE TABLE monthly_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    year_month TEXT NOT NULL,       -- 2026-01
    opening_position INTEGER,
    closing_position INTEGER,
    total_bought INTEGER,
    total_sold INTEGER,
    realized_gain REAL,
    dividend_income REAL,
    created_at TEXT NOT NULL,
    UNIQUE (asset_id, year_month),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

-- Alocação por classe de ativo
CREATE TABLE allocation_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date TEXT NOT NULL,
    asset_class TEXT NOT NULL,
    total_value REAL NOT NULL,
    percentage REAL NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (snapshot_date, asset_class)
);
```

### 2. Integração com Preços de Mercado

Para calcular o valor real da carteira:

```sql
-- Cotações diárias
CREATE TABLE market_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    reference_date TEXT NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL NOT NULL,
    volume INTEGER,
    source TEXT NOT NULL,           -- B3, YAHOO, ALPHA_VANTAGE
    created_at TEXT NOT NULL,
    UNIQUE (ticker, reference_date)
);

-- View para posição valorizada
CREATE VIEW portfolio_valuation AS
SELECT 
    a.id,
    a.ticker,
    a.asset_class,
    a.asset_type,
    COALESCE(SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE -o.quantity END), 0) as position,
    mp.close_price as current_price,
    position * mp.close_price as market_value,
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) as total_cost,
    (market_value - total_cost) as unrealized_gain
FROM assets a
LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
LEFT JOIN market_prices mp ON a.ticker = mp.ticker 
    AND mp.reference_date = (SELECT MAX(reference_date) FROM market_prices WHERE ticker = a.ticker)
WHERE a.status = 'ACTIVE'
GROUP BY a.id;
```

### 3. Índices Recomendados

```sql
-- Otimizar consultas por data
CREATE INDEX idx_operations_trade_date ON operations(trade_date);
CREATE INDEX idx_operations_asset_id ON operations(asset_id);
CREATE INDEX idx_fixed_income_ops_trade_date ON fixed_income_operations(trade_date);
CREATE INDEX idx_market_prices_ticker_date ON market_prices(ticker, reference_date);

-- Otimizar buscas por classe
CREATE INDEX idx_assets_class ON assets(asset_class);
CREATE INDEX idx_assets_status ON assets(status);
```

### 4. Agregações para Dashboard

```python
# Exemplo de endpoint otimizado para dashboard
@app.get("/dashboard/summary")
def get_dashboard_summary():
    """
    Retorna resumo consolidado para o dashboard principal.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total por classe de ativo
        cursor.execute("""
            SELECT 
                a.asset_class,
                COUNT(DISTINCT a.id) as total_assets,
                SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) as total_invested,
                SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.value ELSE 0 END) as total_sold
            FROM assets a
            LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
            WHERE a.status = 'ACTIVE'
            GROUP BY a.asset_class
        """)
        allocation = cursor.fetchall()
        
        # Top 5 maiores posições
        cursor.execute("""
            SELECT 
                a.ticker,
                a.asset_class,
                SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE -o.value END) as net_value
            FROM assets a
            INNER JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
            WHERE a.status = 'ACTIVE'
            GROUP BY a.id
            ORDER BY net_value DESC
            LIMIT 5
        """)
        top_positions = cursor.fetchall()
        
        # Operações recentes
        cursor.execute("""
            SELECT 
                o.trade_date,
                a.ticker,
                o.movement_type,
                o.quantity,
                o.value
            FROM operations o
            INNER JOIN assets a ON o.asset_id = a.id
            WHERE o.status = 'ACTIVE'
            ORDER BY o.trade_date DESC, o.id DESC
            LIMIT 10
        """)
        recent_operations = cursor.fetchall()
        
        return {
            "allocation": allocation,
            "top_positions": top_positions,
            "recent_operations": recent_operations
        }
```

### 5. Estrutura de Resposta para Gráficos

```typescript
// Interface para dados de gráfico de alocação
interface AllocationData {
  asset_class: string;
  total_value: number;
  percentage: number;
  color: string;
}

// Interface para evolução patrimonial
interface PortfolioEvolution {
  date: string;
  total_value: number;
  invested: number;
  gain_loss: number;
}

// Interface para performance por ativo
interface AssetPerformance {
  ticker: string;
  buy_price: number;
  current_price: number;
  return_percentage: number;
  return_value: number;
}
```

---

## Roadmap Sugerido

### Fase 1 — Consolidação (1-2 semanas)

1. **Implementar Dashboard Principal**
   - Card de patrimônio total
   - Gráfico de alocação por classe
   - Lista de operações recentes
   - Top 5 posições

2. **Implementar Página de Análises**
   - Evolução patrimonial (gráfico de linha)
   - Performance por ativo (tabela rankeada)
   - Dividendos/proventos recebidos

3. **Adicionar Testes Automatizados**
   - Testes unitários para repositories
   - Testes de integração para endpoints
   - Testes E2E básicos com Playwright

### Fase 2 — Valorização (2-3 semanas)

4. **Integrar Cotações de Mercado**
   - API de cotações (Yahoo Finance / Alpha Vantage)
   - Job para atualização diária
   - Cálculo de posição valorizada

5. **Mark-to-Market**
   - Valor atual da carteira em tempo real
   - Ganho/perda não realizado
   - Comparação com benchmark (IBOV, CDI)

### Fase 3 — Otimização (1-2 semanas)

6. **Materializar Agregações**
   - Criar tabelas de resumo diário/mensal
   - Jobs de recálculo periódico
   - Cache de consultas frequentes

7. **Performance e Escala**
   - Migrar para PostgreSQL (produção)
   - Implementar paginação em todas as listagens
   - Otimizar queries N+1

### Fase 4 — Novas Features (ongoing)

8. **Proventos e Dividendos** (Issue #1)
9. **Suporte a FIIs completo** (Issue #2)
10. **Suporte a Criptomoedas** (Issue #6)
11. **Suporte a Investimentos Internacionais** (Issue #7)

---

## Conclusão

O Portfolio Manager v2 possui uma base sólida com:

- ✅ Arquitetura bem definida (separação de camadas)
- ✅ Importação robusta com deduplicação
- ✅ Suporte completo a Renda Fixa
- ✅ CRUD funcional para ativos e operações

Os principais gaps são:

- ⚠️ Dashboard e Análises não implementados
- ⚠️ Sem integração com preços de mercado
- ⚠️ Sem testes automatizados

Com as otimizações sugeridas, o sistema estará pronto para:

- Dashboards com grandes volumes de dados
- Cálculo de performance em tempo real
- Escalabilidade para produção

---

**Próximos Passos Imediatos:**

1. Implementar `/dashboard/summary` no backend
2. Criar componentes de gráfico no Dashboard
3. Adicionar cotações mock para desenvolvimento
4. Escrever testes básicos para garantir estabilidade
