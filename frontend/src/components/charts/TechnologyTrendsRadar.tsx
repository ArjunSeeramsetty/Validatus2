import React from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import { Box, Typography } from '@mui/material';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface TechnologyTrend {
  trend: string;
  adoption_rate: number;
  growth_rate: number;
  description: string;
}

interface TechnologyTrendsRadarProps {
  data: TechnologyTrend[];
}

export default function TechnologyTrendsRadar({ data }: TechnologyTrendsRadarProps) {
  // Default technology trends data
  const defaultData = [
    {
      trend: "Smart Controls",
      adoption_rate: 35.2,
      growth_rate: 24.5,
      description: "Automated louvers and weather sensors"
    },
    {
      trend: "IoT Integration",
      adoption_rate: 28.7,
      growth_rate: 31.2,
      description: "Connected home ecosystem integration"
    },
    {
      trend: "Energy Management",
      adoption_rate: 22.4,
      growth_rate: 18.9,
      description: "Solar integration and energy efficiency"
    },
    {
      trend: "AI Automation",
      adoption_rate: 15.8,
      growth_rate: 45.3,
      description: "Intelligent climate and usage optimization"
    },
    {
      trend: "Mobile Apps",
      adoption_rate: 42.1,
      growth_rate: 12.7,
      description: "Remote control and monitoring"
    },
    {
      trend: "Voice Control",
      adoption_rate: 18.9,
      growth_rate: 38.6,
      description: "Voice-activated pergola controls"
    }
  ];

  const trendsData = data && data.length > 0 ? data : defaultData;

  const chartData = {
    labels: trendsData.map(trend => trend.trend),
    datasets: [
      {
        label: 'Adoption Rate (%)',
        data: trendsData.map(trend => trend.adoption_rate),
        backgroundColor: 'rgba(25, 118, 210, 0.2)',
        borderColor: 'rgba(25, 118, 210, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(25, 118, 210, 1)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4
      },
      {
        label: 'Growth Rate (%)',
        data: trendsData.map(trend => trend.growth_rate),
        backgroundColor: 'rgba(46, 125, 50, 0.2)',
        borderColor: 'rgba(46, 125, 50, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(46, 125, 50, 1)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4
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
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#1976d2',
        borderWidth: 1,
        callbacks: {
          label: function(context: any) {
            const trend = trendsData[context.dataIndex];
            return [
              `${context.dataset.label}: ${context.parsed.r}%`,
              `Description: ${trend.description}`
            ];
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 50,
        ticks: {
          stepSize: 10,
          callback: function(value: any) {
            return value + '%';
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        angleLines: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        pointLabels: {
          font: {
            size: 11
          }
        }
      }
    },
    elements: {
      line: {
        tension: 0.1
      }
    }
  };

  return (
    <Box>
      <Box sx={{ height: 350, width: '100%' }}>
        <Radar data={chartData} options={options} />
      </Box>
      
      {/* Trend Descriptions */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Technology Trend Details
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
          {trendsData.map((trend, index) => (
            <Box key={index} sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                {trend.trend}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {trend.description}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Typography variant="caption" color="primary">
                  Adoption: {trend.adoption_rate}%
                </Typography>
                <Typography variant="caption" color="success.main">
                  Growth: {trend.growth_rate}%
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
}
