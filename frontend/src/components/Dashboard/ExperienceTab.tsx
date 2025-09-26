/**
 * Experience Intelligence Tab
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
import { Star, Psychology, Speed, Favorite, Visibility } from '@mui/icons-material';

const ExperienceTab: React.FC<{ data: any }> = ({ data }) => {
  const experienceFactors = [
    {
      name: 'Customer Experience Quality',
      score: 88,
      impact: 'Satisfaction, Retention',
      description: 'Exceptional customer experience with 90%+ satisfaction rates'
    },
    {
      name: 'User Journey & Touchpoints',
      score: 82,
      impact: 'Conversion, Engagement',
      description: 'Optimized user journey with 25% conversion improvement'
    },
    {
      name: 'Service & Support Excellence',
      score: 85,
      impact: 'Retention, NPS',
      description: 'Outstanding service quality with 85+ NPS scores'
    },
    {
      name: 'Digital Experience & Innovation',
      score: 78,
      impact: 'Adoption, Efficiency',
      description: 'Strong digital experience with 30% efficiency gains'
    },
    {
      name: 'Experience Consistency',
      score: 80,
      impact: 'Trust, Brand Perception',
      description: 'Consistent experience across all touchpoints'
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
                <Star sx={{ color: '#13c2c2', mr: 2, fontSize: 28 }} />
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  Experience Intelligence Analysis
                </Typography>
              </Box>

              <Grid container spacing={3}>
                {experienceFactors.map((factor, index) => (
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
                          backgroundColor: '#13c2c220',
                          color: '#13c2c2',
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

export default ExperienceTab;
