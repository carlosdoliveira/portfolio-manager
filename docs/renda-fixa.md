# Funcionalidade Renda Fixa

## Visão Geral

A funcionalidade de Renda Fixa permite gerenciar investimentos em produtos de renda fixa, incluindo CDB, LCI, LCA e Tesouro Direto. O sistema calcula automaticamente projeções de rendimento, imposto de renda (IR) e taxas de custódia.

## Acesso

A funcionalidade está disponível através do menu lateral **"Renda Fixa"** ou pela URL `/fixed-income`.

---

## Funcionalidades Principais

### 1. Dashboard de Estatísticas

Na parte superior da página, são exibidos 4 cards com métricas consolidadas:

- **Total de Ativos**: Número de investimentos cadastrados
- **Total Investido**: Soma de todas as aplicações realizadas
- **Total Resgatado**: Soma de todos os resgates efetuados
- **Saldo Atual**: Diferença entre investido e resgatado

### 2. Tabela de Investimentos

Exibe todos os investimentos de Renda Fixa cadastrados com as seguintes informações:

- **Produto**: Código (ticker) e nome do investimento
- **Emissor**: Instituição emissora (banco, governo, etc.)
- **Indexador**: CDI, IPCA, PRE ou SELIC com taxa contratada
- **Taxa**: Percentual contratado (ex: 110% do CDI)
- **Vencimento**: Data de vencimento com indicador visual:
  - 🟡 **Próximo de vencer**: Menos de 30 dias para vencimento (amarelo)
  - 🔴 **Vencido**: Data já passou (vermelho)
  - ⚪ **Normal**: Acima de 30 dias (padrão)
- **Saldo Atual**: Valor atualmente aplicado
- **Ações**: Botões para visualizar projeção, criar operação e deletar

### 3. Criar Novo Investimento

Clicando no botão **"+ Novo Investimento"**, abre-se um modal com formulário completo:

#### Campos Obrigatórios:

1. **Código/Identificador** (ticker)
   - Exemplo: `CDB_BANCO_XYZ_2026`
   - Usado para identificação única do ativo

2. **Nome do Produto**
   - Exemplo: `CDB Banco XYZ 110% CDI`
   - Nome descritivo do investimento

3. **Emissor**
   - Exemplo: `Banco XYZ`
   - Instituição que emitiu o título

4. **Tipo de Produto**
   - Opções: CDB, LCI, LCA, Tesouro Selic, Tesouro IPCA+, Tesouro Prefixado
   - **Nota**: LCI e LCA são automaticamente isentos de IR

5. **Indexador**
   - Opções: CDI, IPCA, PRE (pré-fixado), SELIC
   - Define como o rendimento é calculado

6. **Taxa Contratada (%)**
   - Para CDI: Ex: 110 = 110% do CDI
   - Para IPCA+: Taxa fixa acima da inflação (ex: 5.5)
   - Para Pré-fixado: Taxa anual fixa
   - Para Selic: Geralmente 100% da Selic

7. **Data de Emissão**
   - Data em que o título foi emitido

8. **Data de Vencimento**
   - Data final do investimento

#### Campo Opcional:

9. **Taxa de Custódia Anual (%)**
   - Apenas para Tesouro Direto: 0.20% (exceto Selic até R$ 10.000)
   - Para outros produtos: 0%

### 4. Registrar Operações

Clicando no botão 💰 de operações, abre-se um modal para registrar:

#### Tipos de Operação:

1. **APLICAÇÃO**
   - Novo aporte no investimento
   - Campos: Valor Bruto, Data da Operação

2. **RESGATE**
   - Retirada parcial ou total
   - Campos adicionais: Valor Líquido (após IR), IR Retido

3. **VENCIMENTO**
   - Liquidação do investimento no vencimento
   - Campos adicionais: Valor Líquido (após IR), IR Retido

### 5. Projeção de Rendimento

Clicando no botão 📊 de projeção, o sistema calcula:

#### Informações do Ativo:
- Tipo de produto
- Indexador e taxa contratada
- Data de vencimento e dias restantes
- Taxa anual usada no cálculo (CDI ou IPCA atual)

