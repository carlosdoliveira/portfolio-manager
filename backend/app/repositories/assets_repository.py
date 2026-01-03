import logging
from datetime import datetime
from app.db.database import get_db

logger = logging.getLogger(__name__)


def create_asset(ticker: str, asset_class: str, asset_type: str, product_name: str) -> int:
    """
    Cria um novo ativo no banco de dados.
    
    Args:
        ticker: Código de negociação do ativo
        asset_class: Classe do ativo (ex: AÇÕES, FII)
        asset_type: Tipo do ativo (ex: ON, PN)
        product_name: Nome do produto
        
    Returns:
        ID do ativo criado
        
    Raises:
        Exception: Se o ticker já existir
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar se já existe
        cursor.execute(
            "SELECT id FROM assets WHERE ticker = ? AND status = 'ACTIVE'",
            (ticker,)
        )
        existing = cursor.fetchone()
        
        if existing:
            logger.info(f"Ativo {ticker} já existe com ID {existing[0]}")
            return existing[0]
        
        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO assets (ticker, asset_class, asset_type, product_name, created_at, status)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE')
            """,
            (ticker, asset_class, asset_type, product_name, now)
        )
        
        asset_id = cursor.lastrowid
        logger.info(f"Ativo {ticker} criado com ID {asset_id}")
        return asset_id


def get_asset_by_ticker(ticker: str) -> dict | None:
    """
    Busca um ativo pelo ticker.
    
    Args:
        ticker: Código de negociação do ativo
        
    Returns:
        Dicionário com dados do ativo ou None se não encontrado
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, ticker, asset_class, asset_type, product_name, created_at, status
            FROM assets
            WHERE ticker = ? AND status = 'ACTIVE'
            """,
            (ticker,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "ticker": row[1],
                "asset_class": row[2],
                "asset_type": row[3],
                "product_name": row[4],
                "created_at": row[5],
                "status": row[6]
            }
        return None


def get_asset_by_id(asset_id: int) -> dict | None:
    """
    Busca um ativo pelo ID.
    
    Args:
        asset_id: ID do ativo
        
    Returns:
        Dicionário com dados do ativo ou None se não encontrado
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, ticker, asset_class, asset_type, product_name, created_at, status
            FROM assets
            WHERE id = ? AND status = 'ACTIVE'
            """,
            (asset_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "ticker": row[1],
                "asset_class": row[2],
                "asset_type": row[3],
                "product_name": row[4],
                "created_at": row[5],
                "status": row[6]
            }
        return None


def list_assets() -> list[dict]:
    """
    Lista todos os ativos ativos com estatísticas de operações.
    
    IMPORTANTE: As operações são CONSOLIDADAS independentemente do mercado.
    Compras em mercado à vista e fracionário são somadas em uma única posição.
    
    Returns:
        Lista de dicionários com dados dos ativos incluindo:
        - total_bought: soma das quantidades compradas (TODOS os mercados)
        - total_sold: soma das quantidades vendidas (TODOS os mercados)
        - current_position: diferença (comprado - vendido) CONSOLIDADA
        - total_bought_value: valor total gasto em compras (R$) CONSOLIDADO
        - total_sold_value: valor total recebido em vendas (R$) CONSOLIDADO
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                a.id, 
                a.ticker, 
                a.asset_class, 
                a.asset_type, 
                a.product_name, 
                a.created_at,
                a.status,
                COUNT(DISTINCT o.id) as total_operations,
                SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) as total_bought,
                SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.quantity ELSE 0 END) as total_sold,
                (SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) - 
                 SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.quantity ELSE 0 END)) as current_position,
                SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) as total_bought_value,
                SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.value ELSE 0 END) as total_sold_value
            FROM assets a
            LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
            WHERE a.status = 'ACTIVE'
            GROUP BY a.id
            ORDER BY a.ticker
            """
        )
        rows = cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "ticker": row[1],
                "asset_class": row[2],
                "asset_type": row[3],
                "product_name": row[4],
                "created_at": row[5],
                "status": row[6],
                "total_operations": row[7] or 0,
                "total_bought": row[8] or 0,
                "total_sold": row[9] or 0,
                "current_position": row[10] or 0,
                "total_bought_value": row[11] or 0.0,
                "total_sold_value": row[12] or 0.0
            }
            for row in rows
        ]


def update_asset(asset_id: int, ticker: str, asset_class: str, asset_type: str, product_name: str) -> None:
    """
    Atualiza um ativo existente.
    
    Args:
        asset_id: ID do ativo
        ticker: Novo código de negociação
        asset_class: Nova classe do ativo
        asset_type: Novo tipo do ativo
        product_name: Novo nome do produto
        
    Raises:
        ValueError: Se o ativo não existir
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar se existe
        cursor.execute(
            "SELECT id FROM assets WHERE id = ? AND status = 'ACTIVE'",
            (asset_id,)
        )
        
        if not cursor.fetchone():
            raise ValueError(f"Ativo {asset_id} não encontrado")
        
        cursor.execute(
            """
            UPDATE assets
            SET ticker = ?, asset_class = ?, asset_type = ?, product_name = ?
            WHERE id = ?
            """,
            (ticker, asset_class, asset_type, product_name, asset_id)
        )
        
        logger.info(f"Ativo {asset_id} ({ticker}) atualizado")


def delete_asset(asset_id: int) -> None:
    """
    Deleta um ativo (soft delete).
    
    Args:
        asset_id: ID do ativo
        
    Raises:
        ValueError: Se o ativo não existir ou tiver operações ativas
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar se existe
        cursor.execute(
            "SELECT id FROM assets WHERE id = ? AND status = 'ACTIVE'",
            (asset_id,)
        )
        
        if not cursor.fetchone():
            raise ValueError(f"Ativo {asset_id} não encontrado")
        
        # Verificar se tem operações ativas
        cursor.execute(
            "SELECT COUNT(*) FROM operations WHERE asset_id = ? AND status = 'ACTIVE'",
            (asset_id,)
        )
        
        count = cursor.fetchone()[0]
        if count > 0:
            raise ValueError(f"Não é possível deletar ativo {asset_id}: possui {count} operações ativas")
        
        cursor.execute(
            "UPDATE assets SET status = 'DELETED' WHERE id = ?",
            (asset_id,)
        )
        
        logger.info(f"Ativo {asset_id} marcado como DELETED")
