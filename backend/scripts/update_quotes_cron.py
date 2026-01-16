#!/usr/bin/env python3
"""
Script de atualização de cotações para execução via cron.

Uso:
    python3 backend/scripts/update_quotes_cron.py

Cron job recomendado (atualizar a cada 15 minutos durante horário de mercado):
    */15 9-18 * * 1-5 cd /path/to/portfolio-manager-v2 && python3 backend/scripts/update_quotes_cron.py
"""

import sys
import os
import logging
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.repositories import quotes_repository
from backend.app.services.market_data_service import MarketDataService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend/data/quotes_update.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


def update_all_quotes():
    """
    Atualiza todas as cotações de ativos com posição.
    """
    try:
        logger.info("=" * 60)
        logger.info(f"🔄 Iniciando atualização de cotações - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Buscar tickers que precisam atualização
        tickers = quotes_repository.get_tickers_to_update()
        
        if not tickers:
            logger.info("ℹ️  Nenhum ticker para atualizar")
            return
        
        logger.info(f"📋 {len(tickers)} tickers para atualizar: {', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''}")
        
        # Buscar cotações do yfinance
        market_service = MarketDataService()
        quotes = market_service.get_batch_quotes(tickers)
        
        # Salvar no banco
        updated_count = 0
        failed_count = 0
        
        for ticker in tickers:
            quote_data = quotes.get(ticker)
            
            if quote_data:
                if quotes_repository.save_quote(ticker, quote_data):
                    updated_count += 1
                    logger.info(f"  ✅ {ticker}: R$ {quote_data.get('price', 0):.2f}")
                else:
                    failed_count += 1
                    logger.warning(f"  ❌ {ticker}: Falha ao salvar")
            else:
                failed_count += 1
                logger.warning(f"  ⚠️  {ticker}: Cotação não disponível")
        
        logger.info(f"✅ Atualização concluída: {updated_count} sucesso, {failed_count} falhas")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "updated": updated_count,
            "failed": failed_count,
            "total": len(tickers)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro fatal na atualização de cotações: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    result = update_all_quotes()
    
    # Exit code: 0 = sucesso, 1 = falha
    sys.exit(0 if result.get("success") else 1)
