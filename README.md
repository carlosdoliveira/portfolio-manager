
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

## Segurança e Validação 🔒

O projeto implementa as seguintes medidas de segurança:

### CORS Configurável
- Origens permitidas via variável de ambiente `CORS_ORIGINS`
- Padrão: `http://localhost:5173` (desenvolvimento)
- Múltiplas origens: use vírgula como separador (ex: `CORS_ORIGINS="http://localhost:5173,http://localhost:3000"`)
- Métodos HTTP explícitos: apenas `GET` e `POST`

### Validação de Entrada
- Endpoint `/operations` usa validação Pydantic com:
  - Tipos de dados estritamente tipados
  - Validação de formato (ex: `movement_type` só aceita "COMPRA" ou "VENDA")
  - Validação de valores (quantidade e preço devem ser > 0)
  - Campos obrigatórios e opcionais claramente definidos

### Tratamento de Erros
- Importação diferencia duplicatas de erros reais
- Captura específica de `sqlite3.IntegrityError` para duplicatas
- Erros inesperados causam rollback e propagam mensagem detalhada
- Responses HTTP apropriados (400 para validação, 503 para problemas de infraestrutura)

## Quickstart (Docker) 🐳
Recomendado para desenvolvimento rápido:

```bash
docker-compose up --build
```

Serviços expostos por padrão:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

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

Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend

```bash
cd frontend
npm install
npm run dev
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
Existe um teste placeholder em `backend/tests`. Para rodar os testes localmente instale `pytest` e execute:

```bash
pip install pytest
pytest backend/tests
```

## Estrutura do projeto 🗂️
- `backend/` — API FastAPI, parsing de Excel, persistência
- `frontend/` — UI em React + Vite
- `docker-compose.yml` — orquestra backend e frontend para desenvolvimento

## Contribuindo 🤝
- Siga os princípios do projeto (eventos imutáveis, import idempotente)
- Abra PRs pequenas e documente mudanças de esquema do banco de dados

---

Se quiser, posso também adicionar exemplos de curl para os endpoints ou tarefas de CI para testes e linting. Quero que eu inclua isso agora? ✨
