import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid,
  Button,
  Chip
} from '@mui/material';
import { TrendingUp, Analytics, Timeline, Settings } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Pergola Analysis',
      description: 'Comprehensive strategic analysis of the pergola market with detailed insights and recommendations.',
      icon: <TrendingUp sx={{ fontSize: 40, color: '#1890ff' }} />,
      path: '/migrated/v2_analysis_20250905_185553_d5654178',
      color: '#1890ff'
    },
    {
      title: 'Advanced Strategy Analysis',
      description: 'Comprehensive Monte Carlo simulation with scenario analysis, driver sensitivity, and business case scoring.',
      icon: <Analytics sx={{ fontSize: 40, color: '#52c41a' }} />,
      path: '/analysis/v2_analysis_20250905_185553_d5654178/advanced',
      color: '#52c41a'
    },
    {
      title: 'Live Action Calculator',
      description: 'Interactive demonstration of action layer calculations with real-time web search integration.',
      icon: <Timeline sx={{ fontSize: 40, color: '#fa8c16' }} />,
      path: '/action-layer/pergola',
      color: '#fa8c16'
    },
    {
      title: 'Sequential Analysis',
      description: 'Step-by-step analysis workflow with real-time progress tracking and human control between stages.',
      icon: <Settings sx={{ fontSize: 40, color: '#722ed1' }} />,
      path: '/sequential/pergola_market',
      color: '#722ed1'
    }
  ];

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 2 }}>
            Validatus Strategic Analysis Platform
          </Typography>
          <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 3 }}>
            Advanced business intelligence and strategic analysis tools
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Chip label="Strategic Analysis" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} />
            <Chip label="Action Layer Calculator" sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }} />
            <Chip label="Sequential Workflow" sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }} />
          </Box>
        </Box>

        {/* Features Grid */}
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={feature.title}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card 
                  sx={{ 
                    height: '100%',
                    backgroundColor: '#1a1a35', 
                    border: '1px solid #3d3d56',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: `0 8px 25px ${feature.color}20`,
                      borderColor: feature.color
                    }
                  }}
                  onClick={() => navigate(feature.path)}
                >
                  <CardContent sx={{ p: 4, textAlign: 'center' }}>
                    <Box sx={{ mb: 3 }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 2 }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#b8b8cc', mb: 3, lineHeight: 1.6 }}>
                      {feature.description}
                    </Typography>
                    <Button
                      variant="contained"
                      sx={{
                        backgroundColor: feature.color,
                        '&:hover': {
                          backgroundColor: feature.color,
                          opacity: 0.9
                        }
                      }}
                    >
                      Explore
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Quick Stats */}
        <Box sx={{ mt: 6, textAlign: 'center' }}>
          <Typography variant="h5" sx={{ color: '#e8e8f0', mb: 3 }}>
            Platform Overview
          </Typography>
          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Typography variant="h4" sx={{ color: '#1890ff', fontWeight: 600 }}>
                    3
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Analysis Modules
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Typography variant="h4" sx={{ color: '#52c41a', fontWeight: 600 }}>
                    1
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Market Analysis
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Typography variant="h4" sx={{ color: '#fa8c16', fontWeight: 600 }}>
                    100%
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Strategic Coverage
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </motion.div>
    </Box>
  );
};

export default HomePage;
