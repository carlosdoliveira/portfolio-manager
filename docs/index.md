# Portfolio Manager v2

Sistema web de gestão de carteira de investimentos com foco em importação B3, renda fixa e análise de performance.

**Versão:** v2.2.0 | **Status:** ✅ MVP Funcional | **Última atualização:** 16/01/2026

---

## 🚀 Início Rápido

### Para Usuários
```bash
./portfolio start    # Inicia containers (backend + frontend)
# Acesse: http://localhost:5173
```

### Para Desenvolvedores
1. 📖 [Guia de Setup](development/setup.md)
2. 🏗️ [Arquitetura](architecture/principios-core.md)
3. 🔌 [API Reference](api/endpoints.md)

---

## ✨ Principais Funcionalidades

### ✅ Implementado
- **Importação B3** — Upload de Excel com deduplicação automática
- **CRUD Completo** — Ativos e operações com interface web
- **Renda Fixa** — CDB, LCI, LCA, Tesouro com projeções e IR
- **Consolidação de Mercados** — Operações à vista e fracionárias unificadas
- **Sistema de Cotações** — Cache otimizado + atualização automática (cron job)
- **Mark-to-Market** — Valor real com cotações de mercado (<100ms)
- **Dashboard Completo** — Cards, gráficos, estatísticas em tempo real
- **Cálculos Consistentes** — Dashboard e Carteira 100% sincronizados

### ⚠️ Em Progresso
- Página de análises (placeholder)
- Testes automatizados (cobertura parcial)

### 📅 Planejado
- Proventos e dividendos
- Eventos corporativos (splits, bonificações)
- Relatórios de IR
- Gráficos históricos

---

## 🏗️ Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | Python + FastAPI | 3.11 |
| Frontend | React + TypeScript + Vite | 18.x / 5.4.x |
| Banco de Dados | SQLite (WAL mode) | 3.x |
| Container | Docker Compose | 2.x |

---

## 🔑 Princípios Arquiteturais

### 1. **Eventos Imutáveis**
Cada operação é armazenada como evento — nunca mutamos registros existentes.

### 2. **Import Idempotente**
Reimportar o mesmo arquivo não cria duplicatas (UNIQUE constraint).

### 3. **Estado Derivado**
Posições e agregações são calculadas em runtime, não armazenadas.

📖 **Leia mais:** [Princípios Core](architecture/principios-core.md)

---

## 🔒 Segurança e Qualidade

### ✅ Implementado

**Validação de Entrada** — Pydantic com tipos e constraints  
**Proteção SQL Injection** — Queries parametrizados  
**CORS Configurável** — `CORS_ORIGINS` via env  
**Gerenciamento de Conexões** — Context managers  
**Logging Estruturado** — Todos os pontos críticos  

📖 **Leia mais:** [REFERENCIA-TECNICA.md](REFERENCIA-TECNICA.md)

---

## 📖 Documentação

### 📚 Principais Documentos
- **[INDEX.md](INDEX.md)** — Página inicial completa
- **[STATUS-PROJETO.md](STATUS-PROJETO.md)** — Estado atual e roadmap
- **[REFERENCIA-TECNICA.md](REFERENCIA-TECNICA.md)** — Especificações técnicas

### 🎯 Por Persona
- **Gestores:** [INDEX.md](INDEX.md) → [STATUS-PROJETO.md](STATUS-PROJETO.md)
- **Backend:** [Setup](development/setup.md) → [API](api/endpoints.md)
- **Frontend:** [Setup](development/setup.md) → [CRUD](guides/crud-implementation.md)

---

## 🛠️ Comandos Úteis

```bash
./portfolio start       # Inicia containers
./portfolio status      # Status dos serviços
./portfolio logs        # Logs em tempo real
./portfolio stop        # Para containers
./portfolio clean-all   # Remove tudo (incluindo DB)
```

**Comandos disponíveis:**
- `start` - Inicia todos os serviços (backend + frontend)
- `stop` - Para todos os serviços
- `restart` - Reinicia todos os serviços
- `status` - Mostra o status atual
- `logs [serviço]` - Exibe logs (api, frontend ou ambos)
- `clean` - Remove containers e imagens Docker
- `clean-all` - Remove tudo, incluindo dados persistidos
- `help` - Exibe ajuda completa

