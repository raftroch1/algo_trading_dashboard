import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import asyncio
from .base_collector import BaseDataCollector

class YFinanceCollector(BaseDataCollector):
    """Data collector implementation using yfinance."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__()
        self.cache_dir = cache_dir
        
    async def fetch_data(
        self,
        symbols: Union[str, List[str]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data from Yahoo Finance.
        
        Args:
            symbols: Single symbol or list of symbols to fetch
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        """
        if isinstance(symbols, str):
            symbols = [symbols]
            
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
            
        result = {}
        for symbol in symbols:
            try:
                # Use yfinance to download data
                ticker = yf.Ticker(symbol)
                df = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=interval
                )
                
                if not df.empty:
                    df = await self.process_data(df)
                    if await self.validate_data(df):
                        result[symbol] = df
                    
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")
                continue
                
        return result
    
    async def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate the collected data.
        
        Checks:
        1. No empty DataFrame
        2. Required columns present
        3. No infinite values
        4. Limited missing values
        """
        if data.empty:
            return False
            
        required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
        if not all(col in data.columns for col in required_columns):
            return False
            
        # Check for infinite values
        if np.any(np.isinf(data[list(required_columns)].values)):
            return False
            
        # Check for limited missing values (max 10% missing)
        missing_pct = data[list(required_columns)].isnull().mean().max()
        if missing_pct > 0.1:
            return False
            
        return True
    
    async def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process the collected data.
        
        1. Handle missing values
        2. Add basic technical indicators
        3. Ensure consistent column names
        """
        # Handle missing values
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        # Ensure column names are consistent
        data.columns = data.columns.str.lower()
        
        # Add basic technical indicators
        if len(data) > 14:  # Minimum length for some indicators
            # Add trading volume moving average
            data['volume_ma'] = data['volume'].rolling(window=20).mean()
            
            # Add price moving averages
            data['ma_20'] = data['close'].rolling(window=20).mean()
            data['ma_50'] = data['close'].rolling(window=50).mean()
            
            # Add daily returns
            data['returns'] = data['close'].pct_change()
            
            # Add volatility (20-day rolling standard deviation)
            data['volatility'] = data['returns'].rolling(window=20).std()
        
        return data
