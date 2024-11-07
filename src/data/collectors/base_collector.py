from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime

class BaseDataCollector(ABC):
    """Abstract base class for all data collectors."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def fetch_data(
        self,
        symbols: Union[str, List[str]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for given symbols.
        
        Args:
            symbols: Single symbol or list of symbols to fetch
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval (e.g., "1m", "5m", "1h", "1d")
            
        Returns:
            Dictionary mapping symbols to their respective DataFrames
        """
        pass
    
    @abstractmethod
    async def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate the collected data.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Boolean indicating if data is valid
        """
        pass
    
    @abstractmethod
    async def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process the collected data before storage.
        
        Args:
            data: Raw DataFrame to process
            
        Returns:
            Processed DataFrame
        """
        pass
