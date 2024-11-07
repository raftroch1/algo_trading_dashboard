import asyncio
import logging
from datetime import datetime, timedelta
from utils.config import Config
from data.pipeline import DataPipeline

async def main():
    """Main entry point for the trading system."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration
        logger.info("Loading configuration...")
        config = Config("config.yaml")
        
        # Initialize data pipeline
        logger.info("Initializing data pipeline...")
        pipeline = DataPipeline(config)
        
        # Initialize pipeline components
        if not await pipeline.initialize():
            logger.error("Failed to initialize pipeline")
            return
        
        # Example: Collect and process historical data
        logger.info("Collecting historical data...")
        start_date = datetime.now() - timedelta(days=365)  # Last year
        success = await pipeline.collect_and_process_data(
            start_date=start_date,
            end_date=datetime.now()
        )
        
        if not success:
            logger.error("Failed to collect and process historical data")
            return
        
        # Example: Update data for specific symbols
        logger.info("Updating recent data...")
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        success = await pipeline.update_data(
            symbols=symbols,
            lookback_days=5
        )
        
        if not success:
            logger.error("Failed to update recent data")
            return
        
        # Example: Retrieve latest data for a symbol
        logger.info("Retrieving latest data for AAPL...")
        latest_data = await pipeline.get_latest_data('AAPL', lookback_days=30)
        
        if latest_data is not None:
            logger.info(f"Retrieved {len(latest_data)} records for AAPL")
            # Print some basic statistics
            logger.info("\nLatest data summary:")
            logger.info(f"Latest close price: {latest_data['close'].iloc[-1]:.2f}")
            logger.info(f"Average volume: {latest_data['volume'].mean():.0f}")
            if 'rsi_14' in latest_data.columns:
                logger.info(f"Latest RSI (14): {latest_data['rsi_14'].iloc[-1]:.2f}")
        else:
            logger.warning("No data retrieved for AAPL")
        
        # Cleanup
        logger.info("Cleaning up...")
        await pipeline.cleanup()
        
        logger.info("Process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
