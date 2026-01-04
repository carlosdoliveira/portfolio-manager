#!/bin/bash
#
# Reset Database - Portfolio Manager v2
#
# Este script deleta o banco de dados SQLite e o recria do zero.
# Útil para começar limpo após mudanças no schema ou lógica de importação.
#
# ATENÇÃO: Todos os dados serão perdidos!
#

set -e  # Exit on error

echo "================================================"
echo "  Portfolio Manager v2 - Reset Database"
echo "================================================"
echo ""
echo "⚠️  ATENÇÃO: Esta operação deletará TODOS os dados!"
echo "   Certifique-se de ter backup se houver dados importantes."
echo ""

# Verificar se usuário confirma
read -p "Deseja continuar? (sim/não): " -r
echo

if [[ ! $REPLY =~ ^[Ss](im|IM)?$ ]] && [[ ! $REPLY =~ ^[Yy](es|ES)?$ ]]; then
    echo "❌ Operação cancelada."
    exit 0
fi

echo "🔄 Parando containers..."
docker compose down

echo "🗑️  Removendo banco de dados antigo..."
if [ -d "backend/data" ]; then
    # Usar sudo porque arquivo pode ter sido criado pelo container (root)
    sudo rm -rf backend/data
    mkdir -p backend/data
    echo "✅ Banco deletado"
else
    mkdir -p backend/data
    echo "ℹ️  Nenhum banco encontrado"
fi

echo "🚀 Iniciando containers..."
docker compose up -d

echo ""
echo "⏳ Aguardando containers iniciarem..."
sleep 3

echo ""
echo "================================================"
echo "✅ BANCO RESETADO COM SUCESSO!"
echo "================================================"
echo ""
echo "O banco foi recriado do zero."
echo "Agora você pode:"
echo "  1. Importar seus arquivos B3 (com consolidação automática)"
echo "  2. Criar operações manualmente"
echo ""
echo "Acesse: http://localhost:5173"
echo ""
