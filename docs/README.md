# 📚 Documentação do Portfolio Manager v2

**Última atualização:** 17 de Janeiro de 2026  
**Versão:** v2.2.0

> 🚀 **Início Rápido:** Leia o [INDEX.md](./INDEX.md) para visão completa do sistema

---

## 📖 Navegação Principal

### Para Todos
- 🏠 **[INDEX.md](./INDEX.md)** — Página inicial completa com visão geral
- 📊 **[STATUS-PROJETO.md](./STATUS-PROJETO.md)** — Estado atual e roadmap
- 📖 **[REFERENCIA-TECNICA.md](./REFERENCIA-TECNICA.md)** — Especificações técnicas

### Para Desenvolvedores

#### 🏗️ Arquitetura
- [Princípios Core](./architecture/principios-core.md) — Event-based, immutability

#### 🔌 API
- [Endpoints](./api/endpoints.md) — Ativos, Operações, Renda Fixa, Cotações

#### 📖 Guias
- [Consolidação de Mercados](./guides/consolidacao-mercados.md) ⭐ **Recomendado**
- [Integração com Cotações](./guides/integracao-cotacoes.md) 🔥 **Implementado**
- [Atualização de Cotações (Cron)](./guides/atualizacao-cotacoes.md) 🔥 **Implementado**
- [Otimização de Carteira](./guides/otimizacao-carteira.md) 🔥 **Implementado**
- [Consistência de Cálculos](./guides/consistencia-calculos.md) ✅ **Resolvido**
- [Implementação CRUD](./guides/crud-implementation.md)
- [Fluxo Visual de Consolidação](./guides/fluxo-consolidacao-visual.md)

#### 🛠️ Desenvolvimento
- [Setup Local](./development/setup.md) — Docker, ambiente

### Documentação Especializada
- 💰 [Renda Fixa](./renda-fixa.md) — Guia completo de RF
- 📈 [Integração com Cotações](./guides/integracao-cotacoes.md) — API de mercado
- ⚡ [Otimização de Carteira](./guides/otimizacao-carteira.md) — Sistema de cache
- 🕒 [Atualização de Cotações](./guides/atualizacao-cotacoes.md) — Cron job automático
- ✅ [Consistência de Cálculos](./guides/consistencia-calculos.md) — Correções implementadas
- 📋 [Diagnóstico de Consolidação](./DIAGNOSTICO-CONSOLIDACAO-FINAL.md) — Debug da consolidação

---

## 🗂️ Estrutura de Pastas

```
docs/
├── INDEX.md                    # 🏠 PÁGINA INICIAL — comece aqui
├── STATUS-PROJETO.md           # 📊 Estado atual e roadmap
├── REFERENCIA-TECNICA.md       # 📖 Especificações técnicas
├── renda-fixa.md              # 💰 Guia de Renda Fixa
├── DIAGNOSTICO-CONSOLIDACAO-FINAL.md  # 🔧 Debug da consolidação
│
├── architecture/               # 🏗️ Decisões arquiteturais
│   └── principios-core.md
│
├── api/                       # 🔌 Documentação de API
│   └── endpoints.md
│
├── guides/                    # 📖 Guias práticos
│   ├── consolidacao-mercados.md         # ⭐ Recomendado
│   ├── integracao-cotacoes.md           # 🔥 Sistema de cotações
│   ├── atualizacao-cotacoes.md          # 🔥 Cron job
│   ├── otimizacao-carteira.md           # 🔥 Cache e performance
│   ├── consistencia-calculos.md         # ✅ Correções implementadas
│   ├── crud-implementation.md
│   ├── exemplo-consolidacao.sql
│   └── fluxo-consolidacao-visual.md
│
├── development/               # 🛠️ Setup e workflows
│   └── setup.md
│
├── deployment/                # 🚀 Deploy (futuro)
│
└── archive/                   # 📦 Documentos históricos
    └── README.md
```

---

## 🎯 Fluxo de Leitura Recomendado

