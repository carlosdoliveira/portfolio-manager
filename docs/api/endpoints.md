# API Reference — Portfolio Manager v2

Documentação completa dos endpoints da API REST do Portfolio Manager v2.

---

## 🔗 Base URL

```
http://localhost:8000
```

**Produção:** A definir

---

## 📋 Endpoints

### 1. Health Check

**GET** `/`

Verifica se a API está online.

#### Response

```json
{
  "message": "Portfolio Manager API — Running"
}
```

#### Status Codes

- `200 OK` — API está funcionando

#### Exemplo

```bash
curl http://localhost:8000/
```

---

### 2. Importar Arquivo B3

**POST** `/import/b3`

Importa um arquivo Excel de negociações da B3.

#### Request

**Content-Type:** `multipart/form-data`

**Body:**
- `file` (File, required): Arquivo Excel da B3 (`.xlsx`)

#### Response

```json
{
  "message": "Importação concluída",
  "summary": {
    "total_rows": 167,
    "inserted": 100,
    "duplicated": 67,
    "unique_assets": 15,
    "imported_at": "2026-01-02T15:30:00"
  }
}
```

#### Status Codes

- `200 OK` — Importação bem-sucedida
- `400 Bad Request` — Arquivo inválido ou formato incorreto
- `500 Internal Server Error` — Erro ao processar arquivo

#### Erros Possíveis

```json
{
  "detail": "Erro ao processar arquivo: arquivo não é um Excel válido"
}
```

```json
{
  "detail": "Erro ao importar: colunas obrigatórias não encontradas"
}
```

#### Exemplo

```bash
curl -X POST http://localhost:8000/import/b3 \
  -F "file=@negociacao-2025-12-31.xlsx"
```

**JavaScript:**

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("http://localhost:8000/import/b3", {
  method: "POST",
  body: formData,
});

const result = await response.json();
console.log(result.summary);
```

---

### 3. Listar Operações

**GET** `/operations`

Retorna todas as operações importadas.

#### Response

```json
[
  {
    "id": 1,
    "trade_date": "2025-12-31",
    "movement_type": "COMPRA",
    "market": "MERCADO A VISTA",
    "institution": "CORRETORA XP",
    "ticker": "PETR4",
    "quantity": 100,
    "price": 30.50,
    "total_value": 3050.00
  },
  {
    "id": 2,
    "trade_date": "2026-01-05",
    "movement_type": "VENDA",
    "market": "MERCADO A VISTA",
    "institution": "CORRETORA XP",
    "ticker": "PETR4",
    "quantity": 50,
    "price": 32.00,
    "total_value": 1600.00
  }
]
```

#### Query Parameters

**Futuros (não implementados ainda):**
- `ticker` (string): Filtrar por ticker
- `movement_type` (string): `COMPRA` ou `VENDA`
- `start_date` (date): Data inicial
- `end_date` (date): Data final
- `limit` (int): Limitar número de resultados
- `offset` (int): Paginação

#### Status Codes

- `200 OK` — Lista retornada com sucesso
- `500 Internal Server Error` — Erro ao buscar operações

#### Exemplo

```bash
curl http://localhost:8000/operations
```

**JavaScript:**

```javascript
const response = await fetch("http://localhost:8000/operations");
const operations = await response.json();
console.log(operations);
```

---

### 4. Buscar Operação por ID

**GET** `/operations/{operation_id}`

Retorna uma operação específica por ID.

#### Path Parameters

- `operation_id` (integer, required): ID da operação

#### Response

```json
{
  "id": 1,
  "trade_date": "2025-12-31",
  "movement_type": "COMPRA",
  "market": "MERCADO A VISTA",
  "institution": "CORRETORA XP",
  "ticker": "PETR4",
  "quantity": 100,
  "price": 30.50,
  "total_value": 3050.00,
  "status": "ACTIVE",
  "asset_class": "Renda Variável",
  "asset_type": "Ações",
  "product_name": "Petrobras PN",
  "source": "MANUAL",
  "created_at": "2026-01-02T15:00:00"
}
```

#### Status Codes

- `200 OK` — Operação encontrada
- `404 Not Found` — Operação não encontrada
- `500 Internal Server Error` — Erro ao buscar operação

#### Exemplo

```bash
curl http://localhost:8000/operations/1
```

**JavaScript:**

```javascript
const response = await fetch("http://localhost:8000/operations/1");
const operation = await response.json();
console.log(operation);
```

---

### 5. Criar Operação Manual

**POST** `/operations`

Cria uma nova operação manualmente (não via importação).

#### Request

**Content-Type:** `application/json`

**Body:**

```json
{
  "trade_date": "2026-01-10",
  "movement_type": "COMPRA",
  "market": "MERCADO A VISTA",
  "institution": "CORRETORA EXEMPLO",
  "ticker": "VALE3",
  "quantity": 200,
  "price": 60.75
}
```

#### Validação

- `trade_date`: String no formato `YYYY-MM-DD`
- `movement_type`: `"COMPRA"` ou `"VENDA"` (obrigatório)
- `market`: String (obrigatório)
- `institution`: String (obrigatório)
- `ticker`: String (obrigatório)
- `quantity`: Integer > 0 (obrigatório)
- `price`: Float > 0 (obrigatório)

#### Response

```json
{
  "id": 168,
  "trade_date": "2026-01-10",
  "movement_type": "COMPRA",
  "market": "MERCADO A VISTA",
  "institution": "CORRETORA EXEMPLO",
  "ticker": "VALE3",
  "quantity": 200,
  "price": 60.75,
  "total_value": 12150.00
}
```

#### Status Codes

- `201 Created` — Operação criada com sucesso
- `400 Bad Request` — Dados inválidos
- `409 Conflict` — Operação duplicada
- `500 Internal Server Error` — Erro ao criar operação

#### Erros Possíveis

```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

