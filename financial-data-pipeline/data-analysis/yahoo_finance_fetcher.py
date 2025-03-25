import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

class YahooFinanceDataFetcher:
    """
    A class to fetch financial data from Yahoo Finance.
    """
    
    def __init__(self):
        """Initialize the data fetcher."""
        pass
    
    def get_historical_data(self, ticker, period="1mo", interval="1d"):
        """
        Get historical stock data.
        
        Parameters:
        - ticker (str): Stock symbol (e.g., 'AAPL', 'MSFT')
        - period (str): Data period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '5y', 'max')
        - interval (str): Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
        - dict: JSON-serializable dictionary of historical data
        """
        try:
            data = yf.Ticker(ticker).history(period=period, interval=interval)
            
            data = data.reset_index()
            
            if isinstance(data['Date'].iloc[0], datetime):
                data['Date'] = data['Date'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            
            result = {
                'ticker': ticker,
                'period': period,
                'interval': interval,
                'data': data.to_dict(orient='records')
            }
            
            return result
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_real_time_price(self, ticker):
        """
        Get the latest price for a stock.
        
        Parameters:
        - ticker (str): Stock symbol (e.g., 'AAPL', 'MSFT')
        
        Returns:
        - dict: Latest price data
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d')
            
            if data.empty:
                return {'error': f'No data found for ticker {ticker}'}
            
            latest_price = data['Close'].iloc[-1]
            
            info = stock.info
            
            result = {
                'ticker': ticker,
                'price': latest_price,
                'currency': info.get('currency', 'USD'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'change': data['Close'].iloc[-1] - data['Open'].iloc[-1],
                'change_percent': ((data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100
            }
            
            return result
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_multiple_tickers(self, tickers):
        """
        Get latest data for multiple tickers.
        
        Parameters:
        - tickers (list): List of stock symbols
        
        Returns:
        - dict: Data for all tickers
        """
        result = {}
        for ticker in tickers:
            result[ticker] = self.get_real_time_price(ticker)
        
        return result
    
    def get_company_info(self, ticker):
        """
        Get company information.
        
        Parameters:
        - ticker (str): Stock symbol
        
        Returns:
        - dict: Company information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            relevant_info = {
                'ticker': ticker,
                'name': info.get('shortName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'country': info.get('country', ''),
                'website': info.get('website', ''),
                'market_cap': info.get('marketCap', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'description': info.get('longBusinessSummary', '')
            }
            
            return relevant_info
        
        except Exception as e:
            return {'error': str(e)}


if __name__ == "__main__":
    fetcher = YahooFinanceDataFetcher()
    
    apple_data = fetcher.get_historical_data('AAPL', period='1mo', interval='1d')
    print(json.dumps(apple_data, indent=2)[:1000] + "...\n")
    
    msft_price = fetcher.get_real_time_price('MSFT')
    print(json.dumps(msft_price, indent=2))
    
    multi_data = fetcher.get_multiple_tickers(['AAPL', 'MSFT', 'GOOGL'])
    print(json.dumps(multi_data, indent=2))
    
    tesla_info = fetcher.get_company_info('TSLA')
    print(json.dumps(tesla_info, indent=2))

