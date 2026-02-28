# Research: Recomendações de Rebalanceamento de Carteiras

**Feature**: 001-wallet-rebalancing-recommendations  
**Date**: 2026-02-22  
**Status**: Complete

## Research Tasks Completed

### 1. Database Schema Design for Wallets

**Decision**: Três novas tabelas no SQLite existente

**Rationale**:
- `wallets`: Tabela principal (id, name, type, created_at, updated_at)
- `wallet_assets`: Join table N:M (wallet_id, asset_id, weight_override nullable)
- `target_allocations`: Alocações-alvo (wallet_id, category, target_percent)
- Schema mantém simplicidade SQLite sem foreign keys complexas
- UNIQUE constraint em `wallets.name` para idempotência (principle II)

**Alternatives Considered**:
- ❌ JSON blob em tabela `user_preferences`: Dificulta queries e escalabilidade
- ❌ MongoDB/NoSQL separado: Adiciona complexidade desnecessária ao stack
- ✅ Tabelas relacionais SQLite: Consistente com arquitetura existente, queries simples

---

### 2. Rebalancing Algorithm Approach

**Decision**: Algoritmo threshold-based simples com priorização por desvio

**Rationale**:
1. Calcular alocação atual: `sum(qty * current_price) / portfolio_total` por categoria
2. Comparar com alocação-alvo: `|actual - target|`
3. Se desvio > threshold (default 5%): gerar sugestões
4. Ordenar ativos por liquidez e desvio para priorizar ajustes
5. Sugerir operações que minimizem número de transações

**Alternatives Considered**:
- ❌ Mean-Variance Optimization (Markowitz): Overkill para MVP, requer dados históricos, complexo
- ❌ Black-Litterman Model: Acadêmico demais, não democratiza
- ✅ Threshold-based: Simples, transparente, usuário entende facilmente

**Key Libraries**: Nenhuma externa necessária - Pandas para cálculos, lógica pura Python

---

### 3. Frontend UX Pattern for Wallets

**Decision**: Padrão dashboard cards + detail view drill-down

**Rationale**:
- **List View**: Grid de cards (WalletCard.tsx) com métricas principais
- **Detail View**: Página expandida com tabs (Ativos | Alocação | Rebalanceamento)
- **Rebalancing Panel**: Modal/drawer com sugestões step-by-step
- Inspiração: Robinhood, Interactive Brokers (simplicidade), Nu Invest (português)

**Alternatives Considered**:
- ❌ Single-page wizard: Rigidez excessiva, impede exploração livre
- ❌ Split-view lado a lado: Ruim em mobile, desperdiça espaço
- ✅ Cards + Drill-down: Familiar, responsivo, escalável

**Components Needed**:
- `WalletCard` (summary), `WalletForm` (CRUD), `AllocationChart` (Recharts pie chart)
- `RebalancingPanel` (recommendations), `AssetAllocationEditor` (target % input)

---

### 4. Integration with Existing position_engine.py

**Decision**: Estender position_engine.py com método `calculate_wallet_positions(wallet_id)`

**Rationale**:
- Reutilizar lógica existente de cálculo de posições
- Filtrar operações por ativos da carteira via join SQL
- Retornar estrutura compatível: `{ticker: {qty, avg_price, current_value, category}}`
- Sem duplicação de código, mantém single source of truth

**Alternatives Considered**:
- ❌ Duplicar lógica em wallet_calculator.py: Viola DRY, bugs divergentes
- ❌ Reescrever position_engine para suportar wallets: Breaking change desnecessário
- ✅ Extensão não-invasiva: Adiciona método novo sem alterar existentes

---

### 5. Portuguese (BR) Language Coverage

**Decision**: Tradução completa em frontend + backend error messages

**Rationale**:
- **Frontend**: Todos labels, placeholders, tooltips, mensagens em PT-BR
- **Backend**: Error messages em português retornados pela API
- **Exemplos educativos**: Tooltips explicam conceitos (ex: "Alocação-alvo: % desejado para cada tipo de ativo")
- Arquivo `locales/pt-BR.json` ou constants diretamente em componentes (simplicidade)

**Alternatives Considered**:
- ❌ i18n completo (react-i18next): Overkill para app monolíngue
- ❌ Backend em inglês, frontend em PT: Inconsistência confunde usuário
- ✅ Hard-coded PT-BR: Simples, performático, suficiente para MVP

---

### 6. Cost Estimation for Rebalancing

**Decision**: Fórmula simplificada com constantes configuráveis

**Rationale**:
```python
# Corretagem fixa por operação (padrão B3: R$ 10-20)
brokerage_fee = 15.00  # Configurável em settings

# Imposto (dedo-duro): 0.005% sobre venda de ações
tax_rate = 0.00005

total_cost = (num_sell_ops + num_buy_ops) * brokerage_fee + sum(sell_values) * tax_rate
benefit = abs(current_allocation - target_allocation) * portfolio_value
net_benefit = benefit - total_cost
```

**Alternatives Considered**:
- ❌ Integração API corretoras (Rico, Clear): Indisponível, requer cadastro
- ❌ Scraping tabelas públicas: Frágil, não confiável
- ✅ Constantes configuráveis: Transparente, usuário pode ajustar, suficientemente preciso

---

### 7. Handling Non-Liquid Assets (Fixed Income)

**Decision**: Rebalanceamento apenas sugere novos aportes, não vendas

**Rationale**:
- Renda Fixa (CDB, LCI, LCA, Tesouro) tem liquidez limitada ou penalidades
- Sistema detecta categoria do ativo (já existe classificação em `assets.type`)
- Para RF: sugestão = "Aportar R$ X em [categoria RF] no próximo investimento"
- Para ações/FIIs: sugestão normal (compra/venda)

**Alternatives Considered**:
- ❌ Sugerir venda de RF: Tecnicamente incorreto, pode gerar prejuízo
- ❌ Ignorar RF no rebalanceamento: Distorce alocação real
- ✅ Sugestões assimétricas: Realista, educativo para o usuário

---

## Technology Decisions Summary

| Aspect | Decision | Justification |
|--------|----------|---------------|
| **Database** | 3 novas tabelas SQLite | Consistente com stack, queries simples |
| **Algorithm** | Threshold-based (5% desvio) | Simples, transparente, democrático |
| **Frontend** | React cards + drill-down | Padrão UX conhecido, responsivo |
| **Charts** | Recharts (já no projeto) | Sem dependência nova, sufficient |
| **Cálculos** | Extensão position_engine.py | Reutiliza código, sem duplicação |
| **Idioma** | Hard-coded PT-BR | Simplicidade > i18n desnecessário |
| **Custos** | Fórmula com constantes | Configurável, transparente |
| **RF handling** | Apenas aportes, sem vendas | Realista para liquidez RF |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cotações desatualizadas | Alto - recomendações incorretas | Validar freshness antes de calcular, alertar se > 24h |
| Algoritmo muito agressivo | Médio - sugestões impraticáveis | Threshold configurável, exibir "benefício líquido" |
| RF sem categoria | Médio - sugestões erradas | Validar classificação assets na migration |
| Performance com 50+ ativos | Baixo - cálculo lento | Limit inicial 20 ativos/carteira, otimizar depois |

---

## Dependencies & Prerequisites

**External Libraries**: Nenhuma nova  
**Database Changes**: Migration para 3 tabelas  
**API Dependencies**: yfinance (já integrado) para cotações  
**Frontend Dependencies**: Recharts (já instalado)  

**Blockers**: Nenhum identificado

---

**Status**: ✅ Research Complete - Ready for Phase 1 (Design)
