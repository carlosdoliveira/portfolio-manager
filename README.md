
# Portfolio Manager v2

Aplicação MVP para gerenciar operações financeiras importadas a partir de relatórios da B3.

## Principais funcionalidades ✅
- Importação de relatórios da B3 (Excel)
- Deduplicação / import idempotente por chave de negócio
- Persistência em SQLite com histórico imutável de operações (eventos)
- API simples para operações manuais e listagem

## Princípios do projeto 🔧
- **Eventos imutáveis**: cada movimento (compra / venda) é armazenado como um novo registro — nunca mutamos operações existentes.
- **Import idempotente**: reimportar o mesmo arquivo não cria duplicatas; a deduplicação é aplicada via UNIQUE constraint na base.
- **Derivações são calculadas**: posições/LP/P&L devem ser calculadas a partir das operações (não armazenadas como estado final).

## Segurança e Qualidade 🔒

O projeto implementa as seguintes medidas de segurança e qualidade:

### ✅ Implementado

**CORS Configurável**
- Origens permitidas via variável de ambiente `CORS_ORIGINS`
- Padrão: `http://localhost:5173` (desenvolvimento)
- Múltiplas origens: use vírgula como separador (ex: `CORS_ORIGINS="http://localhost:5173,http://localhost:3000"`)
- Métodos HTTP explícitos: apenas `GET` e `POST`

**Validação de Entrada**
- Endpoint `/operations` usa validação Pydantic com:
  - Tipos de dados estritamente tipados
  - Validação de formato (ex: `movement_type` só aceita "COMPRA" ou "VENDA")
  - Validação de valores (quantidade e preço devem ser > 0)
  - Campos obrigatórios e opcionais claramente definidos

**Tratamento de Erros**
- Importação diferencia duplicatas de erros reais
- Captura específica de `sqlite3.IntegrityError` para duplicatas
- Erros inesperados causam rollback e propagam mensagem detalhada
- Responses HTTP apropriados (400 para validação, 503 para problemas de infraestrutura)

**Proteção SQL Injection**
- Todos os queries usam placeholders parametrizados (`?`)
- Zero concatenação de strings em SQL

**Gerenciamento de Conexões DB**
- Context manager garante fechamento de conexões
- Commit automático em sucesso
- Rollback automático em erro
- Zero leaks de recursos

**Logging Estruturado**
- Logs em todos os pontos críticos:
  - Startup da aplicação
  - Importações B3 (início, validação, duplicatas, erros)
  - Operações manuais
  - Listagem de operações
- Formato padronizado com timestamp
- Níveis apropriados (INFO, DEBUG, ERROR)

### 🎉 Status: Pronto para Produção!

**Todas as medidas críticas de segurança e qualidade foram implementadas.**

Próximos passos recomendados (não bloqueantes):
- Testes unitários para maior confiança
- Healthcheck que verifica banco de dados
- Rate limiting para proteção contra abuso

**Documentação completa:** [docs/oportunidades-backend.md](docs/oportunidades-backend.md)

## Quickstart (Recomendado) 🚀

### Usando o CLI (Mais Fácil)

O projeto inclui um script CLI que facilita o gerenciamento de todos os serviços:

