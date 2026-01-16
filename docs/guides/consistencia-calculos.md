# Consistência de Cálculos: Dashboard vs Carteira

## Problema Identificado

**Sintoma:** Dashboard e Carteira mostravam valores diferentes para "Valor Atual da Carteira":
- **Dashboard:** R$ 67.652,37
- **Carteira:** R$ 58.465,92
- **Diferença:** R$ 9.186,45

## Diagnóstico

### Causas Raiz

1. **Dashboard (antes da correção):**
   - Buscava cotações APENAS de Ações e ETFs
   - Usava **valor investido** para FIIs e outros ativos
   - Somava R$ 24.556 de FIIs como valor investido (não mark-to-market)

2. **Carteira (antes da correção):**
   - Buscava cotações de todos os ativos
   - **NÃO contabilizava** ativos sem cotação disponível
   - Ignorava CIEL3 (sem cotação) = R$ 2.466

### Análise Detalhada

```
Dashboard (valor incorreto):
├─ Ações/ETF com cotação:   R$ 43.096 ✅
├─ FIIs (valor investido):  R$ 24.556 ❌ (deveria ser cotação)
└─ Total:                   R$ 67.652

Carteira (valor incorreto):
├─ Ações/ETF com cotação:   R$ 43.096 ✅
├─ FIIs com cotação:        R$ 15.370 ✅ (mas estava faltando)
├─ CIEL3 sem cotação:       R$     0 ❌ (deveria somar valor investido)
└─ Total:                   R$ 58.466

Valor correto (mark-to-market):
├─ Ativos com cotação:      R$ 58.444 ✅
├─ CIEL3 (valor investido): R$  2.466 ✅
└─ Total:                   R$ 60.910 ✅
```

## Solução Implementada

### 1. Backend - Dashboard Repository

**Mudança:** Buscar cotações de **TODOS** os ativos (não apenas Ações/ETFs).

```python
# ❌ ANTES - Apenas Ações e ETFs
cursor.execute("""
    SELECT ticker, ...
    FROM assets a
    WHERE a.status = 'ACTIVE' AND (a.asset_class = 'AÇÕES' OR a.asset_class = 'ETF')
""")

# ✅ DEPOIS - Todos os ativos
cursor.execute("""
    SELECT ticker, asset_class, ...
    FROM assets a
    WHERE a.status = 'ACTIVE'
    GROUP BY a.ticker, a.asset_class
""")
```

**Mudança:** Remover cálculo separado de "outros ativos".

```python
# ❌ ANTES - Somava valor investido de FIIs
cursor.execute("""
    SELECT SUM(bought - sold) FROM operations
    WHERE asset_class NOT IN ('AÇÕES', 'ETF')
""")
current_value += other_value  # Valor investido, não mark-to-market!

# ✅ DEPOIS - FIIs incluídos no loop principal com cotação
# (código removido, lógica agora é unificada)
```

### 2. Frontend - Portfolio.tsx

**Mudança:** Implementar fallback para ativos sem cotação.

```typescript
// ❌ ANTES - Ignorava ativos sem cotação
const portfolioMarketValue = assets.reduce((sum, asset) => {
  const quote = quotes[asset.ticker];
  
  if (quote && quote.price && position > 0) {
    return sum + (quote.price * position);
  }
  
  return sum;  // ❌ Retorna sem somar nada!
}, 0);

// ✅ DEPOIS - Fallback para valor investido
const portfolioMarketValue = assets.reduce((sum, asset) => {
  const quote = quotes[asset.ticker];
  const position = asset.current_position || 0;
  
  if (position > 0) {
    if (quote && quote.price) {
      return sum + (quote.price * position);  // Mark-to-market
    } else {
      const invested = asset.total_bought_value - asset.total_sold_value;
      return sum + invested;  // ✅ Fallback para valor investido
    }
  }
  
  return sum;
}, 0);
```

## Resultado

### Valores Após Correção

| Local | Valor | Status |
|-------|-------|--------|
| Dashboard | R$ 60.909,73 | ✅ Correto |
| Carteira | R$ 60.909,73 | ✅ Correto |
| Diferença | R$ 0,00 | ✅ Consistente |

### Detalhamento do Cálculo

