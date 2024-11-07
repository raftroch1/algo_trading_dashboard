from typing import List, Dict, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

class DataValidator:
    """Utility class for data validation and quality checks."""
    
    @staticmethod
    def check_timeseries_continuity(
        data: pd.DataFrame,
        interval: str,
        max_gaps: int = 5
    ) -> bool:
        """
        Check if the time series has significant gaps.
        
        Args:
            data: DataFrame with datetime index
            interval: Expected interval between data points
            max_gaps: Maximum number of allowed gaps
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            return False
            
        # Create expected date range
        expected_range = pd.date_range(
            start=data.index.min(),
            end=data.index.max(),
            freq=interval
        )
        
        # Count missing dates
        missing_dates = expected_range.difference(data.index)
        return len(missing_dates) <= max_gaps
    
    @staticmethod
    def check_price_validity(
        data: pd.DataFrame,
        price_cols: List[str] = ['open', 'high', 'low', 'close']
    ) -> bool:
        """
        Check if price data is valid.
        
        Args:
            data: DataFrame containing price data
            price_cols: List of price column names
        """
        if not all(col in data.columns for col in price_cols):
            return False
            
        # Check for negative prices
        if (data[price_cols] < 0).any().any():
            return False
            
        # Check high/low relationship
        if 'high' in price_cols and 'low' in price_cols:
            if not (data['high'] >= data['low']).all():
                return False
                
        # Check for unrealistic price changes (>50% in one period)
        for col in price_cols:
            pct_change = data[col].pct_change().abs()
            if (pct_change > 0.5).any():
                return False
                
        return True
    
    @staticmethod
    def check_volume_validity(data: pd.DataFrame) -> bool:
        """Check if volume data is valid."""
        if 'volume' not in data.columns:
            return False
            
        # Check for negative volume
        if (data['volume'] < 0).any():
            return False
            
        # Check for unrealistic volume spikes (>1000% of moving average)
        volume_ma = data['volume'].rolling(window=20).mean()
        volume_ratio = data['volume'] / volume_ma
        if (volume_ratio > 10).any():
            return False
            
        return True
    
    @staticmethod
    def check_data_quality(
        data: pd.DataFrame,
        required_columns: List[str],
        min_rows: int = 100
    ) -> Dict[str, Union[bool, str]]:
        """
        Comprehensive data quality check.
        
        Args:
            data: DataFrame to validate
            required_columns: List of required column names
            min_rows: Minimum number of rows required
            
        Returns:
            Dictionary containing validation results and messages
        """
        results = {
            'valid': True,
            'message': 'Data validation passed'
        }
        
        # Check basic requirements
        if data.empty:
            results.update({'valid': False, 'message': 'Empty DataFrame'})
            return results
            
        if len(data) < min_rows:
            results.update({
                'valid': False,
                'message': f'Insufficient data: {len(data)} rows < {min_rows} required'
            })
            return results
            
        # Check required columns
        missing_cols = set(required_columns) - set(data.columns)
        if missing_cols:
            results.update({
                'valid': False,
                'message': f'Missing required columns: {missing_cols}'
            })
            return results
            
        # Check for duplicate indices
        if data.index.duplicated().any():
            results.update({
                'valid': False,
                'message': 'Duplicate indices found'
            })
            return results
            
        # Check for missing values
        missing_pct = data[required_columns].isnull().mean() * 100
        high_missing = missing_pct[missing_pct > 5].index.tolist()
        if high_missing:
            results.update({
                'valid': False,
                'message': f'High missing values (>5%) in columns: {high_missing}'
            })
            return results
            
        return results
