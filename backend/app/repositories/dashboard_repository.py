import logging
from app.db.database import get_db
from app.services.market_data_service import get_market_data_service

logger = logging.getLogger(__name__)


def get_dashboard_summary() -> dict:
    """
    Busca um resumo completo da carteira para o dashboard.
    
    O cálculo do valor atual da carteira (`current_value`) utiliza cotações de 
    mercado em tempo real para Ações e ETFs, obtidas via MarketDataService.
    Para outros ativos (FIIs, etc.) ou quando cotações não estão disponíveis,
    utiliza-se o valor investido como fallback.
    
    Os campos `daily_change` e `daily_change_percent` representam o lucro/prejuízo
    TOTAL acumulado da carteira (variação = current_value - total_invested), não
    a variação diária. Os nomes foram mantidos para compatibilidade com o frontend.
    
    Returns:
        Dicionário com:
        - total_assets: número total de ativos com posição
        - total_invested: valor total investido (compras - vendas)
        - current_value: valor atual da carteira calculado com cotações de mercado
                        para Ações/ETFs, valor investido para outros ativos
        - total_bought_value: soma de todas as compras
        - total_sold_value: soma de todas as vendas
        - top_positions: lista dos 5 maiores ativos por valor investido
        - recent_operations: lista das 10 operações mais recentes
        - asset_allocation: distribuição por classe de ativo
        - daily_change: lucro/prejuízo total em reais (valor atual - investido)
        - daily_change_percent: percentual de retorno sobre investimento
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Totalizadores gerais
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT a.id) as total_assets,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.value ELSE 0 END), 0) as total_bought,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.value ELSE 0 END), 0) as total_sold
            FROM assets a
            LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
            WHERE a.status = 'ACTIVE'
        """)
        
        row = cursor.fetchone()
        total_assets = row[0] if row else 0
        total_bought_value = row[1] if row else 0
        total_sold_value = row[2] if row else 0
        total_invested = total_bought_value - total_sold_value
        
        # 2. Top 5 posições por valor investido
        cursor.execute("""
            SELECT 
                a.id,
                a.ticker,
                a.asset_class,
                a.product_name,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.quantity ELSE 0 END), 0) as total_bought,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.quantity ELSE 0 END), 0) as total_sold,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.value ELSE 0 END), 0) as bought_value,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.value ELSE 0 END), 0) as sold_value
            FROM assets a
            LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
            WHERE a.status = 'ACTIVE'
            GROUP BY a.id, a.ticker, a.asset_class, a.product_name
            HAVING (total_bought - total_sold) > 0
            ORDER BY (bought_value - sold_value) DESC
            LIMIT 5
        """)
        
        top_positions = []
        for row in cursor.fetchall():
            current_position = row[4] - row[5]
            net_value = row[6] - row[7]
            average_price = net_value / current_position if current_position > 0 else 0
            
            top_positions.append({
                "id": row[0],
                "ticker": row[1],
                "asset_class": row[2],
                "product_name": row[3],
                "quantity": current_position,
                "invested_value": net_value,
                "average_price": average_price
            })
        
        # 3. Operações recentes (últimas 10)
        cursor.execute("""
            SELECT 
                o.id,
                o.asset_id,
                a.ticker,
                a.asset_class,
                a.product_name,
                o.movement_type,
                o.quantity,
                o.price,
                o.value,
                o.trade_date,
                o.market,
                o.source
            FROM operations o
            INNER JOIN assets a ON o.asset_id = a.id
            WHERE o.status = 'ACTIVE'
            ORDER BY o.trade_date DESC, o.id DESC
            LIMIT 10
        """)
        
        recent_operations = []
        for row in cursor.fetchall():
            recent_operations.append({
                "id": row[0],
                "asset_id": row[1],
                "ticker": row[2],
                "asset_class": row[3],
                "product_name": row[4],
                "movement_type": row[5],
                "quantity": row[6],
                "price": row[7],
                "value": row[8],
                "trade_date": row[9],
                "market": row[10],
                "source": row[11]
            })
        
        # 4. Distribuição por classe de ativo
        cursor.execute("""
            SELECT 
                a.asset_class,
                COUNT(DISTINCT a.id) as count,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.value ELSE 0 END), 0) as bought_value,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.value ELSE 0 END), 0) as sold_value
            FROM assets a
            LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
            WHERE a.status = 'ACTIVE'
            GROUP BY a.asset_class
            HAVING (bought_value - sold_value) > 0
            ORDER BY (bought_value - sold_value) DESC
        """)
        
        asset_allocation = []
        for row in cursor.fetchall():
            net_value = row[2] - row[3]
            percentage = (net_value / total_invested * 100) if total_invested > 0 else 0
            
            asset_allocation.append({
                "asset_class": row[0],
                "count": row[1],
                "value": net_value,
                "percentage": round(percentage, 2)
            })
        
        # 5. Calcular valor atual da carteira com cotações
        market_service = get_market_data_service()
        current_value = 0
        quotes_found = False
        tickers_with_positions = []
        
        logger.info("💰 Calculando valor atual da carteira com cotações...")
        
        # Buscar todos os ativos com posição para pegar cotações
        try:
            sql_query = """
                SELECT 
                    a.ticker,
                    COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.quantity ELSE 0 END), 0) as total_bought,
                    COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.quantity ELSE 0 END), 0) as total_sold,
                    COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.value ELSE 0 END), 0) as bought_value,
                    COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.value ELSE 0 END), 0) as sold_value
                FROM assets a
                LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
                WHERE a.status = 'ACTIVE' AND (a.asset_class = 'AÇÕES' OR a.asset_class = 'ETF')
                GROUP BY a.ticker
                HAVING (total_bought - total_sold) > 0
            """
            cursor.execute(sql_query)
            
            rows = cursor.fetchall()
            logger.info(f"🔎 Query retornou {len(rows)} linhas")
            
            for row in rows:
                ticker = row[0]
                current_position = row[1] - row[2]
                invested_value = row[3] - row[4]
                tickers_with_positions.append((ticker, current_position, invested_value))
                logger.info(f"  🎯 {ticker}: posição={current_position}, investido=R$ {invested_value:.2f}")
        except Exception as e:
            logger.error(f"❌ Erro ao buscar ações: {e}", exc_info=True)
        
        logger.info(f"📈 Encontrados {len(tickers_with_positions)} ativos com posição em ações")
        
        # Buscar cotações em lote
        if tickers_with_positions:
            tickers = [t[0] for t in tickers_with_positions]
            logger.info(f"🔍 Buscando cotações para: {', '.join(tickers[:5])}{'...' if len(tickers) > 5 else ''}")
            quotes = market_service.get_batch_quotes(tickers)
            logger.info(f"✅ Recebidas {len([q for q in quotes.values() if q])} cotações válidas de {len(tickers)} tickers")
            
            for ticker, position, invested in tickers_with_positions:
                quote = quotes.get(ticker)
                if quote and quote.get('price'):
                    # Usar cotação atual
                    market_value = position * quote['price']
                    current_value += market_value
                    quotes_found = True
                    logger.info(f"  📊 {ticker}: {position} x R$ {quote['price']:.2f} = R$ {market_value:.2f} (investido: R$ {invested:.2f})")
                else:
                    # Se não tiver cotação, usar valor investido
                    current_value += invested
                    logger.info(f"  ⚠️  {ticker}: sem cotação, usando valor investido R$ {invested:.2f}")
        
        # Para fundos imobiliários e outros ativos, usar valor investido
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'COMPRA' THEN o.value ELSE 0 END), 0) as bought,
                COALESCE(SUM(CASE WHEN UPPER(o.movement_type) = 'VENDA' THEN o.value ELSE 0 END), 0) as sold
            FROM operations o
            INNER JOIN assets a ON a.id = o.asset_id
            WHERE a.status = 'ACTIVE' AND a.asset_class NOT IN ('AÇÕES', 'ETF') AND o.status = 'ACTIVE'
        """)
        other_value_row = cursor.fetchone()
        if other_value_row:
            other_value = other_value_row[0] - other_value_row[1]
            current_value += other_value
            logger.info(f"💼 Outros ativos (FIIs, etc): R$ {other_value:.2f}")
        
        # Se não encontrou nenhuma cotação válida para ações/ETFs, usar valor investido total
        if not quotes_found and current_value == 0:
            current_value = total_invested
            logger.warning("⚠️  Nenhuma cotação encontrada, usando valor investido total")
        
        # 6. Calcular variação (lucro/prejuízo total)
        variation = current_value - total_invested
        variation_percent = (variation / total_invested * 100) if total_invested > 0 else 0
        
        logger.info(f"Dashboard summary: {total_assets} ativos, R$ {total_invested:.2f} investido, R$ {current_value:.2f} atual, variação: R$ {variation:.2f} ({variation_percent:.2f}%)")
        
        return {
            "total_assets": total_assets,
            "total_invested": total_invested,
            "current_value": current_value,
            "total_bought_value": total_bought_value,
            "total_sold_value": total_sold_value,
            "top_positions": top_positions,
            "recent_operations": recent_operations,
            "asset_allocation": asset_allocation,
            # ATENÇÃO: estes campos representam lucro/prejuízo TOTAL acumulado,
            # não variação diária. Os nomes foram mantidos por compatibilidade com frontend legado.
            "daily_change": variation,
            "daily_change_percent": variation_percent
        }
