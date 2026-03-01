# 🎯 Roadmap de Reconciliação de Posições

**Data:** 17/01/2026  
**Status:** 🔴 CRÍTICO - Posições com erro de +2.925%

---

## 🔍 Diagnóstico do Problema

### Situação Atual
- **Posição Real (B3):** 4.558,14 ações
- **Posição Sistema:** 137.876,00 ações
- **Diferença:** +133.317,86 ações **(2.925% acima!)**
- **Tickers com erro:** 11 de 11 (100%)

### Causa Raiz Identificada

O **arquivo de movimentação B3** (`movimentacao-*.xlsx`) contém registros de "Atualização" que NÃO são operações reais de compra/venda, mas sim **snapshots de posição** gerados após eventos corporativos:

```
Exemplo ITSA4:
- 2021-08-26: 7 registros "Atualização" (saldo após bonificação)
- 2023-10-02: 6 registros "Atualização" (saldo após dividendos)
- 2024-03-08: 5 registros "Atualização" (saldo após split)
```

**O sistema está importando TODAS como compras**, multiplicando a posição real!

---

## 🚨 Impacto nos Ativos

| Ticker | Posição B3 | Posição Sistema | Erro (%) |
|--------|------------|-----------------|----------|
| ITSA4  | 1.248,48   | 56.254,00       | +4.406%  |
| ITSA3  | 140,76     | 7.380,00        | +5.143%  |
| JHSF3  | 207,00     | 8.466,00        | +3.989%  |
| BRSR6  | 380,00     | 8.270,00        | +2.076%  |
| KOGN3  | 968,00     | 7.708,00        | +696%    |

---

## ✅ Solução Proposta

### Fase 1: Correção do Importador ⚡ **URGENTE**

#### 1.1. Identificar Registros de "Atualização"

No arquivo de movimentação, a coluna `Movimentação` contém:
- ✅ **Operações reais**: "Compra", "Venda", "Transferência"
- ❌ **Não-operações**: "Atualização", "Rendimento" (sem valor de operação)

**Ação:**
```python
# Em importer.py, ao processar movimentação:
def is_real_operation(row):
    """
    Retorna True apenas para operações que movimentam posição real.
    Filtra snapshots de saldo e rendimentos.
    """
    movimentacao = row.get('Movimentação', '')
    
    # Atualização de saldo = snapshot, não é operação real
    if 'Atualização' in movimentacao:
        return False
    
    # Rendimento sem operação (dividendos, JCP)
    if 'Rendimento' in movimentacao and row.get('Quantidade', 0) == 0:
        return False
    
    # Bonificação com quantidade > 0 É operação real (adiciona ações)
    if 'Bonificação' in movimentacao and row.get('Quantidade', 0) > 0:
        return True
    
    # Compra/Venda tradicionais
    if row.get('Entrada/Saída') in ['Credito', 'Debito']:
        return True
    
    return False
```

#### 1.2. Separar Eventos Corporativos de Operações

**Criar nova lógica:**
- **Operações reais** → Tabela `operations`
- **Eventos informativos** → Tabela `corporate_events_log` (nova)

---

### Fase 2: Importação do Arquivo de Posição 📊

#### 2.1. Criar Endpoint `/import/posicao-b3`

```python
@app.post("/import/posicao-b3")
async def import_posicao_b3(file: UploadFile):
    """
    Importa arquivo de posição B3 (posicao-*.xlsx) e usa
    como fonte de verdade para reconciliação.
    """
    df = pd.read_excel(file.file)
    
    # Validar colunas
    required = ['Código de Negociação', 'Quantidade']
    if not all(col in df.columns for col in required):
        raise ValueError("Arquivo inválido")
    
    # Criar snapshot de posição
    snapshot_date = datetime.now().isoformat()
    
    for _, row in df.iterrows():
        ticker = extract_ticker(row['Código de Negociação'])
        qty_real = row['Quantidade']
        
        # Buscar posição calculada no sistema
        qty_sistema = calculate_position(ticker)
        
        # Se diferente, registrar discrepância
        if abs(qty_sistema - qty_real) > 0.01:
            register_reconciliation_issue(
                ticker=ticker,
                qty_expected=qty_real,
                qty_calculated=qty_sistema,
                snapshot_date=snapshot_date
            )
    
    return {"status": "success", "issues": get_reconciliation_issues()}
```

#### 2.2. Nova Tabela `position_snapshots`

```sql
CREATE TABLE position_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    snapshot_date TEXT NOT NULL,
    source TEXT DEFAULT 'B3',
    created_at TEXT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);
```

---

### Fase 3: Sistema de Reconciliação 🔧

#### 3.1. Endpoint de Diagnóstico

