# 📚 Portfolio Manager v2 — Documentação

**Última atualização:** 17 de Janeiro de 2026  
**Versão:** v2.3.0

Bem-vindo à documentação completa do Portfolio Manager v2, um sistema de gestão de carteira de investimentos com foco em importação B3, renda fixa e análise de performance.

---

## 🚀 Início Rápido

### Novos Usuários
1. 📖 [**Guia de Setup**](./development/setup.md) — Configure o ambiente local
2. 🎯 [**Visão Geral do Sistema**](#visão-geral) — Entenda o que o sistema faz
3. 📊 [**Status do Projeto**](./STATUS-PROJETO.md) — Veja o que está implementado

### Desenvolvedores
1. 🏗️ [**Arquitetura**](./architecture/principios-core.md) — Princípios e decisões técnicas
2. 🔌 [**API Reference**](./api/endpoints.md) — Endpoints e contratos
3. 📝 [**Guias de Implementação**](#guias-práticos) — Como fazer tarefas comuns

---

## 📋 Índice Geral

### 📊 Status e Releases

- [**STATUS-PROJETO.md**](./STATUS-PROJETO.md) ⭐ **PRINCIPAL**
  - Estado atual completo do projeto
  - Funcionalidades implementadas e pendentes
  - Roadmap e próximos passos

- [**CHECKPOINT-v2.3.0**](./CHECKPOINT-v2.3.0-otimizacao-cotacoes.md) 🔥 **NOVO**
  - Sistema de cache inteligente para cotações
  - Performance 15-30x mais rápida
  - Carregamento progressivo

- [**CHECKPOINT-v2.2.0**](./CHECKPOINT-v2.2.0.md)
  - Sistema de cache de cotações inicial
  - Script de atualização via cron
  
- [**REFERENCIA-TECNICA.md**](./REFERENCIA-TECNICA.md)
  - Documentação técnica detalhada
  - Especificações de API
  - Schemas e interfaces

### 🏗️ Arquitetura
- [**Princípios Core**](./architecture/principios-core.md)
  - Event-based architecture
  - Operações imutáveis
  - Import idempotente

### 🔌 API
- [**Endpoints**](./api/endpoints.md)
  - Ativos, Operações, Renda Fixa, Cotações
  - Request/Response schemas
  - Códigos de erro

### 📖 Guias Práticos

- [**Análise de Eventos Corporativos**](./ANALISE-EVENTOS-CORPORATIVOS.md) 🚨 **CRÍTICO**
  - Bonificações, desdobros, grupamentos não registrados
  - Mudanças de ticker e reconciliação com B3
  - 7 tipos de eventos identificados, 235 ocorrências
  
- [**Recomendação de Abordagem**](./RECOMENDACAO-EVENTOS-CORPORATIVOS.md) 💡 **IMPORTANTE**
  - Implementação incremental vs. sistema completo
  - 3 semanas vs. 8 semanas (trade-offs)
  - Roadmap pragmático e justificativa técnica

- [**Otimização de Cotações**](./guides/otimizacao-cotacoes.md) 🔥 **RECOMENDADO**
  - Sistema de cache inteligente
  - Carregamento progressivo
  - Performance e troubleshooting

- [**Consolidação de Mercados**](./guides/consolidacao-mercados.md) ⭐
  - Como operações à vista e fracionárias são consolidadas
  - Exemplos práticos e SQL

- [**Integração com Cotações**](./guides/integracao-cotacoes.md)
  - Cotações em tempo quase real via yfinance
  - API endpoints e uso no frontend
  - Cache e performance
  
- [**Consistência de Cálculos**](./guides/consistencia-calculos.md)
  - Cálculos de P&L, preço médio, variação
  - Validação e testes

- [**Implementação CRUD**](./guides/crud-implementation.md)
  - Padrões de criação de recursos
  - Best practices

- [**Renda Fixa**](./renda-fixa.md)
  - Funcionalidades completas de RF
  - Cálculo de projeções e IR

### 🛠️ Desenvolvimento
- [**Setup Local**](./development/setup.md)
  - Docker Compose
  - Configuração de ambiente
  - Comandos úteis

### 🚀 Deploy
- Em construção

### 📦 Arquivo
- [**archive/**](./archive/) — Documentos históricos e substituídos

---

## 📖 Visão Geral

### O que é o Portfolio Manager v2?

Sistema web para gestão de carteira de investimentos pessoais com foco em:

#### ✅ Funcionalidades Principais

| Feature | Status | Descrição |
|---------|--------|-----------|
| **Importação B3** | ✅ Completo | Upload de relatórios Excel B3, deduplicação automática |
| **Carteira** | ✅ Completo | CRUD de ativos, posições consolidadas, histórico |
| **Renda Fixa** | ✅ Completo | Gestão completa: CDB, LCI, LCA, Tesouro + projeções |
| **Consolidação de Mercados** | ✅ Completo | Operações à vista e fracionárias somadas automaticamente |
| **Cotações de Mercado** | ✅ Completo | Integração com yfinance, preços em tempo quase real |
| **Dashboard** | ⚠️ Placeholder | Visão geral da carteira (pendente) |
| **Análises** | ⚠️ Placeholder | Gráficos e métricas (pendente) |

#### 🎯 Casos de Uso Atuais

1. **Importar operações da B3**
   - Baixe o relatório de negociações em Excel
   - Arraste para a área de upload
   - Sistema classifica automaticamente (Ações, FIIs, ETFs, RF)
   - Deduplica operações repetidas

2. **Gerenciar ativos manualmente**
   - Criar, editar e deletar ativos
   - Registrar operações de compra/venda
   - Ver histórico completo

3. **Acompanhar Renda Fixa**
   - Cadastrar investimentos RF com todos os detalhes
   - Projeções de rendimento com IR regressivo
   - Cálculo automático de isenção para LCI/LCA

4. **Visualizar posições consolidadas**
   - Posição atual por ativo
   - Preço médio de compra
   - Total investido vs vendido

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **Backend** | Python + FastAPI | 3.11 |
| **Banco de Dados** | SQLite (WAL mode) | 3.x |
| **Frontend** | React + TypeScript + Vite | 18.x / 5.4.x |
| **Containerização** | Docker Compose | 2.x |

### Princípios Arquiteturais

1. **Event-Based Architecture**
   - Operações são eventos imutáveis
   - Estado é derivado, não armazenado
   - Auditoria completa por design

2. **Import Idempotente**
   - Mesmo arquivo pode ser importado múltiplas vezes
   - Deduplicação baseada em chave de negócio
   - UNIQUE constraint no banco

3. **Consolidação Transparente**
   - Operações em diferentes mercados são somadas
   - Preservação das operações originais
   - UI explica o comportamento

📖 **Leia mais:** [Princípios Core](./architecture/principios-core.md)

---

## 📊 Status de Implementação

### Backend (FastAPI)

| Módulo | Status | Endpoints Implementados |
|--------|--------|------------------------|
| **Ativos** | ✅ 100% | POST, GET, PUT, DELETE |
| **Operações** | ✅ 100% | POST, GET, PUT, DELETE |
| **Importação B3** | ✅ 100% | POST /import/b3 |
| **Renda Fixa** | ✅ 100% | CRUD + projeções |
| **Dashboard API** | ❌ 0% | - |

### Frontend (React + TypeScript)

| Página | Status | Funcionalidades |
|--------|--------|-----------------|
| **Import** | ✅ 100% | Upload, drag-and-drop, feedback |
| **Portfolio** | ✅ 100% | CRUD ativos, tabela, estatísticas |
| **AssetDetail** | ✅ 100% | Operações, resumo por mercado |
| **FixedIncome** | ✅ 100% | CRUD RF, projeções, operações |
| **Dashboard** | ⚠️ 5% | Apenas placeholder |
| **Analysis** | ⚠️ 5% | Apenas placeholder |
| **Settings** | ⚠️ 5% | Apenas placeholder |

### Testes

| Tipo | Status | Cobertura |
|------|--------|-----------|
| **Testes Unitários** | ⚠️ Mínimo | < 5% |
| **Testes Integração** | ⚠️ Mínimo | 1 teste de consolidação |
| **Testes E2E** | ❌ Não implementado | 0% |

📖 **Leia mais:** [STATUS-PROJETO.md](./STATUS-PROJETO.md)

---

## 🎯 Roadmap

### ✅ Fase 1 — MVP (Concluída)
- Import B3 com deduplicação
- CRUD de ativos e operações
- Renda Fixa completa
- Consolidação de mercados

### 🚧 Fase 2 — Dashboards (Em Progresso)
- [ ] Dashboard principal com cards
- [ ] Gráficos de alocação
- [ ] Análise de performance
- [ ] Operações recentes

### 📅 Fase 3 — Valorização (Planejada)
- [ ] Integração com cotações (Yahoo Finance)
- [ ] Mark-to-market
- [ ] Ganho/perda não realizado
- [ ] Benchmark (IBOV, CDI)

### 🔮 Fase 4 — Avançado (Futuro)
- [ ] Proventos e dividendos
- [ ] Eventos corporativos (splits, bonificações)
- [ ] Relatórios de IR
- [ ] API externa para apps mobile

---

## 📚 Guias por Persona

### 👨‍💼 Gestores / Product Owners

**Leitura recomendada:**
1. [Visão Geral](#visão-geral) (acima)
2. [Status do Projeto](./STATUS-PROJETO.md)
3. [Roadmap](#roadmap) (acima)

**Perguntas comuns:**
- ❓ **O que está pronto?** → [Status de Implementação](#status-de-implementação)
- ❓ **Quando teremos dashboards?** → [Roadmap - Fase 2](#roadmap)
- ❓ **Quais são os riscos?** → [Problemas Conhecidos](./STATUS-PROJETO.md#problemas-conhecidos)

---

### 👨‍💻 Desenvolvedores Backend

**Leitura recomendada:**
1. [Setup Local](./development/setup.md)
2. [Princípios Core](./architecture/principios-core.md)
3. [API Endpoints](./api/endpoints.md)
4. [Referência Técnica](./REFERENCIA-TECNICA.md)

**Tarefas comuns:**
- 🔨 **Adicionar novo endpoint** → Ver padrão em [API Endpoints](./api/endpoints.md)
- 🔨 **Criar nova tabela** → Ver schema em [Modelagem de Dados](./STATUS-PROJETO.md#modelagem-de-dados)
- 🔨 **Implementar cálculo** → Ver exemplo em [Projeções RF](./REFERENCIA-TECNICA.md)

---

### 👨‍💻 Desenvolvedores Frontend

**Leitura recomendada:**
1. [Setup Local](./development/setup.md)
2. [API Endpoints](./api/endpoints.md)
3. [Guia CRUD](./guides/crud-implementation.md)

**Tarefas comuns:**
- 🔨 **Criar nova página** → Ver padrão em Portfolio.tsx
- 🔨 **Consumir API** → Ver client.ts
- 🔨 **Adicionar formulário** → Ver OperationForm.tsx

---

### 👨‍🔬 QA / Testadores

**Leitura recomendada:**
1. [Status do Projeto](./STATUS-PROJETO.md)
2. [Guia de Consolidação](./guides/consolidacao-mercados.md)

**Cenários de teste:**
- ✅ **Import B3** → Arquivo sample em `samples/`
- ✅ **Consolidação** → Script em `tests/test_consolidacao_mercados.py`
- ✅ **Renda Fixa** → Testar CDB, LCI, Tesouro

---

## 🆘 Suporte e Contribuição

### Reportar Bugs
1. Verifique se já não existe issue aberta
2. Use o template em [COMO-CRIAR-ISSUES.md](./COMO-CRIAR-ISSUES.md)
3. Inclua logs e prints quando possível

### Contribuir com Código
1. Fork o repositório
2. Crie branch: `feature/nome-da-feature`
3. Siga os [Princípios Core](./architecture/principios-core.md)
4. Abra Pull Request com descrição clara

### Melhorar Documentação
- Documentação está em `docs/`
- Formato: Markdown
- Siga estrutura existente

---

## 📞 Links Importantes

| Recurso | Link |
|---------|------|
| **Repositório** | [github.com/carlosdoliveira/portfolio-manager](https://github.com/carlosdoliveira/portfolio-manager) |
| **Issues** | [GitHub Issues](https://github.com/carlosdoliveira/portfolio-manager/issues) |
| **Changelog** | [CHANGELOG.md](../CHANGELOG.md) |
| **License** | MIT |

---

## 🏆 Conquistas Recentes

- ✅ **Jan/2026** — Consolidação de mercados implementada
- ✅ **Jan/2026** — Renda Fixa completa com projeções
- ✅ **Jan/2026** — Import B3 com deduplicação
- ✅ **Dez/2025** — MVP funcional

---

## 📝 Convenções de Documentação

- 📖 **Guias práticos** → `docs/guides/`
- 🏗️ **Decisões de arquitetura** → `docs/architecture/`
- 🔌 **Documentação de API** → `docs/api/`
- 🛠️ **Setup e desenvolvimento** → `docs/development/`

---

**Mantido por:** Equipe Portfolio Manager v2  
**Última revisão:** 03/01/2026
