# API Contracts: Wallets & Rebalancing

**Feature**: 001-wallet-rebalancing-recommendations  
**Base URL**: `/api/wallets`  
**Date**: 2026-02-22

## Table of Contents

1. [Wallet CRUD](#wallet-crud)
2. [Wallet Assets Management](#wallet-assets-management)
3. [Target Allocations](#target-allocations)
4. [Rebalancing Recommendations](#rebalancing-recommendations)

---

## Wallet CRUD

### `GET /api/wallets`

Lista todas as carteiras do usuário com métricas calculadas.

**Request**:
```http
GET /api/wallets HTTP/1.1
```

**Response 200 OK**:
```json
{
  "wallets": [
    {
      "id": 1,
      "name": "Principal",
      "type": "Mista",
      "total_value": 125000.50,
      "cost_basis": 100000.00,
      "profitability": 25.00,
      "num_assets": 12,
      "last_updated": "2026-02-22T14:30:00Z",
      "is_balanced": false,
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Aposentadoria",
      "type": "RF",
      "total_value": 50000.00,
      "cost_basis": 48000.00,
      "profitability": 4.17,
      "num_assets": 5,
      "last_updated": "2026-02-22T14:30:00Z",
      "is_balanced": true,
      "created_at": "2025-06-10T11:00:00Z"
    }
  ],
  "total_portfolio_value": 175000.50
}
```

**Response 500**:
```json
{
  "detail": "Erro ao calcular métricas das carteiras: [error message]"
}
```

---

### `GET /api/wallets/{id}`

Detalhes de uma carteira específica incluindo ativos e alocação atual.

**Request**:
```http
GET /api/wallets/1 HTTP/1.1
```

**Response 200 OK**:
```json
{
  "id": 1,
  "name": "Principal",
  "type": "Mista",
  "total_value": 125000.50,
  "cost_basis": 100000.00,
  "profitability": 25.00,
  "num_assets": 12,
  "last_updated": "2026-02-22T14:30:00Z",
  "is_balanced": false,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2026-02-20T16:45:00Z",
  "assets": [
    {
      "asset_id": 5,
      "ticker": "PETR4",
      "name": "Petrobras PN",
      "category": "Ações",
      "quantity": 200,
      "avg_price": 28.50,
      "current_price": 32.00,
      "current_value": 6400.00,
      "profitability": 12.28,
      "weight_in_wallet": 5.12
    }
  ],
  "allocation": {
    "categories": [
      {
        "category": "Ações",
        "current_value": 75000.00,
        "current_percent": 60.00,
        "target_percent": 50.00,
        "deviation": 10.00,
        "num_assets": 8
      },
      {
        "category": "FIIs",
        "current_value": 37500.00,
        "current_percent": 30.00,
        "target_percent": 30.00,
        "deviation": 0.00,
        "num_assets": 3
      },
      {
        "category": "RF",
        "current_value": 12500.50,
        "current_percent": 10.00,
        "target_percent": 20.00,
        "deviation": -10.00,
        "num_assets": 1
      }
    ]
  }
}
```

**Response 404**:
```json
{
  "detail": "Carteira não encontrada"
}
```

---

### `POST /api/wallets`

Cria nova carteira.

**Request**:
```http
POST /api/wallets HTTP/1.1
Content-Type: application/json

{
  "name": "Dividendos",
  "type": "Ações"
}
```

**Validation Rules**:
- `name`: Required, 3-50 chars, unique
- `type`: Required, must be one of: 'Ações', 'FIIs', 'RF', 'Mista'

**Response 201 Created**:
```json
{
  "id": 3,
  "name": "Dividendos",
  "type": "Ações",
  "total_value": 0.00,
  "cost_basis": 0.00,
  "profitability": 0.00,
  "num_assets": 0,
  "last_updated": null,
  "is_balanced": true,
  "created_at": "2026-02-22T14:35:00Z",
  "updated_at": "2026-02-22T14:35:00Z"
}
```

**Response 400 Bad Request**:
```json
{
  "detail": "Nome da carteira já existe"
}
```

**Response 422 Unprocessable Entity**:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "Nome deve ter entre 3 e 50 caracteres",
      "type": "value_error"
    }
  ]
}
```

---

### `PUT /api/wallets/{id}`

Atualiza nome ou tipo de carteira existente.

**Request**:
```http
PUT /api/wallets/3 HTTP/1.1
Content-Type: application/json

{
  "name": "Dividendos Premium",
  "type": "Mista"
}
```

**Response 200 OK**:
```json
{
  "id": 3,
  "name": "Dividendos Premium",
  "type": "Mista",
  "updated_at": "2026-02-22T14:40:00Z"
}
```

**Response 404**:
```json
{
  "detail": "Carteira não encontrada"
}
```

**Response 400**:
```json
{
  "detail": "Nome da carteira já existe em outra carteira"
}
```

---

### `DELETE /api/wallets/{id}`

Deleta carteira. **Não deleta ativos**, apenas remove atribuições.

**Request**:
```http
DELETE /api/wallets/3 HTTP/1.1
```

**Response 204 No Content**: (no body)

**Response 404**:
```json
{
  "detail": "Carteira não encontrada"
}
```

---

## Wallet Assets Management

### `POST /api/wallets/{id}/assets`

Atribui múltiplos ativos a uma carteira.

**Request**:
```http
POST /api/wallets/1/assets HTTP/1.1
Content-Type: application/json

{
  "asset_ids": [5, 7, 12],
  "weight_overrides": {
    "5": 30.0
  }
}
```

**Fields**:
- `asset_ids`: Array de IDs de ativos a adicionar
- `weight_overrides` (optional): Map de asset_id → peso customizado (0-100)

**Response 200 OK**:
```json
{
  "wallet_id": 1,
  "added_assets": 3,
  "skipped_duplicates": 0,
  "assets": [
    {"asset_id": 5, "ticker": "PETR4", "weight_override": 30.0},
    {"asset_id": 7, "ticker": "VALE3", "weight_override": null},
    {"asset_id": 12, "ticker": "ITSA4", "weight_override": null}
  ]
}
```

**Response 404**:
```json
{
  "detail": "Carteira não encontrada"
}
```

**Response 400**:
```json
{
  "detail": "Ativos não encontrados: [7, 12]"
}
```

---

### `DELETE /api/wallets/{wallet_id}/assets/{asset_id}`

Remove atribuição de ativo de uma carteira.

**Request**:
```http
DELETE /api/wallets/1/assets/5 HTTP/1.1
```

**Response 204 No Content**: (no body)

**Response 404**:
```json
{
  "detail": "Ativo não está atribuído a esta carteira"
}
```

---

## Target Allocations

### `GET /api/wallets/{id}/allocations/target`

Retorna alocações-alvo configuradas para a carteira.

**Request**:
```http
GET /api/wallets/1/allocations/target HTTP/1.1
```

**Response 200 OK**:
```json
{
  "wallet_id": 1,
  "target_allocations": [
    {"category": "Ações", "target_percent": 50.0},
    {"category": "FIIs", "target_percent": 30.0},
    {"category": "RF", "target_percent": 20.0}
  ],
  "total_percent": 100.0
}
```

**Response 404**:
```json
{
  "detail": "Carteira não encontrada"
}
```

---

### `PUT /api/wallets/{id}/allocations/target`

Define ou atualiza alocações-alvo de uma carteira.

**Request**:
```http
PUT /api/wallets/1/allocations/target HTTP/1.1
Content-Type: application/json

{
  "allocations": [
    {"category": "Ações", "target_percent": 60.0},
    {"category": "FIIs", "target_percent": 25.0},
    {"category": "RF", "target_percent": 15.0}
  ]
}
```

**Validation Rules**:
- `SUM(target_percent)` must equal 100.0
- Each `category` must be in: 'Ações', 'FIIs', 'RF', 'ETFs', 'Outros'
- `target_percent` must be >= 0 and <= 100

**Response 200 OK**:
```json
{
  "wallet_id": 1,
  "target_allocations": [
    {"category": "Ações", "target_percent": 60.0},
    {"category": "FIIs", "target_percent": 25.0},
    {"category": "RF", "target_percent": 15.0}
  ],
  "total_percent": 100.0,
  "updated_at": "2026-02-22T15:00:00Z"
}
```

**Response 400**:
```json
{
  "detail": "Soma das alocações deve ser 100%. Atual: 95.0%"
}
```

---

## Rebalancing Recommendations

### `GET /api/wallets/{id}/rebalancing`

Calcula e retorna recomendações de rebalanceamento **sob demanda** (não persistido).

**Request**:
```http
GET /api/wallets/1/rebalancing?threshold=5.0 HTTP/1.1
```

**Query Parameters**:
- `threshold` (optional, default=5.0): Desvio mínimo em pontos percentuais para gerar sugestões

**Response 200 OK**:
```json
{
  "wallet_id": 1,
  "generated_at": "2026-02-22T15:05:00Z",
  "is_balanced": false,
  "threshold_used": 5.0,
  "suggestions": [
    {
      "ticker": "PETR4",
      "action": "Vender",
      "quantity": 50,
      "estimated_price": 32.00,
      "estimated_value": 1600.00,
      "reason": "Categoria Ações está 10% acima do alvo (60% vs 50%)"
    },
    {
      "ticker": "HGLG11",
      "action": "Comprar",
      "quantity": 15,
      "estimated_price": 160.00,
      "estimated_value": 2400.00,
      "reason": "Categoria FIIs está OK, mas aumentar para balancear venda de Ações"
    },
    {
      "ticker": "CDB Banco X",
      "action": "Aportar",
      "quantity": null,
      "estimated_price": null,
      "estimated_value": 1200.00,
      "reason": "Categoria RF está 10% abaixo do alvo (10% vs 20%). Aportar em próximo investimento."
    }
  ],
  "estimated_costs": {
    "brokerage_fees": 30.00,
    "taxes": 0.08,
    "total": 30.08
  },
  "net_benefit": 1250.00,
  "is_recommended": true,
  "summary": "Carteira desbalanceada. Benefício líquido de R$ 1.250,00 após custos. Recomendado executar rebalanceamento."
}
```

**Response 200 OK (Balanced)**:
```json
{
  "wallet_id": 1,
  "generated_at": "2026-02-22T15:05:00Z",
  "is_balanced": true,
  "threshold_used": 5.0,
  "suggestions": [],
  "estimated_costs": {
    "brokerage_fees": 0.00,
    "taxes": 0.00,
    "total": 0.00
  },
  "net_benefit": 0.00,
  "is_recommended": false,
  "summary": "Carteira balanceada ✓. Próxima revisão recomendada em 3 meses."
}
```

**Response 404**:
```json
{
  "detail": "Carteira não encontrada"
}
```

**Response 400**:
```json
{
  "detail": "Carteira não possui alocação-alvo definida. Configure antes de solicitar rebalanceamento."
}
```

**Response 400**:
```json
{
  "detail": "Cotações desatualizadas (última atualização há 48 horas). Atualize cotações antes de calcular rebalanceamento."
}
```

---

## Error Handling

Todos os endpoints seguem padrão FastAPI:

**422 Unprocessable Entity** (validation errors):
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message in Portuguese",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Erro interno: [technical details]"
}
```

---

## Rate Limits & Performance

- `GET /api/wallets`: No limit, fast (< 500ms)
- `GET /api/wallets/{id}`: Cached 60s, < 1s
- `GET /api/wallets/{id}/rebalancing`: Heavy calculation, limit 1 req/min per wallet, < 3s
- All POST/PUT/DELETE: No limit

---

**Status**: ✅ Contracts Complete
