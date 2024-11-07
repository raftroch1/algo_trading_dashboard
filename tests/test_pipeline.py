import sys
import os
import pytest
import pandas as pd
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import Config
from src.data.pipeline import DataPipeline
from src.data.collectors.yfinance_collector import YFinanceCollector
from src.utils.data_validation import DataValidator

@pytest.fixture
async def pipeline():
    """Create a test pipeline instance."""
    config = Config("config.yaml")
    pipeline = DataPipeline(config)
    initialized = await pipeline.initialize()
    assert initialized, "Pipeline failed to initialize"
    yield pipeline
    await pipeline.cleanup()

@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    data = pd.DataFrame({
        'open': [100.0 + i for i in range(len(dates))],
        'high': [105.0 + i for i in range(len(dates))],
        'low': [95.0 + i for i in range(len(dates))],
        'close': [102.0 + i for i in range(len(dates))],
        'volume': [1000000 + i * 1000 for i in range(len(dates))]
    }, index=dates)
    return data

@pytest.mark.asyncio
async def test_yfinance_collector():
    """Test YFinance data collector."""
    collector = YFinanceCollector()
    
    # Test data collection
    symbols = ['AAPL']
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    data = await collector.fetch_data(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )
    
    assert data is not None
    assert 'AAPL' in data
    assert not data['AAPL'].empty
    assert all(col in data['AAPL'].columns 
              for col in ['open', 'high', 'low', 'close', 'volume'])

@pytest.mark.asyncio
async def test_data_validation(sample_data):
    """Test data validation functionality."""
    validator = DataValidator()
    
    # Test data quality check
    result = validator.check_data_quality(
        sample_data,
        required_columns=['open', 'high', 'low', 'close', 'volume']
    )
    assert result['valid']
    
    # Test price validity
    assert validator.check_price_validity(sample_data)
    
    # Test volume validity
    assert validator.check_volume_validity(sample_data)
    
    # Test timeseries continuity
    assert validator.check_timeseries_continuity(sample_data, '1d')

@pytest.mark.asyncio
async def test_pipeline_data_collection(pipeline):
    """Test full pipeline data collection and processing."""
    # Test collecting data for a single symbol
    success = await pipeline.collect_and_process_data(
        symbols=['AAPL'],
        start_date=datetime.now() - timedelta(days=5),
        end_date=datetime.now(),
        interval='1d'
    )
    assert success
    
    # Test retrieving latest data
    data = await pipeline.get_latest_data('AAPL', lookback_days=5)
    assert data is not None
    assert not data.empty
    assert all(col in data.columns 
              for col in ['open', 'high', 'low', 'close', 'volume'])

@pytest.mark.asyncio
async def test_pipeline_data_update(pipeline):
    """Test pipeline data update functionality."""
    success = await pipeline.update_data(
        symbols=['AAPL'],
        lookback_days=2
    )
    assert success

def test_config_loading():
    """Test configuration loading."""
    config = Config("config.yaml")
    
    assert config.db_config is not None
    assert config.collection_config is not None
    assert config.ml_config is not None
    
    assert isinstance(config.collection_config.symbols, list)
    assert len(config.collection_config.symbols) > 0
    assert isinstance(config.collection_config.default_interval, str)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
