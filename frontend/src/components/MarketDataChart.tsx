import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist';
import { Box, Paper, Typography } from '@mui/material';

interface MarketDataPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface MarketDataChartProps {
  symbol: string;
  data: MarketDataPoint[];
}

const MarketDataChart: React.FC<MarketDataChartProps> = ({ symbol, data }) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data || data.length === 0 || !chartRef.current) return;

    // Prepare data for candlestick chart
    const chartData = {
      x: data.map(d => d.timestamp),
      open: data.map(d => d.open),
      high: data.map(d => d.high),
      low: data.map(d => d.low),
      close: data.map(d => d.close),
      decreasing: { line: { color: '#FF4136' } },
      increasing: { line: { color: '#2ECC40' } },
      type: 'candlestick',
      xaxis: 'x',
      yaxis: 'y'
    };

    // Volume bar chart
    const volumeData = {
      x: data.map(d => d.timestamp),
      y: data.map(d => d.volume),
      type: 'bar',
      name: 'Volume',
      yaxis: 'y2',
      marker: {
        color: data.map((d, i) => 
          i > 0 ? (d.close > data[i-1].close ? '#2ECC40' : '#FF4136') : '#2ECC40'
        )
      }
    };

    const layout = {
      dragmode: 'zoom',
      showlegend: false,
      xaxis: {
        rangeslider: {
          visible: false
        },
        type: 'date'
      },
      yaxis: {
        title: 'Price',
        autorange: true,
        domain: [0.3, 1]
      },
      yaxis2: {
        title: 'Volume',
        autorange: true,
        domain: [0, 0.2]
      },
      grid: {
        rows: 2,
        columns: 1,
        pattern: 'independent'
      }
    };

    Plotly.newPlot(chartRef.current, [chartData, volumeData], layout);

    // Cleanup
    return () => {
      if (chartRef.current) {
        Plotly.purge(chartRef.current);
      }
    };
  }, [data]);

  return (
    <Paper elevation={3} sx={{ p: 2, m: 2 }}>
      <Typography variant="h6" gutterBottom>
        {symbol} Market Data
      </Typography>
      <Box ref={chartRef} sx={{ width: '100%', height: '600px' }} />
    </Paper>
  );
};

export default MarketDataChart;
