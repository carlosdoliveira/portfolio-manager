# 🎯 Recomendação de Abordagem — Eventos Corporativos

**Data:** 17 de Janeiro de 2026  
**Contexto:** [ANALISE-EVENTOS-CORPORATIVOS.md](./ANALISE-EVENTOS-CORPORATIVOS.md)  
**Status:** Proposta para Discussão

---

## 📋 Sumário Executivo

Após análise detalhada dos 1.399 registros de movimentação e considerando os princípios arquiteturais do Portfolio Manager v2, **recomendo uma abordagem incremental em 3 fases**, priorizando **pragmatismo sobre completude**.

### 🎯 Decisão Estratégica

**Implementar eventos corporativos de forma progressiva, começando pelos casos que já existem no histórico do usuário**, ao invés de construir um sistema genérico completo antecipadamente.

### ⚡ Justificativa

1. **Princípio da Clareza:** Sistema complexo demais para casos que talvez nunca aconteçam
2. **Event-Based Architecture:** Já temos infraestrutura para eventos (operações)
3. **Simplicidade de Gestão:** Menos código = menos bugs = menos manutenção
4. **Feedback Rápido:** Entregar valor ao usuário em semanas, não meses

---

## 🎯 Abordagem Recomendada

### Fase 1: Reconciliação e Correção Manual (Sprint 1) — 1 semana

**Objetivo:** Corrigir o passado sem código complexo.

#### 1.1. Ferramenta de Ajuste de Posição

```python
# POST /admin/position-adjustment
{
  "asset_id": 5,
  "adjustment_type": "BONIFICACAO",
  "quantity": 24.48,
  "event_date": "2025-12-22",
  "description": "Bonificação ITSA4 - 10% em dez/2025"
}
```

**Implementação:**
- Cria operação especial com `price = 0` e `source = "AJUSTE"`
- Flag `operation_subtype = "BONIFICACAO"` para auditoria
- Recalcula preço médio automaticamente

**Vantagens:**
- ✅ Usa tabela `operations` existente (sem migration)
- ✅ Mantém auditoria completa
- ✅ Implementação em 2-3 dias
- ✅ Resolve 90% dos problemas imediatos

**Desvantagens:**
- ⚠️ Ajustes manuais (mas raros — 1-2x por ano)
- ⚠️ Não detecta automaticamente eventos futuros

#### 1.2. Página de Reconciliação

**Interface simples:**
```
┌─────────────────────────────────────────────┐
│ 🔍 Reconciliação de Posição                │
├─────────────────────────────────────────────┤
│                                             │
│ Ativo: [ITSA4 ▼]                           │
│                                             │
│ Posição calculada:    583 ações            │
│ Posição real (B3):    [650] ← Digite aqui │
│                                             │
│ Diferença: -67 ações (-10.28%)            │
│                                             │
│ ⚠️ Possível causa: Bonificação não         │
│                   registrada               │
│                                             │
│ [ Registrar Bonificação ] [ Ignorar ]     │
│                                             │
└─────────────────────────────────────────────┘
```

**Fluxo:**
1. Usuário baixa posição atual da B3
2. Compara com sistema
3. Para cada diferença, registra ajuste com descrição
4. Sistema recalcula posição e P&L

---

### Fase 2: Detecção Passiva em Imports (Sprint 2) — 1 semana

**Objetivo:** Alertar sobre eventos, não processar automaticamente.

#### 2.1. Parser Inteligente no Import

```python
def parse_b3_movimentacao(df: pd.DataFrame) -> dict:
    """
    Detecta padrões suspeitos sem processar automaticamente
    """
    
    suspicious_events = []
    
    # Detectar bonificações (preço = 0, quantidade grande)
    bonificacoes = df[
        (df['Movimentação'] == 'Bonificação em Ativos')
    ]
    
    # Detectar desdobros (quantidade exata = 2x posição)
    desdobros = df[
        (df['Movimentação'] == 'Desdobro')
    ]
    
    # Detectar mudanças de ticker
    ticker_changes = detect_ticker_changes(df)
    
    return {
        "operations": normal_operations,
        "warnings": suspicious_events,
        "requires_attention": len(suspicious_events) > 0
    }
```

