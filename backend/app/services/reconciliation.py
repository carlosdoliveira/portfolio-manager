"""
Serviço de Reconciliação de Posições

Responsável por:
- Importar snapshots de posição B3
- Comparar posição calculada vs posição real
- Identificar e corrigir discrepâncias
- Aplicar ajustes automáticos
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from io import BytesIO

from app.db.database import get_db
from app.services.importer import normalize_ticker, classify_asset

logger = logging.getLogger(__name__)


def extract_ticker_from_product(produto):
    """
    Extrai código de negociação do nome do produto.
    
    Formatos:
    - Ações/FIIs/ETFs: "ITSA4 - ITAUSA S.A." -> "ITSA4"
    - Renda Fixa: "CDB - CDB124AUGT1 - BANCO X" -> "CDB124AUGT1"
    - Sem separador: mantém como está
    """
    if pd.isna(produto):
        return produto
    produto_str = str(produto).strip()
    
    if " - " not in produto_str:
        return produto_str
    
    parts = produto_str.split(" - ")
    
    # Tipos de renda fixa
    if parts[0] in ["CDB", "LCI", "LCA", "CRI", "CRA", "Debênture", "Debenture"]:
        return parts[1].strip() if len(parts) > 1 else produto_str
    else:
        # Ações, FIIs, ETFs: primeira parte
        return parts[0].strip()



def import_position_snapshot(file) -> Dict:
    """
    Importa arquivo de posição B3 (posicao-*.xlsx) e cria snapshot.
    
    Args:
        file: UploadFile com arquivo Excel de posição
    
    Returns:
        Dicionário com resumo da importação e discrepâncias encontradas
    """
    logger.info(f"Importando snapshot de posição: {file.filename}")
    
    try:
        df = pd.read_excel(file.file)
        logger.debug(f"Arquivo lido: {len(df)} linhas")
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        raise ValueError(f"Arquivo Excel inválido: {e}")
    
    # Validar colunas obrigatórias
    required = ['Código de Negociação', 'Quantidade']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
    
    # Filtrar linhas válidas
    df = df[df['Código de Negociação'].notna()].copy()
    
    snapshot_date = datetime.now().isoformat()
    snapshots_created = 0
    discrepancies = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for idx, row in df.iterrows():
            try:
                # Extrair ticker limpo
                ticker_raw = row['Código de Negociação']
                ticker = extract_ticker_from_product(ticker_raw)
                ticker = normalize_ticker(ticker, "")
                
                qty_b3 = float(row['Quantidade'])
                
                # Buscar ou criar ativo
                cursor.execute("SELECT id FROM assets WHERE ticker = ?", (ticker,))
                result = cursor.fetchone()
                
                if not result:
                    # Criar ativo se não existe
                    asset_class, asset_type = classify_asset(ticker)
                    cursor.execute("""
                        INSERT INTO assets (ticker, asset_class, asset_type, product_name, created_at, status)
                        VALUES (?, ?, ?, ?, ?, 'ACTIVE')
                    """, (ticker, asset_class, asset_type, ticker, datetime.utcnow().isoformat()))
                    asset_id = cursor.lastrowid
                    logger.info(f"Ativo criado: {ticker} (ID {asset_id})")
                else:
                    asset_id = result[0]
                
                # Criar snapshot
                cursor.execute("""
                    INSERT INTO position_snapshots (asset_id, quantity, snapshot_date, source, created_at)
                    VALUES (?, ?, ?, 'B3', ?)
                """, (asset_id, qty_b3, snapshot_date, datetime.utcnow().isoformat()))
                
                snapshots_created += 1
                
                # Calcular posição no sistema
                qty_sistema = calculate_position_by_asset_id(cursor, asset_id)
                
                # Registrar discrepância
                diff = qty_sistema - qty_b3
                if abs(diff) > 0.01:
                    discrepancies.append({
                        "ticker": ticker,
                        "qty_b3": qty_b3,
                        "qty_sistema": qty_sistema,
                        "difference": diff,
                        "error_pct": (diff / qty_b3 * 100) if qty_b3 > 0 else 0
                    })
                
            except Exception as e:
                logger.error(f"Erro ao processar linha {idx} ({ticker_raw}): {e}")
                continue
    
    logger.info(f"Snapshot importado: {snapshots_created} posições, {len(discrepancies)} discrepâncias")
    
    return {
        "status": "success",
        "snapshot_date": snapshot_date,
        "total_positions": len(df),
        "snapshots_created": snapshots_created,
        "discrepancies_found": len(discrepancies),
        "discrepancies": sorted(discrepancies, key=lambda x: abs(x['difference']), reverse=True)[:20]
    }


def calculate_position_by_asset_id(cursor, asset_id: int) -> float:
    """
    Calcula posição atual de um ativo baseado nas operações.
    
    Args:
        cursor: Cursor do banco de dados
        asset_id: ID do ativo
    
    Returns:
        Quantidade atual (compras - vendas)
    """
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN movement_type = 'COMPRA' THEN quantity ELSE 0 END) as compras,
            SUM(CASE WHEN movement_type = 'VENDA' THEN quantity ELSE 0 END) as vendas
        FROM operations
        WHERE asset_id = ? AND status = 'ACTIVE'
    """, (asset_id,))
    
    result = cursor.fetchone()
    if result:
        compras = result[0] or 0
        vendas = result[1] or 0
        return compras - vendas
    return 0


