import os
from typing import Dict, Any
import yaml
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    type: str  # 'influxdb' or 'timescaledb'
    url: str
    port: int
    username: str
    password: str
    database: str
    org: str = ''  # For InfluxDB
    bucket: str = ''  # For InfluxDB
    ssl: bool = True

@dataclass
class DataCollectionConfig:
    """Data collection settings."""
    default_interval: str = "1d"
    max_retries: int = 3
    retry_delay: int = 5
    timeout: int = 30
    cache_dir: str = "cache"
    symbols: list = None
    start_date: datetime = None
    end_date: datetime = None

@dataclass
class MLConfig:
    """Machine learning configuration settings."""
    model_dir: str = "models"
    train_test_split: float = 0.2
    validation_split: float = 0.1
    batch_size: int = 32
    epochs: int = 100
    early_stopping_patience: int = 10
    learning_rate: float = 0.001

class Config:
    """Configuration manager for the trading system."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config_data = self._load_config()
        
        # Initialize configuration objects
        self.db_config = self._init_db_config()
        self.collection_config = self._init_collection_config()
        self.ml_config = self._init_ml_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            self._create_default_config()
            
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        default_config = {
            'database': {
                'type': 'influxdb',
                'url': 'http://localhost',
                'port': 8086,
                'username': 'admin',
                'password': 'admin',
                'database': 'trading_data',
                'org': 'trading_org',
                'bucket': 'market_data',
                'ssl': True
            },
            'data_collection': {
                'default_interval': '1d',
                'max_retries': 3,
                'retry_delay': 5,
                'timeout': 30,
                'cache_dir': 'cache',
                'symbols': ['AAPL', 'GOOGL', 'MSFT'],
                'start_date': '2023-01-01',
                'end_date': 'now'
            },
            'ml': {
                'model_dir': 'models',
                'train_test_split': 0.2,
                'validation_split': 0.1,
                'batch_size': 32,
                'epochs': 100,
                'early_stopping_patience': 10,
                'learning_rate': 0.001
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def _init_db_config(self) -> DatabaseConfig:
        """Initialize database configuration."""
        db_config = self.config_data.get('database', {})
        return DatabaseConfig(
            type=db_config.get('type', 'influxdb'),
            url=db_config.get('url', 'http://localhost'),
            port=db_config.get('port', 8086),
            username=db_config.get('username', 'admin'),
            password=db_config.get('password', 'admin'),
            database=db_config.get('database', 'trading_data'),
            org=db_config.get('org', 'trading_org'),
            bucket=db_config.get('bucket', 'market_data'),
            ssl=db_config.get('ssl', True)
        )
    
    def _init_collection_config(self) -> DataCollectionConfig:
        """Initialize data collection configuration."""
        collection_config = self.config_data.get('data_collection', {})
        
        # Parse dates
        start_date = collection_config.get('start_date')
        if isinstance(start_date, str) and start_date != 'now':
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        elif isinstance(start_date, (date, datetime)):
            start_date = datetime.combine(start_date, datetime.min.time())
        else:
            start_date = datetime.now()
            
        end_date = collection_config.get('end_date')
        if isinstance(end_date, str) and end_date != 'now':
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        elif isinstance(end_date, (date, datetime)):
            end_date = datetime.combine(end_date, datetime.min.time())
        else:
            end_date = datetime.now()
            
        return DataCollectionConfig(
            default_interval=collection_config.get('default_interval', '1d'),
            max_retries=collection_config.get('max_retries', 3),
            retry_delay=collection_config.get('retry_delay', 5),
            timeout=collection_config.get('timeout', 30),
            cache_dir=collection_config.get('cache_dir', 'cache'),
            symbols=collection_config.get('symbols', ['AAPL', 'GOOGL', 'MSFT']),
            start_date=start_date,
            end_date=end_date
        )
    
    def _init_ml_config(self) -> MLConfig:
        """Initialize machine learning configuration."""
        ml_config = self.config_data.get('ml', {})
        return MLConfig(
            model_dir=ml_config.get('model_dir', 'models'),
            train_test_split=ml_config.get('train_test_split', 0.2),
            validation_split=ml_config.get('validation_split', 0.1),
            batch_size=ml_config.get('batch_size', 32),
            epochs=ml_config.get('epochs', 100),
            early_stopping_patience=ml_config.get('early_stopping_patience', 10),
            learning_rate=ml_config.get('learning_rate', 0.001)
        )