### Usando Docker Compose Diretamente

Alternativa ao CLI para usuários avançados:

```bash
docker-compose up --build
```

Serviços expostos por padrão:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

O banco de dados SQLite é persistido em `./backend/data/portfolio.db` via volume do Docker.

### Variáveis de Ambiente

**Backend (CORS):**

Para configurar origens CORS em produção, defina a variável de ambiente:

```bash
CORS_ORIGINS="https://seu-dominio.com,https://app.seu-dominio.com" docker-compose up
```

Ou adicione no arquivo `.env` na raiz do projeto.

📖 **Detalhes completos:** [docs/development/setup.md](development/setup.md)

---

## 📡 API Principal

### Endpoints Disponíveis
- `GET /health` — Status de saúde
- `POST /import/b3` — Upload Excel B3
- `GET /assets` — Listar ativos com agregações
- `POST /assets` — Criar novo ativo
- `GET /operations` — Listar operações
- `POST /operations` — Criar operação manual
- `POST /fixed-income/assets` — Criar ativo RF
- `GET /fixed-income/projection/{id}` — Projeção de rendimento
- `GET /dashboard/summary` — Resumo completo da carteira
- `GET /quotes/portfolio/current` — Cotações com cache (<100ms)
- `POST /quotes/update` — Atualizar cache de cotações

📖 **Documentação completa:** [api/endpoints.md](api/endpoints.md)  
⚡ **Performance:** [guides/otimizacao-carteira.md](guides/otimizacao-carteira.md)  
🔄 **Cache de cotações:** [guides/atualizacao-cotacoes.md](guides/atualizacao-cotacoes.md)

---

## 🗂️ Estrutura do Projeto

```
portfolio-manager-v2/
├── portfolio              # CLI de gerenciamento
├── docker-compose.yml     # Orquestração
├── backend/              # FastAPI + SQLite
│   ├── app/
│   │   ├── main.py       # Endpoints
│   │   ├── db/           # Database
│   │   ├── repositories/ # Data layer
│   │   └── services/     # Business logic
│   └── data/             # SQLite (persistido)
├── frontend/             # React + TypeScript
│   └── src/
│       ├── pages/        # Páginas
│       ├── components/   # Componentes
│       └── api/          # HTTP client
├── docs/                 # 📚 Documentação
│   ├── INDEX.md          # 🏠 Página inicial
│   ├── STATUS-PROJETO.md # Estado atual
│   ├── api/              # API docs
│   ├── guides/           # Guias práticos
│   └── architecture/     # Decisões técnicas
└── tests/                # Testes automatizados
```

---

## 🧪 Testes

```bash
# Backend
docker compose exec api pytest tests/

# Teste de consolidação
python3 tests/test_consolidacao_mercados.py
```

📖 **Mais informações:** [STATUS-PROJETO.md](STATUS-PROJETO.md)

---

## 🔧 Solução de Problemas

| Problema | Solução |
|----------|---------|
| Containers não iniciam | `./portfolio clean && ./portfolio start` |
| Porta em uso | Ajuste `docker-compose.yml` |
| Banco corrompido | `./portfolio clean-all && ./portfolio start` |
| Ver logs | `./portfolio logs [api\|frontend]` |

📖 **Troubleshooting completo:** [development/setup.md](development/setup.md)

---

## 🤝 Contribuindo

1. Siga os [Princípios Core](architecture/principios-core.md)
2. Use CLI `./portfolio` para desenvolvimento
3. Documente mudanças significativas
4. Execute testes antes de submeter

📖 **Guia de contribuição:** [INDEX.md](INDEX.md)

---

## 📞 Links Úteis

- 📚 [Documentação Completa](INDEX.md)
- 📊 [Status do Projeto](STATUS-PROJETO.md)
- 🔌 [API Reference](api/endpoints.md)
- 📝 [Changelog](../CHANGELOG.md)
- 🐛 [Issues](https://github.com/carlosdoliveira/portfolio-manager/issues)

---

## 📄 Licença

MIT — Uso pessoal e educacional

---

**Mantido por:** Equipe Portfolio Manager v2  
**Versão:** v2.1.0  
**Última atualização:** 09/01/2026
