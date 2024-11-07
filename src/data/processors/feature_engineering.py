from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass
from ..storage.base_storage import BaseTimeSeriesStorage

@dataclass
class FeatureConfig:
    """Configuration for feature engineering."""
    name: str
    params: Dict[str, Union[int, float, str]]

class FeatureEngineer:
    """Feature engineering processor for market data."""
    
    def __init__(self, config: Dict[str, any]):
        """
        Initialize feature engineer with configuration.
        
        Args:
            config: Feature engineering configuration dictionary
        """
        self.config = config
        self.features_config = self._parse_config()
        
    def _parse_config(self) -> Dict[str, List[FeatureConfig]]:
        """Parse configuration into structured format."""
        features = {}
        
        # Parse technical indicators
        tech_indicators = self.config.get('technical_indicators', {})
        features['momentum'] = [
            FeatureConfig(name=ind['name'], params=ind)
            for ind in tech_indicators.get('momentum', [])
        ]
        features['volatility'] = [
            FeatureConfig(name=ind['name'], params=ind)
            for ind in tech_indicators.get('volatility', [])
        ]
        features['volume'] = [
            FeatureConfig(name=ind['name'], params=ind)
            for ind in tech_indicators.get('volume', [])
        ]
        
        return features
    
    def calculate_momentum_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum-based technical indicators."""
        for indicator in self.features_config['momentum']:
            if indicator.name == 'RSI':
                for period in indicator.params.get('periods', [14]):
                    data[f'rsi_{period}'] = self._calculate_rsi(
                        data['close'],
                        period=period
                    )
                    
            elif indicator.name == 'MACD':
                fast = indicator.params.get('fast_period', 12)
                slow = indicator.params.get('slow_period', 26)
                signal = indicator.params.get('signal_period', 9)
                
                macd, signal_line, histogram = self._calculate_macd(
                    data['close'],
                    fast_period=fast,
                    slow_period=slow,
                    signal_period=signal
                )
                
                data['macd'] = macd
                data['macd_signal'] = signal_line
                data['macd_hist'] = histogram
                
            elif indicator.name == 'ADX':
                period = indicator.params.get('period', 14)
                data[f'adx_{period}'] = self._calculate_adx(
                    data['high'],
                    data['low'],
                    data['close'],
                    period=period
                )
                
        return data
    
    def calculate_volatility_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility-based technical indicators."""
        for indicator in self.features_config['volatility']:
            if indicator.name == 'ATR':
                period = indicator.params.get('period', 14)
                data[f'atr_{period}'] = self._calculate_atr(
                    data['high'],
                    data['low'],
                    data['close'],
                    period=period
                )
                
            elif indicator.name == 'BOLLINGER_BANDS':
                period = indicator.params.get('period', 20)
                std_dev = indicator.params.get('std_dev', 2)
                
                bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(
                    data['close'],
                    period=period,
                    std_dev=std_dev
                )
                
                data[f'bb_upper_{period}'] = bb_upper
                data[f'bb_middle_{period}'] = bb_middle
                data[f'bb_lower_{period}'] = bb_lower
                
            elif indicator.name == 'KELTNER_CHANNELS':
                period = indicator.params.get('period', 20)
                atr_period = indicator.params.get('atr_period', 10)
                
                kc_upper, kc_middle, kc_lower = self._calculate_keltner_channels(
                    data['high'],
                    data['low'],
                    data['close'],
                    period=period,
                    atr_period=atr_period
                )
                
                data[f'kc_upper_{period}'] = kc_upper
                data[f'kc_middle_{period}'] = kc_middle
                data[f'kc_lower_{period}'] = kc_lower
                
        return data
    
    def calculate_volume_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based technical indicators."""
        for indicator in self.features_config['volume']:
            if indicator.name == 'OBV':
                data['obv'] = self._calculate_obv(
                    data['close'],
                    data['volume']
                )
                
            elif indicator.name == 'VWAP':
                data['vwap'] = self._calculate_vwap(
                    data['high'],
                    data['low'],
                    data['close'],
                    data['volume']
                )
                
            elif indicator.name == 'CVD':
                data['cvd'] = self._calculate_cvd(
                    data['close'],
                    data['volume']
                )
                
        return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(
        self,
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple:
        """Calculate MACD, Signal line, and Histogram."""
        exp1 = prices.ewm(span=fast_period, adjust=False).mean()
        exp2 = prices.ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        hist = macd - signal
        return macd, signal, hist
    
    def _calculate_adx(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Calculate Average Directional Index."""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = up_move.where(
            (up_move > down_move) & (up_move > 0),
            0
        )
        minus_dm = down_move.where(
            (down_move > up_move) & (down_move > 0),
            0
        )
        
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return adx
    
    def _calculate_atr(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Calculate Average True Range."""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(period).mean()
    
    def _calculate_bollinger_bands(
        self,
        prices: pd.Series,
        period: int = 20,
        std_dev: int = 2
    ) -> tuple:
        """Calculate Bollinger Bands."""
        middle = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    def _calculate_keltner_channels(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 20,
        atr_period: int = 10
    ) -> tuple:
        """Calculate Keltner Channels."""
        middle = close.rolling(period).mean()
        atr = self._calculate_atr(high, low, close, atr_period)
        upper = middle + (2 * atr)
        lower = middle - (2 * atr)
        return upper, middle, lower
    
    def _calculate_obv(
        self,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """Calculate On-Balance Volume."""
        direction = np.where(close > close.shift(1), 1, -1)
        direction[0] = 0  # first row
        return (direction * volume).cumsum()
    
    def _calculate_vwap(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """Calculate Volume Weighted Average Price."""
        typical_price = (high + low + close) / 3
        return (typical_price * volume).cumsum() / volume.cumsum()
    
    def _calculate_cvd(
        self,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """Calculate Cumulative Volume Delta."""
        direction = np.where(close > close.shift(1), 1, -1)
        direction[0] = 0  # first row
        return (direction * volume).cumsum()
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process market data with all configured features.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional feature columns
        """
        # Ensure required columns exist
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"Data must contain columns: {required_columns}")
        
        # Calculate all indicators
        data = self.calculate_momentum_indicators(data)
        data = self.calculate_volatility_indicators(data)
        data = self.calculate_volume_indicators(data)
        
        return data
