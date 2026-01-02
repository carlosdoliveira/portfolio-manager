# 🔧 Referência Técnica — Portfolio Manager v2

Este documento detalha a implementação técnica do sistema para desenvolvedores.

---

## API Endpoints

### Ativos (Assets)

#### `POST /assets`
Cria um novo ativo.

**Request Body:**
```json
{
  "ticker": "PETR4",
  "asset_class": "AÇÕES",
  "asset_type": "PN",
  "product_name": "PETROBRAS PN"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "ticker": "PETR4",
  "asset_class": "AÇÕES",
  "asset_type": "PN",
  "product_name": "PETROBRAS PN",
  "created_at": "2026-01-02T10:00:00",
  "status": "ACTIVE"
}
```

---

#### `GET /assets`
Lista todos os ativos com agregações.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "ticker": "PETR4",
    "asset_class": "AÇÕES",
    "asset_type": "PN",
    "product_name": "PETROBRAS PN",
    "created_at": "2026-01-02T10:00:00",
    "status": "ACTIVE",
    "total_bought": 100,
    "total_sold": 50,
    "current_position": 50,
    "avg_price": 35.50,
    "total_bought_value": 3550.00,
    "total_sold_value": 1800.00
  }
]
```

---

#### `GET /assets/{asset_id}`
Busca um ativo pelo ID.

**Response:** `200 OK` (mesmo formato do item acima)

---

#### `PUT /assets/{asset_id}`
Atualiza um ativo existente.

**Request Body:**
```json
{
  "ticker": "PETR3",
  "asset_class": "AÇÕES",
  "asset_type": "ON",
  "product_name": "PETROBRAS ON"
}
```

**Response:** `200 OK`

---

#### `DELETE /assets/{asset_id}`
Soft delete de um ativo.

**Response:** `200 OK`
```json
{
  "message": "Asset deleted successfully"
}
```

---

### Operações (Operations)

#### `POST /operations`
Cria uma nova operação.

**Request Body:**
```json
{
  "asset_id": 1,
  "movement_type": "COMPRA",
  "quantity": 100,
  "price": 35.50,
  "value": 3550.00,
  "trade_date": "2026-01-02",
  "source": "MANUAL",
  "market": "BOVESPA",
  "institution": "XP"
}
```

**Response:** `201 Created`

---

#### `GET /operations`
Lista todas as operações.

**Query Parameters:**
- `asset_id` (opcional): Filtrar por ativo

---

#### `GET /assets/{asset_id}/operations`
Lista operações de um ativo específico.

---

### Importação B3

#### `POST /import/b3`
Importa arquivo Excel da B3.

**Request:** `multipart/form-data`
- `file`: Arquivo .xlsx

**Response:** `200 OK`
```json
{
  "success": true,
  "imported": 15,
  "duplicates": 3,
  "errors": 0,
  "message": "Import completed successfully"
}
```

---

### Renda Fixa

#### `POST /fixed-income/assets`
Cria um ativo de renda fixa.

**Request Body:**
```json
{
  "ticker": "CDB-XP-2026",
  "asset_class": "RENDA FIXA",
  "asset_type": "CDB",
  "product_name": "CDB XP 120% CDI",
  "issuer": "Banco XP",
  "product_type": "CDB",
  "indexer": "CDI",
  "rate": 120.0,
  "maturity_date": "2027-01-02",
  "issue_date": "2026-01-02",
  "custody_fee": 0.0
}
```

---

#### `GET /fixed-income/assets`
Lista ativos de renda fixa com saldos.

**Response:**
```json
[
  {
    "id": 1,
    "asset_id": 5,
    "ticker": "CDB-XP-2026",
    "product_name": "CDB XP 120% CDI",
    "issuer": "Banco XP",
    "product_type": "CDB",
    "indexer": "CDI",
    "rate": 120.0,
    "maturity_date": "2027-01-02",
    "issue_date": "2026-01-02",
    "custody_fee": 0.0,
    "total_invested": 10000.00,
    "total_redeemed": 0.00,
    "current_balance": 10000.00
  }
]
```

---

#### `PUT /fixed-income/assets/{asset_id}`
Atualiza um ativo de renda fixa.

**Request Body (parcial):**
```json
{
  "rate": 115.0,
  "maturity_date": "2027-06-01"
}
```

---

#### `POST /fixed-income/operations`
Cria operação de renda fixa.

**Request Body:**
```json
{
  "asset_id": 5,
  "operation_type": "APLICACAO",
  "amount": 10000.00,
  "trade_date": "2026-01-02"
}
```

---

#### `GET /fixed-income/projection/{asset_id}`
Calcula projeção de rendimento.

**Query Parameters:**
- `target_date` (opcional): Data alvo (default: vencimento)
- `current_index_rate` (opcional): Taxa do indexador (default: CDI 11.15%)

**Response:**
```json
{
  "asset_id": 5,
  "ticker": "CDB-XP-2026",
  "product_type": "CDB",
  "indexer": "CDI",
  "rate": 120.0,
  "issue_date": "2026-01-02",
  "maturity_date": "2027-01-02",
  "target_date": "2027-01-02",
  "principal": 10000.00,
  "gross_return": 1338.00,
  "gross_value": 11338.00,
  "days_invested": 365,
  "ir_rate": 0.175,
  "ir_amount": 234.15,
  "net_value": 11103.85,
  "net_return": 1103.85,
  "effective_rate_annual": 11.04
}
```

---

## Classificação de Ativos

A função `classify_asset()` em [importer.py](../backend/app/services/importer.py) determina automaticamente a classe do ativo:

### Regras de Classificação

```python
def classify_asset(ticker: str, product_name: str) -> tuple[str, str]:
    """
    Classifica um ativo baseado no ticker e nome do produto.
    
    Retorna: (asset_class, asset_type)
    """
