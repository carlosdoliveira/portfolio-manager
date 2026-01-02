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
    logger.debug("Listando todas as operações ativas")
    
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
            created_at,
            status
        FROM operations
        WHERE status = 'ACTIVE'
        ORDER BY trade_date DESC, id DESC
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
        "status",
    ]

    operations = [dict(zip(columns, row)) for row in rows]
    logger.info(f"Listadas {len(operations)} operações ativas")
    return operations

def get_operation_by_id(operation_id: int):
    """Busca uma operação específica por ID."""
    logger.debug(f"Buscando operação ID: {operation_id}")
    
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
                created_at,
                status,
                market,
                institution
            FROM operations
            WHERE id = ?
        """, (operation_id,))
        
        row = cursor.fetchone()
    
    if not row:
        logger.warning(f"Operação ID {operation_id} não encontrada")
        return None
    
    columns = [
        "id", "asset_class", "asset_type", "product_name", "ticker",
        "movement_type", "quantity", "price", "value", "trade_date",
        "source", "created_at", "status", "market", "institution"
    ]
    
    operation = dict(zip(columns, row))
    logger.debug(f"Operação encontrada: {operation['ticker']} - {operation['status']}")
    return operation

def update_operation(operation_id: int, data: dict):
    """
    Atualiza uma operação seguindo o princípio de imutabilidade:
    1. Marca a operação antiga como CANCELLED
    2. Cria uma nova operação com os dados atualizados
    
    Retorna o ID da nova operação criada.
    """
    logger.info(f"Atualizando operação ID: {operation_id}")
    
    # Buscar operação original
    original = get_operation_by_id(operation_id)
    if not original:
        raise ValueError(f"Operação {operation_id} não encontrada")
    
    if original["status"] != "ACTIVE":
        raise ValueError(f"Operação {operation_id} não está ativa (status: {original['status']})")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Marcar operação antiga como CANCELLED
        cursor.execute("""
            UPDATE operations
            SET status = 'CANCELLED'
            WHERE id = ?
        """, (operation_id,))
        
        logger.info(f"Operação {operation_id} marcada como CANCELLED")
        
        # 2. Criar nova operação com dados atualizados
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
                status,
                market,
                institution
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
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
        
        new_id = cursor.lastrowid
        logger.info(f"Nova operação criada com ID: {new_id}")
        
        return new_id

def delete_operation(operation_id: int):
    """
    Soft delete: marca a operação como DELETED ao invés de remover do banco.
    Preserva auditoria e histórico.
    """
    logger.info(f"Deletando operação ID: {operation_id}")
    
    # Verificar se existe e está ativa
    operation = get_operation_by_id(operation_id)
    if not operation:
        raise ValueError(f"Operação {operation_id} não encontrada")
    
    if operation["status"] != "ACTIVE":
        raise ValueError(f"Operação {operation_id} não está ativa (status: {operation['status']})")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE operations
            SET status = 'DELETED'
            WHERE id = ?
        """, (operation_id,))
        
        logger.info(f"Operação {operation_id} marcada como DELETED")

    