```json
{
  "detail": "Operação duplicada"
}
```

#### Exemplo

```bash
curl -X POST http://localhost:8000/operations \
  -H "Content-Type: application/json" \
  -d '{
    "trade_date": "2026-01-10",
    "movement_type": "COMPRA",
    "market": "MERCADO A VISTA",
    "institution": "CORRETORA EXEMPLO",
    "ticker": "VALE3",
    "quantity": 200,
    "price": 60.75
  }'
```

**JavaScript:**

```javascript
const operation = {
  trade_date: "2026-01-10",
  movement_type: "COMPRA",
  market: "MERCADO A VISTA",
  institution: "CORRETORA EXEMPLO",
  ticker: "VALE3",
  quantity: 200,
  price: 60.75,
};

const response = await fetch("http://localhost:8000/operations", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(operation),
});

const result = await response.json();
console.log(result);
```

---

### 6. Atualizar Operação

**PUT** `/operations/{operation_id}`

Atualiza uma operação existente seguindo o princípio de imutabilidade:
1. Marca a operação antiga como `CANCELLED`
2. Cria uma nova operação com os dados atualizados

**Importante:** Esta abordagem preserva o histórico completo e a auditoria.

#### Path Parameters

- `operation_id` (integer, required): ID da operação a ser atualizada

#### Request

**Content-Type:** `application/json`

**Body:**

```json
{
  "trade_date": "2026-01-10",
  "movement_type": "COMPRA",
  "market": "MERCADO A VISTA",
  "institution": "CORRETORA EXEMPLO",
  "ticker": "VALE3",
  "quantity": 250,
  "price": 62.00
}
```

#### Response

```json
{
  "status": "success",
  "message": "Operação atualizada com sucesso",
  "old_id": 1,
  "new_id": 2
}
```

#### Status Codes

- `200 OK` — Operação atualizada com sucesso
- `400 Bad Request` — Dados inválidos ou operação não está ativa
- `404 Not Found` — Operação não encontrada
- `500 Internal Server Error` — Erro ao atualizar operação

#### Erros Possíveis

```json
{
  "detail": "Operação 1 não encontrada"
}
```

```json
{
  "detail": "Operação 1 não está ativa (status: CANCELLED)"
}
```

#### Exemplo

```bash
curl -X PUT http://localhost:8000/operations/1 \
  -H "Content-Type: application/json" \
  -d '{
    "trade_date":"2026-01-10",
    "movement_type":"COMPRA",
    "market":"MERCADO A VISTA",
    "institution":"TESTE",
    "ticker":"VALE3",
    "quantity":250,
    "price":62.00
  }'
```

**JavaScript:**

```javascript
const updatedOperation = {
  trade_date: "2026-01-10",
  movement_type: "COMPRA",
  market: "MERCADO A VISTA",
  institution: "TESTE",
  ticker: "VALE3",
  quantity: 250,
  price: 62.00,
};

const response = await fetch("http://localhost:8000/operations/1", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(updatedOperation),
});

const result = await response.json();
console.log(result); // { old_id: 1, new_id: 2, ... }
```

---

### 7. Deletar Operação

**DELETE** `/operations/{operation_id}`

Realiza soft delete de uma operação, marcando-a como `DELETED` ao invés de removê-la do banco.

**Importante:** A operação não é removida fisicamente, preservando auditoria.

#### Path Parameters

- `operation_id` (integer, required): ID da operação a ser deletada

#### Response

```json
{
  "status": "success",
  "message": "Operação deletada com sucesso",
  "deleted_id": 1
}
```