#### Valores Projetados:

1. **Saldo Atual**
   - Valor atualmente aplicado

2. **Projeção Bruta (no vencimento)**
   - Valor total sem descontos
   - Ganho bruto em verde

3. **IR (Imposto de Renda)**
   - Taxa regressiva baseada no tempo:
     - Até 180 dias: 22.5%
     - 181 a 360 dias: 20%
     - 361 a 720 dias: 17.5%
     - Acima de 720 dias: 15%
   - **LCI/LCA são isentos**

4. **Taxa de Custódia** (apenas Tesouro)
   - 0.20% ao ano sobre o valor aplicado
   - Isento até R$ 10.000 no Tesouro Selic

5. **Valor Líquido Projetado** (DESTAQUE)
   - Valor final após todos os descontos
   - Ganho líquido
   - Percentual de rendimento sobre o saldo atual

#### Exemplo de Cálculo:

```
Investimento: CDB 110% CDI
Saldo Atual: R$ 10.000,00
Dias até vencimento: 362 dias
CDI atual: 13.75%
Taxa IR: 17.5% (entre 361-720 dias)

Cálculo:
- Taxa anualizada: 13.75% × 110% = 15.125%
- Rendimento bruto: R$ 10.000 × (1 + 0.15125)^(362/365) = R$ 11.498
- Ganho bruto: R$ 1.498
- IR: R$ 1.498 × 17.5% = R$ 262
- Valor líquido: R$ 11.498 - R$ 262 = R$ 11.236
- Ganho líquido: R$ 1.236 (+12.36%)
```

### 6. Deletar Investimento

Clicando no botão 🗑️, o sistema solicita confirmação e remove o ativo do banco de dados.

**⚠️ ATENÇÃO**: Esta ação é irreversível e remove todas as operações relacionadas.

---

## Fórmulas de Cálculo

### 1. Rendimento CDI
```
Taxa_Final = CDI_Atual × (Taxa_Contratada / 100)
Valor_Final = Saldo_Atual × (1 + Taxa_Final)^(Dias / 365)
```

### 2. Rendimento IPCA+
```
Taxa_Final = IPCA_Atual + Taxa_Contratada
Valor_Final = Saldo_Atual × (1 + Taxa_Final)^(Dias / 365)
```

### 3. Rendimento Pré-fixado
```
Valor_Final = Saldo_Atual × (1 + Taxa_Contratada)^(Dias / 365)
```

### 4. Rendimento Selic
```
Taxa_Final = Selic_Atual × (Taxa_Contratada / 100)
Valor_Final = Saldo_Atual × (1 + Taxa_Final)^(Dias / 365)
```

### 5. Cálculo de IR Regressivo
```
Dias aplicados:
- 0-180 dias: IR = 22.5%
- 181-360 dias: IR = 20.0%
- 361-720 dias: IR = 17.5%
- +721 dias: IR = 15.0%

IR_Retido = Ganho_Bruto × Taxa_IR
```

### 6. Taxa de Custódia (Tesouro Direto)
```
Custódia_Anual = 0.20% (apenas Tesouro)
Custódia_Proporcional = Saldo_Atual × 0.002 × (Dias / 365)

Exceção: Tesouro Selic até R$ 10.000 é isento
```

---

## API Endpoints

### Backend (FastAPI)

#### 1. Criar Ativo de Renda Fixa
```http
POST /fixed-income/assets
Content-Type: application/json

{
  "asset_id": 3,
  "issuer": "Banco XYZ",
  "product_type": "CDB",
  "indexer": "CDI",
  "rate": 110.0,
  "maturity_date": "2026-12-31",
  "issue_date": "2026-01-01",
  "custody_fee": 0.0
}
```

#### 2. Listar Ativos
```http
GET /fixed-income/assets

Resposta: Array de FixedIncomeAsset com totais agregados
```

#### 3. Buscar Ativo Específico
```http
GET /fixed-income/assets/{id}

Resposta: Objeto FixedIncomeAsset
```

