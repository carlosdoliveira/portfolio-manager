# Análise de Oportunidades por Tipo de Investimento

## Data: 2026-01-02

## Visão Geral

Este documento analisa oportunidades de funcionalidades baseadas nos diferentes tipos de investimentos que podem ser gerenciados pela ferramenta Portfolio Manager v2.

---

## Tipos de Investimentos Brasileiros

### 1. Ações (ON/PN)
**Status Atual:** ✅ Suportado (COMPRA/VENDA)

**Características:**
- Negociação em pregão B3
- Dividendos e JCP
- Bonificações
- Desdobramentos e grupamentos
- Subscrições
- Direitos de venda

**Oportunidades:**
1. 🎯 **Proventos (Dividendos e JCP)** - ALTA PRIORIDADE
2. 🎯 **Bonificações** - Recebimento gratuito de ações
3. 🎯 **Desdobramentos/Grupamentos** - Ajuste automático de quantidade
4. 📊 **Preço Médio por Ticker** - Cálculo automático
5. 💰 **Lucro/Prejuízo Realizado** - Por venda
6. 📈 **Posição Consolidada** - Quantidade atual por ticker

---

### 2. Fundos Imobiliários (FIIs)
**Status Atual:** ⚠️ Suportado parcialmente (como ações)

**Características:**
- Dividendos mensais obrigatórios
- Amortizações de cotas
- Subscrições de novas cotas
- Cisão e incorporação
- Isenção de IR em dividendos

**Oportunidades:**
1. 🎯 **Proventos Mensais** - ALTA PRIORIDADE (FIIs pagam todo mês)
2. 🎯 **Amortizações** - Redução de cotas com pagamento
3. 📊 **Yield Mensal** - Rendimento médio mensal
4. 💡 **Alertas de Pagamento** - Próximos dividendos esperados
5. 📈 **DY Acumulado** - Dividend Yield anualizado

---

### 3. Renda Fixa (CDB, LCI, LCA, Tesouro Direto)
**Status Atual:** ❌ Não suportado

**Características:**
- Data de vencimento
- Taxa contratada (% CDI, IPCA+, Pré-fixado)
- Resgate automático ou manual
- Taxa de custódia (Tesouro)
- IR regressivo (15% a 22.5%)

**Oportunidades:**
1. 🎯 **Suporte a Renda Fixa** - ALTA PRIORIDADE
2. 📅 **Data de Vencimento** - Campo obrigatório
3. 💰 **Resgate Automático** - Entrada de saldo no vencimento
4. 📊 **Rentabilidade Contratada** - % CDI, IPCA+, Pré
5. ⚠️ **Alertas de Vencimento** - Próximos resgates
6. 💸 **Taxa de Custódia** - Cálculo automático (Tesouro)
7. 🧮 **Projeção de Rendimento** - Quanto vai render até o vencimento

---

### 4. ETFs (Exchange Traded Funds)
**Status Atual:** ✅ Suportado (como ações)

**Características:**
- Negociação em bolsa
- Dividendos (alguns ETFs)
- Taxa de administração embutida
- Rebalanceamento interno automático

**Oportunidades:**
1. 📊 **Identificação de ETF** - Campo "asset_type" específico
2. 💰 **Proventos** - Alguns ETFs distribuem dividendos
3. 📈 **Tracking Error** - Comparar com índice de referência

---

### 5. BDRs (Brazilian Depositary Receipts)
**Status Atual:** ⚠️ Suportado parcialmente (como ações)

**Características:**
- Representa ação estrangeira
- Dividendos em dólar convertidos
- Taxa de conversão aplicada
- Imposto na fonte (EUA: 30%)

**Oportunidades:**
1. 🎯 **Moeda Estrangeira** - Suporte a USD, EUR
2. 💵 **Conversão Cambial** - Registro de taxa de câmbio
3. 💰 **Proventos em Moeda Estrangeira**
4. 📊 **Ganho/Perda Cambial** - Variação do câmbio

---

### 6. Criptomoedas
**Status Atual:** ❌ Não suportado

**Características:**
- 24/7 negociação
- Alta volatilidade
- Exchanges diferentes
- Transferências entre wallets
- Staking (rendimento)