### 👨‍💼 Gestores / Product Owners
1. [INDEX.md](./INDEX.md) — Visão geral
2. [STATUS-PROJETO.md](./STATUS-PROJETO.md) — O que está pronto
3. Próximos passos em [STATUS-PROJETO.md#próximos-passos](./STATUS-PROJETO.md#próximos-passos)

### 👨‍💻 Desenvolvedores Backend
1. [development/setup.md](./development/setup.md) — Configure ambiente
2. [architecture/principios-core.md](./architecture/principios-core.md) — Entenda arquitetura
3. [api/endpoints.md](./api/endpoints.md) — Veja endpoints disponíveis
4. [REFERENCIA-TECNICA.md](./REFERENCIA-TECNICA.md) — Detalhes técnicos

### 👨‍💻 Desenvolvedores Frontend
1. [development/setup.md](./development/setup.md) — Configure ambiente
2. [api/endpoints.md](./api/endpoints.md) — APIs disponíveis
3. [guides/crud-implementation.md](./guides/crud-implementation.md) — Padrões de CRUD

### 👨‍🔬 QA / Testadores
1. [STATUS-PROJETO.md](./STATUS-PROJETO.md) — Funcionalidades implementadas
2. [guides/consolidacao-mercados.md](./guides/consolidacao-mercados.md) — Como testar consolidação
3. `tests/test_consolidacao_mercados.py` — Scripts de teste

---

## 🔍 Busca Rápida

### Como fazer...

| Tarefa | Documento |
|--------|-----------|
| **Configurar ambiente local** | [development/setup.md](./development/setup.md) |
| **Entender consolidação de mercados** | [guides/consolidacao-mercados.md](./guides/consolidacao-mercados.md) |
| **Ver endpoints da API** | [api/endpoints.md](./api/endpoints.md) |
| **Integrar cotações de mercado** | [guides/integracao-cotacoes.md](./guides/integracao-cotacoes.md) |
| **Implementar cache de cotações** | [guides/otimizacao-carteira.md](./guides/otimizacao-carteira.md) |
| **Configurar cron job de cotações** | [guides/atualizacao-cotacoes.md](./guides/atualizacao-cotacoes.md) |
| **Calcular projeção de RF** | [REFERENCIA-TECNICA.md](./REFERENCIA-TECNICA.md#cálculo-de-projeção) |
| **Criar novo CRUD** | [guides/crud-implementation.md](./guides/crud-implementation.md) |
| **Saber o que está implementado** | [STATUS-PROJETO.md](./STATUS-PROJETO.md#funcionalidades-implementadas) |
| **Ver próximos passos** | [STATUS-PROJETO.md](./STATUS-PROJETO.md#próximos-passos) |
| **Resolver bugs de cálculo** | [guides/consistencia-calculos.md](./guides/consistencia-calculos.md) |

---

## 📦 Documentação Arquivada

Análises antigas e documentos obsoletos foram movidos para [`archive/`](./archive/):

- Análises de código de Dezembro/2025
- Oportunidades de melhoria (já consolidadas)
- Versões antigas de documentos
- CORRECAO-CALCULOS-CARTEIRA.md (bug resolvido)
- PENDENCIAS.md (consolidado em STATUS-PROJETO.md)

**Motivo:** Informações já consolidadas em STATUS-PROJETO.md e INDEX.md

---

## 🆕 Novidades

### Janeiro 2026

#### v2.2.0 (16 Jan 2026) 🔥
- ✅ **Sistema de cache de cotações** — SQLite com TTL de 15min
- ✅ **Cron job automático** — Atualização em lote a cada 15 minutos
- ✅ **Performance otimizada** — Dashboard/Carteira <100ms (redução de 95%)
- ✅ **Consistência de cálculos** — Dashboard e Carteira 100% sincronizados
- ✅ **Mark-to-market real** — FIIs agora calculados com cotação de mercado
- ✅ **Fallback inteligente** — Valor investido para ativos sem cotação
- ✅ **Cores de lucro/prejuízo** — Verde (positivo) e vermelho (negativo)

#### v2.1.0 (09 Jan 2026)
- ✅ Consolidação de mercados documentada e implementada
- ✅ Renda Fixa com projeções completas
- ✅ Documentação reorganizada e atualizada
- ✅ INDEX.md criado como página inicial

### Próximas Adições
- 🔜 Página de análises completa (Sprint 2)
- 🔜 Testes automatizados (Sprint 1-2)
- 🔜 Proventos e dividendos (Sprint 3)
- 🔜 Gráficos históricos (Sprint 4)

---

## 🤝 Como Contribuir com a Documentação

### Adicionar Novo Documento
1. Escolha a pasta apropriada (`guides/`, `architecture/`, etc.)
2. Use formato Markdown (.md)
3. Adicione link no INDEX.md
4. Mantenha linguagem clara e exemplos práticos

### Atualizar Documento Existente
1. Edite o arquivo
2. Atualize "Última atualização" no topo
3. Se mudança significativa, adicione em "Novidades"

### Arquivar Documento Obsoleto
1. Mova para `archive/`
2. Atualize `archive/README.md`
3. Remova links do INDEX.md e README.md
4. Adicione nota de redirecionamento (se necessário)

---

## 📞 Suporte

- **Bugs:** Abra issue no GitHub
- **Dúvidas:** Consulte INDEX.md primeiro
- **Sugestões:** Pull requests são bem-vindos!

---

## 🏆 Princípios de Documentação

✅ **Clareza** — Prefira exemplos a explicações longas  
✅ **Atualidade** — Documente enquanto desenvolve  
✅ **Organização** — Cada documento tem um propósito claro  
✅ **Navegabilidade** — Links internos facilitam navegação  
✅ **Acessibilidade** — Comece sempre pelo INDEX.md  

---

**Mantido por:** Equipe Portfolio Manager v2  
**Próxima Revisão:** 20/01/2026 (Planejamento Sprint 2)  
**Versão Atual:** v2.2.0