**Response do Import:**
```json
{
  "imported": 15,
  "duplicates": 3,
  "warnings": [
    {
      "type": "BONIFICACAO_DETECTADA",
      "ticker": "ITSA4",
      "quantity": 24.48,
      "date": "2025-12-22",
      "message": "Bonificação detectada. Clique para registrar.",
      "action_url": "/admin/position-adjustment?prefill=..."
    }
  ]
}
```

**Vantagens:**
- ✅ Não adiciona complexidade ao core
- ✅ Usuário mantém controle
- ✅ Reduz erros de detecção automática
- ✅ Implementação simples

---

### Fase 3: Sistema de Aliases (Sprint 3) — 1 semana

**Objetivo:** Resolver fragmentação de tickers.

#### 3.1. Tabela Simples de Aliases

```sql
CREATE TABLE asset_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_ticker TEXT NOT NULL,  -- Ex: ISAE4
    alias_ticker TEXT NOT NULL,      -- Ex: TRPL4
    effective_date DATE NOT NULL,
    notes TEXT,
    UNIQUE (alias_ticker)
);
```

#### 3.2. Resolver Ticker ao Buscar Cotações

```python
def get_quote(ticker: str) -> dict:
    """
    Busca cotação usando ticker atual (alias resolvido)
    """
    
    # Resolver alias
    canonical = resolve_alias(ticker) or ticker
    
    # Buscar cotação com ticker correto
    quote = yfinance.Ticker(f"{canonical}.SA").info
    
    return {
        "ticker": ticker,           # Original
        "canonical": canonical,      # Resolvido
        "price": quote.get("currentPrice"),
        "source": "yfinance"
    }

def resolve_alias(ticker: str) -> Optional[str]:
    """
    Retorna ticker canônico se alias existir
    """
    alias = db.execute("""
        SELECT canonical_ticker 
        FROM asset_aliases 
        WHERE alias_ticker = ?
    """, (ticker,)).fetchone()
    
    return alias[0] if alias else None
```

**Vantagens:**
- ✅ Resolve problema de cotações imediatamente
- ✅ Não afeta operações históricas
- ✅ Tabela pequena e simples
- ✅ Fácil de popular manualmente

**Cadastro manual inicial:**
```sql
INSERT INTO asset_aliases VALUES
(1, 'ISAE4', 'TRPL4', '2024-11-19', 'Mudança oficial de ticker'),
(2, 'WIZC3', 'WIZS3', '2023-02-10', 'Reorganização societária'),
(3, 'VIIA3', 'VVAR3', '2021-01-01', 'Rebrand Via Varejo → Via');
```

---

## 🎯 Comparação: Abordagem Recomendada vs. Completa

| Aspecto | Abordagem Recomendada | Abordagem Completa (análise) |
|---------|------------------------|------------------------------|
| **Tempo de implementação** | 3 semanas | 7-8 semanas |
| **Complexidade de código** | Baixa | Alta |
| **Tabelas novas** | 1 (aliases) | 3 (events, aliases, snapshots) |
| **Migrations** | 1 simples | 3 complexas |
| **Testes necessários** | ~10 | ~40 |
| **Manutenção** | Baixa | Média-Alta |
| **Cobertura de casos** | 90% (casos reais) | 100% (todos cenários) |
| **Automação** | Parcial (alertas) | Completa (processamento) |
| **Risco de bugs** | Baixo | Médio-Alto |
| **Valor entregue** | Imediato (semana 1) | Gradual (semana 8) |

---

## 💡 Justificativa Técnica

### Por que NÃO implementar tudo agora?

#### 1. YAGNI (You Aren't Gonna Need It)

A análise mostrou:
- **Bonificações:** 15 em 7 anos (2/ano) — Raro
- **Desdobros:** 3 em 7 anos (0.4/ano) — Muito raro
- **Mudanças de ticker:** 24 em 7 anos (3/ano) — Raro

