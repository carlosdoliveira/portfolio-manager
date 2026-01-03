# 📊 Guia: Consolidação de Mercados (Fracionário + À Vista)

**Data**: 3 de janeiro de 2026  
**Versão**: 2.0 (Atualizado com normalização de tickers)  
**Status**: ✅ Implementado

---

## 📋 Visão Geral

No mercado brasileiro de ações, existem dois tipos de negociação:

- **Mercado à Vista**: Lotes padrão de 100 ações (ex: `ABEV3`, `PETR4`)
- **Mercado Fracionário**: Menos de 100 ações (ex: `ABEV3F`, `PETR4F`)

Embora negociados com **tickers diferentes**, representam o **mesmo ativo**. O Portfolio Manager v2 implementa **consolidação automática em dois níveis**:

1. **Normalização de Ticker** (nível de ativo): `ABEV3F` → `ABEV3`
2. **Consolidação de Operações** (nível de cálculos): Soma todas operações independente do mercado

---

## 🎯 Comportamento do Sistema

### Antes da Implementação
```
Carteira:
├─ ABEV3  (100 ações, mercado à vista)
└─ ABEV3F (20 ações, mercado fracionário)

Total na carteira: 2 linhas separadas ❌
```

### Depois da Implementação
```
Carteira:
└─ ABEV3 (120 ações consolidadas)
    ├─ 100 do mercado à vista
    └─ 20 do mercado fracionário

Total na carteira: 1 linha ✅
```

**Histórico de operações** continua mostrando a origem de cada operação (vista ou fracionário).

---

## ⚙️ Como Funciona

### Nível 1: Normalização de Ticker no Import

Quando um arquivo B3 é importado, o sistema:

1. **Identifica o mercado** de cada operação
2. **Normaliza o ticker**:
   - Se `MERCADO FRACIONARIO` + ticker termina com `F` → Remove o `F`
   - Caso contrário → Mantém o ticker original
3. **Cria ou busca o ativo consolidado**
4. **Vincula a operação** ao ativo consolidado
5. **Mantém o campo `market`** em cada operação para rastreabilidade

#### Código de Normalização

```python
def normalize_ticker(ticker: str, market: str) -> str:
    """
    Remove sufixo F de tickers fracionários.
    
    Examples:
        >>> normalize_ticker("ABEV3F", "MERCADO FRACIONARIO")
        "ABEV3"
        
        >>> normalize_ticker("ABEV3", "MERCADO A VISTA")
        "ABEV3"
    """
    ticker = ticker.strip().upper()
    market = (market or "").strip().upper()
    
    if "FRACIONARIO" in market and ticker.endswith("F"):
        return ticker[:-1]
    
    return ticker
```

### Nível 2: Consolidação de Operações

Na listagem de ativos, a query SQL agrega **todas as operações** do ativo consolidado:

```sql
SELECT 
    a.id, 
    a.ticker, 
    -- Soma TODAS compras (vista + fracionário)
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) as total_bought,
    -- Soma TODAS vendas (vista + fracionário)
    SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.quantity ELSE 0 END) as total_sold,
    -- Posição = comprado - vendido
    (SUM(...) - SUM(...)) as current_position,
    -- Valores em R$
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) as total_bought_value,
    SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.value ELSE 0 END) as total_sold_value
FROM assets a
LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
WHERE a.status = 'ACTIVE'
GROUP BY a.id;
```

### Fluxo Completo de Importação

```
Arquivo B3 (Excel)
    ↓
Leitura do DataFrame
    ↓
Para cada linha:
    ├─ ticker_raw = "ABEV3F"
    ├─ market = "MERCADO FRACIONARIO"
    ├─ ticker_normalized = normalize_ticker("ABEV3F", "MERCADO FRACIONARIO")
    ├─ ticker_normalized = "ABEV3"
    ↓
Criar/Buscar ativo com ticker "ABEV3"
    ↓
Criar operação vinculada ao ativo "ABEV3"
    ├─ quantity: 20
    ├─ price: 15.50
    ├─ market: "MERCADO FRACIONARIO" ← mantido para histórico
    ↓
Resultado: Operação consolidada no ativo "ABEV3"
```

---

## 📊 Exemplos Práticos

