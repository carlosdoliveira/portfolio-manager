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
    
    with get_db() as conn:
        cursor = conn.cursor()

        for idx, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO operations (
                        trade_date,
                        movement_type,
                        market,
                        institution,
                        ticker,
                        quantity,
                        price,
                        value,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["Data do Negócio"],
                    row["Tipo de Movimentação"],
                    row["Mercado"],
                    row["Instituição"],
                    row["Código de Negociação"],
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
        logger.info(f"Importação concluída: {inserted} inseridas, {duplicated} duplicadas")

    # 3. Resumo honesto
    return {
        "total_rows": len(df),
        "inserted": inserted,
        "duplicated": duplicated,
        "unique_assets": int(df["Código de Negociação"].nunique()),
        "imported_at": datetime.utcnow().isoformat()
    }
