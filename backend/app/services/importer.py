
import pandas as pd
from app.db.database import get_connection

def import_b3_excel(upload_file):
    df = pd.read_excel(upload_file.file)
    conn = get_connection()

    imported = 0
    for _, row in df.iterrows():
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM investments
            WHERE asset = ? AND date = ? AND quantity = ?
            """,
            (row['Ativo'], str(row['Data']), row['Quantidade'])
        )
        exists = cursor.fetchone()[0]

        if not exists:
            cursor.execute(
                """
                INSERT INTO investments (asset, asset_type, quantity, price, date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row['Ativo'],
                    row.get('Tipo', 'Desconhecido'),
                    row['Quantidade'],
                    row['Preco'],
                    str(row['Data'])
                )
            )
            imported += 1

    conn.commit()
    conn.close()
    return imported
