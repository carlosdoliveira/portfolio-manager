#!/usr/bin/env python3
"""
Script de Migração: Consolidação de Tickers Fracionários

Este script consolida tickers fracionários (ex: ABEV3F) com seus
equivalentes do mercado à vista (ex: ABEV3), movendo todas as operações
para o ativo consolidado.

ATENÇÃO: Faça backup do banco de dados antes de executar!

Uso:
    python migrate_consolidate_tickers.py [--dry-run]
    
    --dry-run: Apenas mostra o que seria feito, sem modificar o banco
"""

import sqlite3
import sys
import os
from datetime import datetime

# Adicionar o diretório pai ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = "/app/app/data/portfolio.db"

def get_db_connection():
    """Cria conexão com o banco de dados."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado em: {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def find_fractional_tickers(conn):
    """
    Encontra todos os tickers fracionários (terminam com F).
    
    Returns:
        Lista de dicts com informações dos tickers fracionários
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id,
            ticker,
            asset_class,
            asset_type,
            product_name,
            status,
            (SELECT COUNT(*) FROM operations WHERE asset_id = assets.id AND status = 'ACTIVE') as op_count
        FROM assets
        WHERE ticker LIKE '%F' 
          AND status = 'ACTIVE'
          AND asset_class = 'AÇÕES'
        ORDER BY ticker
    """)
    
    return [dict(row) for row in cursor.fetchall()]

def find_or_create_consolidated_asset(conn, fractional_asset, dry_run=False):
    """
    Encontra ou cria o ativo consolidado (sem F).
    
    Args:
        conn: Conexão com banco
        fractional_asset: Dict com dados do ativo fracionário
        dry_run: Se True, não cria o ativo, apenas simula
    
    Returns:
        ID do ativo consolidado
    """
    ticker_fractional = fractional_asset['ticker']
    ticker_consolidated = ticker_fractional[:-1]  # Remove o F
    
    cursor = conn.cursor()
    
    # Verificar se ativo consolidado já existe
    cursor.execute("""
        SELECT id, ticker, asset_class, asset_type, product_name
        FROM assets
        WHERE ticker = ? AND status = 'ACTIVE'
    """, (ticker_consolidated,))
    
    existing = cursor.fetchone()
    
    if existing:
        print(f"  ✅ Ativo consolidado já existe: {ticker_consolidated} (ID: {existing['id']})")
        return existing['id']
    
    # Criar novo ativo consolidado
    if dry_run:
        print(f"  🔍 [DRY-RUN] Criaria ativo: {ticker_consolidated}")
        return -1  # ID fake para dry-run
    
    cursor.execute("""
        INSERT INTO assets (ticker, asset_class, asset_type, product_name, created_at, status)
        VALUES (?, ?, ?, ?, ?, 'ACTIVE')
    """, (
        ticker_consolidated,
        fractional_asset['asset_class'],
        fractional_asset['asset_type'],
        fractional_asset['product_name'].replace('F', ''),  # Remove F do nome também
        datetime.utcnow().isoformat()
    ))
    
    new_id = cursor.lastrowid
    print(f"  ✨ Ativo consolidado criado: {ticker_consolidated} (ID: {new_id})")
    return new_id

def migrate_operations(conn, fractional_asset_id, consolidated_asset_id, dry_run=False):
    """
    Move todas as operações do ativo fracionário para o consolidado.
    
    Args:
        conn: Conexão com banco
        fractional_asset_id: ID do ativo fracionário
        consolidated_asset_id: ID do ativo consolidado
        dry_run: Se True, não faz as mudanças
    
    Returns:
        Número de operações migradas
    """
    cursor = conn.cursor()
    
    # Contar operações a migrar
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM operations
        WHERE asset_id = ? AND status = 'ACTIVE'
    """, (fractional_asset_id,))
    
    count = cursor.fetchone()['count']
    
    if count == 0:
        print(f"  ℹ️  Nenhuma operação para migrar")
        return 0
    
    if dry_run:
        print(f"  🔍 [DRY-RUN] Migraria {count} operações")
        return count
    
    # Migrar operações
    cursor.execute("""
        UPDATE operations
        SET asset_id = ?
        WHERE asset_id = ? AND status = 'ACTIVE'
    """, (consolidated_asset_id, fractional_asset_id))
    
    print(f"  ✅ {count} operações migradas")
    return count

def soft_delete_fractional_asset(conn, fractional_asset_id, dry_run=False):
    """
    Marca o ativo fracionário como DELETED (soft delete).
    
    Args:
        conn: Conexão com banco
        fractional_asset_id: ID do ativo fracionário
        dry_run: Se True, não faz a mudança
    """
    if dry_run:
        print(f"  🔍 [DRY-RUN] Marcaria ativo {fractional_asset_id} como DELETED")
        return
    
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE assets
        SET status = 'DELETED'
        WHERE id = ?
    """, (fractional_asset_id,))
    
    print(f"  🗑️  Ativo fracionário marcado como DELETED")

def main():
    """Função principal de migração."""
    dry_run = "--dry-run" in sys.argv
    
    print("=" * 70)
    print("🔄 MIGRAÇÃO: Consolidação de Tickers Fracionários")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  MODO DRY-RUN: Nenhuma alteração será feita no banco\n")
    else:
        print("\n⚠️  ATENÇÃO: Esta operação modificará o banco de dados!")
        print("   Certifique-se de ter um backup antes de continuar.\n")
        
        resposta = input("Deseja continuar? (sim/não): ").strip().lower()
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada pelo usuário")
            sys.exit(0)
    
    print()
    
    # Conectar ao banco
    conn = get_db_connection()
    
    try:
        # Encontrar tickers fracionários
        fractional_tickers = find_fractional_tickers(conn)
        
        if not fractional_tickers:
            print("✅ Nenhum ticker fracionário encontrado. Nada a fazer!")
            return
        
        print(f"📊 Encontrados {len(fractional_tickers)} tickers fracionários:\n")
        
        total_operations = 0
        
        # Processar cada ticker fracionário
        for frac_asset in fractional_tickers:
            print(f"🔹 Processando: {frac_asset['ticker']} (ID: {frac_asset['id']})")
            print(f"   Operações ativas: {frac_asset['op_count']}")
            
            # Encontrar ou criar ativo consolidado
            consol_asset_id = find_or_create_consolidated_asset(conn, frac_asset, dry_run)
            
            # Migrar operações
            migrated = migrate_operations(conn, frac_asset['id'], consol_asset_id, dry_run)
            total_operations += migrated
            
            # Soft delete do ativo fracionário
            soft_delete_fractional_asset(conn, frac_asset['id'], dry_run)
            
            print()
        
        # Commit das mudanças
        if not dry_run:
            conn.commit()
            print("=" * 70)
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"   • {len(fractional_tickers)} ativos consolidados")
            print(f"   • {total_operations} operações migradas")
            print("=" * 70)
        else:
            print("=" * 70)
            print("🔍 DRY-RUN COMPLETO - Nenhuma alteração foi feita")
            print(f"   • {len(fractional_tickers)} ativos seriam consolidados")
            print(f"   • {total_operations} operações seriam migradas")
            print("=" * 70)
            print("\nPara executar de verdade, rode sem --dry-run:")
            print("  python migrate_consolidate_tickers.py")
    
    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        if not dry_run:
            conn.rollback()
            print("   Rollback executado - banco não foi alterado")
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
