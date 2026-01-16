# 📋 Pendências do Projeto — Portfolio Manager v2

**Data:** 9 de Janeiro de 2026  
**Versão:** v2.1.0  
**Status Geral:** ✅ MVP Funcional com Cotações

---

## 🎯 Visão Geral

O Portfolio Manager v2 está **funcional e operacional** para uso real, com todas as funcionalidades core implementadas:
- ✅ Importação B3 com deduplicação
- ✅ CRUD completo de ativos e operações
- ✅ Renda Fixa com projeções e IR
- ✅ Consolidação de mercados (fracionário/vista)
- ✅ Cotações de mercado em tempo quase real
- ✅ Cálculos corretos de posições e valores

As pendências listadas abaixo são **melhorias futuras**, não impedem o uso do sistema.

---

## 🔴 Prioridade Alta (P1)

### 1. Dashboard Principal
**Status:** ✅ Implementado  
**Arquivo:** [frontend/src/pages/Dashboard.tsx](../frontend/src/pages/Dashboard.tsx)  
**Data de Conclusão:** 9 de Janeiro de 2026

**Implementado:**
- ✅ Cards de resumo (total investido, valor atual, variação)
- ✅ Top 5 posições com drill-down
- ✅ Operações recentes (últimas 10)
- ✅ Gráfico de alocação por classe de ativo
- ✅ Endpoint `/dashboard/summary` no backend
- ✅ Integração com repository layer

**Detalhes técnicos:**
- Repository: `dashboard_repository.py`
- Endpoint: `GET /dashboard/summary`
- Componentes: Cards estatísticos, tabela de posições, lista de operações
- Navegação: Click para detalhes de ativo

---

### 2. Página de Análises
**Status:** Placeholder  
**Arquivo:** [frontend/src/pages/Analysis.tsx](../frontend/src/pages/Analysis.tsx)  
**Impacto:** Feature prometida não entregue

**O que falta:**
- Gráfico de distribuição por classe (pizza)
- Timeline de operações (linha)
- Top 5 maiores posições (barra)
- Métricas de performance

**Estimativa:** 6 horas

**Bibliotecas sugeridas:**
- Chart.js ou Recharts para gráficos

---

## 🟡 Prioridade Média (P2)

### 3. Página de Configurações
**Status:** Placeholder  
**Arquivo:** [frontend/src/pages/Settings.tsx](../frontend/src/pages/Settings.tsx)  
**Impacto:** Baixo (funcionalidades básicas funcionam)

**O que falta:**
- Configuração de tema (light/dark)
- Configuração de moeda
- Preferências de exibição
- Gerenciamento de cache de cotações

**Estimativa:** 4 horas

---

### 4. Testes Automatizados
**Status:** Cobertura parcial  
**Locais:** `backend/tests/`, `frontend/src/`  
**Impacto:** Risco de regressão em mudanças futuras

**O que existe:**
- ✅ 20 testes de consolidação de mercados
- ✅ Testes de normalização de ticker
- ❌ Sem testes de endpoints da API
- ❌ Sem testes de componentes React
- ❌ Sem testes de integração

**O que falta:**
- Testes unitários para repositories (3h)
- Testes de integração para endpoints (3h)
- Testes de componentes React (4h)

**Estimativa total:** 10 horas

**Ferramentas sugeridas:**
- Backend: pytest
- Frontend: Vitest + React Testing Library

---

### 5. Paginação nas Listagens
**Status:** Não implementado  
**Impacto:** Performance com muitos registros (>100)

**Endpoints afetados:**
- `GET /assets`
- `GET /operations`
- `GET /operations/asset/{id}`
- `GET /fixed-income/assets`

**O que falta:**
- Query params: `limit`, `offset`, `page`
- Response: `total`, `page`, `per_page`, `items`
- Componente de paginação no frontend

**Estimativa:** 4 horas

---

## 🟢 Prioridade Baixa (P3)

### 6. Melhorias de UX
- Loading states mais elaborados
- Skeleton screens
- Toasts/notificações mais sofisticados
- Animações de transição

**Estimativa:** 6 horas

---

### 7. Cache de Consultas
**Status:** Apenas cache de cotações implementado  
**Impacto:** Queries repetidas desnecessárias

