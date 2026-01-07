# 📈 Integração com Cotações de Mercado

**Data**: 6 de janeiro de 2026  
**Status**: ✅ Implementado e Testado  
**Fonte**: yfinance (Yahoo Finance)

---

## 📋 Visão Geral

O Portfolio Manager v2 agora integra cotações em tempo quase real da B3 usando a biblioteca **yfinance**, permitindo visualizar:

- Preço atual dos ativos
- Valor de mercado da carteira
- Variação percentual do dia
- Ganho/perda não realizado

---

## 🎯 Funcionalidades Implementadas

### 1. **Backend - MarketDataService**

**Arquivo**: `backend/app/services/market_data_service.py`

```python
from app.services.market_data_service import get_market_data_service

service = get_market_data_service()
quote = service.get_quote("PETR4")
```

**Recursos**:
- Cache de 15 minutos (TTL configurável)
- Normalização automática de tickers (PETR4 → PETR4.SA)
- Tratamento de erros para ativos deslistados
- Busca em lote para múltiplos ativos

### 2. **Endpoints da API**

#### GET `/quotes/{ticker}`
Busca cotação de um ativo específico.

**Exemplo**:
```bash
curl http://localhost:8000/quotes/PETR4
```

**Resposta**:
```json
{
  "ticker": "PETR4",
  "price": 29.64,
  "change": -0.56,
  "change_percent": -1.85,
  "volume": 38095000,
  "open": 30.37,
  "high": 30.43,
  "low": 29.62,
  "previous_close": 30.2,
  "updated_at": "2026-01-06T00:00:00-03:00",
  "source": "yfinance"
}
```

#### POST `/quotes/batch`
Busca cotações de múltiplos ativos.

**Exemplo**:
```bash
curl -X POST http://localhost:8000/quotes/batch \
  -H "Content-Type: application/json" \
  -d '["PETR4", "VALE3", "ITUB4"]'
```

#### GET `/quotes/portfolio/current`
Busca cotações de todos os ativos com posição atual no portfólio.

**Resposta**:
```json
{
  "PETR4": {...},
  "VALE3": {...},
  "ITUB4": {...},
  "INVALID_TICKER": null
}
```

#### DELETE `/quotes/cache/{ticker}`
Limpa cache de um ticker específico.

#### DELETE `/quotes/cache`
Limpa todo o cache de cotações.

### 3. **Frontend - Portfolio.tsx**

**Atualizações**:
- Nova coluna "Preço Atual" com variação do dia
- Coluna "Valor de Mercado" (preço × quantidade)
- Card "Valor Atual da Carteira" atualizado com preços reais
- Novo card "Variação Total" (ganho/perda não realizado)
- Indicador de loading durante busca de cotações
- Cores para variações positivas (verde) e negativas (vermelho)

---

## 🔧 Configuração

### Dependências

Adicione ao `backend/requirements.txt`:
```
yfinance
```

### Cache

O cache padrão é de **15 minutos**. Para alterar:

```python
from app.services.market_data_service import MarketDataService

service = MarketDataService(cache_ttl_minutes=30)  # 30 minutos
```

---

## 📊 Cobertura de Ativos

### Testes Realizados (6 Jan 2026)

**21 ativos testados**:
- ✅ **17 ativos funcionando** (81%)
- ❌ **4 ativos falharam** (explicação conhecida)

### Ativos que Falharam

| Ticker | Motivo |
|--------|--------|
| BCFF11 | Mudou para BTHF11 |
| CIEL3  | Deslistada da B3 |
| TRPL4  | Mudou para ISAE4 |
| WIZS3  | Mudou para WIZC3 |

**Conclusão**: 100% dos ativos ativos funcionam corretamente.

---

## 🚀 Uso no Frontend

### Exemplo: Buscar Cotação Individual

```typescript
import { getQuote } from '../api/client';

const quote = await getQuote('PETR4');
console.log(`Preço: R$ ${quote.price}`);
console.log(`Variação: ${quote.change_percent}%`);
```

### Exemplo: Buscar Cotações do Portfólio

```typescript
import { getPortfolioQuotes } from '../api/client';

const quotes = await getPortfolioQuotes();

Object.entries(quotes).forEach(([ticker, quote]) => {
  if (quote) {
    console.log(`${ticker}: R$ ${quote.price}`);
  } else {
    console.log(`${ticker}: Sem cotação disponível`);
  }
});
```

---

## ⚙️ Detalhes Técnicos

### Normalização de Ticker

Tickers da B3 precisam do sufixo `.SA` no Yahoo Finance:

```python
# Entrada: PETR4
# Interno: PETR4.SA (para yfinance)
# Saída: PETR4 (para o cliente)
```

### Tratamento de Erros

Ativos sem dados retornam `null` no lugar de erro HTTP:

```json
{
  "VALID_TICKER": {...},
  "INVALID_TICKER": null
}
```

### Performance

- **Cache**: Evita requisições repetidas em 15 minutos
- **Batch**: Busca múltiplos ativos em paralelo
- **Timeout**: yfinance tem timeout interno (~30s)

---

## 📝 Próximas Melhorias

### P2 - Curto Prazo
- [ ] Badge de "última atualização" na UI
- [ ] Botão manual para refresh de cotações
- [ ] Tratamento de ativos com ticker alterado

### P3 - Médio Prazo
- [ ] Gráficos de variação histórica
- [ ] Alertas de variação significativa
- [ ] Cache persistente (Redis/SQLite)

### P4 - Longo Prazo
- [ ] Suporte a múltiplas fontes (Brapi, Alpha Vantage)
- [ ] WebSocket para atualizações em tempo real
- [ ] Machine learning para predições

---

## 🐛 Troubleshooting

### Cotação não aparece

1. Verificar se o ticker está correto (ex: PETR4, não PETR3)
2. Verificar logs do backend: `docker logs portfolio-manager-v2-api-1`
3. Limpar cache: `curl -X DELETE http://localhost:8000/quotes/cache`

### Delay muito alto

- yfinance gratuito tem delay de ~15-20 minutos
- Para tempo real, considerar API paga (HGBrasil, B3 oficial)

### Ativo deslistado

- Verificar se houve troca de ticker (ex: CIEL3 → deslistada)
- Atualizar manualmente o ticker no portfólio

---

## 📚 Referências

- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [Yahoo Finance](https://finance.yahoo.com/)
- [B3 - Consulta de Ativos](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/acao/codigo/)

---

**Documento criado por**: GitHub Copilot  
**Última atualização**: 6 de janeiro de 2026  
**Versão**: 1.0