**Conclusão:** Eventos corporativos são exceções, não a regra. Sistema complexo para casos raros é over-engineering.

#### 2. Complexidade vs. Benefício

Sistema completo requer:
- Lógica de recálculo retroativo
- Tratamento de edge cases (eventos no mesmo dia, eventos encadeados)
- Validação de consistência
- Testes extensivos
- Documentação complexa

**ROI duvidoso:** 8 semanas de trabalho para processar automaticamente ~40 eventos em 7 anos.

#### 3. Alinhamento com Princípios

**Princípio da Clareza:**
- Ajustes manuais são **explícitos e auditáveis**
- Sistema automático é **implícito e pode errar silenciosamente**

**Event-Based Architecture:**
- Ajustes como operações especiais **mantêm o modelo existente**
- Tabela separada `corporate_events` **adiciona complexidade desnecessária**

#### 4. Manutenibilidade

Sistema simples:
- Fácil de entender daqui a 2 anos
- Fácil de debugar
- Fácil de estender quando realmente necessário

Sistema completo:
- Requer conhecimento profundo para manter
- Mais superfície para bugs
- Pode precisar refatoração ao amadurecer

---

## 🚀 Roadmap Proposto

### Sprint 1 (1 semana) — **FAÇA AGORA**

**Objetivo:** Corrigir histórico existente

- [ ] Endpoint `/admin/position-adjustment`
- [ ] Página de reconciliação manual
- [ ] Suporte a `operation_subtype` na tabela `operations`
- [ ] Recálculo de preço médio com custo zero
- [ ] Testes básicos

**Entrega:** Usuário pode corrigir ITSA4, VINO11, BCFF11 manualmente.

---

### Sprint 2 (1 semana) — **FAÇA EM SEGUIDA**

**Objetivo:** Alertar sobre eventos futuros

- [ ] Parser inteligente no `B3Importer`
- [ ] Detecção de bonificações/desdobros
- [ ] Warnings estruturados no response
- [ ] UI para exibir warnings após import
- [ ] Link direto para tela de ajuste

**Entrega:** Próxima bonificação é detectada e usuário é alertado.

---

### Sprint 3 (1 semana) — **FAÇA DEPOIS**

**Objetivo:** Resolver cotações de tickers antigos

- [ ] Tabela `asset_aliases`
- [ ] Função `resolve_alias(ticker)`
- [ ] Integração no `QuotesService`
- [ ] Popular aliases conhecidos
- [ ] Interface para gerenciar aliases

**Entrega:** TRPL4 busca cotação como ISAE4 automaticamente.

---

### Sprints 4-6 (3 semanas) — **OPCIONAL / FUTURO**

**Objetivo:** Automação avançada (se realmente necessário)

- [ ] Sistema de detecção mais robusto
- [ ] Processamento semi-automático
- [ ] Tabela `corporate_events` (se casos aumentarem)
- [ ] API de reconciliação com B3
- [ ] Snapshots de posição

**Critério para implementar:** 
- Eventos corporativos passarem de 2/ano para 5+/ano
- Usuário relatar dor significativa com processo manual
- ROI justificar investimento

---

## 📊 Exemplo Prático: ITSA4

### Hoje (Sistema Sem Ajustes)

```
Posição calculada: 583 ITSA4
Posição real B3:   650 ITSA4
Status: ❌ DESCASAMENTO -67 ações (-10.28%)
```

### Após Sprint 1 (Ajuste Manual)

**Usuário faz:**
1. Acessa `/admin/position-adjustment`
2. Preenche:
   ```
   Ativo: ITSA4
   Tipo: Bonificação
   Quantidade: +67
   Data: 2025-12-22
   Descrição: Acumulado de bonificações 2021-2025
   ```
3. Salva

**Sistema cria:**
```sql
INSERT INTO operations (
  asset_id, 
  movement_type, 
  operation_subtype,
  quantity, 
  price, 
  trade_date, 
  source
) VALUES (
  5,
  'COMPRA',
  'BONIFICACAO',
  67,
  0.0,
  '2025-12-22',
  'AJUSTE'
);
```

