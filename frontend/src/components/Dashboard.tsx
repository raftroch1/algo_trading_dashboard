import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert
} from '@mui/material';
import axios from 'axios';
import MarketDataChart from './MarketDataChart';

const API_BASE_URL = 'http://localhost:8000';

interface MarketData {
  symbol: string;
  interval: string;
  data: any[];
}

const Dashboard: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL');
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);

  // Fetch available symbols
  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/symbols`);
        setAvailableSymbols(response.data.symbols);
      } catch (err) {
        setError('Failed to fetch available symbols');
        console.error('Error fetching symbols:', err);
      }
    };

    fetchSymbols();
  }, []);

  // Fetch market data for selected symbol
  useEffect(() => {
    const fetchMarketData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(
          `${API_BASE_URL}/market-data/${selectedSymbol}`
        );
        setMarketData(response.data);
      } catch (err) {
        setError('Failed to fetch market data');
        console.error('Error fetching market data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();

    // Set up WebSocket connection for real-time updates
    const ws = new WebSocket(
      `ws://localhost:8000/ws/market-data/${selectedSymbol}`
    );

    ws.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setMarketData((prevData) => {
        if (!prevData) return null;
        return {
          ...prevData,
          data: [...prevData.data, newData.data]
        };
      });
    };

    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('WebSocket connection error');
    };

    setWsConnection(ws);

    // Cleanup WebSocket connection
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [selectedSymbol]);

  const handleSymbolChange = (event: any) => {
    setSelectedSymbol(event.target.value);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Trading Dashboard
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Symbol</InputLabel>
                <Select
                  value={selectedSymbol}
                  label="Symbol"
                  onChange={handleSymbolChange}
                >
                  {availableSymbols.map((symbol) => (
                    <MenuItem key={symbol} value={symbol}>
                      {symbol}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {loading ? (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight="400px"
              >
                <CircularProgress />
              </Box>
            ) : (
              marketData && (
                <MarketDataChart
                  symbol={marketData.symbol}
                  data={marketData.data}
                />
              )
            )}
          </Grid>

          {/* Additional panels can be added here */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Technical Indicators
              </Typography>
              {/* Add technical indicators component here */}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Trading Signals
              </Typography>
              {/* Add trading signals component here */}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard;
