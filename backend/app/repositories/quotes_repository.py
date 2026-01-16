"""
Repository para gerenciamento de cotações em cache.

Armazena cotações no banco de dados para:
- Reduzir chamadas à API do yfinance
- Melhorar performance de cálculos
- Permitir consultas históricas
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict
from app.db.database import get_db

logger = logging.getLogger(__name__)


def save_quote(ticker: str, quote_data: dict) -> bool:
    """
    Salva ou atualiza cotação no banco de dados.
    
    Args:
        ticker: Código do ativo
        quote_data: Dados da cotação do yfinance
        
    Returns:
        True se salvou com sucesso
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO quotes (
                    ticker, price, change_value, change_percent,
                    volume, open_price, high_price, low_price,
                    previous_close, source, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ticker) DO UPDATE SET
                    price = excluded.price,
                    change_value = excluded.change_value,
                    change_percent = excluded.change_percent,
                    volume = excluded.volume,
                    open_price = excluded.open_price,
                    high_price = excluded.high_price,
                    low_price = excluded.low_price,
                    previous_close = excluded.previous_close,
                    source = excluded.source,
                    updated_at = excluded.updated_at
            """, (
                ticker,
                quote_data.get('price', 0),
                quote_data.get('change', 0),
                quote_data.get('change_percent', 0),
                quote_data.get('volume', 0),
                quote_data.get('open', 0),
                quote_data.get('high', 0),
                quote_data.get('low', 0),
                quote_data.get('previous_close', 0),
                quote_data.get('source', 'yfinance'),
                quote_data.get('updated_at', datetime.now().isoformat())
            ))
            
            logger.info(f"Cotação salva: {ticker} = R$ {quote_data.get('price', 0):.2f}")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao salvar cotação de {ticker}: {e}")
        return False


def get_quote(ticker: str) -> Optional[Dict]:
    """
    Busca cotação do banco de dados.
    
    Args:
        ticker: Código do ativo
        
    Returns:
        Dados da cotação ou None se não encontrada
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ticker, price, change_value, change_percent,
                    volume, open_price, high_price, low_price,
                    previous_close, source, updated_at
                FROM quotes
                WHERE ticker = ?
            """, (ticker,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'ticker': row[0],
                'price': row[1],
                'change': row[2],
                'change_percent': row[3],
                'volume': row[4],
                'open': row[5],
                'high': row[6],
                'low': row[7],
                'previous_close': row[8],
                'source': row[9],
                'updated_at': row[10]
            }
            
    except Exception as e:
        logger.error(f"Erro ao buscar cotação de {ticker}: {e}")
        return None


def get_all_quotes() -> List[Dict]:
    """
    Busca todas as cotações do banco.
    
    Returns:
        Lista de cotações
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ticker, price, change_value, change_percent,
                    volume, open_price, high_price, low_price,
                    previous_close, source, updated_at
                FROM quotes
                ORDER BY ticker
            """)
            
            quotes = []
            for row in cursor.fetchall():
                quotes.append({
                    'ticker': row[0],
                    'price': row[1],
                    'change': row[2],
                    'change_percent': row[3],
                    'volume': row[4],
                    'open': row[5],
                    'high': row[6],
                    'low': row[7],
                    'previous_close': row[8],
                    'source': row[9],
                    'updated_at': row[10]
                })
            
            return quotes
            
    except Exception as e:
        logger.error(f"Erro ao buscar todas as cotações: {e}")
        return []


def get_tickers_to_update() -> List[str]:
    """
    Busca lista de tickers que precisam ser atualizados.
    Retorna todos os tickers de ativos ativos (AÇÕES e ETF).
    
    Returns:
        Lista de tickers
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT a.ticker
                FROM assets a
                LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
                WHERE a.status = 'ACTIVE' 
                  AND (a.asset_class = 'AÇÕES' OR a.asset_class = 'ETF')
                GROUP BY a.ticker
                HAVING (
                    COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.quantity ELSE 0 END), 0)
                ) > 0
                ORDER BY a.ticker
            """)
            
            return [row[0] for row in cursor.fetchall()]
            
    except Exception as e:
        logger.error(f"Erro ao buscar tickers para atualizar: {e}")
        return []
