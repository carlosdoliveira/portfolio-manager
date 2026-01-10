# Referência Técnica

Documentação técnica completa do Portfolio Manager v2.

---

## 🏗️ Arquitetura do Sistema

### Visão Geral

O Portfolio Manager v2 segue uma arquitetura em camadas:

```
┌─────────────────────────────────────┐
│         Frontend (React)            │
│    TypeScript + Vite + React 18     │
└─────────────────┬───────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────┐
│       Backend API (FastAPI)         │
│          Python 3.11                │
├─────────────────────────────────────┤
│         Business Logic              │
│    Services + Repositories          │
├─────────────────────────────────────┤
│         Database Layer              │
│        SQLite (WAL mode)            │
└─────────────────────────────────────┘
```

### Princípios Fundamentais

#### 1. Eventos Imutáveis
- Operações financeiras são eventos que nunca mudam
- Vendas são novas operações, não modificações
- Histórico completo é sempre mantido

#### 2. Import Idempotente
- Reimportar o mesmo arquivo não cria duplicatas
- Deduplicação via UNIQUE constraint no banco
- Hash ou chave de negócio para identificar duplicatas

#### 3. Estado Derivado
- Posições são calculadas, não armazenadas
- Agregações feitas em tempo de consulta
- Fonte única da verdade: tabela de operações

---

## 📊 Modelo de Dados

### Tabela: `assets`

Armazena os ativos negociados.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER | Chave primária |
| `ticker` | TEXT | Código do ativo (ex: PETR4) |
| `asset_type` | TEXT | Tipo (STOCK, FII, etc.) |
| `description` | TEXT | Descrição opcional |
| `created_at` | DATETIME | Data de criação |

**Constraints:**
- `ticker` é UNIQUE

### Tabela: `operations`

Armazena todas as operações (compra e venda).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER | Chave primária |
| `asset_id` | INTEGER | FK para `assets` |
| `trade_date` | DATE | Data da operação |
| `movement_type` | TEXT | COMPRA ou VENDA |
| `market` | TEXT | VISTA ou FRACIONARIO |
| `institution` | TEXT | Corretora |
| `quantity` | INTEGER | Quantidade |
| `price` | REAL | Preço unitário |
| `total_cost` | REAL | Custo total |
| `created_at` | DATETIME | Data de registro |

**Constraints:**
- UNIQUE constraint em (`trade_date`, `movement_type`, `market`, `institution`, `ticker`, `quantity`, `price`)

### Tabela: `fixed_income_assets`

Armazena ativos de renda fixa.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER | Chave primária |
| `asset_type` | TEXT | CDB, LCI, LCA, TESOURO |
| `issuer` | TEXT | Emissor |
| `application_date` | DATE | Data de aplicação |
| `maturity_date` | DATE | Data de vencimento |
| `applied_value` | REAL | Valor aplicado |
| `rate` | REAL | Taxa (% a.a.) |
| `created_at` | DATETIME | Data de registro |

---

## 🔌 API Reference

### Endpoints de Saúde

#### `GET /health`