### Exemplo 1: Compras em Ambos Mercados

**Operações**:
```
01/01/2026 | COMPRA | MERCADO A VISTA     | ABEV3  | 100 | R$ 15,00 | R$ 1.500
02/01/2026 | COMPRA | MERCADO FRACIONARIO | ABEV3F | 20  | R$ 15,50 | R$ 310
```

**Resultado na Carteira**:
```
ABEV3
├─ Posição Atual: 120 ações
├─ Total Investido: R$ 1.810,00
├─ Preço Médio: R$ 15,08
└─ Total de Operações: 2
```

### Exemplo 2: Compra e Venda Consolidadas

**Operações**:
```
01/01/2026 | COMPRA | MERCADO A VISTA     | PETR4  | 200 | R$ 30,00 | R$ 6.000
15/01/2026 | VENDA  | MERCADO FRACIONARIO | PETR4F | 50  | R$ 32,00 | R$ 1.600
```

**Resultado na Carteira**:
```
PETR4
├─ Posição Atual: 150 ações (200 - 50)
├─ Total Comprado: R$ 6.000,00
├─ Total Vendido: R$ 1.600,00
└─ Investimento Líquido: R$ 4.400,00
```

---

## 📱 Visualização na Interface

### Página Portfolio

```
┌─────────────────────────────────────────────────────┐
│ ABEV3 - Ambev S.A.                      Ações / ON  │
├─────────────────────────────────────────────────────┤
│ Posição Atual:    120 ações                         │
│ Total Comprado:   R$ 1.810,00                       │
│ Total Vendido:    R$ 0,00                           │
│ Preço Médio:      R$ 15,08                          │
└─────────────────────────────────────────────────────┘
```

### Histórico de Operações (Detalhe do Ativo)

```
┌────────────┬────────┬──────────┬────────┬───────────┬───────────┐
│ Data       │ Tipo   │ Mercado  │ Qtd    │ Preço     │ Valor     │
├────────────┼────────┼──────────┼────────┼───────────┼───────────┤
│ 02/01/2026 │ COMPRA │ 🟦 Vista │ 100    │ R$ 15,00  │ R$ 1.500  │
│ 03/01/2026 │ COMPRA │ 🟨 Frac  │ 20     │ R$ 15,50  │ R$ 310    │
└────────────┴────────┴──────────┴────────┴───────────┴───────────┘

Consolidado: 120 ações por R$ 1.810,00 (preço médio: R$ 15,08)
```

---

## 🔄 Migração de Dados Existentes

Se você já possui dados importados **antes** da consolidação, use o script de migração:

### Passo 1: Backup do Banco

```bash
cp backend/app/data/portfolio.db backend/app/data/portfolio.db.backup
```

### Passo 2: Dry-Run (Simular)

```bash
docker compose exec backend python scripts/migrate_consolidate_tickers.py --dry-run
```

**Saída esperada**:
```
🔄 MIGRAÇÃO: Consolidação de Tickers Fracionários
⚠️  MODO DRY-RUN: Nenhuma alteração será feita no banco

📊 Encontrados 3 tickers fracionários:

🔹 Processando: ABEV3F (ID: 5)
   Operações ativas: 2
  ✅ Ativo consolidado já existe: ABEV3 (ID: 2)
  🔍 [DRY-RUN] Migraria 2 operações
  🔍 [DRY-RUN] Marcaria ativo 5 como DELETED

✅ DRY-RUN COMPLETO - Nenhuma alteração foi feita
   • 3 ativos seriam consolidados
   • 5 operações seriam migradas
```

### Passo 3: Executar Migração

```bash
docker compose exec backend python scripts/migrate_consolidate_tickers.py
```

O script pedirá confirmação antes de modificar o banco.

### Passo 4: Validar

```bash
# Ver ativos consolidados
docker compose exec backend sqlite3 /app/app/data/portfolio.db \
  "SELECT ticker, COUNT(*) as ops FROM assets a 
   JOIN operations o ON a.id = o.asset_id 
   WHERE a.status = 'ACTIVE' 
   GROUP BY ticker;"
```

---

## 🧪 Testes

### Testes Automatizados

```bash
# Rodar testes de normalização
docker compose exec backend pytest tests/test_ticker_normalization.py -v
```

