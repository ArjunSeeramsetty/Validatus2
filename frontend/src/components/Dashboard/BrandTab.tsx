/**
 * Brand Intelligence Tab
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
import { Loyalty } from '@mui/icons-material';

const BrandTab: React.FC = () => {
  const brandFactors = [
    {
      name: 'Brand Recognition & Awareness',
      score: 82,
      impact: 'Adoption, ASP',
      description: 'Strong brand recognition with 15-25% premium positioning'
    },
    {
      name: 'Brand Loyalty & Advocacy',
      score: 78,
      impact: 'Retention, NRR',
      description: 'High customer loyalty with 8-12% referral rates'
    },
    {
      name: 'Brand Perception & Trust',
      score: 85,
      impact: 'Conversion, Margin',
      description: 'Excellent brand trust with 20-30% conversion uplift'
    },
    {
      name: 'Brand Differentiation',
      score: 75,
      impact: 'ASP, Market Share',
      description: 'Clear differentiation with 10-20% market share potential'
    },
    {
      name: 'Brand Experience & Engagement',
      score: 80,
      impact: 'Retention, Satisfaction',
      description: 'Strong brand experience with 85%+ satisfaction rates'
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
                <Loyalty sx={{ color: '#eb2f96', mr: 2, fontSize: 28 }} />
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  Brand Intelligence Analysis
                </Typography>
              </Box>

              <Grid container spacing={3}>
                {brandFactors.map((factor, index) => (
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
                          backgroundColor: '#eb2f9620',
                          color: '#eb2f96',
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

export default BrandTab;
