from typing import Dict, List, Optional, Union
import asyncio
import pandas as pd
from datetime import datetime, timedelta
import logging
from .collectors.yfinance_collector import YFinanceCollector
from .processors.feature_engineering import FeatureEngineer
from .storage.influxdb_storage import InfluxDBStorage
from ..utils.config import Config
from ..utils.data_validation import DataValidator

class DataPipeline:
    """Orchestrates the data collection, processing, and storage workflow."""
    
    def __init__(self, config: Config):
        """
        Initialize the data pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = self._setup_logger()
        
        # Initialize components
        self.collector = YFinanceCollector(
            cache_dir=config.collection_config.cache_dir
        )
        
        self.feature_engineer = FeatureEngineer(
            config=config.config_data.get('features', {})
        )
        
        self.storage = InfluxDBStorage(
            url=config.db_config.url,
            token=f"{config.db_config.username}:{config.db_config.password}",
            org=config.db_config.org,
            bucket=config.db_config.bucket,
            verify_ssl=config.db_config.ssl
        )
        
        self.validator = DataValidator()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self) -> bool:
        """Initialize pipeline components."""
        try:
            # Connect to database
            self.logger.info("Connecting to database...")
            if not await self.storage.connect():
                self.logger.error("Failed to connect to database")
                return False
            
            self.logger.info("Pipeline initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing pipeline: {str(e)}")
            return False
    
    async def collect_and_process_data(
        self,
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: Optional[str] = None
    ) -> bool:
        """
        Collect and process data for specified symbols.
        
        Args:
            symbols: List of symbols to collect data for
            start_date: Start date for data collection
            end_date: End date for data collection
            interval: Data interval
        """
        try:
            # Use configuration defaults if not specified
            symbols = symbols or self.config.collection_config.symbols
            start_date = start_date or self.config.collection_config.start_date
            end_date = end_date or self.config.collection_config.end_date
            interval = interval or self.config.collection_config.default_interval
            
            self.logger.info(f"Starting data collection for {len(symbols)} symbols")
            
            # Collect raw data
            raw_data = await self.collector.fetch_data(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            
            if not raw_data:
                self.logger.error("No data collected")
                return False
            
            # Process each symbol's data
            for symbol, data in raw_data.items():
                self.logger.info(f"Processing data for {symbol}")
                
                # Validate raw data
                if not await self.collector.validate_data(data):
                    self.logger.warning(f"Invalid data for {symbol}, skipping")
                    continue
                
                # Calculate features
                processed_data = self.feature_engineer.process_data(data)
                
                # Validate processed data
                validation_result = self.validator.check_data_quality(
                    processed_data,
                    required_columns=['open', 'high', 'low', 'close', 'volume']
                )
                
                if not validation_result['valid']:
                    self.logger.warning(
                        f"Data validation failed for {symbol}: "
                        f"{validation_result['message']}"
                    )
                    continue
                
                # Store processed data
                success = await self.storage.write_data(
                    measurement=f"market_data_{interval}",
                    data=processed_data,
                    tags={'symbol': symbol}
                )
                
                if not success:
                    self.logger.error(f"Failed to store data for {symbol}")
                    continue
                
                self.logger.info(f"Successfully processed and stored data for {symbol}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in data pipeline: {str(e)}")
            return False
    
    async def update_data(
        self,
        symbols: Optional[List[str]] = None,
        lookback_days: int = 5
    ) -> bool:
        """
        Update data for specified symbols.
        
        Args:
            symbols: List of symbols to update
            lookback_days: Number of days to look back for updates
        """
        try:
            symbols = symbols or self.config.collection_config.symbols
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            self.logger.info(f"Updating data for {len(symbols)} symbols")
            
            return await self.collect_and_process_data(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            self.logger.error(f"Error updating data: {str(e)}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup pipeline resources."""
        try:
            self.logger.info("Cleaning up pipeline resources")
            await self.storage.disconnect()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    async def get_latest_data(
        self,
        symbol: str,
        lookback_days: int = 30
    ) -> Optional[pd.DataFrame]:
        """
        Retrieve latest data for a symbol.
        
        Args:
            symbol: Symbol to retrieve data for
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with latest data or None if not found
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=lookback_days)
            
            data = await self.storage.read_data(
                measurement=f"market_data_{self.config.collection_config.default_interval}",
                start_time=start_time,
                end_time=end_time,
                tags={'symbol': symbol}
            )
            
            return data if not data.empty else None
            
        except Exception as e:
            self.logger.error(f"Error retrieving latest data: {str(e)}")
            return None