#### Status Codes

- `200 OK` — Operação deletada com sucesso
- `400 Bad Request` — Operação não está ativa
- `404 Not Found` — Operação não encontrada
- `500 Internal Server Error` — Erro ao deletar operação

#### Erros Possíveis

```json
{
  "detail": "Operação 1 não encontrada"
}
```

```json
{
  "detail": "Operação 1 não está ativa (status: DELETED)"
}
```

#### Exemplo

```bash
curl -X DELETE http://localhost:8000/operations/1
```

**JavaScript:**

```javascript
const response = await fetch("http://localhost:8000/operations/1", {
  method: "DELETE",
});

const result = await response.json();
console.log(result); // { status: "success", deleted_id: 1, ... }
```

---

## 🔒 Autenticação

**Status:** Não implementada ainda.

**Futura implementação:**
- JWT tokens
- OAuth 2.0 (Google, GitHub)

---

## ⚠️ CORS

A API está configurada para aceitar requisições de:

```
http://localhost:5173
```

**Métodos HTTP permitidos:**
- GET
- POST
- PUT
- DELETE

Para produção, configure a variável de ambiente `CORS_ORIGINS`:

```bash
CORS_ORIGINS=https://seu-dominio.com,https://app.seu-dominio.com
```

**Nota:** Múltiplas origens devem ser separadas por vírgula.

---

## 📊 Rate Limiting

**Status:** Não implementado ainda.

**Planejado:**
- 100 requisições por minuto por IP
- 1000 requisições por hora por IP

---

## 🧪 Testando a API

### Usando cURL

```bash
# Health check
curl http://localhost:8000/

# Listar operações
curl http://localhost:8000/operations

# Criar operação
curl -X POST http://localhost:8000/operations \
  -H "Content-Type: application/json" \
  -d '{"trade_date":"2026-01-10","movement_type":"COMPRA","market":"MERCADO A VISTA","institution":"TESTE","ticker":"PETR4","quantity":100,"price":30.50}'
```

### Usando Postman

1. Importar collection (disponível em breve)
2. Configurar `baseUrl` para `http://localhost:8000`
3. Executar requests

### Usando Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/")
print(response.json())

# Listar operações
response = requests.get("http://localhost:8000/operations")
print(response.json())

# Criar operação
operation = {
    "trade_date": "2026-01-10",
    "movement_type": "COMPRA",
    "market": "MERCADO A VISTA",
    "institution": "TESTE",
    "ticker": "VALE3",
    "quantity": 100,
    "price": 60.50
}
response = requests.post("http://localhost:8000/operations", json=operation)
print(response.json())
```

---

## 📝 Schemas de Dados

### OperationCreate (Request)

```typescript
interface OperationCreate {
  asset_class: string;       // "Renda Variável", "Renda Fixa", etc.
  asset_type: string;        // "Ações", "Debêntures", etc.
  product_name: string;      // Nome completo do produto
  ticker?: string | null;    // Código de negociação (opcional)
  trade_date: string;        // "YYYY-MM-DD"
  movement_type: string;     // "COMPRA" | "VENDA"
  quantity: number;          // integer > 0
  price: number;             // float > 0
  market?: string | null;    // "MERCADO A VISTA", etc. (opcional)
  institution?: string | null; // Nome da corretora (opcional)
}
```

### Operation (Response)

```typescript
interface Operation {
  id: number;
  asset_class: string;
  asset_type: string;
  product_name: string;
  ticker: string | null;
  trade_date: string;
  movement_type: string;
  quantity: number;
  price: number;
  value: number;             // quantity * price (calculado)
  status: string;            // "ACTIVE" | "CANCELLED" | "DELETED"
  source: string;            // "MANUAL" | "B3_IMPORT"
  created_at: string;        // ISO 8601 timestamp
  market: string | null;
  institution: string | null;
}
```

### ImportSummary

```typescript
interface ImportSummary {
  total_rows: number;
  inserted: number;
  duplicated: number;
  unique_assets: number;
  imported_at: string;       // ISO 8601 timestamp
}
```

---

## 🚧 Endpoints Futuros

### Análise de Carteira

```
GET /portfolio/summary
GET /portfolio/positions
GET /portfolio/pl
```

### Estatísticas

```
GET /analytics/performance
GET /analytics/distribution
```

### Configurações

```
GET /settings
PUT /settings
```

---

## 📚 Documentação Interativa

Acesse a documentação interativa gerada pelo FastAPI:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🆘 Suporte

Para dúvidas ou problemas:

1. Consulte a [documentação completa](../README.md)
2. Veja [exemplos de uso](../guides/)
3. Abra uma issue no GitHub
