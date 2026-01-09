# 📊 Consolidação de Operações por Mercado

## Visão Geral

O Portfolio Manager v2 implementa **consolidação automática** de operações, independentemente do mercado de negociação. Isso significa que compras feitas no **mercado à vista** e no **mercado fracionário** são somadas em uma única posição por ativo.

---

## Como Funciona

### Armazenamento de Operações

Cada operação importada do Excel B3 ou criada manualmente contém:

- **trade_date**: Data da negociação
- **movement_type**: COMPRA ou VENDA
- **market**: MERCADO A VISTA, MERCADO FRACIONARIO, etc.
- **institution**: Instituição financeira
- **ticker**: Código de negociação do ativo
- **quantity**: Quantidade negociada
- **price**: Preço unitário
- **value**: Valor total da operação

### Consolidação na Carteira

Na listagem de ativos (`GET /assets`), a query SQL agrega **todas as operações** sem considerar o mercado:

```sql
SELECT 
    a.id, 
    a.ticker, 
    a.asset_class, 
    a.asset_type, 
    a.product_name,
    -- CONSOLIDAÇÃO: soma TODAS as compras, independente do mercado
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) as total_bought,
    -- CONSOLIDAÇÃO: soma TODAS as vendas, independente do mercado
    SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.quantity ELSE 0 END) as total_sold,
    -- Posição atual = comprado - vendido (CONSOLIDADO)
    (SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) - 
     SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.quantity ELSE 0 END)) as current_position
FROM assets a
LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
WHERE a.status = 'ACTIVE'
GROUP BY a.id
```

---

## Exemplos Práticos

### Cenário 1: Compras em Mercados Diferentes

**Operações:**
- 01/01/2026: COMPRA de 10 PETR4 no MERCADO A VISTA a R$ 30,00
- 05/01/2026: COMPRA de 5 PETR4 no MERCADO FRACIONARIO a R$ 31,00

**Resultado Consolidado:**
- **Posição Atual**: 15 ações (10 + 5)
- **Total Investido**: R$ 455,00 (300 + 155)
- **Preço Médio**: R$ 30,33 (455 / 15)

### Cenário 2: Compra e Venda em Mercados Diferentes

**Operações:**
- 01/01/2026: COMPRA de 100 VALE3 no MERCADO A VISTA a R$ 60,00
- 05/01/2026: COMPRA de 50 VALE3 no MERCADO FRACIONARIO a R$ 62,00
- 10/01/2026: VENDA de 30 VALE3 no MERCADO A VISTA a R$ 65,00

**Resultado Consolidado:**
- **Posição Atual**: 120 ações (100 + 50 - 30)
- **Total Comprado**: 150 ações
- **Total Vendido**: 30 ações
- **Saldo Investido**: R$ 7.150,00 (9.100 - 1.950)

---

## Interface do Usuário

### Página de Carteira (`/portfolio`)

Mostra **apenas a posição consolidada** por ativo:

| Ticker | Posição Atual | Total Comprado (R$) | Total Vendido (R$) |
|--------|---------------|---------------------|-------------------|
| PETR4  | 15           | R$ 455,00           | R$ 0,00           |
| VALE3  | 120          | R$ 9.100,00         | R$ 1.950,00       |

### Página de Detalhes do Ativo (`/portfolio/:id`)

Mostra:

1. **Posição Consolidada** no card de estatísticas (com nota "Consolidada (todos os mercados)")
2. **Resumo por Mercado** (seção informativa que aparece quando há operações em múltiplos mercados)
3. **Tabela de Operações** com coluna "Mercado" mostrando cada transação individual

#### Exemplo de Resumo por Mercado:

```
📊 Resumo por Mercado

ℹ️ A posição atual é consolidada automaticamente. 
   Operações em mercado à vista e fracionário são somadas.

┌─────────────────────────┬──────────┬─────────┬───────────┐
│ Mercado                 │ Comprado │ Vendido │ Operações │
├─────────────────────────┼──────────┼─────────┼───────────┤
│ MERCADO A VISTA         │ 100      │ 30      │ 2         │
│ MERCADO FRACIONARIO     │ 50       │ 0       │ 1         │
└─────────────────────────┴──────────┴─────────┴───────────┘
```

---

## Princípios de Design

### 1. Eventos Imutáveis

Cada operação é armazenada **exatamente como ocorreu** na realidade:
- Não modificamos o mercado de origem
- Não mesclamos operações no banco de dados
- Mantemos auditoria completa

### 2. Consolidação em Runtime

A posição consolidada é **calculada dinamicamente**:
- Facilita auditoria
- Permite drill-down nas operações individuais
- Mantém flexibilidade para futuras análises

### 3. Transparência

O usuário pode:
- Ver a posição consolidada na carteira
- Ver o resumo por mercado na página de detalhes
- Ver cada operação individual com seu mercado de origem

---

## Benefícios da Consolidação

### Para o Usuário

1. **Visão Simplificada**: Um ativo = uma linha na carteira
2. **Cálculo Correto**: Preço médio considera TODAS as compras
3. **Posição Real**: Reflete exatamente quantas ações você possui

### Para o Sistema

1. **Auditabilidade**: Todas as operações são preservadas
2. **Flexibilidade**: Fácil adicionar análises futuras (ex: comparar custos por mercado)
3. **Correção**: Impossível ter posições duplicadas ou inconsistentes

---

## Casos de Uso

### ✅ Casos Suportados

- Importar relatório B3 com operações em múltiplos mercados
- Criar operações manuais com mercado especificado
- Editar operações mantendo o mercado original
- Visualizar posição consolidada na carteira
- Drill-down nas operações individuais por ativo

### ⚠️ Casos Especiais

- **Operações sem mercado especificado**: Campo `market` pode ser NULL
  - Ainda são consolidadas normalmente
  - Aparecem como "NÃO ESPECIFICADO" no resumo

- **Operações manuais antigas**: Podem não ter campo `market`
  - Sistema trata como NULL
  - Consolidação funciona normalmente

---

## Código Relevante

### Backend

- **Repositório**: `/backend/app/repositories/assets_repository.py`
  - Função: `list_assets()` - Retorna posições consolidadas

- **API**: `/backend/app/main.py`
  - Endpoint: `GET /assets` - Lista ativos com consolidação

### Frontend

- **Carteira**: `/frontend/src/pages/Portfolio.tsx`
  - Mostra posição consolidada

- **Detalhes**: `/frontend/src/pages/AssetDetail.tsx`
  - Mostra resumo por mercado + tabela de operações

---

## Futuras Melhorias

1. **Análise de Custos por Mercado**
   - Comparar se mercado fracionário tem custos maiores
   - Alertar se diferença de preço for significativa

2. **Preferência de Mercado**
   - Sugerir mercado mais vantajoso baseado em histórico
   - Configuração de mercado padrão por usuário

3. **Relatórios por Mercado**
   - Dashboard com breakdown por mercado
   - Gráficos de evolução por tipo de mercado

---

## Conclusão

A consolidação automática de operações por mercado é uma feature **fundamental** do Portfolio Manager v2. Ela garante que:

- ✅ A carteira mostra a posição **real** do usuário
- ✅ O preço médio é calculado **corretamente**
- ✅ A auditoria das operações é **preservada**
- ✅ A experiência do usuário é **simplificada**

Esta abordagem segue os princípios core do projeto:
- **Event-based thinking**: Operações são eventos imutáveis
- **Derived state**: Posição é calculada, não armazenada
- **Clarity over abstraction**: Código explícito e documentado
