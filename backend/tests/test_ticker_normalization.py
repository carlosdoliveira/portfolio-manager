"""
Testes para a função de normalização de tickers.
"""

import pytest
from app.services.importer import normalize_ticker


class TestNormalizeTicker:
    """Testes para normalização de tickers fracionários e à vista."""
    
    def test_normalize_fractional_market_with_f(self):
        """Deve remover F de ticker fracionário."""
        result = normalize_ticker("ABEV3F", "MERCADO FRACIONARIO")
        assert result == "ABEV3"
    
    def test_normalize_fractional_lowercase(self):
        """Deve funcionar com mercado em lowercase."""
        result = normalize_ticker("PETR4F", "mercado fracionario")
        assert result == "PETR4"
    
    def test_normalize_fractional_mixed_case(self):
        """Deve funcionar com mercado em mixed case."""
        result = normalize_ticker("VALE3F", "Mercado Fracionário")
        assert result == "VALE3"
    
    def test_keep_vista_market_unchanged(self):
        """Não deve alterar ticker do mercado à vista."""
        result = normalize_ticker("ABEV3", "MERCADO A VISTA")
        assert result == "ABEV3"
    
    def test_keep_fii_with_f_in_name(self):
        """Não deve alterar FII mesmo que tenha F no nome."""
        # FIIs não são mercado fracionário, então não devem ser normalizados
        result = normalize_ticker("HFOF11", "MERCADO A VISTA")
        assert result == "HFOF11"
    
    def test_keep_ticker_without_f_in_fractional(self):
        """Não deve alterar ticker sem F mesmo em mercado fracionário."""
        result = normalize_ticker("VALE3", "MERCADO FRACIONARIO")
        assert result == "VALE3"
    
    def test_normalize_strips_whitespace(self):
        """Deve remover espaços em branco do ticker."""
        result = normalize_ticker("  ABEV3F  ", "MERCADO FRACIONARIO")
        assert result == "ABEV3"
    
    def test_normalize_uppercase_ticker(self):
        """Deve converter ticker para uppercase."""
        result = normalize_ticker("abev3f", "MERCADO FRACIONARIO")
        assert result == "ABEV3"
    
    def test_handle_empty_market(self):
        """Deve lidar com mercado vazio sem erro."""
        result = normalize_ticker("ABEV3F", "")
        assert result == "ABEV3F"  # Não normaliza se mercado não for identificado
    
    def test_handle_none_market(self):
        """Deve lidar com mercado None sem erro."""
        result = normalize_ticker("ABEV3F", None)
        assert result == "ABEV3F"  # Não normaliza se mercado for None
    
    def test_multiple_f_in_ticker(self):
        """Deve remover apenas o último F."""
        # Caso hipotético: ticker com F no meio
        result = normalize_ticker("FESA4F", "MERCADO FRACIONARIO")
        assert result == "FESA4"  # Remove apenas o F final
    
    def test_common_tickers_fractional(self):
        """Deve normalizar tickers comuns do mercado fracionário."""
        test_cases = [
            ("PETR4F", "MERCADO FRACIONARIO", "PETR4"),
            ("VALE3F", "MERCADO FRACIONARIO", "VALE3"),
            ("ITUB4F", "MERCADO FRACIONARIO", "ITUB4"),
            ("BBDC4F", "MERCADO FRACIONARIO", "BBDC4"),
            ("BBAS3F", "MERCADO FRACIONARIO", "BBAS3"),
        ]
        
        for ticker, market, expected in test_cases:
            result = normalize_ticker(ticker, market)
            assert result == expected, f"Failed for {ticker}"
    
    def test_common_tickers_vista(self):
        """Não deve alterar tickers comuns do mercado à vista."""
        test_cases = [
            ("PETR4", "MERCADO A VISTA", "PETR4"),
            ("VALE3", "MERCADO A VISTA", "VALE3"),
            ("ITUB4", "MERCADO A VISTA", "ITUB4"),
            ("BBDC4", "MERCADO A VISTA", "BBDC4"),
            ("BBAS3", "MERCADO A VISTA", "BBAS3"),
        ]
        
        for ticker, market, expected in test_cases:
            result = normalize_ticker(ticker, market)
            assert result == expected, f"Failed for {ticker}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
