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

# Colunas do arquivo de Movimentação (não apenas negociação)
MOVIMENTACAO_COLUMNS = [
    "Data",
    "Movimentação",
    "Produto",
    "Instituição",
    "Quantidade",
    "Preço unitário",
    "Valor da Operação",
]

def is_real_operation(row: pd.Series) -> bool:
    """
    Determina se um registro do arquivo de movimentação é uma operação real
    ou apenas um snapshot/atualização de saldo.
    
    CRÍTICO: Arquivo de movimentação contém "Atualização" que são snapshots
    de posição após eventos corporativos, NÃO são operações reais!
    
    Args:
        row: Linha do DataFrame de movimentação
    
    Returns:
        True se é operação real (deve ser importada)
        False se é snapshot/informativo (deve ser ignorado)
    """
    movimentacao = str(row.get('Movimentação', '')).strip()
    
    # Atualização de saldo = snapshot após evento corporativo
    # NÃO É OPERAÇÃO REAL, apenas registro informativo!
    if 'Atualização' in movimentacao or 'Atualizacao' in movimentacao:
        return False
    
    # Rendimento de dividendos/JCP sem movimentação de quantidade
    # (apenas crédito em conta, não altera posição de ações)
    if 'Rendimento' in movimentacao:
        quantidade = row.get('Quantidade', 0)
        if quantidade == 0 or pd.isna(quantidade):
            return False
    
    # Bonificação com quantidade > 0 É operação real (adiciona ações)
    if 'Bonificação' in movimentacao or 'Bonificacao' in movimentacao:
        quantidade = row.get('Quantidade', 0)
        if quantidade > 0:
            return True
    
    # Desdobro é operação real
    if 'Desdobro' in movimentacao:
        return True
    
    # Compra/Venda tradicionais (Credito/Debito)
    entrada_saida = row.get('Entrada/Saída', '')
    if entrada_saida in ['Credito', 'Debito']:
        return True
    
    # Transferências e subscrições
    if any(x in movimentacao for x in ['Transferência', 'Transferencia', 'Subscri']):
        return True
    
    # Default: se não identificou, não importar (seguro)
    return False

def detect_corporate_events(df: pd.DataFrame) -> list:
    """
    Detecta eventos corporativos no DataFrame do extrato B3.
    
    Retorna lista de eventos detectados:
    - Bonificações (preço = 0, movimento específico)
    - Desdobros (quantidade exata duplicada)
    - Atualizações de saldo
    - Leilões de fração
    
    Args:
        df: DataFrame com dados do Excel B3
    
    Returns:
        Lista de dicionários com eventos detectados
    """
    events = []
    
    # Verificar se coluna Movimentação existe
    movimentacao_col = None
    for col in df.columns:
        if 'movimenta' in col.lower():
            movimentacao_col = col
            break
    
    if not movimentacao_col:
        logger.warning("Coluna 'Movimentação' não encontrada, pulando detecção de eventos")
        return events
    
    logger.info(f"Detectando eventos corporativos em {len(df)} registros")
    
    # 1. Detectar Bonificações
    bonificacoes = df[df[movimentacao_col].str.contains('Bonificação', case=False, na=False)]
    for idx, row in bonificacoes.iterrows():
        ticker = row.get("Código de Negociação", "")
        events.append({
            "type": "BONIFICACAO",
            "ticker": ticker,
            "quantity": float(row.get("Quantidade", 0)),
            "date": row.get("Data do Negócio", ""),
            "description": f"Bonificação detectada: {row.get(movimentacao_col, '')}",
            "original_row": idx
        })
    
    # 2. Detectar Desdobros
    desdobros = df[df[movimentacao_col].str.contains('Desdobro', case=False, na=False)]
    for idx, row in desdobros.iterrows():
        ticker = row.get("Código de Negociação", "")
        events.append({
            "type": "DESDOBRO",
            "ticker": ticker,
            "quantity": float(row.get("Quantidade", 0)),
            "date": row.get("Data do Negócio", ""),
            "description": f"Desdobro detectado: {row.get(movimentacao_col, '')}",
            "original_row": idx
        })
    
    # 3. Detectar Atualizações (eventos externos)
    atualizacoes = df[df[movimentacao_col].str.contains('Atualização', case=False, na=False)]
    for idx, row in atualizacoes.iterrows():
        ticker = row.get("Código de Negociação", "")
        events.append({
            "type": "CORRECAO",
            "ticker": ticker,
            "quantity": float(row.get("Quantidade", 0)),
            "date": row.get("Data do Negócio", ""),
            "description": f"Atualização de saldo: {row.get(movimentacao_col, '')}",
            "original_row": idx
        })
    
    # 4. Detectar Leilões de Fração
    leiloes = df[df[movimentacao_col].str.contains('Leilão de Fração', case=False, na=False)]
    for idx, row in leiloes.iterrows():
        ticker = row.get("Código de Negociação", "")
        # Leilões são vendas, geralmente quantidade negativa
        qty = float(row.get("Quantidade", 0))
        events.append({
            "type": "CORRECAO",  # Tratamos como correção pois não altera PM
            "ticker": ticker,
            "quantity": qty,
            "date": row.get("Data do Negócio", ""),
            "description": f"Leilão de fração: venda de {abs(qty)} fracionárias",
            "original_row": idx,
            "skip": True  # Flag para não criar ajuste (já é operação normal)
        })
    
    # 5. Detectar Subscrições
    subscricoes = df[df[movimentacao_col].str.contains('Direito de Subscrição|Subscrição', case=False, na=False)]
    for idx, row in subscricoes.iterrows():
        ticker = row.get("Código de Negociação", "")
        events.append({
            "type": "SUBSCRICAO",
            "ticker": ticker,
            "quantity": float(row.get("Quantidade", 0)),
            "date": row.get("Data do Negócio", ""),
            "description": f"Subscrição detectada: {row.get(movimentacao_col, '')}",
            "original_row": idx
        })
    
    logger.info(f"Eventos detectados: {len(events)} ({len(bonificacoes)} bonificações, {len(desdobros)} desdobros, {len(atualizacoes)} atualizações)")
    
    return events