```

| Condição | asset_class | asset_type |
|----------|-------------|------------|
| Ticker termina em `11` | FUNDO IMOBILIÁRIO | FII |
| Ticker inicia com ETF_ ou prefixos conhecidos | ETF | ETF |
| Produto contém CDB, LCI, LCA, etc. | RENDA FIXA | CDB/LCI/LCA/etc |
| Ticker termina em 3, 5, 7, 9 | AÇÕES | ON |
| Ticker termina em 4, 6, 8 | AÇÕES | PN |
| Outros | AÇÕES | ON (default) |

### Prefixos de ETF Reconhecidos

```python
ETF_PREFIXES = [
    "BOVA", "SMAL", "IVVB", "HASH", "DIVO", "FIND", 
    "GOVE", "ISUS", "PIBB", "BRAX", "ECOO", "MATB",
    "IMAB", "FIXA", "IRFM", "GOLD", "SPXI", "XBOV"
]
```

---

## Cálculo de IR Regressivo (Renda Fixa)

O imposto de renda para renda fixa segue a tabela regressiva:

| Dias Investidos | Alíquota |
|-----------------|----------|
| Até 180 dias | 22.5% |
| 181 a 360 dias | 20.0% |
| 361 a 720 dias | 17.5% |
| Acima de 720 dias | 15.0% |

**Isenções:**
- LCI (Letra de Crédito Imobiliário): Isento
- LCA (Letra de Crédito do Agronegócio): Isento

### Implementação

```python
def get_ir_rate(days: int, product_type: str) -> float:
    """Retorna a alíquota de IR baseada nos dias e tipo de produto."""
    
    # LCI e LCA são isentos
    if product_type.upper() in ["LCI", "LCA"]:
        return 0.0
    
    if days <= 180:
        return 0.225  # 22.5%
    elif days <= 360:
        return 0.20   # 20%
    elif days <= 720:
        return 0.175  # 17.5%
    else:
        return 0.15   # 15%
```

---

## Projeção de Rendimento

O cálculo de projeção suporta 4 indexadores:

### CDI (Certificado de Depósito Interbancário)

```
rendimento_bruto = principal * ((1 + taxa_cdi/100) ^ (dias/365) - 1) * (taxa_contratada/100)
```

### IPCA+ (Inflação + Taxa Prefixada)

```
rendimento_ipca = principal * ((1 + taxa_ipca/100) ^ (dias/365) - 1)
rendimento_prefixado = principal * (taxa_contratada/100) * (dias/365)
rendimento_bruto = rendimento_ipca + rendimento_prefixado
```

### PRE (Prefixado)

```
rendimento_bruto = principal * ((1 + taxa_contratada/100) ^ (dias/365) - 1)
```

### SELIC

```
rendimento_bruto = principal * ((1 + taxa_selic/100) ^ (dias/365) - 1) * (taxa_contratada/100)
```

---

## Banco de Dados

### Conexão

O sistema usa SQLite com WAL (Write-Ahead Logging) para melhor concorrência:

```python
def get_db():
    """Context manager para conexão com o banco."""
    conn = sqlite3.connect(
        DB_PATH, 
        timeout=30.0,
        check_same_thread=False
    )
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### Localização

O banco de dados é criado em: `/app/app/data/portfolio.db`

O diretório é criado automaticamente se não existir.

---

## Idempotência na Importação

A tabela `operations` possui uma constraint UNIQUE que garante que a mesma operação não seja importada duas vezes:

```sql
UNIQUE (trade_date, movement_type, market, institution, asset_id, quantity, price, source)
```

Quando há conflito, o registro é ignorado:

```python
cursor.execute("""
    INSERT INTO operations (...)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
""", values)
```

---

## Frontend — Interfaces TypeScript

### Asset

```typescript
interface Asset {
  id: number;
  ticker: string;
  asset_class: string;
  asset_type: string;
  product_name: string;
  created_at: string;
  status: string;
  total_bought: number;
  total_sold: number;
  current_position: number;
  avg_price: number;
  total_bought_value: number;
  total_sold_value: number;
}
```

### Operation

```typescript
interface Operation {
  id: number;
  asset_id: number;
  movement_type: 'COMPRA' | 'VENDA';
  quantity: number;
  price: number;
  value: number;
  trade_date: string;
  source: 'B3' | 'MANUAL';
  market?: string;
  institution?: string;
}
```

### FixedIncomeAsset

```typescript
interface FixedIncomeAsset {
  id: number;
  asset_id: number;
  ticker: string;
  product_name: string;
  issuer: string;
  product_type: string;
  indexer: 'CDI' | 'IPCA' | 'PRE' | 'SELIC';
  rate: number;
  maturity_date: string;
  issue_date: string;
  custody_fee: number;
  total_invested: number;
  total_redeemed: number;
  current_balance: number;
}
```

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | Caminho do banco SQLite | `/app/app/data/portfolio.db` |
| `CORS_ORIGINS` | Origens permitidas | `http://localhost:5173` |
| `API_PORT` | Porta da API | `8000` |

---

## Docker

### Desenvolvimento

```bash
docker-compose up --build
```

### Serviços

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `api` | 8000 | Backend FastAPI |
| `frontend` | 5173 | Frontend Vite (dev server) |

### Volumes

- `./backend/app/data:/app/app/data` — Persistência do banco de dados
