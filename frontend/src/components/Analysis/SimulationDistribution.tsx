/**
 * Simulation Distribution Component
 */
import React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';

interface SimulationDistributionProps {
  selectedMetric: string;
}

const SimulationDistribution: React.FC<SimulationDistributionProps> = ({ 
  selectedMetric 
}) => {
  
  const renderDistributionChart = () => {
    // Mock distribution data - in real implementation, this would come from the API
    const mockData = {
      roi: {
        mean: 0.18,
        std: 0.05,
        percentiles: {
          p10: 0.12,
          p25: 0.15,
          p50: 0.18,
          p75: 0.21,
          p90: 0.24
        }
      },
      adoption: {
        mean: 0.12,
        std: 0.03,
        percentiles: {
          p10: 0.08,
          p25: 0.10,
          p50: 0.12,
          p75: 0.14,
          p90: 0.16
        }
      },
      financial: {
        mean: 150000,
        std: 25000,
        percentiles: {
          p10: 120000,
          p25: 135000,
          p50: 150000,
          p75: 165000,
          p90: 180000
        }
      }
    };

    const metricData = mockData[selectedMetric as keyof typeof mockData] || mockData.roi;
    
    // Calculate domain from percentiles
    const domainMin = selectedMetric === 'financial' 
      ? metricData.percentiles.p10 
      : metricData.percentiles.p10;
    const domainMax = selectedMetric === 'financial' 
      ? metricData.percentiles.p90 
      : metricData.percentiles.p90;
    
    // Generate histogram bins based on domain
    const numBins = 15;
    const binWidth = (domainMax - domainMin) / numBins;
    const histogramBins = Array.from({ length: numBins }, (_, i) => domainMin + i * binWidth);
    
    return (
      <Box>
        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
          {selectedMetric.toUpperCase()} Distribution
        </Typography>
        
        {/* Distribution Summary */}
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={6} md={3}>
              <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#1890ff' }}>
                    {selectedMetric === 'financial' ? `$${(metricData.mean / 1000).toFixed(0)}K` : `${(metricData.mean * 100).toFixed(1)}%`}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Mean
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#52c41a' }}>
                    {selectedMetric === 'financial' ? `$${(metricData.percentiles.p50 / 1000).toFixed(0)}K` : `${(metricData.percentiles.p50 * 100).toFixed(1)}%`}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Median
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#fa8c16' }}>
                    {selectedMetric === 'financial' ? `$${(metricData.percentiles.p25 / 1000).toFixed(0)}K` : `${(metricData.percentiles.p25 * 100).toFixed(1)}%`}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    25th Percentile
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#ff4d4f' }}>
                    {selectedMetric === 'financial' ? `$${(metricData.percentiles.p75 / 1000).toFixed(0)}K` : `${(metricData.percentiles.p75 * 100).toFixed(1)}%`}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    75th Percentile
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Distribution Visualization */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 2 }}>
            Probability Distribution
          </Typography>
          
          {/* Dynamic histogram bars based on domain */}
          <Box sx={{ display: 'flex', alignItems: 'end', height: 200, gap: 1 }}>
            {histogramBins.map((value, index) => {
              const height = Math.random() * 0.8 + 0.2; // Random height for demo
              const isInRange = value >= metricData.percentiles.p25 && value <= metricData.percentiles.p75;
              
              return (
                <Box
                  key={index}
                  sx={{
                    flex: 1,
                    height: `${height * 100}%`,
                    backgroundColor: isInRange ? '#1890ff' : '#3d3d56',
                    borderRadius: '2px 2px 0 0',
                    minHeight: 20
                  }}
                />
              );
            })}
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
              {selectedMetric === 'financial' ? `$${(domainMin / 1000).toFixed(0)}K` : `${(domainMin * 100).toFixed(1)}%`}
            </Typography>
            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
              {selectedMetric === 'financial' ? `$${(domainMax / 1000).toFixed(0)}K` : `${(domainMax * 100).toFixed(1)}%`}
            </Typography>
          </Box>
        </Box>

        {/* Confidence Intervals */}
        <Box>
          <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 2 }}>
            Confidence Intervals
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                80% Confidence
              </Typography>
              <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                {selectedMetric === 'financial' 
                  ? `$${(metricData.percentiles.p10 / 1000).toFixed(0)}K - $${(metricData.percentiles.p90 / 1000).toFixed(0)}K`
                  : `${(metricData.percentiles.p10 * 100).toFixed(1)}% - ${(metricData.percentiles.p90 * 100).toFixed(1)}%`
                }
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                50% Confidence
              </Typography>
              <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                {selectedMetric === 'financial' 
                  ? `$${(metricData.percentiles.p25 / 1000).toFixed(0)}K - $${(metricData.percentiles.p75 / 1000).toFixed(0)}K`
                  : `${(metricData.percentiles.p25 * 100).toFixed(1)}% - ${(metricData.percentiles.p75 * 100).toFixed(1)}%`
                }
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>
    );
  };

  return (
    <Box>
      {renderDistributionChart()}
    </Box>
  );
};

export default SimulationDistribution;