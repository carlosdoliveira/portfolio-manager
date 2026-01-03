"""
Testes de Integração: Consolidação Fracionário/Vista no Import B3

Valida que a importação de arquivos B3 consolida corretamente
operações de mercado fracionário e à vista no mesmo ativo.
"""

import pytest
import pandas as pd
import sqlite3
import tempfile
import os
from datetime import datetime
from io import BytesIO
from app.services.importer import import_b3_excel, normalize_ticker
from app.db.database import get_db


@pytest.fixture
def temp_db():
    """Cria banco de dados temporário para testes."""
    # Criar arquivo temporário
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Configurar path temporário
    original_db_path = os.environ.get('DB_PATH')
    os.environ['DB_PATH'] = path
    
    # Criar schema
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            asset_class TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            trade_date TEXT NOT NULL,
            movement_type TEXT NOT NULL,
            market TEXT,
            institution TEXT,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            value REAL NOT NULL,
            created_at TEXT NOT NULL,
            source TEXT DEFAULT 'MANUAL',
            status TEXT DEFAULT 'ACTIVE',
            FOREIGN KEY (asset_id) REFERENCES assets(id),
            UNIQUE(asset_id, trade_date, movement_type, market, institution, quantity, price)
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    if original_db_path:
        os.environ['DB_PATH'] = original_db_path
    else:
        os.environ.pop('DB_PATH', None)
    
    try:
        os.unlink(path)
    except:
        pass


