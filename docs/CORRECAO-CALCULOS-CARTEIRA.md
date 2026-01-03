# 🛠️ Roadmap de Correção: Cálculos da Carteira

**Data**: 3 de janeiro de 2026  
**Status**: 🔴 Problemas Críticos Identificados  
**Prioridade**: 🔥 CRÍTICA - Bloqueia uso normal do sistema

---

## 📋 Sumário Executivo

Durante testes de uso real do sistema de Portfolio Manager v2, foram identificados **7 problemas críticos** relacionados aos cálculos financeiros e consolidação de ativos. Os valores de carteira, posição e investimentos aparecem **zerados** em todas as telas, impedindo o uso efetivo do sistema para gestão de investimentos.

### Situação Atual

| Componente | Status | Impacto |
|-----------|--------|---------|
| Importação B3 | ✅ Funciona | Nenhum |
| Classificação de Produtos | ✅ Funciona | Nenhum |
| Cálculo de Totalizadores | ❌ Zerados | **CRÍTICO** |
| Cálculo por Ativo | ❌ Zerados | **CRÍTICO** |
| Consolidação Fracionário/Vista | ❌ Não Implementado | **ALTO** |
| Preço Médio | ❌ Zerado | **CRÍTICO** |
| Histórico de Operações | ⚠️ Funciona parcialmente | Médio |

---

## 🐛 Problemas Identificados

### 1. ✅ Importação Funcionando (Referência)
**Status**: Funcionando corretamente  
**Descrição**: A importação de dados B3 ocorre conforme esperado e os ativos são incluídos na carteira.

---

### 2. ✅ Consolidação Fracionário/Vista IMPLEMENTADA
**Status**: ✅ **IMPLEMENTADO**  
**Prioridade**: P1  
**Data de Implementação**: 3 de janeiro de 2026

#### Descrição da Solução
Implementada normalização de ticker no importador B3 para consolidar automaticamente ações fracionárias (ex: `ABEV3F`) com ações do mercado à vista (ex: `ABEV3`).

#### O que foi implementado

1. **Função `normalize_ticker()`** em `services/importer.py`
   - Remove sufixo 'F' de tickers fracionários
   - Preserva tickers do mercado à vista inalterados
   - Não afeta FIIs e ETFs

2. **Ajuste no fluxo de importação**
   - Normalização ocorre antes de criar/buscar ativos
   - Campo `market` preservado em operações para rastreabilidade
   - Logging mostra tickers antes e depois da normalização

3. **Script de migração** (`scripts/migrate_consolidate_tickers.py`)
   - Consolida dados existentes no banco
   - Modo `--dry-run` para simulação segura
   - Backup automático recomendado antes de executar

4. **Testes unitários** (`tests/test_ticker_normalization.py`)
   - 15 casos de teste cobrindo cenários diversos
   - Edge cases (espaços, maiúsculas, mercado None/vazio)
   - Tickers comuns do mercado brasileiro

5. **Documentação completa** ([guia consolidacao-mercados.md](./guides/consolidacao-mercados.md))
   - Como funciona em detalhes
   - Exemplos práticos
   - FAQ completo
   - Instruções de migração

#### Comportamento Atual ✅
- `ABEV3F` → Normalizado para `ABEV3` (único ativo na interface)
- Posição total = soma de operações de ambos mercados
- Histórico mostra origem (vista ou fracionário) de cada operação

