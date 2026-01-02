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
    return sqlite3.connect(DB_PATH)

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            asset_class TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            ticker TEXT,

            movement_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            value REAL NOT NULL,

            trade_date TEXT NOT NULL,
            created_at TEXT NOT NULL,

            source TEXT NOT NULL,

            market TEXT,
            institution TEXT,

            UNIQUE (
                trade_date,
                movement_type,
                market,
                institution,
                ticker,
                quantity,
                price,
                source
            )
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado com sucesso")