**Oportunidades:**
1. 🎯 **Suporte a Cripto** - BTC, ETH, etc.
2. 💱 **Múltiplas Exchanges** - Binance, Mercado Bitcoin
3. 🔄 **Transferências** - Entre wallets/exchanges
4. 📊 **Staking Rewards** - Rendimento de staking
5. 💸 **Taxas de Rede** - Gas fees

---

### 7. Fundos de Investimento
**Status Atual:** ❌ Não suportado

**Características:**
- Aplicação e resgate
- Come-cotas semestral (maio/novembro)
- Taxa de administração
- Taxa de performance
- Rendimento sem movimentação física

**Oportunidades:**
1. 🎯 **Suporte a Fundos** - Aplicação/Resgate
2. 📅 **Come-Cotas** - Cálculo automático IR
3. 💰 **Rentabilidade Acumulada** - Sem venda física
4. 📊 **Taxa de Administração** - Impacto no rendimento

---

## Funcionalidades Transversais (Aplicáveis a Múltiplos Tipos)

### 1. **Proventos Completo** 🎯 CRÍTICO
**Aplicável a:** Ações, FIIs, ETFs, BDRs, Alguns Fundos

**Descrição:**
Sistema completo de gerenciamento de proventos (dividendos, JCP, rendimentos)

**Campos necessários:**
- Tipo (Dividendo, JCP, Rendimento, Amortização)
- Valor por cota/ação
- Data COM (última data para ter direito)
- Data de pagamento
- Asset relacionado

**Impacto:**
- Calcula DY (Dividend Yield)
- Rastreia rendimento passivo
- Essencial para estratégia buy & hold
- Base para cálculo de IR (JCP tem retenção)

---

### 2. **Eventos Corporativos** 🎯 ALTA PRIORIDADE
**Aplicável a:** Ações, FIIs, ETFs

**Tipos:**
- Bonificação (ganho de ações grátis)
- Desdobramento (split - 1 ação vira 2)
- Grupamento (1 ação vira 0.5)
- Subscrição (direito de compra com desconto)

**Impacto:**
- Ajusta quantidade de ativos automaticamente
- Mantém preço médio correto
- Essencial para auditoria histórica

---

### 3. **Preço Médio & Posição** 📊 ALTA PRIORIDADE
**Aplicável a:** TODOS os tipos

**Cálculo:**
```
Preço Médio = (Σ (Quantidade × Preço de Compra)) / Quantidade Total
Posição Atual = Quantidade Comprada - Quantidade Vendida
```

**Impacto:**
- Base para cálculo de lucro/prejuízo
- Decisão de compra/venda
- Rebalanceamento de carteira

---

### 4. **Lucro/Prejuízo Realizado** 💰 ALTA PRIORIDADE
**Aplicável a:** Ações, FIIs, ETFs, BDRs, Cripto

**Cálculo:**
```
L/P = (Preço de Venda - Preço Médio) × Quantidade Vendida
```

**Impacto:**
- Saber quanto ganhou/perdeu em cada operação
- Base para IR (day-trade 20%, swing 15%)
- Análise de performance

---

### 5. **Imposto de Renda** 🧮 MÉDIA PRIORIDADE
**Aplicável a:** TODOS (cada tipo tem regra diferente)

**Regras:**
- Ações: 15% sobre lucro (swing), 20% (day-trade), isenção até R$ 20k/mês
- FIIs: Isento em dividendos, 20% sobre ganho de capital
- Renda Fixa: 22.5% a 15% (regressivo)
- Day-trade: 1% retenção na fonte + ajuste na declaração

**Impacto:**
- DARF automático
- Declaração de IR simplificada
- Compliance fiscal

---

### 6. **Integração com APIs de Cotação** 📡 MÉDIA PRIORIDADE
**Aplicável a:** Ações, FIIs, ETFs, BDRs

**Fontes:**
- B3 API (oficial, mas limitada)
- Yahoo Finance (grátis, boa cobertura)
- Alpha Vantage (grátis com limite)
- Brapi (API brasileira gratuita)

**Impacto:**
- Valor atual do portfólio em tempo real
- Gráficos de evolução
- Alertas de preço

---

### 7. **Moeda Estrangeira** 💵 MÉDIA PRIORIDADE
**Aplicável a:** BDRs, Stocks internacionais, Cripto

