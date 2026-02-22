import logging
from typing import Dict, Optional
from datetime import datetime

from app.db.database import get_db

logger = logging.getLogger(__name__)


def _num(value: Optional[float], fallback: float = 0.0) -> float:
    try:
        if value is None:
            return fallback
        return float(value)
    except Exception:
        return fallback


def compute_asset_position(asset_id: int) -> Dict:
    """
    Calcula posição e preço médio de um ativo considerando eventos corporativos.

    Regras:
    - COMPRA: aumenta quantidade e custo (usa value se disponível, senão quantity*price)
    - VENDA: reduz quantidade; custo reduz por PM*q (exceto ajustes de reconciliação)
    - BONIFICACAO/DESDOBRO: aumenta quantidade com custo 0 (custo inalterado)
    - GRUPAMENTO: reduz quantidade com custo 0 (custo inalterado)
    - AJUSTE_RECONCILIACAO (source='RECONCILIATION'): ajusta apenas quantidade (custo intacto)
    - SUBSCRICAO: se value/preço disponível, trata como compra; senão custo 0
    - Ignora linhas de 'Atualização' e 'Transferência - Liquidação' (não devem existir como operações)

    Retorna: dict com quantity, total_cost, average_price, invested_value e detalhes.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, movement_type, quantity, price, value, trade_date,
                   source, operation_subtype, notes
            FROM operations
            WHERE asset_id = ? AND status = 'ACTIVE'
            ORDER BY trade_date ASC, id ASC
            """,
            (asset_id,),
        )
        rows = cursor.fetchall()

    qty = 0.0
    cost = 0.0
    total_bought_value = 0.0
    total_sold_value = 0.0

    timeline = []

    def pm() -> float:
        return (cost / qty) if qty > 0 else 0.0

    for (op_id, mtype, q, price, value, tdate, source, subtype, notes) in rows:
        q = _num(q, 0.0)
        price = _num(price, 0.0)
        value = _num(value, q * price)

        before = {"qty": qty, "cost": cost, "pm": pm()}

        # Ajuste de reconciliação: altera quantidade sem mexer no custo
        if source == "RECONCILIATION" and (subtype == "AJUSTE_RECONCILIACAO" or subtype == "RECONCILIACAO"):
            # Usa movement_type para direção
            if mtype == "COMPRA":
                qty += q
            else:
                qty -= q
            after = {"qty": qty, "cost": cost, "pm": pm()}
            timeline.append({
                "id": op_id, "date": tdate, "type": mtype, "subtype": subtype,
                "quantity": q, "price": price, "value": value,
                "before": before, "after": after, "note": "reconciliation-adjustment"
            })
            continue

        # Eventos corporativos (quantidade-only)
        if subtype in ("BONIFICACAO", "DESDOBRO"):
            qty += q
            after = {"qty": qty, "cost": cost, "pm": pm()}
            timeline.append({
                "id": op_id, "date": tdate, "type": "EVENT", "subtype": subtype,
                "quantity": q, "price": 0.0, "value": 0.0,
                "before": before, "after": after
            })
            continue
        if subtype == "GRUPAMENTO":
            qty -= q
            if qty < 0:
                qty = 0.0
            after = {"qty": qty, "cost": cost, "pm": pm()}
            timeline.append({
                "id": op_id, "date": tdate, "type": "EVENT", "subtype": subtype,
                "quantity": -q, "price": 0.0, "value": 0.0,
                "before": before, "after": after
            })
            continue
        if subtype and subtype.startswith("SUBSCRICAO"):
            # Trata como compra com custo se houver valor/preço
            buy_cost = value if value > 0 else (q * price)
            qty += q
            cost += buy_cost
            total_bought_value += buy_cost
            after = {"qty": qty, "cost": cost, "pm": pm()}
            timeline.append({
                "id": op_id, "date": tdate, "type": "COMPRA", "subtype": subtype,
                "quantity": q, "price": price, "value": buy_cost,
                "before": before, "after": after
            })
            continue

        # Operações de compra/venda
        if mtype == "COMPRA":
            buy_cost = value if value > 0 else (q * price)
            qty += q
            cost += buy_cost
            total_bought_value += buy_cost
            after = {"qty": qty, "cost": cost, "pm": pm()}
            timeline.append({
                "id": op_id, "date": tdate, "type": mtype, "subtype": subtype,
                "quantity": q, "price": price, "value": buy_cost,
                "before": before, "after": after
            })
        elif mtype == "VENDA":
            sell_value = value if value > 0 else (q * price)
            # custo reduz pelo PM vigente, exceto se for venda de ajuste (já tratada acima)
            reduce_cost = pm() * q
            qty -= q
            if qty < 0:
                qty = 0.0
            cost -= reduce_cost
            if cost < 0:
                cost = 0.0
            total_sold_value += sell_value
            after = {"qty": qty, "cost": cost, "pm": pm()}
            timeline.append({
                "id": op_id, "date": tdate, "type": mtype, "subtype": subtype,
                "quantity": -q, "price": price, "value": sell_value,
                "before": before, "after": after
            })
        else:
            # tipos diversos sem impacto na posição (ex.: Rendimento)
            timeline.append({
                "id": op_id, "date": tdate, "type": mtype, "subtype": subtype,
                "quantity": 0.0, "price": price, "value": value,
                "before": before, "after": before, "note": "ignored"
            })

    return {
        "asset_id": asset_id,
        "quantity": round(qty, 8),
        "total_cost": round(cost, 8),
        "average_price": round((cost / qty) if qty > 0 else 0.0, 8),
        "invested_value": round(total_bought_value - total_sold_value, 8),
        "events_applied": True,
        "timeline_count": len(timeline),
    }


def compute_asset_position_by_ticker(ticker: str) -> Dict:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM assets WHERE ticker = ? AND status='ACTIVE'", (ticker,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Ativo {ticker} não encontrado")
        return compute_asset_position(row[0])