```bash
# Iniciar a aplicação
./portfolio start

# Ver status dos serviços
./portfolio status

# Ver logs em tempo real
./portfolio logs

# Parar a aplicação
./portfolio stop

# Remover tudo (incluindo banco de dados)
./portfolio clean-all
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

Para configurar origens CORS em produção, defina a variável de ambiente:

```bash
CORS_ORIGINS="https://seu-dominio.com,https://app.seu-dominio.com" docker-compose up
```

Ou adicione no arquivo `.env` na raiz do projeto:

```env
CORS_ORIGINS=https://seu-dominio.com,https://app.seu-dominio.com
```

## Executando localmente (sem Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Gerenciamento do Projeto 🛠️

### Estrutura de Diretórios
- `backend/` — API FastAPI, parsing de Excel, persistência
- `frontend/` — UI em React + Vite
- `docker-compose.yml` — orquestra backend e frontend
- `portfolio` — CLI para gerenciamento simplificado

### Fluxo de Desenvolvimento Recomendado

1. **Primeira vez:**
   ```bash
   ./portfolio start
   ```

2. **Durante desenvolvimento:**
   ```bash
   # Ver logs em tempo real
   ./portfolio logs
   
   # Ver logs apenas do backend
   ./portfolio logs api
   
   # Reiniciar após mudanças
   ./portfolio restart
   ```

3. **Limpeza:**
   ```bash
   # Remove containers e volumes Docker
   ./portfolio clean
   
   # Remove tudo incluindo dados
   ./portfolio clean-all
   ```

## Endpoints principais (API) 📡
- `GET /health` — status de saúde
- `POST /import/b3` — importa um arquivo Excel da B3 (form-data, campo `file`)
	- Retorna um resumo: `{ total_rows, inserted, duplicated, unique_assets, imported_at }`
- `POST /operations` — cria operação manual. Exemplo mínimo de payload:

```json
{
	"asset_class": "Renda Variável",
	"asset_type": "Ação",
	"product_name": "Empresa X",
	"ticker": "XPLG",
	"movement_type": "COMPRA",
	"quantity": 100,
	"price": 10.5,
	"trade_date": "2025-12-31"
}
```

- `GET /operations` — lista operações ordenadas por data

## Formato de importação (B3) 📄
O importador espera as seguintes colunas no Excel (nomes conforme relatório da B3):

- `Data do Negócio` (formato `DD/MM/YYYY`)
- `Tipo de Movimentação`
- `Mercado`
- `Instituição`
- `Código de Negociação`
- `Quantidade`
- `Preço`
- `Valor`

Ao encontrar linhas com os mesmos valores para os campos da chave de deduplicação, a linha é considerada duplicada e será ignorada (não causa exceção para o usuário).

## Banco de dados 🗄️
- SQLite localizado em `backend/app/data/portfolio.db` (criado automaticamente)
- A tabela `operations` contém uma UNIQUE constraint para garantir idempotência:

	(trade_date, movement_type, market, institution, ticker, quantity, price, source)

## Testes 🧪

Existe um teste placeholder em `backend/tests`. Para rodar os testes localmente:

```bash
# Com Docker (recomendado)
docker compose exec api pytest tests/

# Sem Docker
cd backend
pip install pytest
pytest tests/
```

## Solução de Problemas 🔧

### Containers não iniciam
```bash
./portfolio clean
./portfolio start
```

### Porta já em uso
Se as portas 8000 ou 5173 estiverem em uso, ajuste no `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Usar porta 8001 ao invés de 8000
```

### Banco de dados corrompido
```bash
./portfolio clean-all  # Remove tudo
./portfolio start      # Recria o banco
```

### Ver logs detalhados
```bash
./portfolio logs api       # Logs do backend
./portfolio logs frontend  # Logs do frontend
```

## Estrutura do projeto 🗂️
```
portfolio-manager-v2/
├── portfolio              # CLI de gerenciamento
├── docker-compose.yml     # Orquestração de serviços
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── main.py       # Endpoints e configuração
│   │   ├── db/           # Conexão e schema
│   │   ├── repositories/ # Camada de dados
│   │   └── services/     # Lógica de negócio
│   └── data/             # SQLite (persistido)
└── frontend/             # UI React + Vite
    └── src/
        ├── pages/        # Páginas da aplicação
        ├── components/   # Componentes reutilizáveis
        └── api/          # Cliente HTTP
```

## Contribuindo 🤝
- Siga os princípios do projeto (eventos imutáveis, import idempotente)
- Use o CLI `./portfolio` para desenvolvimento
- Abra PRs pequenas e documente mudanças de esquema do banco de dados
- Execute testes antes de submeter: `docker compose exec api pytest`

## Licença 📄

Este projeto é de uso pessoal e educacional.

---

**Dúvidas?** Execute `./portfolio help` para ver todos os comandos disponíveis.
