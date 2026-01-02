import pandas as pd
import sqlite3
import logging
from datetime import datetime
from app.db.database import get_db

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "Data do Negócio",
    "Tipo de Movimentação",
    "Mercado",
    "Instituição",
    "Código de Negociação",
    "Quantidade",
    "Preço",
    "Valor",
]

def classify_asset(ticker: str, product_name: str = None) -> tuple[str, str]:
    """
    Classifica um ativo com base no ticker.
    
    Regras:
    - FIIs: ticker termina com 11 (ex: HGLG11)
    - ETFs: ticker termina com 11 e começa com prefixos conhecidos ou contém ETF/INDX
    - Renda Fixa: LCI, LCA, CDB, RDB no ticker ou product_name
    - Ações: demais casos, ON (números 3, 5, 7, 9) ou PN (números 4, 6, 8)
    
    Returns:
        (asset_class, asset_type)
    """
    ticker = ticker.upper().strip()
    product_upper = (product_name or "").upper()
    
    # Verificar Renda Fixa
    rf_keywords = ["LCI", "LCA", "CDB", "RDB", "TESOURO", "DEBÊNTURE", "CRI", "CRA"]
    if any(kw in ticker for kw in rf_keywords) or any(kw in product_upper for kw in rf_keywords):
        # Determinar tipo específico
        if "LCI" in ticker or "LCI" in product_upper:
            return ("RENDA FIXA", "LCI")
        elif "LCA" in ticker or "LCA" in product_upper:
            return ("RENDA FIXA", "LCA")
        elif "CDB" in ticker or "CDB" in product_upper:
            return ("RENDA FIXA", "CDB")
        elif "RDB" in ticker or "RDB" in product_upper:
            return ("RENDA FIXA", "RDB")
        elif "TESOURO" in ticker or "TESOURO" in product_upper:
            return ("RENDA FIXA", "TESOURO")
        else:
            return ("RENDA FIXA", "OUTROS")
    
    # Verificar se termina com 11 (potencial FII ou ETF)
    if ticker.endswith("11"):
        # Prefixos conhecidos de ETFs
        etf_prefixes = ["BOVA", "SMAL", "IVVB", "PIBB", "DIVO", "MATB", "FIND", "HASH", "QBTC", "ETHE"]
        if any(ticker.startswith(prefix) for prefix in etf_prefixes):
            return ("ETF", "ETF")
        
        # Se contém palavras indicativas de ETF
        if "ETF" in product_upper or "INDX" in product_upper or "INDEX" in product_upper:
            return ("ETF", "ETF")
        
        # Caso contrário, é FII
        return ("FUNDO IMOBILIÁRIO", "FII")
    
    # Verificar tipo de ação pela numeração
    if len(ticker) >= 2:
        last_digit = ticker[-1]
        
        # Ações ordinárias (ON)
        if last_digit in ["3", "5", "7", "9"]:
            return ("AÇÕES", "ON")
        
        # Ações preferenciais (PN)
        if last_digit in ["4", "6", "8"]:
            return ("AÇÕES", "PN")
    
    # Padrão: ação ordinária
    return ("AÇÕES", "ON")

def import_b3_excel(file):
    logger.info(f"Iniciando importação de arquivo B3: {file.filename}")
    
    try:
        df = pd.read_excel(file.file)
        logger.debug(f"Arquivo lido com sucesso: {len(df)} linhas")
    except Exception as e:
        logger.error(f"Erro ao ler arquivo Excel: {e}")
        raise ValueError(f"Arquivo Excel inválido: {e}")

    # 1. Validação de colunas
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        logger.error(f"Colunas obrigatórias ausentes: {missing}")
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
    
    logger.debug("Validação de colunas: OK")

    # 2. Normalização
    df["Data do Negócio"] = pd.to_datetime(
        df["Data do Negócio"], format="%d/%m/%Y"
    ).dt.date.astype(str)
    logger.debug("Normalização de datas: OK")

    inserted = 0
    duplicated = 0
    assets_created = set()
    
    # Cache de ativos para evitar múltiplas consultas
    asset_cache = {}
    
    with get_db() as conn:
        cursor = conn.cursor()

        # Primeiro passo: criar todos os ativos únicos necessários
        unique_tickers = df["Código de Negociação"].unique()
        for ticker in unique_tickers:
            try:
                # Verificar se ativo já existe
                cursor.execute("SELECT id FROM assets WHERE ticker = ?", (ticker,))
                result = cursor.fetchone()
                
                if result:
                    asset_cache[ticker] = result[0]
                else:
                    # Classificar ativo automaticamente
                    asset_class, asset_type = classify_asset(ticker)
                    
                    # Criar novo ativo
                    cursor.execute("""
                        INSERT INTO assets (ticker, asset_class, asset_type, product_name, created_at, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (ticker, asset_class, asset_type, ticker, datetime.utcnow().isoformat(), "ACTIVE"))
                    asset_cache[ticker] = cursor.lastrowid
                    assets_created.add(ticker)
                    logger.debug(f"Ativo criado: {ticker} -> {asset_class}/{asset_type}")
            except Exception as e:
                logger.error(f"Erro ao criar/buscar ativo {ticker}: {e}")
                # Se já existe, buscar ID
                cursor.execute("SELECT id FROM assets WHERE ticker = ?", (ticker,))
                result = cursor.fetchone()
                if result:
                    asset_cache[ticker] = result[0]

        # Segundo passo: inserir operações
        for idx, row in df.iterrows():
            try:
                ticker = row["Código de Negociação"]
                asset_id = asset_cache.get(ticker)
                
                if not asset_id:
                    logger.warning(f"Asset ID não encontrado para ticker {ticker}, pulando linha {idx}")
                    continue
                
                cursor.execute("""
                    INSERT INTO operations (
                        asset_id,
                        trade_date,
                        movement_type,
                        market,
                        institution,
                        quantity,
                        price,
                        value,
                        created_at,
                        source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'B3')
                """, (
                    asset_id,
                    row["Data do Negócio"],
                    row["Tipo de Movimentação"],
                    row["Mercado"],
                    row["Instituição"],
                    int(row["Quantidade"]),
                    float(row["Preço"]),
                    float(row["Valor"]),
                    datetime.utcnow().isoformat()
                ))

                inserted += 1

            except sqlite3.IntegrityError:
                # Violação de UNIQUE → duplicata identificada
                duplicated += 1
                logger.debug(f"Duplicata detectada na linha {idx}")
            except Exception as e:
                # Erro inesperado: rollback automático pelo context manager
                logger.error(f"Erro ao processar linha {idx}: {str(e)}")
                raise ValueError(f"Erro ao processar linha {idx}: {str(e)}")
        
        # Context manager faz commit automático aqui
        logger.info(f"Importação concluída: {inserted} inseridas, {duplicated} duplicadas, {len(assets_created)} ativos criados")

    # 3. Resumo honesto
    return {
        "total_rows": len(df),
        "inserted": inserted,
        "duplicated": duplicated,
        "assets_created": len(assets_created),
        "unique_assets": int(df["Código de Negociação"].nunique()),
        "imported_at": datetime.utcnow().isoformat()
    }
