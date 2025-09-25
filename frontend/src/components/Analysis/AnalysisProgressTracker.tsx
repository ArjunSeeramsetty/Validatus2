import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, LinearProgress, Grid,
  Chip, Paper, Alert, Button, List, ListItem, ListItemIcon,
  ListItemText, Divider, CircularProgress
} from '@mui/material';
import {
  CheckCircle, Schedule, Error, Analytics, TrendingUp,
  Assessment, Speed, Insights, Refresh, PlayArrow
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAnalysisSessions } from '../../hooks/useAnalysisData';

interface AnalysisProgressTrackerProps {
  sessionId: string;
  onAnalysisComplete?: (results: any) => void;
}

interface AnalysisStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  estimatedTime?: number;
  actualTime?: number;
  insights?: string[];
}

const AnalysisProgressTracker: React.FC<AnalysisProgressTrackerProps> = ({
  sessionId,
  onAnalysisComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisSteps, setAnalysisSteps] = useState<AnalysisStep[]>([
    {
      id: 'knowledge_processing',
      name: 'Knowledge Base Processing',
      description: 'Analyzing collected content and creating vector embeddings',
      status: 'pending',
      progress: 0,
      estimatedTime: 2
    },
    {
      id: 'layer_scoring',
      name: 'Strategic Layer Scoring',
      description: 'Calculating 10 strategic layers (L01-L10) with expert analysis',
      status: 'pending',
      progress: 0,
      estimatedTime: 5
    },
    {
      id: 'factor_analysis',
      name: 'Strategic Factor Analysis',
      description: 'Computing 28 strategic factors (F1-F28) with mathematical models',
      status: 'pending',
      progress: 0,
      estimatedTime: 8
    },
    {
      id: 'expert_personas',
      name: 'Expert Persona Analysis',
      description: 'Running 10 expert personas for comprehensive insights',
      status: 'pending',
      progress: 0,
      estimatedTime: 6
    },
    {
      id: 'action_layers',
      name: 'Action Layer Calculation',
      description: 'Processing 18 action layers (L01-L18) for strategic recommendations',
      status: 'pending',
      progress: 0,
      estimatedTime: 4
    },
    {
      id: 'monte_carlo',
      name: 'Monte Carlo Simulation',
      description: 'Running advanced simulations for risk assessment and scenario planning',
      status: 'pending',
      progress: 0,
      estimatedTime: 7
    },
    {
      id: 'bayesian_blending',
      name: 'Bayesian Data Blending',
      description: 'Combining multiple data sources with advanced statistical models',
      status: 'pending',
      progress: 0,
      estimatedTime: 3
    },
    {
      id: 'results_compilation',
      name: 'Results Compilation',
      description: 'Aggregating insights and generating comprehensive recommendations',
      status: 'pending',
      progress: 0,
      estimatedTime: 2
    }
  ]);

  const { sessions } = useAnalysisSessions();
  const currentSession = sessions.find(s => s.id === sessionId);

  useEffect(() => {
    if (currentSession?.status === 'running' && !isRunning) {
      startAnalysis();
    }
  }, [currentSession]);

  const startAnalysis = async () => {
    setIsRunning(true);
    setError(null);
    
    try {
      // Simulate analysis progress
      for (let stepIndex = 0; stepIndex < analysisSteps.length; stepIndex++) {
        // Mark current step as running
        setAnalysisSteps(prev => prev.map((step, index) => ({
          ...step,
          status: index === stepIndex ? 'running' : 
                  index < stepIndex ? 'completed' : 'pending',
          progress: index === stepIndex ? 0 : 
                   index < stepIndex ? 100 : 0
        })));

        setCurrentStep(stepIndex);

        // Simulate step progress
        const step = analysisSteps[stepIndex];
        for (let progress = 0; progress <= 100; progress += 10) {
          setAnalysisSteps(prev => prev.map((s, index) => 
            index === stepIndex ? { ...s, progress } : s
          ));
          
          // Update overall progress
          const overallProg = ((stepIndex * 100) + progress) / analysisSteps.length;
          setOverallProgress(Math.round(overallProg));
          
          await new Promise(resolve => setTimeout(resolve, 200));
        }

        // Mark step as completed
        setAnalysisSteps(prev => prev.map((step, index) => ({
          ...step,
          status: index === stepIndex ? 'completed' : step.status,
          progress: index === stepIndex ? 100 : step.progress
        })));

        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Analysis complete
      setIsRunning(false);
      onAnalysisComplete?.(generateMockResults());
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
      setIsRunning(false);
    }
  };

  const generateMockResults = () => ({
    sessionId,
    topic: currentSession?.topic || 'Strategic Analysis',
    status: 'completed',
    layerScores: {
      'Strategic Planning': Math.round(Math.random() * 40 + 60),
      'Market Analysis': Math.round(Math.random() * 40 + 60),
      'Competitive Intelligence': Math.round(Math.random() * 40 + 60),
      'Risk Assessment': Math.round(Math.random() * 40 + 60),
      'Value Creation': Math.round(Math.random() * 40 + 60),
      'Implementation': Math.round(Math.random() * 40 + 60)
    },
    factorScores: {
      'Market Size': Math.round(Math.random() * 40 + 60),
      'Growth Rate': Math.round(Math.random() * 40 + 60),
      'Competition Level': Math.round(Math.random() * 40 + 60),
      'Technology Readiness': Math.round(Math.random() * 40 + 60),
      'Regulatory Environment': Math.round(Math.random() * 40 + 60),
      'Customer Demand': Math.round(Math.random() * 40 + 60)
    },
    insights: [
      'Strategic analysis completed with high confidence scores',
      'Multiple growth opportunities identified in target segments',
      'Risk factors have been thoroughly assessed and mitigated',
      'Implementation roadmap provides clear next steps'
    ],
    recommendations: [
      'Focus on high-potential market segments identified',
      'Invest in technology infrastructure to support growth',
      'Develop strategic partnerships in key markets',
      'Implement risk monitoring and mitigation strategies'
    ],
    createdAt: new Date().toISOString()
  });

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle sx={{ color: '#52c41a' }} />;
      case 'running': return <CircularProgress size={20} sx={{ color: '#1890ff' }} />;
      case 'failed': return <Error sx={{ color: '#ff4d4f' }} />;
      default: return <Schedule sx={{ color: '#8c8ca0' }} />;
    }
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed': return '#52c41a';
      case 'running': return '#1890ff';
      case 'failed': return '#ff4d4f';
      default: return '#8c8ca0';
    }
  };

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
          <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Analytics sx={{ color: '#1890ff', fontSize: 32 }} />
            <Box>
              <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                Strategic Analysis Progress
              </Typography>
              <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
                {currentSession?.topic || 'Analysis Session'}
              </Typography>
            </Box>
          </Box>
        </motion.div>

        {/* Overall Progress */}
        <motion.div variants={itemVariants}>
          <Card sx={{ background: '#1a1a35', border: '1px solid #3d3d56', mb: 4 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  Overall Progress
                </Typography>
                <Typography variant="h6" sx={{ color: '#1890ff', fontWeight: 600 }}>
                  {overallProgress}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={overallProgress}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: '#3d3d56',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(90deg, #1890ff 0%, #52c41a 100%)',
                    borderRadius: 6
                  }
                }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                  {isRunning ? 'Analysis in progress...' : 'Analysis complete'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                  Step {currentStep + 1} of {analysisSteps.length}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div variants={itemVariants}>
            <Alert severity="error" sx={{ mb: 3, backgroundColor: '#2d1b1f', border: '1px solid #ef4444' }}>
              {error}
            </Alert>
          </motion.div>
        )}

        {/* Analysis Steps */}
        <Grid container spacing={3}>
          {analysisSteps.map((step, index) => (
            <Grid item xs={12} md={6} key={step.id}>
              <motion.div variants={itemVariants}>
                <Card sx={{ 
                  background: '#1a1a35', 
                  border: '1px solid #3d3d56',
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'translateY(-2px)' }
                }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {getStepIcon(step.status)}
                      <Typography variant="h6" sx={{ 
                        color: '#e8e8f0', 
                        fontWeight: 600, 
                        ml: 2,
                        flexGrow: 1
                      }}>
                        {step.name}
                      </Typography>
                      <Chip
                        label={step.status.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: `${getStepColor(step.status)}20`,
                          color: getStepColor(step.status),
                          fontWeight: 600
                        }}
                      />
                    </Box>

                    <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                      {step.description}
                    </Typography>

                    {step.status === 'running' && (
                      <Box sx={{ mb: 2 }}>
                        <LinearProgress
                          variant="determinate"
                          value={step.progress}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: '#3d3d56',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: '#1890ff',
                              borderRadius: 4
                            }
                          }}
                        />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                            {step.progress}% complete
                          </Typography>
                          {step.estimatedTime && (
                            <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                              ~{step.estimatedTime} min
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    )}

                    {step.status === 'completed' && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckCircle sx={{ color: '#52c41a', fontSize: 16 }} />
                        <Typography variant="caption" sx={{ color: '#52c41a', fontWeight: 600 }}>
                          Completed successfully
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Action Buttons */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
            {!isRunning && overallProgress === 0 && (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={startAnalysis}
                sx={{
                  background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                  px: 4,
                  py: 1.5,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                  }
                }}
              >
                Start Analysis
              </Button>
            )}

            {isRunning && (
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                disabled
                sx={{
                  borderColor: '#1890ff',
                  color: '#1890ff',
                  px: 4,
                  py: 1.5
                }}
              >
                Analysis Running...
              </Button>
            )}

            {!isRunning && overallProgress === 100 && (
              <Button
                variant="contained"
                startIcon={<Assessment />}
                href="/results"
                sx={{
                  background: 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                  px: 4,
                  py: 1.5,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #389e0d 0%, #52c41a 100%)',
                  }
                }}
              >
                View Results
              </Button>
            )}
          </Box>
        </motion.div>

        {/* Performance Metrics */}
        <motion.div variants={itemVariants}>
          <Paper sx={{ 
            p: 3, 
            mt: 4, 
            background: '#1a1a35', 
            border: '1px solid #3d3d56' 
          }}>
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, fontWeight: 600 }}>
              Analysis Performance
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ color: '#1890ff', fontWeight: 700 }}>
                    {analysisSteps.filter(s => s.status === 'completed').length}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Steps Completed
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ color: '#52c41a', fontWeight: 700 }}>
                    {Math.round(analysisSteps.reduce((acc, step) => acc + step.actualTime || 0, 0))}m
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Total Time
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ color: '#fa8c16', fontWeight: 700 }}>
                    {analysisSteps.length}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Total Steps
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ color: '#722ed1', fontWeight: 700 }}>
                    {isRunning ? 'Live' : 'Complete'}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Status
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </motion.div>
      </motion.div>
    </Box>
  );
};

export default AnalysisProgressTracker;