#### Próximos Passos
- Adicionar badges visuais no histórico (Item #7, P2)
- Implementar filtro por mercado (opcional, P3)

---

### 3. ✅ Classificação de Produtos (Referência)
**Status**: Funcionando corretamente  
**Descrição**: As classificações estão acontecendo corretamente:
- Ações: identificadas como `AÇÕES`
- ETFs: identificados como `ETF`
- Fundos Imobiliários: identificados como `FII`

---

### 4. ❌ Totalizadores da Carteira Zerados
**Status**: 🔴 **CRÍTICO - BUG**  
**Prioridade**: P0 (Mais Alta)

#### Descrição do Problema
Na área principal da página **Portfolio**, os seguintes valores aparecem zerados:
- **Valor Atual da Carteira**: R$ 0,00
- **Total Investido**: R$ 0,00
- **Total Resgatado**: R$ 0,00

#### Localização no Código
**Frontend**: `/frontend/src/pages/Portfolio.tsx` (linhas 140-143)

```typescript
const totalAssets = assets.length;
const totalBoughtValue = assets.reduce((sum, asset) => sum + (asset.total_bought_value || 0), 0);
const totalSoldValue = assets.reduce((sum, asset) => sum + (asset.total_sold_value || 0), 0);
const currentValue = totalBoughtValue - totalSoldValue;
```

**Backend**: `/backend/app/repositories/assets_repository.py` (função `list_assets()`)

```python
SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) as total_bought_value,
SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.value ELSE 0 END) as total_sold_value
```

#### Análise Técnica
**Hipóteses de Causa**:

1. **Campo `value` não está sendo calculado/persistido corretamente** nas operações
   - Verificar se `operations.value = quantity * price` está sendo executado
   - Inspecionar registros no SQLite: `SELECT id, quantity, price, value FROM operations LIMIT 10;`

2. **Query SQL retornando NULL em vez de 0**
   - O `LEFT JOIN` pode retornar NULL se não houver operações
   - Verificar se `row[11]` e `row[12]` estão sendo tratados corretamente

3. **Tipo de dado incorreto no SQLite**
   - Verificar schema: `value REAL NOT NULL` está correto?
   - Pode estar armazenado como TEXT em vez de REAL

#### Plano de Correção

**Passo 1**: Validar dados na base (5min)
```sql
-- Conectar ao banco
sqlite3 /app/app/data/portfolio.db

-- Verificar operações
SELECT 
    id, 
    asset_id, 
    movement_type, 
    quantity, 
    price, 
    value,
    value IS NULL as is_null,
    typeof(value) as value_type
FROM operations 
WHERE status = 'ACTIVE'
LIMIT 10;

-- Verificar se cálculo está correto
SELECT 
    id,
    quantity,
    price,
    value,
    (quantity * price) as calculated_value,
    (value - (quantity * price)) as diff
FROM operations
WHERE status = 'ACTIVE';
```

**Passo 2**: Corrigir inserção de operações (10min)
- Arquivo: `/backend/app/repositories/operations_repository.py`
- Garantir que `value` seja calculado e persistido como `REAL`
- Adicionar validação de tipos

**Passo 3**: Corrigir query de listagem (5min)
- Arquivo: `/backend/app/repositories/assets_repository.py`
- Garantir COALESCE para tratar NULL: `COALESCE(SUM(...), 0.0) as total_bought_value`

**Passo 4**: Testar e validar (10min)
- Reimportar arquivo B3 de teste
- Verificar valores no frontend
- Validar cálculos manualmente

#### Tempo Estimado
**30 minutos**

---

### 5. ❌ Valores por Ativo Zerados
**Status**: 🔴 **CRÍTICO - BUG**  
**Prioridade**: P0 (Mais Alta)

#### Descrição do Problema
Em cada linha da tabela de ativos na página **Portfolio**, os seguintes valores aparecem zerados:
- **Posição Atual**: 0
- **Total Comprado**: R$ 0,00
- **Total Vendido**: R$ 0,00

#### Causa Raiz
Mesma causa do problema #4: query SQL retornando valores zerados ou NULL.

#### Plano de Correção
Mesma correção do problema #4 (consolidada).

#### Tempo Estimado
**Incluído na correção do problema #4**

---

### 6. ❌ Detalhe do Ativo com Valores Zerados
**Status**: 🔴 **CRÍTICO - BUG**  
**Prioridade**: P1

#### Descrição do Problema
Ao abrir a página de detalhe de um ativo (`/portfolio/:id`), os seguintes valores aparecem zerados:
- **Preço Médio**: R$ 0,00
- **Total Investido**: R$ 0,00
- **Posição Atual**: 0 (esperado, sem cotação)

#### Comportamento Esperado
- **Preço Médio**: Calculado como `total_bought_value / total_bought_quantity`
- **Total Investido**: Soma de todas as compras (`SUM(value WHERE movement_type = 'COMPRA')`)
- **Posição Atual**: Depende de API externa (OK estar zerado por enquanto)

#### Localização no Código
**Frontend**: `/frontend/src/pages/AssetDetail.tsx`  
**Backend**: Endpoint `/assets/{asset_id}` (precisa ser verificado se retorna cálculos)

#### Análise Técnica
O endpoint de detalhe do ativo pode não estar calculando:
- `average_price` (preço médio de compra)
- `total_invested` (total gasto em compras)

#### Plano de Correção

**Passo 1**: Verificar endpoint atual (5min)
```bash
curl http://localhost:8000/assets/1 | jq
```

**Passo 2**: Adicionar cálculos no backend (15min)
- Arquivo: `/backend/app/main.py` ou novo endpoint em `repositories`
- Query deve calcular:
  - `average_price = SUM(value WHERE COMPRA) / SUM(quantity WHERE COMPRA)`
  - `total_invested = SUM(value WHERE COMPRA)`
  - `current_position = SUM(quantity WHERE COMPRA) - SUM(quantity WHERE VENDA)`

**Exemplo de Query**:
```sql
SELECT 
    a.id,
    a.ticker,
    a.asset_class,
    COUNT(CASE WHEN o.movement_type = 'COMPRA' THEN 1 END) as buy_count,
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) as total_bought_qty,
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) as total_invested,
    CASE 
        WHEN SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) > 0
        THEN SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) / 
             SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END)
        ELSE 0
    END as average_price
FROM assets a
LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
WHERE a.id = ?
GROUP BY a.id;
```

**Passo 3**: Atualizar frontend (5min)
- Garantir que `AssetDetail.tsx` exibe os novos campos

**Passo 4**: Testar (5min)

#### Tempo Estimado
**30 minutos**

---

### 7. ⚠️ Histórico de Operações Parcialmente Funcional
**Status**: 🟡 **FUNCIONANDO MAS PRECISA MELHORIA**  
**Prioridade**: P2

#### Descrição do Problema
O histórico de operações mostra as operações do ativo selecionado corretamente, mas:

**Problema Atual**:
- Histórico mostra todas operações com ticker exato (ex: `ABEV3F` separado de `ABEV3`)
- Não há indicação visual de qual mercado é cada operação

**Comportamento Esperado**:
- Para ações, o ticker do produto deve ser **consolidado** (ex: apenas `ABEV3`)
- No histórico, deve distinguir claramente:
  - 🟦 **Mercado à Vista** (ABEV3)
  - 🟨 **Mercado Fracionário** (ABEV3F)
- Badge ou coluna indicando o mercado

#### Plano de Correção

**Passo 1**: Adicionar campo de mercado no histórico (10min)
- Backend já retorna `market` no endpoint de operações
- Frontend precisa exibir na tabela

**Passo 2**: Criar badge visual (10min)
- CSS: `.market-badge-vista` e `.market-badge-fracionario`
- Componente: `<span className={`market-badge market-badge-${market.toLowerCase()}`}>`

**Passo 3**: Implementar filtro por mercado (15min)
- Dropdown para filtrar "Todos", "À Vista", "Fracionário"

#### Tempo Estimado
**35 minutos**

---

## 🎯 Plano de Ação Priorizado

### Sprint 1: Correções Críticas (Bloqueadores)
**Objetivo**: Fazer a carteira funcionar com valores corretos  
**Tempo Estimado**: 2-3 horas

| Prioridade | Item | Tempo | Dependências |
|-----------|------|-------|--------------|
| **P0** | #4 + #5: Corrigir totalizadores e valores por ativo | 30min | Nenhuma |
| **P0** | Validar correção com dados reais | 20min | Item anterior |
| **P1** | #6: Corrigir detalhe do ativo (preço médio) | 30min | Item #4 resolvido |
| **P1** | #2: Implementar consolidação fracionário/vista | 60min | Planejamento adicional |

### Sprint 2: Melhorias e UX (Nice to Have)
**Objetivo**: Melhorar experiência do usuário  
**Tempo Estimado**: 1-2 horas

| Prioridade | Item | Tempo | Dependências |
|-----------|------|-------|--------------|
| **P2** | #7: Melhorar histórico com badges de mercado | 35min | Nenhuma |
| **P2** | Adicionar loading states e feedback visual | 25min | Nenhuma |
| **P3** | Testes unitários para cálculos | 40min | Sprints anteriores |

---

## 🔍 Análise Detalhada: Consolidação Fracionário/Vista

### Contexto
O mercado brasileiro possui dois tipos de mercado para ações:
- **Mercado à Vista**: lotes de 100 ações (ex: `ABEV3`)
- **Mercado Fracionário**: menos de 100 ações (ex: `ABEV3F`)

Na B3, são negociados com tickers diferentes, mas representam o **mesmo ativo**.

### Problema
Atualmente, o sistema trata `ABEV3` e `ABEV3F` como ativos completamente separados:
- Dois registros na tabela `assets`
- Duas linhas na interface de Portfolio
- Posições não consolidadas

### Solução Proposta

#### Opção 1: Normalização no Import (Recomendada)
**Vantagem**: Dados já entram corretos no banco  
**Desvantagem**: Perde informação do mercado original

**Implementação**:
1. No importador B3 (`services/importer.py`):
   ```python
   def normalize_ticker(ticker: str, market: str) -> str:
       """Remove sufixo F de tickers fracionários."""
       if market == "FRACIONARIO" and ticker.endswith("F"):
           return ticker[:-1]
       return ticker
   ```

2. Ajustar lógica de criação de asset:
   ```python
   # Normalizar ticker antes de buscar/criar
   normalized_ticker = normalize_ticker(ticker, market)
   asset = get_asset_by_ticker(normalized_ticker)
   ```

3. Manter campo `market` em `operations`:
   - Permite rastreabilidade (saber se foi mercado fracionário ou vista)
   - Histórico continua completo

#### Opção 2: Consolidação na Visualização
**Vantagem**: Mantém dados brutos  
**Desvantagem**: Complexidade em queries e frontend

**Implementação**:
1. Backend: criar função de consolidação
2. Frontend: agrupar ativos com base em ticker normalizado
3. Mais complexo, mais propenso a bugs

#### Decisão Recomendada
**Opção 1**: Normalização no import com preservação de `market` em operações.

### Migração de Dados Existentes

Se já existem dados importados:

```sql
-- Criar coluna temporária
ALTER TABLE assets ADD COLUMN normalized_ticker TEXT;

-- Normalizar tickers
UPDATE assets 
SET normalized_ticker = REPLACE(ticker, 'F', '')
WHERE ticker LIKE '%F' AND asset_class = 'AÇÕES';

-- Consolidar operações (CUIDADO: backup antes!)
-- 1. Identificar asset_id destino (sem F)
-- 2. Atualizar operations para apontar para asset_id consolidado
-- 3. Deletar assets duplicados (com F)
```

**⚠️ ATENÇÃO**: Requer script de migração cuidadoso e testado.

---

## 📊 Métricas de Sucesso

Após implementação das correções, validar:

### Critérios de Aceitação Sprint 1

1. **Totalizadores da Carteira**
   - [ ] "Valor Atual" mostra soma correta de todas posições
   - [ ] "Total Investido" mostra soma de todas compras
   - [ ] "Total Resgatado" mostra soma de todas vendas

2. **Valores por Ativo**
   - [ ] "Posição Atual" mostra quantidade consolidada (compras - vendas)
   - [ ] "Total Comprado" mostra valor correto em R$
   - [ ] "Total Vendido" mostra valor correto em R$

3. **Detalhe do Ativo**
   - [ ] "Preço Médio" calculado corretamente
   - [ ] "Total Investido" mostra valor total de compras
   - [ ] Histórico exibe todas operações do ativo

4. **Consolidação Fracionário/Vista**
   - [ ] `ABEV3` e `ABEV3F` aparecem como um único ativo
   - [ ] Posição consolida ambos os mercados
   - [ ] Histórico mostra badge identificando mercado

### Critérios de Aceitação Sprint 2

5. **UX do Histórico**
   - [ ] Badge visual para "À Vista" e "Fracionário"
   - [ ] Filtro por mercado funcional
   - [ ] Design consistente com tema

6. **Qualidade**
   - [ ] Testes unitários para cálculos críticos
   - [ ] Validação de tipos em queries SQL
   - [ ] Tratamento de edge cases (divisão por zero)

---

## 🧪 Plano de Testes

### Testes Manuais

#### Teste 1: Validar Importação e Cálculos
1. Deletar banco de dados: `rm backend/app/data/portfolio.db`
2. Reiniciar containers: `./portfolio restart`
3. Importar arquivo B3 real
4. Verificar valores na página Portfolio
5. Verificar valores no detalhe de um ativo

#### Teste 2: Consolidação Fracionário/Vista
1. Importar arquivo com operações em `ABEV3` e `ABEV3F`
2. Verificar se aparece como um único ativo
3. Validar que posição = soma de ambos os mercados
4. Verificar histórico mostra ambas operações

#### Teste 3: Edge Cases
- [ ] Ativo com apenas compras (sem vendas)
- [ ] Ativo com apenas vendas (sem compras) - não deveria existir
- [ ] Ativo com posição zerada (vendeu tudo)
- [ ] Múltiplas operações no mesmo dia

### Testes Automatizados

Criar testes em `/backend/tests/`:

```python
# test_calculations.py
def test_total_bought_value_calculation():
    """Valida cálculo de valor total investido."""
    # Criar asset
    asset_id = create_asset("PETR4", "AÇÕES", "PN", "Petrobras")
    
    # Criar operações
    create_operation({
        "asset_id": asset_id,
        "movement_type": "COMPRA",
        "quantity": 100,
        "price": 30.50,
        "trade_date": "2025-01-01",
        "source": "B3_IMPORT",
        "market": "VISTA"
    })
    
    # Validar
    assets = list_assets()
    asset = next(a for a in assets if a["id"] == asset_id)
    
    assert asset["total_bought_value"] == 3050.0
    assert asset["current_position"] == 100
```

---

## 📝 Checklist de Implementação

### Fase 1: Diagnóstico (✅ Completo)
- [x] Identificar problemas
- [x] Analisar código existente
- [x] Criar roadmap

### Fase 2: Correções Críticas (⏳ A Fazer)
- [ ] Conectar ao SQLite e validar dados
- [ ] Corrigir inserção do campo `value` em operações
- [ ] Corrigir query de `list_assets()` com COALESCE
- [ ] Adicionar cálculo de preço médio no detalhe
- [ ] Testar com dados reais

### Fase 3: Consolidação (✅ Completo - 3 Jan 2026)
- [x] Implementar normalização de ticker no importer
- [x] Criar script de migração para dados existentes
- [x] Criar testes unitários (15 casos de teste)
- [x] Documentar guia completo de uso
- [ ] Testar consolidação end-to-end com dados reais (próximo passo)
- [ ] Validar histórico mantém distinção de mercado

### Fase 4: Melhorias UX (⏳ A Fazer)
- [ ] Adicionar badges de mercado no histórico
- [ ] Implementar filtro por mercado
- [ ] Adicionar loading states
- [ ] Validar design responsivo

### Fase 5: Testes e Documentação (⏳ A Fazer)
- [ ] Escrever testes unitários
- [ ] Executar testes manuais
- [ ] Atualizar documentação de API
- [ ] Criar guia de troubleshooting

---

## 🎓 Lições Aprendidas e Prevenção

### Problemas Identificados
1. **Cálculos financeiros não validados em desenvolvimento**
   - Faltou teste manual com dados reais
   - Queries SQL não foram testadas isoladamente

2. **Normalização de dados não considerada**
   - Peculiaridade do mercado brasileiro (fracionário/vista) não mapeada
   - Faltou análise de domínio antes de modelar

3. **Falta de testes unitários para lógica de negócio**
   - Cálculos críticos sem cobertura de testes
   - Facilita regressões em mudanças futuras

### Recomendações para Futuro

1. **Sempre validar cálculos financeiros**
   - Teste manual com dados reais antes de deploy
   - Validar manualmente no SQLite

2. **Documentar peculiaridades do domínio**
   - Mercado fracionário/vista deve estar documentado
   - Outros casos especiais (ex: bonificações, desdobramentos)

3. **Testes unitários obrigatórios para cálculos**
   - Todo cálculo financeiro deve ter teste
   - Incluir edge cases (divisão por zero, valores negativos)

4. **Code review focado em lógica de negócio**
   - Revisar queries SQL cuidadosamente
   - Validar tipos de dados (REAL vs TEXT)

---

## 📚 Referências

- [docs/STATUS-PROJETO.md](STATUS-PROJETO.md) - Estado atual do projeto
- [docs/REFERENCIA-TECNICA.md](REFERENCIA-TECNICA.md) - Especificações técnicas
- [docs/architecture/principios-core.md](architecture/principios-core.md) - Princípios arquiteturais
- [backend/app/repositories/assets_repository.py](../backend/app/repositories/assets_repository.py) - Código atual de cálculos
- [backend/app/repositories/operations_repository.py](../backend/app/repositories/operations_repository.py) - Código de operações

---

## ✅ Próximos Passos Imediatos

1. **[ ] Validar dados no SQLite** (5min)
   ```bash
   ./portfolio exec backend "sqlite3 /app/app/data/portfolio.db 'SELECT * FROM operations LIMIT 10'"
   ```

2. **[ ] Iniciar correção do problema #4** (30min)
   - Arquivo: `backend/app/repositories/operations_repository.py`
   - Garantir campo `value` é REAL

3. **[ ] Testar localmente** (10min)
   - Reimportar arquivo B3
   - Validar valores na interface

4. **[ ] Commit das correções críticas**
   ```bash
   git commit -m "fix: corrige cálculos de valores da carteira (P0)"
   ```

5. **[ ] Planejar consolidação fracionário/vista** (Sprint separada)
   - Criar issue detalhada
   - Discutir abordagem com time

---

**Documento criado por**: GitHub Copilot  
**Última atualização**: 3 de janeiro de 2026  
**Versão**: 1.0
