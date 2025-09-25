import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  Typography, 
  Card, 
  CardContent,
  Button,
  Chip,
  LinearProgress,
  Alert
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Assessment, 
  Timeline, 
  Speed,
  Analytics,
  Dashboard as DashboardIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSystemStatus, useTopics, useAnalysisSessions } from '../hooks/useAnalysisData';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { status, loading: statusLoading, error: statusError } = useSystemStatus();
  const { topics, loading: topicsLoading } = useTopics();
  const { sessions, loading: sessionsLoading } = useAnalysisSessions();

  // Calculate real statistics
  const stats = [
    {
      title: 'Active Topics',
      value: topics.filter(t => t.status === 'active').length.toString(),
      change: '+' + topics.length,
      color: '#1890ff',
      icon: <Assessment />
    },
    {
      title: 'Analysis Sessions',
      value: sessions.length.toString(),
      change: '+' + sessions.filter(s => s.status === 'running').length,
      color: '#52c41a',
      icon: <Timeline />
    },
    {
      title: 'Completion Rate',
      value: sessions.length > 0 ? Math.round((sessions.filter(s => s.status === 'completed').length / sessions.length) * 100) + '%' : '0%',
      change: '+2%',
      color: '#fa8c16',
      icon: <Speed />
    },
    {
      title: 'System Health',
      value: status?.system_status === 'operational' ? 'Good' : 'Issues',
      change: status ? `${status.core_services_count + status.enhanced_services_count} services` : '0 services',
      color: status?.system_status === 'operational' ? '#52c41a' : '#ff4d4f',
      icon: <TrendingUp />
    }
  ];

  const recentAnalyses = sessions.slice(0, 4);

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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0f0f23' }}>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 1 }}>
              Strategic Analysis Dashboard
            </Typography>
            <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
              Welcome to Validatus - Monitor your strategic analysis activities
            </Typography>
          </Box>
        </motion.div>

        {/* System Status Alert */}
        {statusError && (
          <motion.div variants={itemVariants}>
            <Alert severity="warning" sx={{ mb: 3 }}>
              Backend connection issue: Using demo data. Check if backend is running on port 8000.
            </Alert>
          </motion.div>
        )}

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <motion.div variants={itemVariants}>
                <Card sx={{ 
                  background: '#1a1a35', 
                  border: '1px solid #3d3d56',
                  height: '100%'
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ 
                        p: 1, 
                        borderRadius: 2, 
                        backgroundColor: `${stat.color}20`,
                        color: stat.color,
                        mr: 2
                      }}>
                        {stat.icon}
                      </Box>
                      <Box>
                        <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 700 }}>
                          {stat.value}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                          {stat.title}
                        </Typography>
                      </Box>
                    </Box>
                    <Chip 
                      label={stat.change}
                      size="small"
                      sx={{ 
                        backgroundColor: `${stat.color}20`,
                        color: stat.color,
                        fontSize: '0.75rem'
                      }}
                    />
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        <Grid container spacing={3}>
          {/* Recent Analysis */}
          <Grid item xs={12} md={8}>
            <motion.div variants={itemVariants}>
              <Paper sx={{ 
                p: 3, 
                background: '#1a1a35', 
                border: '1px solid #3d3d56' 
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                    Recent Analysis Sessions
                  </Typography>
                  <Button 
                    variant="outlined" 
                    size="small"
                    onClick={() => navigate('/analysis')}
                    sx={{ 
                      borderColor: '#1890ff',
                      color: '#1890ff',
                      '&:hover': {
                        borderColor: '#40a9ff',
                        backgroundColor: '#1890ff20'
                      }
                    }}
                  >
                    View All
                  </Button>
                </Box>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {recentAnalyses.length > 0 ? recentAnalyses.map((analysis) => (
                    <Box 
                      key={analysis.id}
                      sx={{ 
                        p: 2, 
                        borderRadius: 2, 
                        backgroundColor: '#252547',
                        border: '1px solid #3d3d56'
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ color: '#e8e8f0', fontWeight: 500 }}>
                          {analysis.topic}
                        </Typography>
                        <Chip 
                          label={analysis.status}
                          size="small"
                          sx={{
                            backgroundColor: analysis.status === 'completed' ? '#52c41a20' : 
                                           analysis.status === 'running' ? '#1890ff20' : '#fa8c1620',
                            color: analysis.status === 'completed' ? '#52c41a' : 
                                  analysis.status === 'running' ? '#1890ff' : '#fa8c16'
                          }}
                        />
                      </Box>
                      
                      {analysis.status === 'running' && (
                        <Box sx={{ mt: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              Progress
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              {analysis.progress}%
                            </Typography>
                          </Box>
                          <LinearProgress 
                            variant="determinate" 
                            value={analysis.progress}
                            sx={{
                              backgroundColor: '#3d3d56',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: '#1890ff'
                              }
                            }}
                          />
                        </Box>
                      )}
                    </Box>
                  )) : (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body2" sx={{ color: '#8c8ca0' }}>
                        No analysis sessions yet. Create your first analysis to get started.
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Paper>
            </motion.div>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <Paper sx={{ 
                p: 3, 
                background: '#1a1a35', 
                border: '1px solid #3d3d56' 
              }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 3 }}>
                  Quick Actions
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      fullWidth
                      variant={index === 0 ? "contained" : "outlined"}
                      onClick={action.action}
                      sx={{
                        py: 1.5,
                        justifyContent: 'flex-start',
                        ...(index === 0 ? {
                          background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                          },
                        } : {
                          borderColor: action.color,
                          color: action.color,
                          '&:hover': {
                            borderColor: action.color,
                            backgroundColor: `${action.color}20`
                          },
                        })
                      }}
                    >
                      <Box sx={{ textAlign: 'left', width: '100%' }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {action.title}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          {action.description}
                        </Typography>
                      </Box>
                    </Button>
                  ))}
                </Box>
              </Paper>
            </motion.div>
          </Grid>
        </Grid>

        {/* Backend Status */}
        {status && (
          <motion.div variants={itemVariants}>
            <Box sx={{ mt: 4, p: 2, backgroundColor: '#1a1a35', borderRadius: 2, border: '1px solid #3d3d56' }}>
              <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Backend Status: {status.system_status} | 
                Core Services: {status.core_services_count} | 
                Enhanced: {status.enhanced_services_count} | 
                Phase C: {status.phase_c_services_count} | 
                Phase E: {status.phase_e_services_count}
              </Typography>
              <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                Enabled Phases: {status.enabled_phases.join(', ') || 'Base only'}
              </Typography>
            </Box>
          </motion.div>
        )}
      </motion.div>
    </Box>
  );
};

export default DashboardPage;