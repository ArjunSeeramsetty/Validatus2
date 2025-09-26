/**
 * Product Intelligence Tab - simplified implementation
 */
import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip
} from '@mui/material';
import { Store, Build, Star, Speed, Timeline } from '@mui/icons-material';

const ProductTab: React.FC<{ data: any }> = ({ data }) => {
  const productFactors = [
    {
      name: 'Market Readiness & Timing',
      score: 75,
      impact: 'Conversion, Lead-time',
      description: 'Strong market readiness with 4-10 week installation windows'
    },
    {
      name: 'Competitive Disruption',
      score: 68,
      impact: 'Adoption, Margin', 
      description: 'Moderate disruption potential with 5-15% margin flexibility'
    },
    {
      name: 'Quality & Reliability',
      score: 85,
      impact: 'Margin, Retention',
      description: 'High quality standards with 2-8% warranty claim rates'
    },
    {
      name: 'Differentiation & Positioning',
      score: 78,
      impact: 'ASP, Adoption',
      description: 'Strong differentiation with 15-45% premium potential'
    },
    {
      name: 'Innovation & Lifecycle',
      score: 72,
      impact: 'Margin, Adoption',
      description: 'Continuous innovation pipeline with 3-point margin impact'
    }
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Store sx={{ color: '#722ed1', mr: 2, fontSize: 28 }} />
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  Product Intelligence Analysis
                </Typography>
              </Box>

              <Grid container spacing={3}>
                {productFactors.map((factor, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Box sx={{ p: 2, backgroundColor: '#1a1a35', borderRadius: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                        <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                          {factor.name}
                        </Typography>
                        <Typography 
                          variant="h5" 
                          sx={{ 
                            color: getScoreColor(factor.score),
                            fontWeight: 700
                          }}
                        >
                          {factor.score}
                        </Typography>
                      </Box>
                      
                      <LinearProgress
                        variant="determinate"
                        value={factor.score}
                        sx={{
                          mb: 2,
                          backgroundColor: '#3d3d56',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getScoreColor(factor.score)
                          }
                        }}
                      />
                      
                      <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                        {factor.description}
                      </Typography>
                      
                      <Chip
                        size="small"
                        label={`Impact: ${factor.impact}`}
                        sx={{
                          backgroundColor: '#722ed120',
                          color: '#722ed1',
                          fontSize: '0.75rem'
                        }}
                      />
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProductTab;