def create_b3_excel_mock(operations):
    """
    Cria um arquivo Excel mock no formato B3.
    
    Args:
        operations: Lista de dicts com dados das operações
    
    Returns:
        BytesIO com arquivo Excel
    """
    df = pd.DataFrame(operations)
    
    # Garantir que tem todas as colunas necessárias
    required_cols = [
        "Data do Negócio",
        "Tipo de Movimentação",
        "Mercado",
        "Instituição",
        "Código de Negociação",
        "Quantidade",
        "Preço",
        "Valor"
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
    
    # Converter para Excel
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    
    return buffer


class MockFile:
    """Mock de arquivo para simular upload."""
    def __init__(self, buffer, filename="test.xlsx"):
        self.file = buffer
        self.filename = filename


def test_normalize_ticker_removes_f_from_fractional():
    """Testa que normalize_ticker remove F de tickers fracionários."""
    result = normalize_ticker("ABEV3F", "MERCADO FRACIONARIO")
    assert result == "ABEV3"


def test_normalize_ticker_keeps_vista_unchanged():
    """Testa que normalize_ticker não altera tickers do mercado à vista."""
    result = normalize_ticker("ABEV3", "MERCADO A VISTA")
    assert result == "ABEV3"


def test_import_consolidates_fractional_and_vista(temp_db):
    """
    Testa que importação consolida operações de mercado fracionário e à vista
    no mesmo ativo.
    """
    # Configurar DB path
    import app.db.database as db_module
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db
    
    try:
        # Criar operações de teste: vista + fracionário do mesmo ativo
        operations = [
            {
                "Data do Negócio": "01/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO A VISTA",
                "Instituição": "CLEAR",
                "Código de Negociação": "ABEV3",
                "Quantidade": 100,
                "Preço": 15.00,
                "Valor": 1500.00
            },
            {
                "Data do Negócio": "02/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO FRACIONARIO",
                "Instituição": "CLEAR",
                "Código de Negociação": "ABEV3F",
                "Quantidade": 20,
                "Preço": 15.50,
                "Valor": 310.00
            }
        ]
        
        # Criar arquivo Excel mock
        excel_file = create_b3_excel_mock(operations)
        mock_file = MockFile(excel_file, "test_consolidacao.xlsx")
        
        # Importar
        result = import_b3_excel(mock_file)
        
        # Validações
        assert result["inserted"] == 2, "Deveria inserir 2 operações"
        assert result["duplicated"] == 0, "Não deveria ter duplicatas"
        
        # Verificar que foi criado apenas 1 ativo (ABEV3)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT ticker, asset_class FROM assets WHERE status = 'ACTIVE'")
        assets = cursor.fetchall()
        
        assert len(assets) == 1, f"Deveria ter apenas 1 ativo consolidado, mas tem {len(assets)}: {assets}"
        assert assets[0][0] == "ABEV3", f"Ticker deveria ser ABEV3, mas é {assets[0][0]}"
        assert assets[0][1] == "AÇÕES", f"Asset class deveria ser AÇÕES, mas é {assets[0][1]}"
        
        # Verificar que ambas operações estão vinculadas ao mesmo asset_id
        cursor.execute("""
            SELECT o.id, o.quantity, o.price, o.market, a.ticker
            FROM operations o
            JOIN assets a ON o.asset_id = a.id
            WHERE o.status = 'ACTIVE'
            ORDER BY o.trade_date
        """)
        ops = cursor.fetchall()
        
        assert len(ops) == 2, f"Deveria ter 2 operações, mas tem {len(ops)}"
        
        # Primeira operação (vista)
        assert ops[0][1] == 100, "Quantidade da primeira operação deveria ser 100"
        assert ops[0][3] == "MERCADO A VISTA", "Mercado deveria ser preservado"
        assert ops[0][4] == "ABEV3", "Ticker do ativo deveria ser ABEV3"
        
        # Segunda operação (fracionário)
        assert ops[1][1] == 20, "Quantidade da segunda operação deveria ser 20"
        assert ops[1][3] == "MERCADO FRACIONARIO", "Mercado deveria ser preservado"
        assert ops[1][4] == "ABEV3", "Ticker do ativo deveria ser ABEV3 (consolidado)"
        
        conn.close()
        
    finally:
        # Restaurar DB path original
        db_module.DB_PATH = original_db_path


def test_import_multiple_assets_with_fractional(temp_db):
    """
    Testa importação de múltiplos ativos, alguns com fracionário e outros não.
    """
    import app.db.database as db_module
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db
    
    try:
        operations = [
            # ABEV3 - Vista
            {
                "Data do Negócio": "01/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO A VISTA",
                "Instituição": "CLEAR",
                "Código de Negociação": "ABEV3",
                "Quantidade": 100,
                "Preço": 15.00,
                "Valor": 1500.00
            },
            # ABEV3F - Fracionário (deve consolidar com ABEV3)
            {
                "Data do Negócio": "02/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO FRACIONARIO",
                "Instituição": "CLEAR",
                "Código de Negociação": "ABEV3F",
                "Quantidade": 20,
                "Preço": 15.50,
                "Valor": 310.00
            },
            # PETR4 - Vista (sem fracionário)
            {
                "Data do Negócio": "03/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO A VISTA",
                "Instituição": "CLEAR",
                "Código de Negociação": "PETR4",
                "Quantidade": 50,
                "Preço": 30.00,
                "Valor": 1500.00
            },
            # VALE3F - Apenas fracionário (deve criar VALE3)
            {
                "Data do Negócio": "04/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO FRACIONARIO",
                "Instituição": "CLEAR",
                "Código de Negociação": "VALE3F",
                "Quantidade": 15,
                "Preço": 60.00,
                "Valor": 900.00
            }
        ]
        
        excel_file = create_b3_excel_mock(operations)
        mock_file = MockFile(excel_file, "test_multiplos.xlsx")
        
        result = import_b3_excel(mock_file)
        
        assert result["inserted"] == 4, "Deveria inserir 4 operações"
        
        # Verificar ativos criados
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT ticker FROM assets WHERE status = 'ACTIVE' ORDER BY ticker")
        assets = [row[0] for row in cursor.fetchall()]
        
        # Deve ter apenas 3 ativos: ABEV3, PETR4, VALE3 (sem F)
        assert len(assets) == 3, f"Deveria ter 3 ativos, mas tem {len(assets)}: {assets}"
        assert "ABEV3" in assets, "Deveria ter ABEV3"
        assert "PETR4" in assets, "Deveria ter PETR4"
        assert "VALE3" in assets, "Deveria ter VALE3"
        assert "ABEV3F" not in assets, "NÃO deveria ter ABEV3F (consolidado)"
        assert "VALE3F" not in assets, "NÃO deveria ter VALE3F (consolidado)"
        
        # Verificar contagem de operações por ativo
        cursor.execute("""
            SELECT a.ticker, COUNT(o.id) as op_count
            FROM assets a
            LEFT JOIN operations o ON a.id = o.asset_id
            WHERE a.status = 'ACTIVE'
            GROUP BY a.ticker
            ORDER BY a.ticker
        """)
        counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        assert counts["ABEV3"] == 2, f"ABEV3 deveria ter 2 operações (vista + fracionário), mas tem {counts['ABEV3']}"
        assert counts["PETR4"] == 1, f"PETR4 deveria ter 1 operação, mas tem {counts['PETR4']}"
        assert counts["VALE3"] == 1, f"VALE3 deveria ter 1 operação, mas tem {counts['VALE3']}"
        
        conn.close()
        
    finally:
        db_module.DB_PATH = original_db_path


def test_import_does_not_affect_fiis(temp_db):
    """
    Testa que FIIs com F no nome não são normalizados.
    """
    import app.db.database as db_module
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db
    
    try:
        operations = [
            {
                "Data do Negócio": "01/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO A VISTA",
                "Instituição": "CLEAR",
                "Código de Negociação": "HFOF11",  # FII com F no nome
                "Quantidade": 10,
                "Preço": 100.00,
                "Valor": 1000.00
            }
        ]
        
        excel_file = create_b3_excel_mock(operations)
        mock_file = MockFile(excel_file, "test_fii.xlsx")
        
        result = import_b3_excel(mock_file)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT ticker, asset_class FROM assets WHERE status = 'ACTIVE'")
        assets = cursor.fetchall()
        
        assert len(assets) == 1
        assert assets[0][0] == "HFOF11", "Ticker FII não deveria ser alterado"
        assert assets[0][1] == "FUNDO IMOBILIÁRIO", "Deveria ser classificado como FII"
        
        conn.close()
        
    finally:
        db_module.DB_PATH = original_db_path


def test_reimport_same_file_deduplicates(temp_db):
    """
    Testa que reimportar o mesmo arquivo não cria duplicatas.
    """
    import app.db.database as db_module
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db
    
    try:
        operations = [
            {
                "Data do Negócio": "01/01/2026",
                "Tipo de Movimentação": "COMPRA",
                "Mercado": "MERCADO FRACIONARIO",
                "Instituição": "CLEAR",
                "Código de Negociação": "ABEV3F",
                "Quantidade": 20,
                "Preço": 15.50,
                "Valor": 310.00
            }
        ]
        
        excel_file1 = create_b3_excel_mock(operations)
        mock_file1 = MockFile(excel_file1, "test_dedup.xlsx")
        
        # Primeira importação
        result1 = import_b3_excel(mock_file1)
        assert result1["inserted"] == 1
        assert result1["duplicated"] == 0
        
        # Segunda importação (mesmo arquivo)
        excel_file2 = create_b3_excel_mock(operations)
        mock_file2 = MockFile(excel_file2, "test_dedup.xlsx")
        
        result2 = import_b3_excel(mock_file2)
        assert result2["inserted"] == 0, "Não deveria inserir na segunda vez"
        assert result2["duplicated"] == 1, "Deveria detectar 1 duplicata"
        
        # Verificar que ainda tem apenas 1 operação
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM operations WHERE status = 'ACTIVE'")
        count = cursor.fetchone()[0]
        assert count == 1, f"Deveria ter apenas 1 operação, mas tem {count}"
        
        conn.close()
        
    finally:
        db_module.DB_PATH = original_db_path


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
