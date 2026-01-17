"""
Serviço de cotações de mercado usando yfinance.

Responsável por buscar cotações em tempo quase real da B3,
com cache persistente (banco de dados) para evitar requisições excessivas.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from app.repositories import quotes_repository


class MarketDataService:
    """
    Serviço para buscar cotações de ativos da B3 usando Yahoo Finance.
    
    Cache: 15 minutos (delay típico do Yahoo Finance para dados gratuitos)
    """
    
    def __init__(self, cache_ttl_minutes: int = 15):
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = timedelta(minutes=cache_ttl_minutes)
    
    def _is_cache_valid(self, ticker: str) -> bool:
        """Verifica se o cache em memória está válido para o ticker."""
        if ticker not in self._cache:
            return False
        
        cached_time = self._cache[ticker].get('cached_at')
        if not cached_time:
            return False
        
        return datetime.now() - cached_time < self._cache_ttl
    
    def _is_db_cache_valid(self, quote: Dict) -> bool:
        """Verifica se o cache do banco de dados está válido."""
        if not quote or 'updated_at' not in quote:
            return False
        
        try:
            updated_at = datetime.fromisoformat(quote['updated_at'])
            return datetime.now() - updated_at < self._cache_ttl
        except (ValueError, TypeError):
            return False
    
    def _normalize_ticker(self, ticker: str) -> str:
        """
        Normaliza ticker para o formato do Yahoo Finance.
        
        Exemplo: PETR4 -> PETR4.SA
        """
        ticker = ticker.upper().strip()
        if not ticker.endswith('.SA'):
            ticker = f'{ticker}.SA'
        return ticker
    
    def get_quote(self, ticker: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Busca cotação de um ativo específico.
        
        Estratégia:
        1. Verificar cache em memória (se válido, retornar)
        2. Verificar cache persistente no banco (se válido, retornar)
        3. Buscar do yfinance e salvar no banco
        
        Args:
            ticker: Código do ativo (ex: PETR4, PETR4.SA)
            force_refresh: Se True, força atualização do yfinance ignorando cache
        
        Returns:
            Dict com dados da cotação ou None se não encontrado
            
        Exemplo de retorno:
        {
            'ticker': 'PETR4',
            'price': 38.50,
            'change': 0.85,
            'change_percent': 2.26,
            'volume': 25000000,
            'open': 37.80,
            'high': 38.90,
            'low': 37.65,
            'previous_close': 37.65,
            'updated_at': '2026-01-06T15:30:00',
            'source': 'yfinance'
        }
        """
        # Normalizar ticker
        ticker_normalized = self._normalize_ticker(ticker)
        original_ticker = ticker.upper().replace('.SA', '')
        
        # Se não forçar refresh, verificar cache em memória
        if not force_refresh and self._is_cache_valid(original_ticker):
            return self._cache[original_ticker]['data']
        
        # Verificar cache persistente (banco de dados)
        if not force_refresh:
            db_quote = quotes_repository.get_quote(original_ticker)
            if db_quote and self._is_db_cache_valid(db_quote):
                # Cachear em memória também
                self._cache[original_ticker] = {
                    'data': db_quote,
                    'cached_at': datetime.now()
                }
                return db_quote
        
        try:
            # Buscar dados do yfinance
            stock = yf.Ticker(ticker_normalized)
            hist = stock.history(period='1d')
            
            if hist.empty:
                return None
            
            # Extrair dados do último pregão
            last_row = hist.iloc[-1]
            last_timestamp = hist.index[-1]
            
            # Validar dados essenciais
            if not last_row['Close'] or last_row['Close'] == 0:
                print(f"Cotação inválida para {ticker_normalized}: preço zero ou nulo")
                return None
            
            # Calcular variação
            previous_close = last_row['Close']
            current_price = last_row['Close']
            
            # Tentar pegar previous_close do info (com tratamento de erro)
            try:
                info = stock.info
                if info and 'previousClose' in info and info['previousClose']:
                    previous_close = info['previousClose']
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                else:
                    change = 0
                    change_percent = 0
            except Exception:
                # Se falhar ao buscar info, usar valores padrão
                change = 0
                change_percent = 0
            
            quote_data = {
                'ticker': original_ticker,
                'price': round(float(current_price), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_percent), 2),
                'volume': int(last_row['Volume']),
                'open': round(float(last_row['Open']), 2),
                'high': round(float(last_row['High']), 2),
                'low': round(float(last_row['Low']), 2),
                'previous_close': round(float(previous_close), 2),
                'updated_at': last_timestamp.isoformat(),
                'source': 'yfinance'
            }
            
            # Salvar no banco de dados (cache persistente)
            quotes_repository.save_quote(original_ticker, quote_data)
            
            # Cachear em memória também
            self._cache[original_ticker] = {
                'data': quote_data,
                'cached_at': datetime.now()
            }
            
            return quote_data
            
        except Exception as e:
            print(f"Erro ao buscar cotação de {ticker_normalized}: {str(e)}")
            return None
    
    def get_batch_quotes(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Busca cotações de múltiplos ativos.
        
        Args:
            tickers: Lista de códigos de ativos
        
        Returns:
            Dicionário com ticker -> dados da cotação
            
        Exemplo:
        {
            'PETR4': {...},
            'VALE3': {...},
            'INVALID': None
        }
        """
        results = {}
        
        for ticker in tickers:
            ticker_clean = ticker.upper().replace('.SA', '')
            results[ticker_clean] = self.get_quote(ticker)
        
        return results
    
    def clear_cache(self, ticker: Optional[str] = None):
        """
        Limpa o cache de cotações.
        
        Args:
            ticker: Se fornecido, limpa apenas o cache deste ticker.
                   Se None, limpa todo o cache.
        """
        if ticker:
            ticker_clean = ticker.upper().replace('.SA', '')
            if ticker_clean in self._cache:
                del self._cache[ticker_clean]
        else:
            self._cache.clear()


# Instância singleton do serviço
_market_data_service = None


def get_market_data_service() -> MarketDataService:
    """Retorna instância singleton do MarketDataService."""
    global _market_data_service
    
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    
    return _market_data_service
