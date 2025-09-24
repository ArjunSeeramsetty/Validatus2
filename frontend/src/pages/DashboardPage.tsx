// frontend/src/pages/DashboardPage.tsx

import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  Grid, 
  Stack,
  Chip,
  Paper
} from '@mui/material';
import { 
  TrendingUpOutlined, 
  AnalyticsOutlined, 
  DashboardOutlined,
  LaunchOutlined
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const handleNavigateToEnhancedAnalytics = () => {
    navigate('/enhanced-analytics');
  };

  return (
    <Box sx={{ p: 3, backgroundColor: '#0f0f23', minHeight: '100vh' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 'bold', mb: 1 }}>
          Strategic Analysis Dashboard
        </Typography>
        <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
          Welcome to the Validatus platform - your comprehensive strategic analysis command center
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
            <CardContent sx={{ p: 3 }}>
              <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                <DashboardOutlined sx={{ color: '#1890ff', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                    Quick Actions
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Access advanced analytics and strategic analysis tools
                  </Typography>
                </Box>
              </Stack>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ 
                    p: 2, 
                    backgroundColor: '#252547', 
                    border: '1px solid #3d3d56',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      borderColor: '#1890ff',
                      transform: 'translateY(-2px)',
                    }
                  }} onClick={handleNavigateToEnhancedAnalytics}>
                    <Stack spacing={2}>
                      <Stack direction="row" alignItems="center" spacing={2}>
                        <TrendingUpOutlined sx={{ color: '#1890ff', fontSize: 24 }} />
                        <Box>
                          <Typography variant="subtitle1" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                            Enhanced Analytics
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                            Phase D Features
                          </Typography>
                        </Box>
                      </Stack>
                      <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                        Advanced F1-F28 factor analysis, Monte Carlo simulations, and real-time progress tracking
                      </Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        endIcon={<LaunchOutlined />}
                        sx={{ 
                          borderColor: '#1890ff', 
                          color: '#1890ff',
                          alignSelf: 'flex-start'
                        }}
                      >
                        Launch
                      </Button>
                    </Stack>
                  </Paper>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Paper sx={{ 
                    p: 2, 
                    backgroundColor: '#252547', 
                    border: '1px solid #3d3d56',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      borderColor: '#52c41a',
                      transform: 'translateY(-2px)',
                    }
                  }}>
                    <Stack spacing={2}>
                      <Stack direction="row" alignItems="center" spacing={2}>
                        <AnalyticsOutlined sx={{ color: '#52c41a', fontSize: 24 }} />
                        <Box>
                          <Typography variant="subtitle1" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                            Analysis Sessions
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                            Standard Analysis
                          </Typography>
                        </Box>
                      </Stack>
                      <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                        Create and manage strategic analysis sessions with comprehensive reporting
                      </Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        endIcon={<LaunchOutlined />}
                        sx={{ 
                          borderColor: '#52c41a', 
                          color: '#52c41a',
                          alignSelf: 'flex-start'
                        }}
                      >
                        Launch
                      </Button>
                    </Stack>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Status Panel */}
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 'bold', mb: 2 }}>
                System Status
              </Typography>
              
              <Stack spacing={2}>
                <Box>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Backend Services</Typography>
                    <Chip label="Operational" color="success" size="small" />
                  </Stack>
                </Box>
                
                <Box>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>WebSocket Connection</Typography>
                    <Chip label="Connected" color="success" size="small" />
                  </Stack>
                </Box>
                
                <Box>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Phase D Features</Typography>
                    <Chip label="Available" color="primary" size="small" />
                  </Stack>
                </Box>
                
                <Box>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Real-time Updates</Typography>
                    <Chip label="Active" color="success" size="small" />
                  </Stack>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', mt: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 'bold', mb: 2 }}>
                Recent Updates
              </Typography>
              
              <Stack spacing={1}>
                <Box>
                  <Typography variant="body2" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                    Phase D Implementation
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Enhanced frontend with real-time analytics
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                    Monte Carlo Simulations
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Interactive 10K iteration visualizations
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                    WebSocket Integration
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Real-time progress tracking and updates
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
