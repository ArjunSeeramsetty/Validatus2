import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Box } from '@mui/material';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface MarketSizeData {
  global_2024: number;
  global_2033: number;
  cagr: number;
  key_segments: {
    residential: number;
    commercial: number;
  };
}

interface MarketSizeChartProps {
  data: MarketSizeData;
}

export default function MarketSizeChart({ data }: MarketSizeChartProps) {
  // Default data if not provided
  const defaultData = {
    global_2024: 3500,
    global_2033: 5800,
    cagr: 6.5,
    key_segments: {
      residential: 75,
      commercial: 25
    }
  };

  const chartData = data || defaultData;

  // Generate forecast data points
  const years = [];
  const marketSizes = [];
  const residentialSizes = [];
  const commercialSizes = [];
  
  for (let year = 2024; year <= 2033; year++) {
    years.push(year.toString());
    const yearsFromStart = year - 2024;
    const totalSize = chartData.global_2024 * Math.pow(1 + chartData.cagr / 100, yearsFromStart);
    marketSizes.push(totalSize);
    residentialSizes.push(totalSize * chartData.key_segments.residential / 100);
    commercialSizes.push(totalSize * chartData.key_segments.commercial / 100);
  }

  const chartConfig = {
    labels: years,
    datasets: [
      {
        label: 'Total Market Size',
        data: marketSizes,
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#1976d2',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
      },
      {
        label: 'Residential Segment',
        data: residentialSizes,
        borderColor: '#2e7d32',
        backgroundColor: 'rgba(46, 125, 50, 0.1)',
        fill: false,
        tension: 0.4,
        pointBackgroundColor: '#2e7d32',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 3,
      },
      {
        label: 'Commercial Segment',
        data: commercialSizes,
        borderColor: '#ed6c02',
        backgroundColor: 'rgba(237, 108, 2, 0.1)',
        fill: false,
        tension: 0.4,
        pointBackgroundColor: '#ed6c02',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 3,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20
        }
      },
      title: {
        display: false
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#1976d2',
        borderWidth: 1,
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: $${context.parsed.y.toFixed(0)}M`;
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Year'
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Market Size ($ Million)'
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          callback: function(value: any) {
            return '$' + value + 'M';
          }
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  };

  return (
    <Box sx={{ height: 350, width: '100%' }}>
      <Line data={chartConfig} options={options} />
    </Box>
  );
}