def get_reconciliation_diagnosis() -> Dict:
    """
    Gera diagnóstico completo de reconciliação.
    
    Compara último snapshot B3 com posições calculadas,
    identificando discrepâncias e sugerindo correções.
    
    Returns:
        Dicionário com diagnóstico completo
    """
    logger.info("Gerando diagnóstico de reconciliação")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Buscar último snapshot de cada ativo
        cursor.execute("""
            SELECT 
                a.id,
                a.ticker,
                a.asset_class,
                ps.quantity as qty_snapshot,
                ps.snapshot_date
            FROM assets a
            INNER JOIN (
                SELECT asset_id, quantity, snapshot_date,
                       ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY snapshot_date DESC) as rn
                FROM position_snapshots
            ) ps ON a.id = ps.asset_id AND ps.rn = 1
            WHERE a.status = 'ACTIVE' AND a.asset_class IN ('AÇÕES', 'FII', 'ETF')
        """)
        
        snapshots = cursor.fetchall()
        
        if not snapshots:
            return {
                "status": "no_snapshots",
                "message": "Nenhum snapshot de posição encontrado. Importe arquivo de posição B3 primeiro."
            }
        
        issues = []
        total_diff = 0
        
        for asset_id, ticker, asset_class, qty_snapshot, snapshot_date in snapshots:
            qty_sistema = calculate_position_by_asset_id(cursor, asset_id)
            diff = qty_sistema - qty_snapshot
            
            if abs(diff) > 0.01:
                # Analisar causa da discrepância
                causes = analyze_discrepancy(cursor, asset_id, ticker, diff)
                
                issues.append({
                    "asset_id": asset_id,
                    "ticker": ticker,
                    "asset_class": asset_class,
                    "qty_expected": qty_snapshot,
                    "qty_calculated": qty_sistema,
                    "difference": diff,
                    "error_pct": (diff / qty_snapshot * 100) if qty_snapshot > 0 else 0,
                    "snapshot_date": snapshot_date,
                    "possible_causes": causes,
                    "suggested_action": suggest_correction(diff, causes)
                })
                
                total_diff += abs(diff)
        
        snapshot_date = snapshots[0][4] if snapshots else None
        
        return {
            "status": "success",
            "snapshot_date": snapshot_date,
            "total_assets": len(snapshots),
            "assets_with_issues": len(issues),
            "assets_ok": len(snapshots) - len(issues),
            "total_difference": total_diff,
            "issues": sorted(issues, key=lambda x: abs(x['difference']), reverse=True)
        }