```
Ações/ETFs com cotação:
  ABEV3:  160 x R$  14,11 = R$  2.257,60
  B3SA3:   53 x R$  15,29 = R$    810,37
  BRSR6:  380 x R$  16,25 = R$  6.175,00
  COGN3:  780 x R$   3,68 = R$  2.870,40
  ISAE4:  101 x R$  25,94 = R$  2.619,94
  ITSA3:  110 x R$  12,18 = R$  1.339,80
  ITSA4:  991 x R$  12,03 = R$ 11.921,73
  IVVB11:  10 x R$ 419,40 = R$  4.194,00
  JHSF3:  207 x R$   8,51 = R$  1.761,57
  KLBN4:  900 x R$   3,72 = R$  3.348,00
  MDIA3:   60 x R$  24,66 = R$  1.479,60
  WIZC3:  200 x R$   9,26 = R$  1.852,00
                            ---------------
  Subtotal Ações/ETF:      R$ 40.630,01

FIIs com cotação:
  BTHF11:  20 x R$   8,95 = R$    179,00
  HGRU11:  24 x R$ 128,00 = R$  3.072,00
  RECR11:  30 x R$  82,73 = R$  2.481,90
  RECT11:  52 x R$  38,55 = R$  2.004,60
  TRXF11:  20 x R$  96,49 = R$  1.929,80
  VINO11:  63 x R$   5,34 = R$    336,42
  XPML11:  71 x R$ 110,00 = R$  7.810,00
                            ---------------
  Subtotal FIIs:           R$ 17.813,72

Ativos sem cotação (fallback):
  CIEL3:  valor investido = R$  2.466,00
                            ---------------
  Subtotal sem cotação:    R$  2.466,00

═══════════════════════════════════════════
TOTAL CARTEIRA:            R$ 60.909,73
```

## Princípios de Cálculo

### Regra Geral

1. **Com cotação disponível:** usar **mark-to-market** (preço × quantidade)
2. **Sem cotação:** usar **valor investido** líquido (compras - vendas)

### Mark-to-Market

> Valor atual de mercado baseado em cotações reais (yfinance)

**Vantagens:**
- Reflete valor real de liquidação
- Atualizado a cada 15 minutos (cache)
- Transparência para o usuário

### Fallback para Valor Investido

> Quando cotação não disponível ou API falha

**Casos de uso:**
- Ação sem liquidez (ex: CIEL3)
- API yfinance temporariamente indisponível
- Ticker não encontrado

## Como Testar

### 1. Verificar Consistência

```bash
# Dashboard
curl -s http://localhost:8000/dashboard/summary | python3 -m json.tool | grep current_value

# Simular cálculo da Carteira
python3 << 'EOF'
import requests

assets = requests.get('http://localhost:8000/assets').json()
quotes = requests.get('http://localhost:8000/quotes/portfolio/current').json()

total = 0
for asset in assets:
    pos = asset['current_position']
    if pos > 0:
        if asset['ticker'] in quotes:
            total += quotes[asset['ticker']]['price'] * pos
        else:
            total += asset['total_bought_value'] - asset['total_sold_value']

print(f"Carteira: R$ {total:,.2f}")
EOF
```

### 2. Logs de Cálculo

```bash
# Buscar logs do Dashboard
docker compose logs api | grep -E "📊|💰|⚠️"

# Verificar ativos sem cotação
docker compose logs api | grep "⚠️"
```

### 3. Validação Frontend

Acesse:
- Dashboard: http://localhost:5173
- Carteira: http://localhost:5173/portfolio

Compare o card **"Valor Atual da Carteira"** em ambas as páginas.

## Monitoramento

### Alertas Importantes

⚠️ **Ativos sem cotação** aparecem nos logs como:
```
⚠️  CIEL3 (AÇÕES): sem cotação, usando valor investido R$ 2466.00
```

🔍 **Investigar se:**
- Ticker está correto
- Ação ainda é negociada
- API yfinance está respondendo

### Métricas

| Métrica | Valor Esperado |
|---------|----------------|
| Ativos com cotação | > 95% |
| Diferença Dashboard/Carteira | = 0 |
| Tempo de resposta quotes | < 500ms |

## Próximos Passos

- [ ] Adicionar indicador visual para ativos sem cotação no frontend
- [ ] Implementar cache de longo prazo para ativos ilíquidos
- [ ] Alertar usuário quando valor investido é usado no lugar de cotação
- [ ] Criar endpoint de health check para validar consistência

## Referências

- [Otimização de Cotações](./otimizacao-carteira.md)
- [Atualização de Cotações](./atualizacao-cotacoes.md)
- [Dashboard Repository](../../backend/app/repositories/dashboard_repository.py)
- [Portfolio Component](../../frontend/src/pages/Portfolio.tsx)