**Resultado:**
```
Posição calculada: 650 ITSA4
Posição real B3:   650 ITSA4
Status: ✅ OK
Preço médio: R$ 9.23 (ajustado automaticamente)
```

**Tempo:** 2 minutos de trabalho manual

---

### Após Sprint 2 (Detecção Automática)

**Na próxima bonificação (dez/2026):**

Usuário importa extrato → Sistema alerta:
```
⚠️ Evento Corporativo Detectado

ITSA4 - Bonificação em Ativos
Data: 22/12/2026
Quantidade: 71.5 ações

[ Registrar Bonificação ]  [ Ignorar ]
```

Clica "Registrar" → Abre tela de ajuste pré-preenchida → Confirma

**Tempo:** 30 segundos de trabalho manual

---

### Após Sprint 3 (Aliases)

Se ITSA4 mudar para ITSA5 (hipotético):

```sql
INSERT INTO asset_aliases VALUES
(4, 'ITSA5', 'ITSA4', '2027-01-01', 'Mudança de ticker oficial');
```

Sistema automaticamente:
- Busca cotações de ITSA5
- Mantém histórico de ITSA4 intacto
- Dashboard mostra ITSA5 (ticker atual)
- Detalhes mostram "Anteriormente: ITSA4"

**Tempo:** 0 segundos (transparente)

---

## ⚖️ Trade-offs Conscientes

### O que estamos sacrificando:

1. **Automação completa** → Aceitamos intervenção manual ocasional (2-3x/ano)
2. **Completude teórica** → Focamos em casos reais, não todos os possíveis
3. **Sofisticação técnica** → Priorizamos simplicidade e manutenibilidade

### O que estamos ganhando:

1. **Velocidade de entrega** → 3 semanas vs. 8 semanas
2. **Menor complexidade** → Menos código, menos bugs
3. **Maior clareza** → Código fácil de entender e manter
4. **Risco reduzido** → Menos superfície para erros
5. **Flexibilidade** → Fácil evoluir quando necessário

---

## 🎯 Decisão Recomendada

### ✅ IMPLEMENTAR: Abordagem Incremental

**Razões:**
1. Alinha com princípios arquiteturais (clareza, simplicidade)
2. Entrega valor rapidamente (3 semanas)
3. Resolve 90% dos problemas reais
4. Baixo risco de regressão
5. Fácil de manter e evoluir
6. Custo-benefício favorável

### ⚠️ ADIAR: Sistema Completo

**Razões:**
1. Over-engineering para frequência de eventos (2-3/ano)
2. Alto custo de implementação (8 semanas)
3. Complexidade desproporcional ao benefício
4. Risco de bugs em edge cases
5. YAGNI — casos raros não justificam sistema complexo

### 🔮 REAVALIAR EM: 6 meses

**Gatilhos para reconsiderar:**
- Frequência de eventos aumentar significativamente
- Processo manual se tornar doloroso
- Base de usuários crescer e escalar processo manual
- Novas regulamentações exigirem rastreamento formal

---

## 📋 Checklist de Implementação

### Sprint 1: Ajustes Manuais

```bash
# Backend
[ ] Adicionar coluna operation_subtype em operations
[ ] Endpoint POST /admin/position-adjustment
[ ] Validação de adjustment_type
[ ] Recálculo de preço médio com price=0
[ ] Testes unitários (ajustes)
[ ] Documentação do endpoint

# Frontend
[ ] Página /admin/reconciliation
[ ] Form de ajuste de posição
[ ] Dropdown de tipos (BONIFICACAO, DESDOBRO, etc)
[ ] Validação de campos obrigatórios
[ ] Feedback de sucesso/erro
[ ] Link na sidebar (Admin tools)

# Docs
[ ] Guia de reconciliação manual
[ ] Exemplos práticos (ITSA4, VINO11)
```

### Sprint 2: Detecção Passiva