**Características:**
- Múltiplas moedas (USD, EUR, BTC)
- Taxa de câmbio no momento da operação
- Conversão para BRL na visualização
- Ganho/perda cambial separado

**Impacto:**
- Investimentos internacionais
- Diversificação geográfica
- Proteção cambial

---

### 8. **Relatórios e Dashboards** 📊 MÉDIA PRIORIDADE
**Aplicável a:** TODOS

**Relatórios:**
- Posição consolidada por ativo
- Rentabilidade por classe de ativo
- Evolução patrimonial mensal
- Proventos recebidos no ano
- IR a pagar/pago
- Alocação de portfólio (% por ativo)

**Impacto:**
- Tomada de decisão
- Rebalanceamento
- Compliance
- Performance tracking

---

## Priorização de Implementação

### 🔴 **CRÍTICO (Implementar Primeiro)**

1. **Proventos (Dividendos e JCP)**
   - Motivo: Essencial para FIIs e ações, impacta estratégia de investimento
   - Effort: Médio
   - Value: Muito Alto

2. **Preço Médio & Posição Consolidada**
   - Motivo: Base para qualquer análise de carteira
   - Effort: Baixo
   - Value: Muito Alto

3. **Lucro/Prejuízo Realizado**
   - Motivo: Necessário para IR e análise de performance
   - Effort: Médio
   - Value: Alto

### 🟡 **ALTA PRIORIDADE (Implementar em Seguida)**

4. **Eventos Corporativos (Bonificação, Desdobramento)**
   - Motivo: Mantém histórico correto, essencial para auditoria
   - Effort: Alto
   - Value: Alto

5. **Suporte a Renda Fixa**
   - Motivo: Diversificação de portfólio, mercado grande no Brasil
   - Effort: Alto
   - Value: Alto

6. **Cálculo Automático de IR**
   - Motivo: Compliance, evita multas
   - Effort: Alto
   - Value: Médio-Alto

### 🟢 **MÉDIA PRIORIDADE (Futuro Próximo)**

7. **Integração com APIs de Cotação**
   - Motivo: Melhora UX, valor em tempo real
   - Effort: Médio
   - Value: Médio

8. **Moeda Estrangeira (USD, EUR)**
   - Motivo: Investimentos internacionais crescendo
   - Effort: Alto
   - Value: Médio

9. **Dashboards e Relatórios Avançados**
   - Motivo: Análise e tomada de decisão
   - Effort: Médio
   - Value: Médio

### 🔵 **BAIXA PRIORIDADE (Backlog)**

10. **Suporte a Criptomoedas**
    - Motivo: Nicho específico, APIs complexas
    - Effort: Muito Alto
    - Value: Baixo-Médio

11. **Suporte a Fundos de Investimento**
    - Motivo: Menos transparência, dados difíceis de obter
    - Effort: Alto
    - Value: Baixo-Médio

---

## Roadmap Sugerido

### **Fase 1: Fundação (Q1 2026)**
- ✅ CRUD de Ativos e Operações
- ✅ Importação B3
- 🎯 Proventos
- 🎯 Preço Médio & Posição
- 🎯 Lucro/Prejuízo Realizado

### **Fase 2: Maturidade (Q2 2026)**
- Eventos Corporativos
- Renda Fixa
- Cálculo de IR
- Dashboards básicos

### **Fase 3: Expansão (Q3-Q4 2026)**
- Integração com APIs
- Moeda Estrangeira
- Relatórios avançados
- Mobile app

---

## Conclusão

A ferramenta já tem uma base sólida com CRUD de ativos e operações. As próximas funcionalidades mais críticas são:

1. **Proventos** - Para FIIs e ações gerarem renda passiva
2. **Preço Médio** - Para saber se está lucrando ou não
3. **Lucro Realizado** - Para calcular IR e performance

Essas três funcionalidades transformariam a ferramenta de um simples "registrador de operações" para um **gerenciador de carteira funcional**.

---

## Próximos Passos

1. Criar issues no GitHub para cada oportunidade priorizada
2. Detalhar specs técnicas de cada funcionalidade
3. Implementar Fase 1 iterativamente
4. Coletar feedback de usuários reais