**Cobertura**:
- ✅ Normalização de tickers fracionários
- ✅ Manutenção de tickers à vista
- ✅ Tratamento de edge cases (espaços, maiúsculas/minúsculas)
- ✅ Mercados com valores None ou vazios
- ✅ FIIs com F no nome (não devem ser normalizados)
- ✅ Tickers comuns (PETR4, VALE3, ITUB4, etc.)

### Teste Manual

1. **Criar arquivo B3 de teste** com operações em ambos mercados

2. **Importar via interface** (`/import`)

3. **Validar**:
   - ✅ Apenas 1 ativo `ABEV3` aparece na carteira
   - ✅ Posição mostra 120 ações
   - ✅ Histórico exibe ambas operações com distinção de mercado

---

## ❓ FAQ

### 1. O que acontece se eu importar um arquivo com ABEV3F depois de já ter importado ABEV3?

✅ **Resposta**: As operações serão consolidadas automaticamente no ativo `ABEV3`. O sistema normaliza o ticker `ABEV3F` para `ABEV3` antes de criar a operação.

### 2. Eu vou perder a informação de qual mercado foi a operação?

❌ **Não**. O campo `market` em `operations` é preservado. O histórico continua mostrando se foi mercado à vista ou fracionário.

### 3. E se eu já tenho dados importados com ABEV3 e ABEV3F separados?

🔧 **Use o script de migração**:
```bash
docker compose exec backend python scripts/migrate_consolidate_tickers.py
```

### 4. FIIs e ETFs também são consolidados?

❌ **Não**. A normalização só se aplica a tickers com sufixo `F` em mercado fracionário. FIIs (ex: HGLG11, HFOF11) e ETFs (ex: BOVA11) não são afetados.

### 5. Posso desabilitar a consolidação?

⚠️ **Não recomendado**. A consolidação é parte fundamental da lógica de negócio. Se desabilitar, você terá posições duplicadas e cálculos incorretos.

### 6. Como calcular o preço médio considerando ambos os mercados?

💡 **Automático**. O sistema calcula:
```
preço_médio = total_investido / total_quantidade

Exemplo:
- 100 ações à vista a R$ 15,00 = R$ 1.500,00
- 20 ações fracionárias a R$ 15,50 = R$ 310,00
- Total: R$ 1.810,00 / 120 = R$ 15,08
```

### 7. A consolidação afeta operações manuais (CRUD)?

✅ **Sim**. Se você criar uma operação manual para `ABEV3`, ela será consolidada com operações importadas de `ABEV3F`. O sistema trata tudo de forma uniforme.

### 8. Posso ver quantas operações foram de cada mercado?

✅ **Sim**. No histórico do ativo, cada operação mostra o campo `market`. Você pode filtrar ou contar por mercado se necessário.

---

## 🎨 Melhorias Futuras

### Badges de Mercado no Histórico (P2)

**Status**: Planejado no roadmap

```tsx
// Em AssetDetail.tsx
<span className={`market-badge market-badge-${market.toLowerCase()}`}>
  {market === "MERCADO A VISTA" ? "🟦 Vista" : "🟨 Fracionário"}
</span>
```

CSS correspondente:
```css
.market-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: 600;
}

.market-badge-vista {
  background-color: #E3F2FD;
  color: #1976D2;
}

.market-badge-fracionario {
  background-color: #FFF9C4;
  color: #F57F17;
}
```

### Filtro por Mercado (P2)

Permitir filtrar operações no histórico:
- 🔵 Todas
- 🟦 Apenas Vista
- 🟨 Apenas Fracionário

---

## 📚 Referências

- [Problema Original (Item #2)](../CORRECAO-CALCULOS-CARTEIRA.md#2-❌-falta-consolidação-fracionáriovista)
- [Código: normalize_ticker()](../../backend/app/services/importer.py)
- [Testes: test_ticker_normalization.py](../../backend/tests/test_ticker_normalization.py)
- [Script de Migração](../../backend/scripts/migrate_consolidate_tickers.py)
- [B3: Mercado Fracionário](http://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/mercado-fracionario/)

---

**Documento criado por**: GitHub Copilot  
**Última atualização**: 3 de janeiro de 2026  
**Versão**: 2.0
