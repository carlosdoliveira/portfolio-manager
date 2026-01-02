import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "portfolio.db"

def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para melhor concorrência
    return conn

@contextmanager
def get_db():
    """
    Context manager para gerenciamento seguro de conexões do banco de dados.
    
    Garante que:
    - Conexões são sempre fechadas, mesmo em caso de exceção
    - Transações são commitadas em caso de sucesso
    - Rollback automático em caso de erro
    
    Uso:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
        logger.debug("Transação commitada com sucesso")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro na transação, rollback executado: {e}")
        raise
    finally:
        conn.close()
        logger.debug("Conexão fechada")

def init_db():
    logger.info("Inicializando banco de dados")
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de ativos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL UNIQUE,
            asset_class TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE'
        )
    """)

    # Tabela de operações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,

            movement_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            value REAL NOT NULL,

            trade_date TEXT NOT NULL,
            created_at TEXT NOT NULL,

            source TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',

            market TEXT,
            institution TEXT,

            FOREIGN KEY (asset_id) REFERENCES assets(id),

            UNIQUE (
                trade_date,
                movement_type,
                market,
                institution,
                asset_id,
                quantity,
                price,
                source
            )
        )
    """)
    
    # Migration: Adicionar coluna status se não existir
    try:
        cursor.execute("ALTER TABLE operations ADD COLUMN status TEXT NOT NULL DEFAULT 'ACTIVE'")
        logger.info("Coluna 'status' adicionada à tabela operations")
    except sqlite3.OperationalError:
        logger.debug("Coluna 'status' já existe na tabela operations")

    # Migration: Adicionar coluna asset_id se não existir
    try:
        cursor.execute("ALTER TABLE operations ADD COLUMN asset_id INTEGER")
        logger.info("Coluna 'asset_id' adicionada à tabela operations")
    except sqlite3.OperationalError:
        logger.debug("Coluna 'asset_id' já existe na tabela operations")

    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado com sucesso")