```python
@app.get("/admin/reconciliation/diagnosis")
async def reconciliation_diagnosis():
    """
    Compara posição sistema vs último snapshot B3.
    Retorna lista de discrepâncias com sugestões de correção.
    """
    issues = []
    
    for asset in get_all_assets():
        qty_sistema = calculate_position(asset.ticker)
        qty_snapshot = get_latest_snapshot_position(asset.id)
        
        if qty_snapshot is None:
            continue
        
        diff = qty_sistema - qty_snapshot
        
        if abs(diff) > 0.01:
            # Analisar causa
            possible_causes = analyze_discrepancy(asset.ticker, diff)
            
            issues.append({
                "ticker": asset.ticker,
                "qty_expected": qty_snapshot,
                "qty_calculated": qty_sistema,
                "difference": diff,
                "possible_causes": possible_causes,
                "suggested_actions": suggest_corrections(asset.ticker, diff)
            })
    
    return {"issues": issues, "total_issues": len(issues)}
```

#### 3.2. Correções Automatizadas

```python
@app.post("/admin/reconciliation/auto-fix")
async def auto_fix_positions(ticker: str = None):
    """
    Aplica correções automáticas baseadas em regras:
    1. Remove operações duplicadas (mesma data, qty, preço)
    2. Remove "Atualizações" importadas incorretamente
    3. Ajusta posição final para bater com snapshot B3
    """
    issues_fixed = []
    
    # Se ticker específico ou todos
    tickers = [ticker] if ticker else get_all_tickers()
    
    for t in tickers:
        # 1. Remover atualizações duplicadas
        removed = remove_duplicate_updates(t)
        
        # 2. Recalcular posição
        new_position = calculate_position(t)
        target_position = get_latest_snapshot_position_by_ticker(t)
        
        # 3. Se ainda diferente, criar ajuste manual
        if abs(new_position - target_position) > 0.01:
            create_manual_adjustment(
                ticker=t,
                quantity_adjustment=target_position - new_position,
                reason="Reconciliação automática com posição B3"
            )
        
        issues_fixed.append({
            "ticker": t,
            "operations_removed": removed,
            "final_adjustment": target_position - new_position
        })
    
    return {"fixed": issues_fixed}
```

---

### Fase 4: Interface de Reconciliação 🖥️

#### 4.1. Página `/admin/reconciliation`

**Componentes:**
1. **Upload de Posição B3**
   - Drag & drop do arquivo `posicao-*.xlsx`
   - Validação e preview antes de importar

2. **Dashboard de Discrepâncias**
   ```
   ┌─────────────────────────────────────────┐
   │ 📊 Status de Reconciliação              │
   ├─────────────────────────────────────────┤
   │ ✗ 11 ativos com diferença               │
   │ ✓ 0 ativos reconciliados                │
   │ ⚠️ Diferença total: +133.317,86 ações   │
   └─────────────────────────────────────────┘
   ```

3. **Lista de Problemas**
   - Tabela com ticker, posição B3, posição sistema, diferença
   - Ações: "Ver Detalhes", "Ajustar Automaticamente", "Ajustar Manualmente"

4. **Wizard de Correção**
   - Passo 1: Analisar causas
   - Passo 2: Revisar operações suspeitas
   - Passo 3: Aprovar correções
   - Passo 4: Aplicar e validar

---

## 📅 Cronograma de Implementação

### Sprint 1 (Imediato - 1 dia)
- [ ] Corrigir importador para **filtrar "Atualizações"**
- [ ] Resetar banco e reimportar sem duplicatas
- [ ] Validar posições contra arquivo B3

### Sprint 2 (Curto prazo - 2 dias)
- [ ] Criar tabela `position_snapshots`
- [ ] Implementar endpoint `/import/posicao-b3`
- [ ] Criar endpoint de diagnóstico

### Sprint 3 (Médio prazo - 3 dias)
- [ ] Sistema de correção automática
- [ ] Interface de reconciliação
- [ ] Testes end-to-end

---

## ⚠️ Ação Imediata Recomendada

**ANTES DE CONTINUAR O DESENVOLVIMENTO:**

1. **Parar importações** até corrigir o importador
2. **Resetar banco de dados**
3. **Aplicar fix no `importer.py`** (Fase 1.1)
4. **Reimportar arquivo de movimentação**
5. **Validar contra `posicao-2026-01-17-17-06-15.xlsx`**

---

## 🎯 Critérios de Sucesso

✅ **Posições reconciliadas:**
- Diferença máxima: ±0,01 ação por ticker
- 100% dos tickers do arquivo B3 validados

✅ **Sistema confiável:**
- Import idempotente (mesma posição em múltiplas importações)
- Dashboard mostra posições corretas
- Reconciliação automática funcional

---

## 📚 Referências

- Arquivo de posição: `samples/posicao-2026-01-17-17-06-15.xlsx`
- Arquivo de movimentação: `samples/movimentacao-2026-01-17-15-40-04.xlsx`
- Documentação B3: https://www.b3.com.br/data/files/8F/99/52/81/B7AF081066FF818E9B2BA2A8/Manual-de-Importacao-de-Dados.pdf
