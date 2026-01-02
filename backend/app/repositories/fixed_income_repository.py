"""
Repositório para gerenciamento de ativos e operações de Renda Fixa.
"""
import sqlite3
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from app.db.database import get_db

logger = logging.getLogger(__name__)


def create_fixed_income_asset(
    asset_id: int,
    issuer: str,
    product_type: str,
    indexer: str,
    rate: float,
    maturity_date: str,
    issue_date: str,
    custody_fee: float = 0.0
) -> int:
    """
    Cria um novo ativo de Renda Fixa vinculado a um asset existente.
    
    Args:
        asset_id: ID do ativo na tabela assets
        issuer: Emissor (Banco, Tesouro Nacional, etc.)
        product_type: Tipo (CDB, LCI, LCA, TESOURO_SELIC, TESOURO_IPCA, TESOURO_PREFIXADO)
        indexer: Indexador (CDI, IPCA, PRE, SELIC)
        rate: Taxa contratada (ex: 110.0 para 110% CDI)
        maturity_date: Data de vencimento (YYYY-MM-DD)
        issue_date: Data de emissão (YYYY-MM-DD)
        custody_fee: Taxa de custódia anual (default 0.0)
    
    Returns:
        ID do ativo de Renda Fixa criado
    """
    logger.info(f"Criando ativo de Renda Fixa para asset_id {asset_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar se já existe RF para este asset
        cursor.execute(
            "SELECT id FROM fixed_income_assets WHERE asset_id = ? AND status = 'ACTIVE'",
            (asset_id,)
        )
        existing = cursor.fetchone()
        if existing:
            raise ValueError(f"Ativo {asset_id} já possui informações de Renda Fixa")
        
        cursor.execute("""
            INSERT INTO fixed_income_assets (
                asset_id, issuer, product_type, indexer, rate,
                maturity_date, custody_fee, issue_date, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (
            asset_id, issuer, product_type, indexer, rate,
            maturity_date, custody_fee, issue_date,
            datetime.utcnow().isoformat()
        ))
        
        fi_id = cursor.lastrowid
        logger.info(f"Ativo de Renda Fixa criado com ID {fi_id}")
        return fi_id


def list_fixed_income_assets() -> List[Dict[str, Any]]:
    """
    Lista todos os ativos de Renda Fixa ativos com suas informações completas.
    
    Returns:
        Lista de dicionários com dados dos ativos
    """
    logger.debug("Listando ativos de Renda Fixa")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                fi.id,
                fi.asset_id,
                a.ticker,
                a.product_name,
                fi.issuer,
                fi.product_type,
                fi.indexer,
                fi.rate,
                fi.maturity_date,
                fi.custody_fee,
                fi.issue_date,
                fi.created_at,
                fi.status,
                COALESCE(SUM(CASE WHEN fio.operation_type = 'APLICACAO' THEN fio.amount ELSE 0 END), 0) as total_invested,
                COALESCE(SUM(CASE WHEN fio.operation_type IN ('RESGATE', 'VENCIMENTO') THEN fio.amount ELSE 0 END), 0) as total_redeemed,
                COUNT(fio.id) as operations_count
            FROM fixed_income_assets fi
            INNER JOIN assets a ON fi.asset_id = a.id
            LEFT JOIN fixed_income_operations fio ON fi.asset_id = fio.asset_id AND fio.status = 'ACTIVE'
            WHERE fi.status = 'ACTIVE'
            GROUP BY fi.id
            ORDER BY fi.maturity_date ASC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            asset = dict(zip(columns, row))
            asset['current_balance'] = asset['total_invested'] - asset['total_redeemed']
            results.append(asset)
        
        logger.debug(f"Encontrados {len(results)} ativos de Renda Fixa")
        return results


def get_fixed_income_by_id(fi_id: int) -> Optional[Dict[str, Any]]:
    """
    Busca um ativo de Renda Fixa por ID.
    
    Args:
        fi_id: ID do ativo de Renda Fixa
    
    Returns:
        Dicionário com dados do ativo ou None se não encontrado
    """
    logger.debug(f"Buscando ativo de Renda Fixa ID {fi_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                fi.*,
                a.ticker,
                a.product_name
            FROM fixed_income_assets fi
            INNER JOIN assets a ON fi.asset_id = a.id
            WHERE fi.id = ? AND fi.status = 'ACTIVE'
        """, (fi_id,))
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None


def get_fixed_income_by_asset_id(asset_id: int) -> Optional[Dict[str, Any]]:
    """
    Busca informações de Renda Fixa por asset_id.
    
    Args:
        asset_id: ID do ativo na tabela assets
    
    Returns:
        Dicionário com dados do ativo ou None se não encontrado
    """
    logger.debug(f"Buscando Renda Fixa para asset_id {asset_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM fixed_income_assets
            WHERE asset_id = ? AND status = 'ACTIVE'
        """, (asset_id,))
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None


def create_fixed_income_operation(
    asset_id: int,
    operation_type: str,
    amount: float,
    trade_date: str,
    net_amount: Optional[float] = None,
    ir_amount: float = 0.0
) -> int:
    """
    Registra uma operação de Renda Fixa (aplicação, resgate ou vencimento).
    
    Args:
        asset_id: ID do ativo
        operation_type: Tipo (APLICACAO, RESGATE, VENCIMENTO)
        amount: Valor bruto da operação
        trade_date: Data da operação (YYYY-MM-DD)
        net_amount: Valor líquido (após IR), opcional
        ir_amount: Valor do IR retido (default 0.0)
    
    Returns:
        ID da operação criada
    """
    logger.info(f"Registrando operação de Renda Fixa: {operation_type} para asset {asset_id}")
    
    # Validações
    valid_types = ['APLICACAO', 'RESGATE', 'VENCIMENTO']
    if operation_type not in valid_types:
        raise ValueError(f"Tipo de operação inválido. Use: {', '.join(valid_types)}")
    
    if amount <= 0:
        raise ValueError("Valor deve ser maior que zero")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar se asset existe e é Renda Fixa
        cursor.execute("""
            SELECT id FROM fixed_income_assets
            WHERE asset_id = ? AND status = 'ACTIVE'
        """, (asset_id,))
        
        if not cursor.fetchone():
            raise ValueError(f"Asset {asset_id} não é um ativo de Renda Fixa ou não existe")
        
        cursor.execute("""
            INSERT INTO fixed_income_operations (
                asset_id, operation_type, amount, net_amount, ir_amount,
                trade_date, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (
            asset_id, operation_type, amount, net_amount, ir_amount,
            trade_date, datetime.utcnow().isoformat()
        ))
        
        op_id = cursor.lastrowid
        logger.info(f"Operação de Renda Fixa criada com ID {op_id}")
        return op_id


def list_fixed_income_operations(asset_id: int) -> List[Dict[str, Any]]:
    """
    Lista todas as operações de um ativo de Renda Fixa.
    
    Args:
        asset_id: ID do ativo
    
    Returns:
        Lista de operações
    """
    logger.debug(f"Listando operações de Renda Fixa para asset {asset_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM fixed_income_operations
            WHERE asset_id = ? AND status = 'ACTIVE'
            ORDER BY trade_date DESC
        """, (asset_id,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def calculate_ir_rate(days_held: int) -> float:
    """
    Calcula a alíquota de IR com base no tempo de aplicação (IR regressivo).
    
    Args:
        days_held: Dias entre aplicação e resgate
    
    Returns:
        Alíquota de IR (0.225, 0.20, 0.175 ou 0.15)
    """
    if days_held <= 180:
        return 0.225  # 22.5%
    elif days_held <= 360:
        return 0.20   # 20.0%
    elif days_held <= 720:
        return 0.175  # 17.5%
    else:
        return 0.15   # 15.0%


def calculate_fixed_income_projection(
    asset_id: int,
    current_cdi_rate: float = 13.75,
    current_ipca_rate: float = 4.5
) -> Dict[str, Any]:
    """
    Calcula projeção de rendimento de um ativo de Renda Fixa.
    
    Args:
        asset_id: ID do ativo
        current_cdi_rate: Taxa CDI atual anual (%)
        current_ipca_rate: Taxa IPCA atual anual (%)
    
    Returns:
        Dicionário com projeção de rendimento
    """
    logger.debug(f"Calculando projeção para asset {asset_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Buscar informações do ativo
        cursor.execute("""
            SELECT fi.*, a.ticker
            FROM fixed_income_assets fi
            INNER JOIN assets a ON fi.asset_id = a.id
            WHERE fi.asset_id = ? AND fi.status = 'ACTIVE'
        """, (asset_id,))
        
        fi_data = cursor.fetchone()
        if not fi_data:
            raise ValueError(f"Ativo {asset_id} não encontrado")
        
        columns = [desc[0] for desc in cursor.description]
        fi = dict(zip(columns, fi_data))
        
        # Buscar operações
        cursor.execute("""
            SELECT SUM(CASE WHEN operation_type = 'APLICACAO' THEN amount ELSE 0 END) as total_invested,
                   SUM(CASE WHEN operation_type IN ('RESGATE', 'VENCIMENTO') THEN amount ELSE 0 END) as total_redeemed,
                   MIN(CASE WHEN operation_type = 'APLICACAO' THEN trade_date END) as first_application
            FROM fixed_income_operations
            WHERE asset_id = ? AND status = 'ACTIVE'
        """, (asset_id,))
        
        ops_row = cursor.fetchone()
        total_invested = ops_row[0] or 0
        total_redeemed = ops_row[1] or 0
        first_application = ops_row[2]
        
        current_balance = total_invested - total_redeemed
        
        if current_balance <= 0:
            return {
                'asset_id': asset_id,
                'ticker': fi['ticker'],
                'current_balance': 0,
                'gross_projection': 0,
                'ir_amount': 0,
                'net_projection': 0,
                'message': 'Sem saldo para projeção'
            }
        
        # Calcular dias até vencimento
        maturity = datetime.fromisoformat(fi['maturity_date'])
        today = datetime.now()
        days_to_maturity = (maturity - today).days
        
        if days_to_maturity <= 0:
            return {
                'asset_id': asset_id,
                'ticker': fi['ticker'],
                'current_balance': current_balance,
                'gross_projection': current_balance,
                'ir_amount': 0,
                'net_projection': current_balance,
                'message': 'Investimento vencido'
            }
        
        # Calcular rendimento bruto baseado no indexador
        indexer = fi['indexer'].upper()
        rate_contracted = fi['rate']
        
        if indexer == 'CDI':
            annual_rate = (current_cdi_rate / 100) * (rate_contracted / 100)
        elif indexer == 'IPCA':
            # IPCA+ tem componente fixo + IPCA
            annual_rate = (current_ipca_rate / 100) + (rate_contracted / 100)
        elif indexer == 'PRE':
            annual_rate = rate_contracted / 100
        elif indexer == 'SELIC':
            # SELIC normalmente é 100% da taxa SELIC (próxima ao CDI)
            annual_rate = (current_cdi_rate / 100) * (rate_contracted / 100)
        else:
            annual_rate = rate_contracted / 100
        
        # Projeção simples (juros compostos)
        years_to_maturity = days_to_maturity / 365.25
        gross_value = current_balance * ((1 + annual_rate) ** years_to_maturity)
        gross_gain = gross_value - current_balance
        
        # Aplicar taxa de custódia se houver (Tesouro)
        custody_fee_amount = 0
        if fi['custody_fee'] > 0:
            custody_fee_amount = current_balance * (fi['custody_fee'] / 100) * years_to_maturity
        
        # Calcular IR
        days_held = (today - datetime.fromisoformat(first_application)).days if first_application else days_to_maturity
        ir_rate = calculate_ir_rate(days_held + days_to_maturity)
        
        # LCI e LCA são isentas de IR
        if fi['product_type'] in ['LCI', 'LCA']:
            ir_amount = 0
        else:
            ir_amount = gross_gain * ir_rate
        
        net_value = gross_value - ir_amount - custody_fee_amount
        net_gain = net_value - current_balance
        
        return {
            'asset_id': asset_id,
            'ticker': fi['ticker'],
            'product_type': fi['product_type'],
            'indexer': indexer,
            'rate_contracted': rate_contracted,
            'maturity_date': fi['maturity_date'],
            'days_to_maturity': days_to_maturity,
            'current_balance': current_balance,
            'gross_projection': gross_value,
            'gross_gain': gross_gain,
            'ir_rate': ir_rate * 100,
            'ir_amount': ir_amount,
            'custody_fee_amount': custody_fee_amount,
            'net_projection': net_value,
            'net_gain': net_gain,
            'annual_rate_used': annual_rate * 100
        }


def delete_fixed_income_asset(asset_id: int) -> None:
    """
    Soft delete de um ativo de Renda Fixa.
    
    Args:
        asset_id: ID do ativo
    """
    logger.info(f"Deletando ativo de Renda Fixa {asset_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE fixed_income_assets
            SET status = 'DELETED'
            WHERE asset_id = ?
        """, (asset_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Ativo {asset_id} não encontrado")
        
        logger.info(f"Ativo de Renda Fixa {asset_id} deletado")
