from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime

class BaseTimeSeriesStorage(ABC):
    """Abstract base class for time series database storage."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the database.
        
        Returns:
            Boolean indicating successful connection
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def write_data(
        self,
        measurement: str,
        data: pd.DataFrame,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Write time series data to database.
        
        Args:
            measurement: Name of the measurement/table
            data: DataFrame containing time series data
            tags: Optional tags/metadata for the data points
            
        Returns:
            Boolean indicating successful write
        """
        pass
    
    @abstractmethod
    async def read_data(
        self,
        measurement: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Read time series data from database.
        
        Args:
            measurement: Name of the measurement/table
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            tags: Filter by specific tags
            fields: Specific fields to retrieve
            
        Returns:
            DataFrame containing requested data
        """
        pass
    
    @abstractmethod
    async def delete_data(
        self,
        measurement: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Delete time series data from database.
        
        Args:
            measurement: Name of the measurement/table
            start_time: Start time for data deletion
            end_time: End time for data deletion
            tags: Filter by specific tags
            
        Returns:
            Boolean indicating successful deletion
        """
        pass
    
    @abstractmethod
    async def list_measurements(self) -> List[str]:
        """
        List all available measurements/tables.
        
        Returns:
            List of measurement names
        """
        pass
    
    @abstractmethod
    async def get_latest_timestamp(
        self,
        measurement: str,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[datetime]:
        """
        Get the latest timestamp for a measurement.
        
        Args:
            measurement: Name of the measurement/table
            tags: Filter by specific tags
            
        Returns:
            Latest timestamp or None if no data exists
        """
        pass
