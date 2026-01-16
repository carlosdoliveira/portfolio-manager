# Changelog — Portfolio Manager v2

Todas as mudanças notáveis do projeto são documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.2.0] - 2026-01-16

### 🔥 Adicionado

#### Sistema de Cache de Cotações
- **Tabela `quotes`** no banco de dados para persistência de cotações
- **Repository `quotes_repository.py`** com funções CRUD para cache
- **Endpoint `POST /quotes/update`** para atualização em lote via cron job
- **Endpoint `GET /quotes`** para listar todas as cotações em cache
- **Endpoint `GET /quotes/{ticker}`** para buscar cotação específica
- **Script `update_quotes_cron.py`** para automação via cron
- Documentação completa: [guides/atualizacao-cotacoes.md](./docs/guides/atualizacao-cotacoes.md)

#### Otimizações de Performance
- **Cache hit rate > 95%**: Redução de 95% no tempo de carregamento
- **Dashboard**: 3-5s → <100ms com cache
- **Carteira**: 3-5s → <100ms com cache
- **Fallback automático**: yfinance quando cache indisponível
- Documentação completa: [guides/otimizacao-carteira.md](./docs/guides/otimizacao-carteira.md)

#### Correções de Cálculos
- **Mark-to-market unificado**: Dashboard e Carteira agora calculam FIIs com cotação real
- **Fallback para valor investido**: Ativos sem cotação somam valor investido
- **Consistência 100%**: Ambas as páginas mostram R$ 60.909,73
- Documentação completa: [guides/consistencia-calculos.md](./docs/guides/consistencia-calculos.md)

#### Interface
- **Cores de lucro/prejuízo**: Verde (positivo) e vermelho (negativo/zero)
- **Variáveis CSS**: Adicionadas `--success-green` e `--danger-red` em `theme.css`
- **Gráfico de alocação**: Pie chart com Recharts no Dashboard

### 🔧 Alterado

#### Backend
- **`dashboard_repository.py`**: Agora busca cotações de TODOS os ativos (não apenas Ações/ETFs)
- **`main.py`**: Endpoint `/quotes/portfolio/current` usa sistema de cache
- **`main.py`**: Imports de `quotes_repository` corrigidos (funções diretas)

#### Frontend
- **`Portfolio.tsx`**: Implementado fallback para ativos sem cotação
- **`Dashboard.tsx`**: Lógica de cores alterada de `>= 0` para `> 0`
- **`theme.css`**: Novas variáveis CSS para consistência de cores

### 🗑️ Removido

#### Lógica Duplicada
- **`dashboard_repository.py`**: Removida query separada para "outros ativos" (FIIs)
- Todos os ativos agora processados no mesmo loop principal

### 📝 Documentação

#### Novos Guias
- **atualizacao-cotacoes.md**: Sistema de cache e cron job
- **otimizacao-carteira.md**: Performance e benchmarks
- **consistencia-calculos.md**: Correção de divergências

#### Arquivados
Movidos para `docs/archive/`:
- CORRECAO-CALCULOS-CARTEIRA.md
- DIAGNOSTICO-CONSOLIDACAO-FINAL.md
- PENDENCIAS.md
- guia.md
- referencia.md
- CHANGELOG-OLD.md

#### Atualizados
- **STATUS-PROJETO.md**: v2.2.0 com métricas e conquistas
- **README.md**: Versão e funcionalidades atualizadas
- **index.md**: Endpoints e referências atualizadas

### 🐛 Corrigido

- **Bug crítico**: Dashboard usava valor investido para FIIs (não mark-to-market)
- **Bug crítico**: Carteira ignorava ativos sem cotação (CIEL3)
- **Bug**: Cores de lucro/prejuízo não apareciam (variáveis CSS faltando)
- **Bug**: Referências incorretas a `quotes_repository.*` no código

---

## [2.1.0] - 2026-01-09

### Adicionado
- Dashboard principal com cards de resumo
- Integração com yfinance para cotações
- Gráfico de alocação por classe de ativo
- Top 5 posições na carteira
- Operações recentes no Dashboard

### Alterado
- Consolidação visual de mercados (fracionário/vista)
- Melhorias de UX em formulários

---

## [2.0.1] - 2026-01-04

### Corrigido
- Cálculos de totalizadores zerados (case-sensitive)
- Preço médio zerado em detalhes do ativo
- Normalização de ticker (acentos)

---

## [2.0.0] - 2025-12-30

### Adicionado
- MVP funcional: CRUD completo
- Importação B3 com deduplicação
- Renda Fixa (CDB, LCI, LCA, Tesouro)
- Projeções de rendimento e cálculo de IR
- Interface web responsiva

---

## [1.0.0] - 2025-12-15

### Adicionado
- Estrutura inicial do projeto
- Backend FastAPI + SQLite
- Frontend React + TypeScript
- Docker Compose

---

## Tipos de Mudanças

- **Adicionado** - para novas funcionalidades
- **Alterado** - para mudanças em funcionalidades existentes
- **Obsoleto** - para funcionalidades que serão removidas
- **Removido** - para funcionalidades removidas
- **Corrigido** - para correção de bugs
- **Segurança** - para vulnerabilidades

---

## Próximas Versões

### [2.3.0] - Planejado
- Página de Análises completa
- Testes automatizados (cobertura 80%+)
- Melhorias de UX (loading skeletons, tooltips)

### [3.0.0] - Futuro
- Proventos e dividendos
- Relatórios de IR
- Eventos corporativos
- PWA com offline support
