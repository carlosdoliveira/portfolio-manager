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

### 4. Criar Operação Manual

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

Para produção, configure a variável de ambiente `CORS_ORIGINS`:

```bash
CORS_ORIGINS=https://seu-dominio.com
```

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
  trade_date: string;        // "YYYY-MM-DD"
  movement_type: string;     // "COMPRA" | "VENDA"
  market: string;
  institution: string;
  ticker: string;
  quantity: number;          // integer > 0
  price: number;             // float > 0
}
```

### Operation (Response)

```typescript
interface Operation {
  id: number;
  trade_date: string;
  movement_type: string;
  market: string;
  institution: string;
  ticker: string;
  quantity: number;
  price: number;
  total_value: number;       // quantity * price
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
