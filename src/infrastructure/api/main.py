from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from ...data.pipeline import DataPipeline
from ...utils.config import Config

app = FastAPI(title="Trading Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize configuration and pipeline
config = Config("config.yaml")
pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global pipeline
    pipeline = DataPipeline(config)
    await pipeline.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if pipeline:
        await pipeline.cleanup()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "online", "timestamp": datetime.now().isoformat()}

@app.get("/symbols")
async def get_symbols():
    """Get list of available symbols."""
    return {"symbols": config.collection_config.symbols}

@app.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    interval: str = "1d",
    lookback_days: int = 30
):
    """
    Get historical market data for a symbol.
    
    Args:
        symbol: Trading symbol (e.g., 'AAPL')
        interval: Data interval (e.g., '1d', '1h')
        lookback_days: Number of days to look back
    """
    try:
        data = await pipeline.get_latest_data(symbol, lookback_days)
        if data is None:
            raise HTTPException(status_code=404, message=f"No data found for {symbol}")
            
        # Convert DataFrame to dict for JSON response
        return {
            "symbol": symbol,
            "interval": interval,
            "data": data.reset_index().to_dict(orient="records")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/technical-indicators/{symbol}")
async def get_technical_indicators(
    symbol: str,
    indicators: List[str] = ["RSI", "MACD", "BB"],
    lookback_days: int = 30
):
    """
    Get technical indicators for a symbol.
    
    Args:
        symbol: Trading symbol
        indicators: List of indicators to calculate
        lookback_days: Number of days to look back
    """
    try:
        data = await pipeline.get_latest_data(symbol, lookback_days)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
            
        # Return only the requested indicators
        indicator_cols = [col for col in data.columns if any(
            ind.lower() in col.lower() for ind in indicators
        )]
        
        if not indicator_cols:
            raise HTTPException(
                status_code=404,
                detail=f"No indicators found among: {indicators}"
            )
            
        result_data = data[indicator_cols]
        return {
            "symbol": symbol,
            "indicators": indicators,
            "data": result_data.reset_index().to_dict(orient="records")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/market-data/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time market data.
    
    Args:
        symbol: Trading symbol to stream
    """
    await manager.connect(websocket)
    try:
        while True:
            # Simulate real-time updates (replace with actual data updates)
            data = await pipeline.get_latest_data(symbol, lookback_days=1)
            if data is not None:
                await websocket.send_json({
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                    "data": data.iloc[-1].to_dict()
                })
            await asyncio.sleep(1)  # Update every second
            
    except Exception as e:
        manager.disconnect(websocket)
        
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "pipeline_status": "connected" if pipeline else "disconnected"
    }
