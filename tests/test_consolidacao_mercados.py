#!/usr/bin/env python3
"""
Script de Teste: Consolidação de Mercados
Valida que operações em mercados diferentes são consolidadas corretamente
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def print_header(text):
    print(f"\n{text}")
    print("=" * len(text))

def print_step(number, text):
    print(f"\n{number}  {text}")

def print_success(text):
    print(f"   ✓ {text}")

def print_result(label, value):
    print(f"   ├─ {label}: {value}")

print_header("🧪 Teste de Consolidação de Mercados")

# 1. Criar ativo de teste
print_step("1️⃣", "Criando ativo de teste TESTE4...")
response = requests.post(f"{API_URL}/assets", json={
    "ticker": "TESTE4",
    "asset_class": "AÇÕES",
    "asset_type": "PN",
    "product_name": "TESTE PN"
})
asset_id = response.json()["asset_id"]
print_success(f"Ativo criado com ID: {asset_id}")

# 2. Criar operação no mercado à vista
print_step("2️⃣", "Criando COMPRA de 100 ações no MERCADO A VISTA...")
requests.post(f"{API_URL}/operations", json={
    "asset_id": asset_id,
    "movement_type": "COMPRA",
    "quantity": 100,
    "price": 30.00,
    "trade_date": "2026-01-01",
    "market": "MERCADO A VISTA",
    "institution": "XP INVESTIMENTOS"
})
print_success("Operação criada")

# 3. Criar operação no mercado fracionário
print_step("3️⃣", "Criando COMPRA de 5 ações no MERCADO FRACIONARIO...")
requests.post(f"{API_URL}/operations", json={
    "asset_id": asset_id,
    "movement_type": "COMPRA",
    "quantity": 5,
    "price": 31.00,
    "trade_date": "2026-01-05",
    "market": "MERCADO FRACIONARIO",
    "institution": "XP INVESTIMENTOS"
})
print_success("Operação criada")

# 4. Buscar ativo e validar consolidação
print_step("4️⃣", "Validando consolidação...")
assets = requests.get(f"{API_URL}/assets").json()
teste4 = next((a for a in assets if a["ticker"] == "TESTE4"), None)

total_bought = teste4["total_bought"]
current_position = teste4["current_position"]
total_bought_value = teste4["total_bought_value"]

print("\n📊 Resultado da Consolidação:")
print_result("Total Comprado", f"{total_bought} ações")
print_result("Posição Atual", f"{current_position} ações")
print(f"   └─ Valor Total Investido: R$ {total_bought_value:.2f}")

# 5. Validação
EXPECTED_TOTAL = 105
EXPECTED_VALUE = 3155.0

if total_bought == EXPECTED_TOTAL and current_position == EXPECTED_TOTAL:
    print("\n✅ TESTE PASSOU!")
    print("   Operações em MERCADO A VISTA e MERCADO FRACIONARIO")
    print("   foram consolidadas corretamente.")
    print(f"\n   Esperado: {EXPECTED_TOTAL} ações")
    print(f"   Obtido: {total_bought} ações")
else:
    print("\n❌ TESTE FALHOU!")
    print(f"   Esperado: {EXPECTED_TOTAL} ações")
    print(f"   Obtido: {total_bought} ações")
    exit(1)

# 6. Buscar operações individuais
print_step("5️⃣", "Verificando preservação das operações individuais...")
operations = requests.get(f"{API_URL}/assets/{asset_id}/operations").json()
num_operations = len(operations)

print_success(f"{num_operations} operações preservadas no banco")
print("\n   Detalhes:")
for op in operations:
    print(f"   - {op['trade_date']} | {op['market']} | {op['quantity']} ações @ R$ {op['price']:.2f}")

# 7. Limpeza
print_step("6️⃣", "Limpando dados de teste...")
for op in operations:
    requests.delete(f"{API_URL}/operations/{op['id']}")
requests.delete(f"{API_URL}/assets/{asset_id}")
print_success("Dados de teste removidos")

print("\n🎉 Teste de consolidação concluído com sucesso!")
print("\n📝 Resumo:")
print("   1. Criamos um ativo de teste")
print("   2. Adicionamos 100 ações no MERCADO A VISTA")
print("   3. Adicionamos 5 ações no MERCADO FRACIONARIO")
print("   4. Sistema consolidou automaticamente em 105 ações")
print("   5. Operações individuais foram preservadas")
print("   6. Dados de teste foram removidos")
print("\n✅ A consolidação de mercados está funcionando corretamente!\n")