Verifica o status da API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-10T12:00:00"
}
```

---

### Endpoints de Assets

#### `GET /assets`

Lista todos os ativos com agregações.

**Query Parameters:**
- `include_aggregations` (boolean, default: true)

**Response:**
```json
[
  {
    "id": 1,
    "ticker": "PETR4",
    "asset_type": "STOCK",
    "total_quantity": 100,
    "average_price": 30.50,
    "current_price": 32.00,
    "unrealized_pnl": 150.00
  }
]
```

#### `POST /assets`

Cria um novo ativo.

**Request Body:**
```json
{
  "ticker": "VALE3",
  "asset_type": "STOCK",
  "description": "Vale S.A."
}
```

**Response:**
```json
{
  "id": 2,
  "ticker": "VALE3",
  "asset_type": "STOCK",
  "description": "Vale S.A.",
  "created_at": "2026-01-10T12:00:00"
}
```

---

### Endpoints de Operations

#### `GET /operations`

Lista todas as operações.

**Query Parameters:**
- `asset_id` (integer, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)

**Response:**
```json
[
  {
    "id": 1,
    "asset_id": 1,
    "trade_date": "2026-01-05",
    "movement_type": "COMPRA",
    "quantity": 100,
    "price": 30.50,
    "total_cost": 3050.00
  }
]
```

#### `POST /operations`

Cria uma nova operação.

**Request Body:**
```json
{
  "asset_id": 1,
  "trade_date": "2026-01-10",
  "movement_type": "COMPRA",
  "market": "VISTA",
  "institution": "XP",
  "quantity": 50,
  "price": 32.00
}
```

---

### Endpoints de Import

#### `POST /import/b3`

Importa arquivo Excel B3.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (Excel file)

**Response:**
```json
{
  "success": true,
  "operations_imported": 25,
  "duplicates_skipped": 3,
  "errors": []
}
```

---

### Endpoints de Renda Fixa

#### `POST /fixed-income/assets`

Cria um ativo de renda fixa.

**Request Body:**
```json
{
  "asset_type": "CDB",
  "issuer": "Banco XYZ",
  "application_date": "2026-01-01",
  "maturity_date": "2027-01-01",
  "applied_value": 10000.00,
  "rate": 12.5
}
```

#### `GET /fixed-income/projection/{id}`

Retorna projeção de rendimento.

**Response:**
```json
{
  "applied_value": 10000.00,
  "gross_return": 1250.00,
  "tax": 187.50,
  "net_return": 1062.50,
  "redemption_value": 11062.50
}
```

---

## 🔒 Segurança

### Validação de Entrada

- Todos os endpoints usam Pydantic para validação
- Tipos são verificados em tempo de request
- Constraints são aplicados (valores positivos, datas válidas, etc.)

### Proteção SQL Injection

- Queries usam parâmetros vinculados (parameterized queries)
- Nunca concatenamos strings SQL diretamente
- Uso de `cursor.execute(sql, params)`

### CORS

Configurável via variável de ambiente:

```bash
CORS_ORIGINS="https://app.exemplo.com,https://exemplo.com"
```

---

## 🧪 Testing

### Executar Testes

```bash
# Backend
docker compose exec api pytest tests/

# Testes específicos
docker compose exec api pytest tests/test_operations.py
```

### Estrutura de Testes

```
tests/
├── test_assets.py           # Testes de ativos
├── test_operations.py       # Testes de operações
├── test_import.py           # Testes de importação
└── test_consolidacao.py     # Testes de consolidação
```

---

## 🚀 Deploy

### Produção com Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `CORS_ORIGINS` | Origens permitidas | `http://localhost:5173` |
| `DATABASE_PATH` | Caminho do banco | `/app/data/portfolio.db` |
| `LOG_LEVEL` | Nível de log | `INFO` |

---

## 📚 Dependências

### Backend

- **FastAPI** - Framework web
- **Uvicorn** - ASGI server
- **Pydantic** - Validação de dados
- **pandas** - Processamento de dados
- **openpyxl** - Leitura de Excel
- **yfinance** - Cotações de mercado

### Frontend

- **React** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Navegação

---

## 🔄 Fluxo de Dados

### Importação B3

```
1. Upload Excel → FastAPI
2. Validação do arquivo
3. Parse com pandas
4. Validação de cada operação
5. Inserção no banco (UNIQUE constraint)
6. Resposta com resultado
```

### Cálculo de Posição

```
1. Query todas as operações do ativo
2. Agregar compras (soma quantidades)
3. Agregar vendas (soma quantidades)
4. Calcular posição: compras - vendas
5. Calcular preço médio ponderado
```

### Cotação de Mercado

```
1. Request ao yfinance
2. Obter último preço
3. Cache por 5 minutos
4. Calcular P&L: (preço_atual - preço_médio) * quantidade
```

---

## 📞 Links Adicionais

- [Documentação da API (Swagger)](http://localhost:8000/docs)
- [Código Fonte](https://github.com/carlosdoliveira/portfolio-manager)
- [Issues e Bugs](https://github.com/carlosdoliveira/portfolio-manager/issues)
- [Changelog](../CHANGELOG.md)