#### 4. Deletar Ativo
```http
DELETE /fixed-income/assets/{id}

Resposta: {"success": true}
```

#### 5. Criar Operação
```http
POST /fixed-income/operations
Content-Type: application/json

{
  "asset_id": 3,
  "operation_type": "APLICACAO",
  "amount": 10000.0,
  "trade_date": "2026-01-01",
  "net_amount": null,
  "ir_amount": 0
}
```

#### 6. Listar Operações de um Ativo
```http
GET /fixed-income/operations/{asset_id}

Resposta: Array de FixedIncomeOperation
```

#### 7. Calcular Projeção
```http
GET /fixed-income/projection/{asset_id}?cdi_rate=13.75&ipca_rate=4.5

Resposta: Objeto FixedIncomeProjection com todos os cálculos
```

---

## Frontend (React + TypeScript)

### Arquivos Criados

1. **frontend/src/pages/FixedIncome.tsx**
   - Componente principal com toda a lógica
   - Gerencia estado, modais e formulários
   - 600+ linhas de código React/TypeScript

2. **frontend/src/pages/FixedIncome.css**
   - Estilos completos com tema consistente
   - Animações e transições suaves
   - Responsividade para mobile

3. **frontend/src/api/client.ts** (atualizado)
   - 5 novas interfaces TypeScript
   - 7 novas funções de API
   - Type-safe com Promise<T>

### Rotas Adicionadas

- `/fixed-income` - Página principal de Renda Fixa
- Menu lateral atualizado com link "Renda Fixa"

---

## Validações e Regras de Negócio

### 1. Validação de Datas
- Data de vencimento deve ser posterior à data de emissão
- Data de operação não pode ser futura (exceto para testes)

### 2. Validação de Valores
- Todos os valores monetários devem ser positivos
- Taxas devem ser expressas em percentual (ex: 110 para 110%)

### 3. Regras de IR
- **LCI e LCA são SEMPRE isentos**, independente do prazo
- CDB, Tesouro e demais produtos seguem tabela regressiva
- IR incide apenas sobre o ganho, não sobre o principal

### 4. Regras de Custódia
- Apenas Tesouro Direto tem taxa de custódia (0.20% a.a.)
- Tesouro Selic até R$ 10.000 é isento de custódia
- Taxa incide sobre o saldo total, não apenas sobre o ganho

### 5. Cálculo de Saldo
```
Saldo_Atual = Total_Investido - Total_Resgatado
```

---

## Testes Realizados

### 1. Teste Backend - CDB 110% CDI
```bash
curl -X POST http://localhost:8000/fixed-income/assets \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": 3,
    "issuer": "Banco XYZ",
    "product_type": "CDB",
    "indexer": "CDI",
    "rate": 110.0,
    "maturity_date": "2026-12-31",
    "issue_date": "2026-01-01",
    "custody_fee": 0.0
  }'

Resultado: ✅ Asset criado com ID 1
```

### 2. Teste Backend - Operação Aplicação
```bash
curl -X POST http://localhost:8000/fixed-income/operations \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": 3,
    "operation_type": "APLICACAO",
    "amount": 10000.0,
    "trade_date": "2026-01-01"
  }'

Resultado: ✅ Operação registrada
```

### 3. Teste Backend - Projeção CDB
```bash
curl http://localhost:8000/fixed-income/projection/3?cdi_rate=13.75

Resultado:
{
  "current_balance": 10000.0,
  "gross_projection": 11498.0,
  "gross_gain": 1498.0,
  "ir_rate": 17.5,
  "ir_amount": 262.15,
  "custody_fee_amount": 0.0,
  "net_projection": 11235.85,
  "net_gain": 1235.85,
  "days_to_maturity": 362
}
```

### 4. Teste Backend - Tesouro Selic
```bash
# Asset criado com custody_fee: 0.20
# Aplicação de R$ 5.000
# Projeção para 1.153 dias

Resultado:
{
  "current_balance": 5000.0,
  "gross_projection": 7540.0,
  "ir_rate": 15.0,
  "ir_amount": 376.0,
  "custody_fee_amount": 31.0,
  "net_projection": 7509.0,
  "net_gain": 2509.0
}
```

