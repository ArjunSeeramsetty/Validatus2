/**
 * Driver Sensitivity Chart Component
 */
import React from 'react';
import { Box, Typography, Slider, Grid, Card, CardContent } from '@mui/material';

interface DriverSensitivityChartProps {
  sensitivities: Record<string, number>;
  onDriverChange: (driver: string, value: number) => void;
}

const DriverSensitivityChart: React.FC<DriverSensitivityChartProps> = ({ 
  sensitivities, 
  onDriverChange 
}) => {
  
  const driverNames: Record<string, string> = {
    'F1': 'Market Growth',
    'F2': 'Competitive Position',
    'F3': 'Technology Adoption',
    'F4': 'Regulatory Environment',
    'F5': 'Economic Conditions'
  };

  const getSensitivityColor = (value: number) => {
    if (value >= 0.7) return '#ff4d4f';  // High sensitivity - Red
    if (value >= 0.4) return '#fa8c16';  // Medium sensitivity - Orange
    return '#52c41a';  // Low sensitivity - Green
  };

  const formatSensitivity = (value: number) => {
    return `${(value * 100).toFixed(0)}%`;
  };

  return (
    <Box>
      <Grid container spacing={2}>
        {Object.entries(sensitivities).map(([driverId, sensitivity]) => (
          <Grid item xs={12} sm={6} md={4} key={driverId}>
            <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
              <CardContent>
                <Typography 
                  variant="subtitle2" 
                  sx={{ color: '#e8e8f0', mb: 1 }}
                >
                  {driverNames[driverId] || driverId}
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      color: getSensitivityColor(sensitivity),
                      fontWeight: 600
                    }}
                  >
                    {formatSensitivity(sensitivity)}
                  </Typography>
                  <Typography 
                    variant="caption" 
                    sx={{ color: '#b8b8cc' }}
                  >
                    Sensitivity
                  </Typography>
                </Box>

                <Box sx={{ px: 1 }}>
                  <Slider
                    value={sensitivity}
                    onChange={(_, value) => onDriverChange(driverId, value as number)}
                    min={0}
                    max={1}
                    step={0.01}
                    sx={{
                      color: getSensitivityColor(sensitivity),
                      '& .MuiSlider-thumb': {
                        backgroundColor: getSensitivityColor(sensitivity),
                        '&:hover': {
                          boxShadow: `0 0 0 8px ${getSensitivityColor(sensitivity)}20`
                        }
                      },
                      '& .MuiSlider-track': {
                        backgroundColor: getSensitivityColor(sensitivity)
                      },
                      '& .MuiSlider-rail': {
                        backgroundColor: '#3d3d56'
                      }
                    }}
                  />
                </Box>

                <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Low
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    High
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default DriverSensitivityChart;
