import pandas as pd
from datetime import datetime
from app.db.database import get_connection

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
    df = pd.read_excel(file.file)

    # 1. Validação de colunas
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    # 2. Normalização
    df["Data do Negócio"] = pd.to_datetime(
        df["Data do Negócio"], format="%d/%m/%Y"
    ).dt.date.astype(str)

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    duplicated = 0

    for _, row in df.iterrows():
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

        except Exception:
            # Violação de UNIQUE → duplicata
            duplicated += 1

    conn.commit()
    conn.close()

    # 3. Resumo honesto
    return {
        "total_rows": len(df),
        "inserted": inserted,
        "duplicated": duplicated,
        "unique_assets": int(df["Código de Negociação"].nunique()),
        "imported_at": datetime.utcnow().isoformat()
    }
