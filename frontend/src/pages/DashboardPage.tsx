import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  Analytics,
  Speed,
  CheckCircle,
  Schedule,
  ArrowForward
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  // Mock data for dashboard
  const stats = [
    {
      title: 'Active Analyses',
      value: '12',
      change: '+8.2%',
      icon: <Analytics sx={{ fontSize: 40 }} />,
      color: '#1890ff'
    },
    {
      title: 'Completed Sessions',
      value: '156',
      change: '+12.5%',
      icon: <CheckCircle sx={{ fontSize: 40 }} />,
      color: '#52c41a'
    },
    {
      title: 'Processing Speed',
      value: '2.3s',
      change: '-15%',
      icon: <Speed sx={{ fontSize: 40 }} />,
      color: '#fa8c16'
    },
    {
      title: 'Success Rate',
      value: '94.2%',
      change: '+2.1%',
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      color: '#722ed1'
    }
  ];

  const recentAnalyses = [
    {
      id: '1',
      topic: 'Market Entry Strategy Analysis',
      progress: 85,
      status: 'running',
      timeRemaining: '5 min'
    },
    {
      id: '2',
      topic: 'Competitive Landscape Assessment',
      progress: 100,
      status: 'completed',
      timeRemaining: 'Completed'
    },
    {
      id: '3',
      topic: 'Financial Performance Review',
      progress: 45,
      status: 'running',
      timeRemaining: '12 min'
    },
    {
      id: '4',
      topic: 'Risk Assessment Framework',
      progress: 100,
      status: 'completed',
      timeRemaining: 'Completed'
    }
  ];

  const quickActions = [
    {
      title: 'Start New Analysis',
      description: 'Begin a comprehensive strategic analysis',
      action: () => navigate('/analysis'),
      color: '#1890ff'
    },
    {
      title: 'View Results',
      description: 'Review completed analysis results',
      action: () => navigate('/results'),
      color: '#52c41a'
    },
    {
      title: 'Manage Topics',
      description: 'Configure analysis topics and parameters',
      action: () => navigate('/topics'),
      color: '#fa8c16'
    },
    {
      title: 'Enhanced Analytics',
      description: 'Access advanced analytics dashboard',
      action: () => navigate('/enhanced-analytics'),
      color: '#722ed1'
    }
  ];

  return (
    <Box sx={{ p: 3, backgroundColor: '#0f0f23', minHeight: '100vh' }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 700, mb: 1 }}>
            Strategic Command Center
          </Typography>
          <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
            Welcome to your AI-powered strategic analysis dashboard
          </Typography>
        </Box>
      </motion.div>

      {/* Statistics Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  background: '#1a1a35',
                  border: '1px solid #3d3d56',
                  borderRadius: 2,
                  height: '100%',
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 32px rgba(24, 144, 255, 0.1)'
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Avatar
                      sx={{
                        backgroundColor: `${stat.color}20`,
                        color: stat.color,
                        width: 56,
                        height: 56
                      }}
                    >
                      {stat.icon}
                    </Avatar>
                    <Chip
                      label={stat.change}
                      size="small"
                      sx={{
                        backgroundColor: stat.change.startsWith('+') ? '#52c41a20' : '#ff4d4f20',
                        color: stat.change.startsWith('+') ? '#52c41a' : '#ff4d4f',
                        fontWeight: 600
                      }}
                    />
                  </Box>
                  <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 700, mb: 1 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    {stat.title}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      <Grid container spacing={3}>
        {/* Recent Analyses */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card
              sx={{
                background: '#1a1a35',
                border: '1px solid #3d3d56',
                borderRadius: 2,
                height: '100%'
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                    Recent Analyses
                  </Typography>
                  <Button
                    variant="text"
                    endIcon={<ArrowForward />}
                    onClick={() => navigate('/analysis')}
                    sx={{ color: '#1890ff' }}
                  >
                    View All
                  </Button>
                </Box>
                
                <List>
                  {recentAnalyses.map((analysis, index) => (
                    <React.Fragment key={analysis.id}>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemAvatar>
                          <Avatar
                            sx={{
                              backgroundColor: analysis.status === 'completed' ? '#52c41a20' : '#1890ff20',
                              color: analysis.status === 'completed' ? '#52c41a' : '#1890ff'
                            }}
                          >
                            {analysis.status === 'completed' ? <CheckCircle /> : <Schedule />}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Typography variant="body1" sx={{ color: '#e8e8f0', fontWeight: 500 }}>
                              {analysis.topic}
                            </Typography>
                          }
                          secondary={
                            <Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                                <Chip
                                  label={analysis.status}
                                  size="small"
                                  sx={{
                                    backgroundColor: analysis.status === 'completed' ? '#52c41a20' : '#1890ff20',
                                    color: analysis.status === 'completed' ? '#52c41a' : '#1890ff',
                                    textTransform: 'capitalize'
                                  }}
                                />
                                <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                                  {analysis.timeRemaining}
                                </Typography>
                              </Box>
                              {analysis.status === 'running' && (
                                <LinearProgress
                                  variant="determinate"
                                  value={analysis.progress}
                                  sx={{
                                    height: 6,
                                    borderRadius: 3,
                                    backgroundColor: '#3d3d56',
                                    '& .MuiLinearProgress-bar': {
                                      backgroundColor: '#1890ff',
                                      borderRadius: 3
                                    }
                                  }}
                                />
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < recentAnalyses.length - 1 && <Divider sx={{ borderColor: '#3d3d56' }} />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <Card
              sx={{
                background: '#1a1a35',
                border: '1px solid #3d3d56',
                borderRadius: 2,
                height: '100%'
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 3 }}>
                  Quick Actions
                </Typography>
                
                <Grid container spacing={2}>
                  {quickActions.map((action, index) => (
                    <Grid item xs={12} key={index}>
                      <Button
                        fullWidth
                        variant="outlined"
                        onClick={action.action}
                        sx={{
                          p: 2,
                          textAlign: 'left',
                          justifyContent: 'flex-start',
                          borderColor: '#3d3d56',
                          color: '#e8e8f0',
                          backgroundColor: 'transparent',
                          '&:hover': {
                            borderColor: action.color,
                            backgroundColor: `${action.color}10`,
                            transform: 'translateY(-2px)'
                          },
                          transition: 'all 0.2s ease-in-out'
                        }}
                      >
                        <Box>
                          <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                            {action.title}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                            {action.description}
                          </Typography>
                        </Box>
                      </Button>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;