### 5. Teste Frontend
✅ Página carrega corretamente em http://localhost:5173/fixed-income  
✅ Tabela exibe investimentos com formatação brasileira (R$)  
✅ Cards de estatísticas calculam corretamente  
✅ Modal de criação abre e valida campos  
✅ Modal de projeção calcula e exibe valores  
✅ Alertas de vencimento funcionam (amarelo/vermelho)  
✅ Responsividade mobile funcional  

---

## Próximos Passos (Melhorias Futuras)

1. **Gráficos de Evolução**
   - Gráfico de linha mostrando crescimento ao longo do tempo
   - Gráfico de pizza com distribuição por tipo de produto

2. **Alertas Automáticos**
   - Notificação por email próximo ao vencimento
   - Alerta de oportunidades de resgate (melhor momento)

3. **Comparação de Produtos**
   - Ferramenta para comparar diferentes investimentos lado a lado
   - Ranking de rentabilidade líquida

4. **Histórico de Taxas**
   - Armazenar histórico de CDI e IPCA
   - Calcular projeção com variação histórica

5. **Simulador de Investimentos**
   - Calcular projeção antes de investir
   - Comparar cenários (pessimista, realista, otimista)

6. **Export de Dados**
   - Exportar relatório em PDF
   - Exportar dados para Excel

7. **Dashboard Consolidado**
   - Integrar estatísticas de RF no dashboard principal
   - Comparar RF com outros tipos de investimento

---

## Tecnologias Utilizadas

### Backend
- **Python 3.11**
- **FastAPI** - Framework web moderno e rápido
- **SQLite** - Banco de dados relacional
- **Pydantic** - Validação de dados

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool rápido
- **React Router** - Roteamento SPA
- **CSS Modules** - Estilos isolados

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração de containers
- **Git** - Controle de versão

---

## Estrutura de Arquivos

```
backend/
├── app/
│   ├── main.py                          # Endpoints REST + Pydantic models
│   ├── db/
│   │   └── database.py                  # Schema + init_db()
│   └── repositories/
│       └── fixed_income_repository.py   # Lógica de negócio + cálculos

frontend/
├── src/
│   ├── pages/
│   │   ├── FixedIncome.tsx              # Componente principal
│   │   └── FixedIncome.css              # Estilos
│   ├── api/
│   │   └── client.ts                    # Interfaces + funções API
│   ├── components/layout/
│   │   └── Sidebar.tsx                  # Menu lateral (atualizado)
│   ├── App.tsx                          # Rotas (atualizado)
│   └── styles/
│       └── theme.css                    # Variáveis CSS (atualizado)
```

---

## Commit e Documentação

Esta implementação completa a **Issue #5 - Suporte a Renda Fixa**.

### Checklist de Conclusão:
- ✅ Backend completo (tabelas + repository + endpoints)
- ✅ Frontend completo (página + estilos + integração)
- ✅ Testes realizados (backend + frontend)
- ✅ Documentação atualizada
- ✅ Cálculos validados (IR + projeções + custódia)
- ✅ UX/UI consistente com o restante da aplicação

### Arquivos Criados/Modificados:
1. `backend/app/db/database.py` (modificado)
2. `backend/app/repositories/fixed_income_repository.py` (novo)
3. `backend/app/main.py` (modificado)
4. `frontend/src/api/client.ts` (modificado)
5. `frontend/src/pages/FixedIncome.tsx` (novo)
6. `frontend/src/pages/FixedIncome.css` (novo)
7. `frontend/src/App.tsx` (modificado)
8. `frontend/src/components/layout/Sidebar.tsx` (modificado)
9. `frontend/src/styles/theme.css` (modificado)
10. `docs/renda-fixa.md` (novo - este arquivo)

---

## Contato e Suporte

Para dúvidas ou sugestões sobre esta funcionalidade, abra uma issue no GitHub.

---

**Desenvolvido com ❤️ para Portfolio Manager v2**
