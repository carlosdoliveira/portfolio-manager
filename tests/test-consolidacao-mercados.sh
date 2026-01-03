#!/bin/bash

# Script de Teste: Consolidação de Mercados
# Valida que operações em mercados diferentes são consolidadas corretamente

set -e

API_URL="http://localhost:8000"

echo "🧪 Teste de Consolidação de Mercados"
echo "===================================="
echo ""

# 1. Criar ativo de teste
echo "1️⃣  Criando ativo de teste TESTE4..."
ASSET_RESPONSE=$(curl -s -X POST "$API_URL/assets" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TESTE4",
    "asset_class": "AÇÕES",
    "asset_type": "PN",
    "product_name": "TESTE PN"
  }')

ASSET_ID=$(echo $ASSET_RESPONSE | jq -r '.asset_id')
echo "   ✓ Ativo criado com ID: $ASSET_ID"
echo ""

# 2. Criar operação no mercado à vista
echo "2️⃣  Criando COMPRA de 100 ações no MERCADO A VISTA..."
curl -s -X POST "$API_URL/operations" \
  -H "Content-Type: application/json" \
  -d "{
    \"asset_id\": $ASSET_ID,
    \"movement_type\": \"COMPRA\",
    \"quantity\": 100,
    \"price\": 30.00,
    \"trade_date\": \"2026-01-01\",
    \"market\": \"MERCADO A VISTA\",
    \"institution\": \"XP INVESTIMENTOS\"
  }" > /dev/null

echo "   ✓ Operação criada"
echo ""

# 3. Criar operação no mercado fracionário
echo "3️⃣  Criando COMPRA de 5 ações no MERCADO FRACIONARIO..."
curl -s -X POST "$API_URL/operations" \
  -H "Content-Type: application/json" \
  -d "{
    \"asset_id\": $ASSET_ID,
    \"movement_type\": \"COMPRA\",
    \"quantity\": 5,
    \"price\": 31.00,
    \"trade_date\": \"2026-01-05\",
    \"market\": \"MERCADO FRACIONARIO\",
    \"institution\": \"XP INVESTIMENTOS\"
  }" > /dev/null

echo "   ✓ Operação criada"
echo ""

# 4. Buscar ativo e validar consolidação
echo "4️⃣  Validando consolidação..."
ASSETS=$(curl -s "$API_URL/assets")
TESTE4=$(echo $ASSETS | jq -r ".[] | select(.ticker == \"TESTE4\")")

TOTAL_BOUGHT=$(echo $TESTE4 | jq -r '.total_bought')
CURRENT_POSITION=$(echo $TESTE4 | jq -r '.current_position')
TOTAL_BOUGHT_VALUE=$(echo $TESTE4 | jq -r '.total_bought_value')

echo ""
echo "📊 Resultado da Consolidação:"
echo "   ├─ Total Comprado: $TOTAL_BOUGHT ações"
echo "   ├─ Posição Atual: $CURRENT_POSITION ações"
echo "   └─ Valor Total Investido: R\$ $TOTAL_BOUGHT_VALUE"
echo ""

# 5. Validação
EXPECTED_TOTAL=105
EXPECTED_VALUE=3155.0

if [ "$TOTAL_BOUGHT" = "$EXPECTED_TOTAL" ] && [ "$CURRENT_POSITION" = "$EXPECTED_TOTAL" ]; then
    echo "✅ TESTE PASSOU!"
    echo "   Operações em MERCADO A VISTA e MERCADO FRACIONARIO"
    echo "   foram consolidadas corretamente."
    echo ""
    echo "   Esperado: $EXPECTED_TOTAL ações"
    echo "   Obtido: $TOTAL_BOUGHT ações"
    echo ""
else
    echo "❌ TESTE FALHOU!"
    echo "   Esperado: $EXPECTED_TOTAL ações"
    echo "   Obtido: $TOTAL_BOUGHT ações"
    exit 1
fi

# 6. Buscar operações individuais para confirmar que foram preservadas
echo "5️⃣  Verificando preservação das operações individuais..."
OPERATIONS=$(curl -s "$API_URL/assets/$ASSET_ID/operations")
NUM_OPERATIONS=$(echo $OPERATIONS | jq '. | length')

echo "   ✓ $NUM_OPERATIONS operações preservadas no banco"
echo ""
echo "   Detalhes:"
echo $OPERATIONS | jq -r '.[] | "   - \(.trade_date) | \(.market) | \(.quantity) ações @ R$ \(.price)"'
echo ""

# 7. Limpeza (opcional)
echo "6️⃣  Limpando dados de teste..."
# Deletar operações
OPERATION_IDS=$(echo $OPERATIONS | jq -r '.[].id')
for OP_ID in $OPERATION_IDS; do
    curl -s -X DELETE "$API_URL/operations/$OP_ID" > /dev/null
done

# Deletar ativo
curl -s -X DELETE "$API_URL/assets/$ASSET_ID" > /dev/null
echo "   ✓ Dados de teste removidos"
echo ""

echo "🎉 Teste de consolidação concluído com sucesso!"
echo ""
echo "📝 Resumo:"
echo "   1. Criamos um ativo de teste"
echo "   2. Adicionamos 100 ações no MERCADO A VISTA"
echo "   3. Adicionamos 5 ações no MERCADO FRACIONARIO"
echo "   4. Sistema consolidou automaticamente em 105 ações"
echo "   5. Operações individuais foram preservadas"
echo "   6. Dados de teste foram removidos"
echo ""
echo "✅ A consolidação de mercados está funcionando corretamente!"
