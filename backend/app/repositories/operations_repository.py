import logging
from datetime import datetime
from app.db.database import get_db

logger = logging.getLogger(__name__)

def create_operation(data: dict):
    logger.info(f"Criando operação: {data.get('ticker', 'N/A')} - {data['movement_type']} - {data['source']}")
    
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO operations (
            asset_class,
            asset_type,
            product_name,
            ticker,
            movement_type,
            quantity,
            price,
            value,
            trade_date,
            created_at,
            source,
            market,
            institution
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["asset_class"],
        data["asset_type"],
        data["product_name"],
        data.get("ticker"),
        data["movement_type"],
        data["quantity"],
        data["price"],
        data["quantity"] * data["price"],
        data["trade_date"],
        datetime.utcnow().isoformat(),
        data["source"],
        data.get("market"),
        data.get("institution"),
        ))
        
        logger.debug(f"Operação criada com sucesso: ID pendente")

def list_operations():
    logger.debug("Listando todas as operações")
    
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            id,
            asset_class,
            asset_type,
            product_name,
            ticker,
            movement_type,
            quantity,
            price,
            value,
            trade_date,
            source,
            created_at
        FROM operations
        ORDER BY trade_date ASC, id ASC
    """)

        rows = cursor.fetchall()

    columns = [
        "id",
        "asset_class",
        "asset_type",
        "product_name",
        "ticker",
        "movement_type",
        "quantity",
        "price",
        "value",
        "trade_date",
        "source",
        "created_at",
    ]

    operations = [dict(zip(columns, row)) for row in rows]
    logger.info(f"Listadas {len(operations)} operações")
    return operations

    