def normalize_ticker(ticker: str, market: str) -> str:
    """
    Normaliza ticker para consolidar mercado fracionário e à vista.
    
    No mercado brasileiro:
    - Mercado à Vista: ABEV3, PETR4, VALE3
    - Mercado Fracionário: ABEV3F, PETR4F, VALE3F
    
    Esta função remove o sufixo 'F' de tickers fracionários para que
    ambos os mercados sejam consolidados em um único ativo.
    
    Args:
        ticker: Código de negociação (ex: ABEV3F)
        market: Tipo de mercado (ex: MERCADO FRACIONARIO)
    
    Returns:
        Ticker normalizado (ex: ABEV3)
    
    Examples:
        >>> normalize_ticker("ABEV3F", "MERCADO FRACIONARIO")
        "ABEV3"
        >>> normalize_ticker("ABEV3", "MERCADO A VISTA")
        "ABEV3"
        >>> normalize_ticker("HGLG11", "MERCADO A VISTA")
        "HGLG11"
    """
    ticker = ticker.strip().upper()
    market = (market or "").strip().upper()
    
    # Normalizar mercado fracionário (aceita com ou sem acento)
    # B3 usa "Mercado Fracionário" com acento
    market_normalized = market.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    
    # Apenas normalizar se for mercado fracionário e terminar com F
    if "FRACIONARIO" in market_normalized and ticker.endswith("F"):
        # Remover apenas o último caractere 'F'
        normalized = ticker[:-1]
        logger.debug(f"Ticker normalizado: {ticker} -> {normalized} (mercado: {market})")
        return normalized
    
    return ticker

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

    # 1. Detectar tipo de arquivo e normalizar colunas
    is_movimentacao = "Movimentação" in df.columns
    is_negociacao = "Data do Negócio" in df.columns
    
    if is_movimentacao:
        logger.info("Detectado arquivo de MOVIMENTAÇÃO")
        # Validar colunas de movimentação
        missing = [c for c in MOVIMENTACAO_COLUMNS if c not in df.columns]
        if missing:
            logger.error(f"Colunas obrigatórias ausentes: {missing}")
            raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
        
        # Normalizar colunas para formato padrão
        df = df.rename(columns={
            "Data": "Data do Negócio",
            "Produto": "Código de Negociação",
            "Preço unitário": "Preço",
            "Valor da Operação": "Valor"
        })
        
        # CRÍTICO: Extrair apenas o código de negociação de ações/FIIs/ETFs
        # Formato: "ITSA4 - ITAUSA S.A." -> "ITSA4"
        # Renda fixa: "CDB - CDB124AUGT1 - BANCO X" -> "CDB124AUGT1"
        # Renda fixa sem " - ": mantém nome completo
        def extract_ticker(produto):
            if pd.isna(produto):
                return produto
            produto_str = str(produto).strip()
            
            if " - " not in produto_str:
                # Não tem separador, retornar como está
                return produto_str
            
            parts = produto_str.split(" - ")
            
            # Se começa com tipo de renda fixa (CDB, LCI, LCA, CRI, CRA, Debênture)
            if parts[0] in ["CDB", "LCI", "LCA", "CRI", "CRA", "Debênture", "Debenture"]:
                # Retornar segunda parte (código do produto)
                return parts[1].strip() if len(parts) > 1 else produto_str
            else:
                # Ações, FIIs, ETFs: retornar apenas o código (primeira parte)
                return parts[0].strip()
        
        df["Código de Negociação"] = df["Código de Negociação"].apply(extract_ticker)
        
        logger.info(f"Extração de tickers concluída. Exemplos: {df['Código de Negociação'].head(5).tolist()}")
        
        # Mapear Entrada/Saída para Tipo de Movimentação
        df["Tipo de Movimentação"] = df["Entrada/Saída"].apply(
            lambda x: "Compra" if x == "Credito" else "Venda"
        )
        
        # Definir mercado como vazio (não existe no arquivo de movimentação)
        df["Mercado"] = ""
        
        # Tratar preços vazios (traço ou NaN) = 0
        df["Preço"] = df["Preço"].replace("-", "0").fillna("0")
        df["Valor"] = df["Valor"].replace("-", "0").fillna("0")
        
        logger.debug("Normalização de colunas de movimentação: OK")
        
    elif is_negociacao:
        logger.info("Detectado arquivo de NEGOCIAÇÃO")
        # Validar colunas de negociação
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            logger.error(f"Colunas obrigatórias ausentes: {missing}")
            raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
    else:
        logger.error("Tipo de arquivo não reconhecido")
        raise ValueError("Arquivo não é nem de Negociação nem de Movimentação B3")
    
    logger.debug("Validação de colunas: OK")

    # 2. Normalização de datas
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
        # IMPORTANTE: normalizar tickers antes de processar
        unique_tickers_raw = df["Código de Negociação"].unique()
        unique_tickers_normalized = set()
        
        # Criar mapeamento ticker_original -> ticker_normalizado
        ticker_normalization_map = {}
        for idx, row in df.iterrows():
            ticker_raw = row["Código de Negociação"]
            market = row["Mercado"]
            ticker_normalized = normalize_ticker(ticker_raw, market)
            ticker_normalization_map[ticker_raw] = ticker_normalized
            unique_tickers_normalized.add(ticker_normalized)
        
        logger.info(f"Tickers únicos (antes normalização): {len(unique_tickers_raw)}")
        logger.info(f"Tickers únicos (após normalização): {len(unique_tickers_normalized)}")
        
        for ticker in unique_tickers_normalized:
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
        skipped_updates = 0
        for idx, row in df.iterrows():
            try:
                # CRÍTICO: Filtrar operações não-reais (snapshots de saldo)
                if not is_real_operation(row):
                    skipped_updates += 1
                    logger.debug(f"Linha {idx} pulada: não é operação real (snapshot/atualização)")
                    continue
                
                ticker_raw = row["Código de Negociação"]
                ticker_normalized = ticker_normalization_map.get(ticker_raw, ticker_raw)
                asset_id = asset_cache.get(ticker_normalized)
                
                if not asset_id:
                    logger.warning(f"Asset ID não encontrado para ticker {ticker_normalized} (original: {ticker_raw}), pulando linha {idx}")
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
                    row["Tipo de Movimentação"].upper(),  # Normalizar para COMPRA/VENDA
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
        logger.info(f"Importação concluída: {inserted} inseridas, {duplicated} duplicadas, {skipped_updates} atualizações ignoradas, {len(assets_created)} ativos criados")

    # 4. Detectar eventos corporativos
    corporate_events = detect_corporate_events(df)

    # 3. Resumo honesto
    return {
        "total_rows": len(df),
        "inserted": inserted,
        "duplicated": duplicated,
        "skipped_non_operations": skipped_updates,
        "assets_created": len(assets_created),
        "unique_assets": int(df["Código de Negociação"].nunique()),
        "imported_at": datetime.utcnow().isoformat(),
        "corporate_events": corporate_events,
        "events_detected": len(corporate_events)
    }