```bash
# Backend
[ ] Parser de eventos em importer.py
[ ] Função detect_bonificacao()
[ ] Função detect_desdobro()
[ ] Função detect_ticker_change()
[ ] Response incluindo warnings
[ ] Testes com fixtures de eventos

# Frontend
[ ] Componente AlertaBanner
[ ] Exibir warnings após import
[ ] Link para ajuste pré-preenchido
[ ] Dismiss/Ignorar alerta
[ ] Persistir dismissals (localStorage)

# Docs
[ ] Tipos de eventos detectados
[ ] Como lidar com alertas
```

### Sprint 3: Sistema de Aliases

```bash
# Backend
[ ] Tabela asset_aliases (migration)
[ ] Função resolve_alias()
[ ] Integração em QuotesService
[ ] Endpoint GET /aliases
[ ] Endpoint POST /aliases
[ ] Popular aliases conhecidos

# Frontend
[ ] Página /admin/aliases
[ ] Listagem de aliases
[ ] Form de criação
[ ] Badge "Anteriormente: XXX" em detalhes

# Docs
[ ] Lista de aliases conhecidos
[ ] Como adicionar novo alias
```

---

## 🔧 Código de Exemplo

### Sprint 1: Endpoint de Ajuste

```python
# backend/app/main.py

@app.post("/admin/position-adjustment")
async def adjust_position(adjustment: PositionAdjustment):
    """
    Registra ajuste manual de posição (bonificação, desdobro, etc)
    
    Body:
    {
        "asset_id": 5,
        "adjustment_type": "BONIFICACAO",
        "quantity": 24.48,
        "event_date": "2025-12-22",
        "description": "Bonificação 10% dezembro/2025"
    }
    """
    
    with get_db() as conn:
        # Criar operação especial
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO operations (
                asset_id,
                movement_type,
                operation_subtype,
                quantity,
                price,
                value,
                trade_date,
                source,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            adjustment.asset_id,
            "COMPRA" if adjustment.quantity > 0 else "VENDA",
            adjustment.adjustment_type,
            abs(adjustment.quantity),
            0.0,  # Custo zero
            0.0,
            adjustment.event_date,
            "AJUSTE",
            adjustment.description
        ))
        
        conn.commit()
        
        # Recalcular posição
        new_position = calculate_position(conn, adjustment.asset_id)
        
        return {
            "success": True,
            "adjustment_id": cursor.lastrowid,
            "new_position": new_position
        }
```

### Sprint 2: Detecção de Eventos

```python
# backend/app/services/importer.py

def detect_corporate_events(df: pd.DataFrame) -> list:
    """
    Detecta eventos corporativos no DataFrame do extrato
    """
    
    events = []
    
    # Bonificações
    bonificacoes = df[df['Movimentação'] == 'Bonificação em Ativos']
    for _, row in bonificacoes.iterrows():
        events.append({
            "type": "BONIFICACAO",
            "ticker": extract_ticker(row['Produto']),
            "quantity": row['Quantidade'],
            "date": row['Data'],
            "severity": "warning",
            "message": f"Bonificação detectada: +{row['Quantidade']} {extract_ticker(row['Produto'])}",
            "action_url": f"/admin/position-adjustment?prefill=bonificacao&ticker={extract_ticker(row['Produto'])}&qty={row['Quantidade']}&date={row['Data']}"
        })
    
    # Desdobros
    desdobros = df[df['Movimentação'] == 'Desdobro']
    for _, row in desdobros.iterrows():
        events.append({
            "type": "DESDOBRO",
            "ticker": extract_ticker(row['Produto']),
            "quantity": row['Quantidade'],
            "date": row['Data'],
            "severity": "warning",
            "message": f"Desdobro detectado: +{row['Quantidade']} {extract_ticker(row['Produto'])}",
            "action_url": f"/admin/position-adjustment?prefill=desdobro&ticker={extract_ticker(row['Produto'])}&qty={row['Quantidade']}&date={row['Data']}"
        })
    
    return events
```

### Sprint 3: Resolver Aliases