def analyze_discrepancy(cursor, asset_id: int, ticker: str, diff: float) -> List[str]:
    """
    Analisa possíveis causas de uma discrepância.
    
    Args:
        cursor: Cursor do banco
        asset_id: ID do ativo
        ticker: Ticker do ativo
        diff: Diferença (sistema - B3)
    
    Returns:
        Lista de possíveis causas
    """
    causes = []
    
    # Verificar se há operações com subtype NULL (possível atualização importada)
    cursor.execute("""
        SELECT COUNT(*) FROM operations 
        WHERE asset_id = ? AND operation_subtype IS NULL
    """, (asset_id,))
    
    null_subtypes = cursor.fetchone()[0]
    if null_subtypes > 0:
        causes.append(f"{null_subtypes} operações sem subtipo (podem ser atualizações)")
    
    # Verificar múltiplas operações na mesma data
    cursor.execute("""
        SELECT trade_date, COUNT(*) as cnt
        FROM operations
        WHERE asset_id = ?
        GROUP BY trade_date
        HAVING cnt > 2
        ORDER BY cnt DESC
        LIMIT 3
    """, (asset_id,))
    
    duplicates = cursor.fetchall()
    if duplicates:
        dates = [f"{d[0]} ({d[1]} ops)" for d in duplicates]
        causes.append(f"Múltiplas operações em: {', '.join(dates)}")
    
    # Verificar se diferença é múltiplo inteiro (possível duplicação)
    if diff > 0 and diff % 100 == 0:
        causes.append("Diferença é múltiplo de 100 (possível duplicação sistemática)")
    
    if not causes:
        causes.append("Causa não identificada automaticamente")
    
    return causes


def suggest_correction(diff: float, causes: List[str]) -> str:
    """
    Sugere ação corretiva baseada na diferença e causas.
    
    Args:
        diff: Diferença (sistema - B3)
        causes: Lista de causas identificadas
    
    Returns:
        Sugestão de correção
    """
    if abs(diff) < 1:
        return "Diferença muito pequena, pode ignorar"
    
    if diff > 0:
        return f"Sistema tem +{diff:.2f} ações a mais. Sugestão: criar ajuste de -{diff:.2f}"
    else:
        return f"Sistema tem {diff:.2f} ações a menos. Sugestão: criar ajuste de +{abs(diff):.2f}"


def auto_fix_positions(ticker: Optional[str] = None) -> Dict:
    """
    Aplica correções automáticas nas posições.
    
    Remove operações duplicadas e cria ajustes para bater com snapshot B3.
    
    Args:
        ticker: Se especificado, corrige apenas este ticker. Senão, todos.
    
    Returns:
        Resumo das correções aplicadas
    """
    logger.info(f"Iniciando correção automática: {ticker or 'TODOS'}")
    
    diagnosis = get_reconciliation_diagnosis()
    
    if diagnosis['status'] != 'success':
        return diagnosis
    
    issues = diagnosis['issues']
    
    if ticker:
        issues = [i for i in issues if i['ticker'] == ticker]
    
    fixed = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for issue in issues:
            asset_id = issue['asset_id']
            ticker = issue['ticker']
            diff = issue['difference']
            
            # Criar ajuste para zerar diferença
            if abs(diff) > 0.01:
                adjustment_qty = -diff  # Inverter sinal
                
                cursor.execute("""
                    INSERT INTO operations (
                        asset_id, trade_date, movement_type, market, institution,
                        quantity, price, value, created_at, source, operation_subtype, notes
                    ) VALUES (?, ?, ?, '', '', ?, 0, 0, ?, 'RECONCILIATION', 'AJUSTE_RECONCILIACAO', ?)
                """, (
                    asset_id,
                    datetime.now().date().isoformat(),
                    'COMPRA' if adjustment_qty > 0 else 'VENDA',
                    abs(adjustment_qty),
                    datetime.utcnow().isoformat(),
                    f"Ajuste automático de reconciliação: {adjustment_qty:+.2f} ações"
                ))
                
                fixed.append({
                    "ticker": ticker,
                    "adjustment": adjustment_qty,
                    "reason": f"Discrepância de {diff:+.2f} ações corrigida"
                })
                
                logger.info(f"Ajuste criado: {ticker} {adjustment_qty:+.2f}")
    
    return {
        "status": "success",
        "fixed_count": len(fixed),
        "adjustments": fixed
    }