**O que falta:**
- Cache de listagens de ativos
- Cache de operações por ativo
- Invalidação inteligente de cache

**Opções:**
- In-memory cache (simples)
- Redis (produção)

**Estimativa:** 4 horas

---

### 8. Logs Padronizados
**Status:** Logs mistos (português/inglês)  
**Impacto:** Dificulta debug

**O que falta:**
- Padronizar idioma (português)
- Estruturar logs JSON
- Adicionar request_id para rastreamento

**Estimativa:** 2 horas

---

### 9. Badges de Mercado no Histórico
**Status:** Não implementado  
**Impacto:** Baixo (informação já existe na coluna)

**O que falta:**
- Badge visual "Vista" / "Fracionário" na tabela de operações
- Filtro por mercado

**Estimativa:** 1 hora

---

## 📅 Backlog (Futuro)

Funcionalidades para versões futuras (não priorizadas):

### Features Financeiras
- Proventos e dividendos (tracking e histórico)
- Eventos corporativos (splits, bonificações, grupamentos)
- Relatórios de IR (darf, ganho de capital)
- Integração com múltiplas corretoras
- Import de extratos de corretoras (além da B3)

### Infraestrutura
- Migração SQLite → PostgreSQL
- API de autenticação (multi-usuário)
- Docker em produção (docker-compose.prod.yml)
- CI/CD com GitHub Actions
- Monitoramento e alertas

### UX/UI
- PWA com offline support
- Dark mode
- Mobile app (React Native ou Flutter)
- Gráficos históricos interativos
- Comparação com benchmarks (IBOV, IFIX)
- Exportação de relatórios (PDF, Excel)

---

## 📊 Métricas de Progresso

| Categoria | Implementado | Total | % |
|-----------|--------------|-------|---|
| **Backend Core** | 100% | 100% | ✅ 100% |
| **Frontend Core** | 80% | 100% | 🟢 80% |
| **Testes** | 20% | 100% | 🔴 20% |
| **Documentação** | 95% | 100% | ✅ 95% |

**Atualização (9 Jan 2026):** Frontend Core aumentou de 70% → 80% com implementação do Dashboard

---

## ~~Sprint 3 (Concluída - 9 Jan 2026)~~
1. ~~Dashboard principal (P1)~~ ✅ Implementado - 8h
**Status:** ✅ Concluído

### Sprint 4 (Próxima - 2 semanas)
1. Página de análises (P1) - 6h
2. Testes básicos (P2) - 10h
3. Paginação (P2) - 4h
**Total:** 20 horas

### Sprint 5 (2-4 semanas)
1. Página de configurações (P2) - 4h
2. Melhorias de UX (P3) - 6h
3. Cache de consultas (P3) - 4h
**Total:** 14 horas

### Sprint 68 horas

### Sprint 5+ (Backlog)
- Features financeiras avançadas
- Migração para PostgreSQL
- Multi-usuário
- PWA

---

## 📚 Referências

- [STATUS-PROJETO.md](./STATUS-PROJETO.md) — Estado completo do projeto
- [INDEX.md](./INDEX.md) — Documentação principal
- [CORRECAO-CALCULOS-CARTEIRA.md](./CORRECAO-CALCULOS-CARTEIRA.md) — Histórico de correções

---

## ✅ Checklist de Desenvolvimento

Ao trabalhar nas pendências, siga este processo:

### Antes de Implementar
- [ ] Ler documentação relacionada
- [ ] Verificar princípios arquiteturais
- [ ] Planejar mudanças no banco de dados (se aplicável)
- [ ] Criar branch de feature

### Durante Implementação
- [ ] Escrever código seguindo padrões do projeto
- [ ] Adicionar logs apropriados
- [ ] Tratar erros explicitamente
- [ ] Validar inputs

### Após Implementação
- [ ] Escrever ou atualizar testes
- [ ] Testar manualmente no browser/Postman
- [ ] Atualizar documentação
- [ ] Verificar erros com get_errors tool
- [ ] Commitar com mensagem descritiva
- [ ] Atualizar este arquivo (PENDENCIAS.md)

---

**Documento criado por:** GitHub Copilot  
**Última atualização:** 9 de janeiro de 2026  
**Próxima revisão:** Sprint planning (Sprint 3)
