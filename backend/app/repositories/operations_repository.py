import logging
from datetime import datetime
from app.db.database import get_db

logger = logging.getLogger(__name__)

def create_operation(data: dict):
    """
    Cria uma nova operação vinculada a um ativo.
    
    Args:
        data: Dicionário com dados da operação (deve conter asset_id)
    """
    logger.info(f"Criando operação: Asset ID {data.get('asset_id')} - {data['movement_type']} - {data['source']}")
    
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO operations (
            asset_id,
            movement_type,
            quantity,
            price,
            value,
            trade_date,
            created_at,
            source,
            market,
            institution
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["asset_id"],
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
        
        operation_id = cursor.lastrowid
        logger.debug(f"Operação criada com sucesso: ID {operation_id}")

def list_operations():
    """Lista todas as operações ativas com dados do ativo."""
    logger.debug("Listando todas as operações ativas")
    
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            o.id,
            o.asset_id,
            a.ticker,
            a.asset_class,
            a.asset_type,
            a.product_name,
            o.movement_type,
            o.quantity,
            o.price,
            o.value,
            o.trade_date,
            o.source,
            o.created_at,
            o.status,
            o.market,
            o.institution
        FROM operations o
        INNER JOIN assets a ON o.asset_id = a.id
        WHERE o.status = 'ACTIVE'
        ORDER BY o.trade_date DESC, o.id DESC
    """)

        rows = cursor.fetchall()

    columns = [
        "id",
        "asset_id",
        "ticker",
        "asset_class",
        "asset_type",
        "product_name",
        "movement_type",
        "quantity",
        "price",
        "value",
        "trade_date",
        "source",
        "created_at",
        "status",
        "market",
        "institution"
    ]

    operations = [dict(zip(columns, row)) for row in rows]
    logger.info(f"Listadas {len(operations)} operações ativas")
    return operations


def list_operations_by_asset(asset_id: int):
    """Lista todas as operações ativas de um ativo específico."""
    logger.debug(f"Listando operações do ativo ID: {asset_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            o.id,
            o.asset_id,
            a.ticker,
            a.asset_class,
            a.asset_type,
            a.product_name,
            o.movement_type,
            o.quantity,
            o.price,
            o.value,
            o.trade_date,
            o.source,
            o.created_at,
            o.status,
            o.market,
            o.institution
        FROM operations o
        INNER JOIN assets a ON o.asset_id = a.id
        WHERE o.asset_id = ? AND o.status = 'ACTIVE'
        ORDER BY o.trade_date DESC, o.id DESC
    """, (asset_id,))

        rows = cursor.fetchall()

    columns = [
        "id",
        "asset_id",
        "ticker",
        "asset_class",
        "asset_type",
        "product_name",
        "movement_type",
        "quantity",
        "price",
        "value",
        "trade_date",
        "source",
        "created_at",
        "status",
        "market",
        "institution"
    ]

    operations = [dict(zip(columns, row)) for row in rows]
    logger.info(f"Listadas {len(operations)} operações do ativo {asset_id}")
    return operations

def get_operation_by_id(operation_id: int):
    """Busca uma operação específica por ID."""
    logger.debug(f"Buscando operação ID: {operation_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                o.id,
                o.asset_id,
                a.ticker,
                a.asset_class,
                a.asset_type,
                a.product_name,
                o.movement_type,
                o.quantity,
                o.price,
                o.value,
                o.trade_date,
                o.source,
                o.created_at,
                o.status,
                o.market,
                o.institution
            FROM operations o
            INNER JOIN assets a ON o.asset_id = a.id
            WHERE o.id = ?
        """, (operation_id,))
        
        row = cursor.fetchone()
    
    if not row:
        logger.warning(f"Operação ID {operation_id} não encontrada")
        return None
    
    columns = [
        "id", "asset_id", "ticker", "asset_class", "asset_type", "product_name",
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
                asset_id,
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
        """, (
            data["asset_id"],
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

    