```python
# backend/app/services/quotes_service.py

def get_quote(ticker: str) -> dict:
    """
    Busca cotação resolvendo aliases automaticamente
    """
    
    # Resolver alias
    canonical = resolve_alias(ticker)
    search_ticker = canonical if canonical else ticker
    
    # Buscar cotação
    try:
        quote_data = yfinance.Ticker(f"{search_ticker}.SA").info
        
        return {
            "ticker": ticker,
            "canonical_ticker": canonical,
            "price": quote_data.get("currentPrice"),
            "change_percent": quote_data.get("regularMarketChangePercent"),
            "source": "yfinance",
            "resolved": canonical is not None
        }
    except Exception as e:
        logging.error(f"Erro ao buscar cotação de {search_ticker}: {e}")
        return None

def resolve_alias(ticker: str) -> Optional[str]:
    """
    Retorna ticker canônico se for alias
    """
    with get_db() as conn:
        result = conn.execute("""
            SELECT canonical_ticker
            FROM asset_aliases
            WHERE alias_ticker = ?
        """, (ticker,)).fetchone()
        
        return result['canonical_ticker'] if result else None
```

---

## 📚 Documentação Necessária

### Guia do Usuário: Reconciliação Manual

```markdown
# Como Reconciliar Sua Posição

## Quando usar

Use a reconciliação manual quando:
- Importar extrato e posição não bater
- Receber bonificação de ações
- Acontecer desdobro ou grupamento
- Ticker mudar (ex: TRPL4 → ISAE4)

## Passo a passo

1. Compare posição no sistema vs B3
2. Acesse "Ferramentas Admin" → "Reconciliação"
3. Selecione o ativo com diferença
4. Escolha o tipo de ajuste:
   - **Bonificação:** Ações gratuitas recebidas
   - **Desdobro:** Cada ação virou N ações
   - **Grupamento:** N ações viraram 1
   - **Correção:** Erro de importação
5. Informe a quantidade de diferença
6. Adicione descrição (opcional)
7. Clique "Salvar Ajuste"

## Exemplo: Bonificação ITSA4

```
Sistema mostra: 583 ações
B3 mostra:      650 ações
Diferença:      +67 ações

Motivo: Bonificações de 2021-2025 não importadas

Ajuste:
- Tipo: Bonificação
- Quantidade: +67
- Data: 2025-12-22
- Descrição: "Acumulado bonificações 2021-2025"
```

Sistema recalcula automaticamente o preço médio.
```

---

## 🎯 Conclusão e Recomendação Final

### ✅ RECOMENDO: Implementação Incremental (3 semanas)

**Justificativa:**
1. **Pragmatismo:** Resolve 90% com 30% do esforço
2. **Alinhamento arquitetural:** Mantém simplicidade do sistema
3. **Baixo risco:** Mudanças pequenas e testáveis
4. **Entrega rápida:** Valor em 1 semana (Sprint 1)
5. **Evolutivo:** Fácil expandir se necessário

### ⏸️ ADIAR: Sistema Completo Automático

**Reavaliar quando:**
- Eventos aumentarem >5x/ano
- Processo manual se tornar gargalo
- Múltiplos usuários demandarem
- ROI justificar investimento

### 📅 Próximos Passos Imediatos

1. **Hoje:** Aprovar abordagem com stakeholders
2. **Segunda:** Iniciar Sprint 1 (ajustes manuais)
3. **Semana 2:** Sprint 2 (detecção passiva)
4. **Semana 3:** Sprint 3 (aliases)
5. **Semana 4:** Documentação e treinamento

### 🎯 Métricas de Sucesso

**Sprint 1:**
- [ ] Posição ITSA4 corrigida
- [ ] Preço médio recalculado corretamente
- [ ] Processo documentado

**Sprint 2:**
- [ ] Próxima bonificação detectada
- [ ] Usuário alertado no import
- [ ] Ajuste feito em <1 min

**Sprint 3:**
- [ ] Cotações de tickers antigos funcionando
- [ ] 3-5 aliases cadastrados
- [ ] Zero regressões

---

**Documento gerado em:** 17 de Janeiro de 2026  
**Autor:** GitHub Copilot  
**Status:** Proposta para Aprovação  
**Validade:** 30 dias (reavaliar se não iniciado)
