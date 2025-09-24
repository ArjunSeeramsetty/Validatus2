// frontend/src/components/enhanced_analytics/RealTimeUpdates/AnalysisProgressStepper.tsx
import React, { useState, useEffect, useMemo } from 'react';
import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  Typography,
  Box,
  Stack,
  LinearProgress,
  Chip,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  Paper,
  Alert,
  Tooltip,
  IconButton,
  Grid,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  InfoOutlined,
  CheckCircleOutlined,
  ErrorOutlined,
  ScheduleOutlined,
  RefreshOutlined,
  ExpandMoreOutlined
} from '@mui/icons-material';
import { useWebSocketSubscription } from '../../../hooks/useWebSocketConnection';

interface AnalysisStep {
  id: string;
  title: string;
  description: string;
  status: 'waiting' | 'process' | 'finish' | 'error';
  progress?: number;
  startTime?: string;
  endTime?: string;
  duration?: number;
  details?: string[];
  errorMessage?: string;
  subSteps?: {
    name: string;
    status: 'pending' | 'running' | 'completed' | 'error';
    progress?: number;
  }[];
}

interface AnalysisProgressData {
  sessionId: string;
  topic: string;
  status: 'initializing' | 'running' | 'completed' | 'error';
  currentStep: string;
  overallProgress: number;
  steps: AnalysisStep[];
  estimatedTimeRemaining?: number;
  statistics?: {
    totalLayers: number;
    completedLayers: number;
    totalFactors: number;
    completedFactors: number;
    evidenceChunks: number;
    patternsTrigger: number;
  };
}

interface AnalysisProgressStepperProps {
  sessionId: string;
  onStepClick?: (stepId: string) => void;
  showDetailedView?: boolean;
  autoRefresh?: boolean;
}

// Define the standard analysis workflow steps
const ANALYSIS_WORKFLOW_STEPS: Omit<AnalysisStep, 'status' | 'progress' | 'startTime' | 'endTime'>[] = [
  {
    id: 'session_initialization',
    title: 'Session Initialization',
    description: 'Setting up analysis session and parameters',
    details: [
      'Creating unique session ID',
      'Validating topic parameters',
      'Initializing progress tracking',
      'Setting up data structures'
    ]
  },
  {
    id: 'knowledge_loading',
    title: 'Knowledge Loading',
    description: 'Loading topic-specific knowledge from vector stores',
    details: [
      'Retrieving vector store data',
      'Loading evidence chunks',
      'Quality filtering content',
      'Preparing knowledge base'
    ]
  },
  {
    id: 'layer_scoring',
    title: 'Strategic Layer Scoring',
    description: 'Analyzing 10 strategic layers with expert personas',
    details: [
      'Consumer layer analysis',
      'Market dynamics evaluation',
      'Product assessment',
      'Brand strength analysis',
      'Experience evaluation',
      'Technology readiness',
      'Operations analysis',
      'Financial health check',
      'Competitive positioning',
      'Regulatory compliance'
    ]
  },
  {
    id: 'factor_calculation',
    title: 'Factor Calculations',
    description: 'Computing F1-F28 strategic factors',
    details: [
      'Market factors (F1-F7)',
      'Product factors (F8-F14)', 
      'Financial factors (F15-F21)',
      'Strategic factors (F22-F28)'
    ]
  },
  {
    id: 'segment_analysis',
    title: 'Segment Analysis',
    description: 'Evaluating market segments and opportunities',
    details: [
      'Enterprise segment analysis',
      'SMB market evaluation',
      'Consumer segment scoring',
      'Government opportunities',
      'Education sector analysis'
    ]
  },
  {
    id: 'pattern_recognition',
    title: 'Pattern Recognition',
    description: 'Identifying strategic patterns and insights',
    details: [
      'Analyzing 41 strategic patterns',
      'Monte Carlo simulations',
      'Pattern correlation analysis',
      'Strategic insights generation'
    ]
  },
  {
    id: 'bayesian_analysis',
    title: 'Bayesian Data Blending',
    description: 'Advanced probabilistic data fusion',
    details: [
      'Data source reliability scoring',
      'Bayesian inference calculations',
      'Uncertainty quantification',
      'Confidence interval computation'
    ]
  },
  {
    id: 'results_compilation',
    title: 'Results Compilation',
    description: 'Finalizing analysis results and insights',
    details: [
      'Aggregating all analysis results',
      'Generating comprehensive insights',
      'Creating recommendation summaries',
      'Preparing export data'
    ]
  }
];

const AnalysisProgressStepper: React.FC<AnalysisProgressStepperProps> = ({
  sessionId,
  onStepClick,
  showDetailedView = true,
  autoRefresh = true
}) => {
  const [progressData, setProgressData] = useState<AnalysisProgressData | null>(null);
  const [lastUpdateTime, setLastUpdateTime] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Subscribe to WebSocket updates for this session
  useWebSocketSubscription('analysis_progress', (data) => {
    if (data.sessionId === sessionId) {
      updateProgressData(data);
    }
  });

  useWebSocketSubscription('analysis_step_complete', (data) => {
    if (data.sessionId === sessionId) {
      updateStepStatus(data.stepId, 'finish', data);
    }
  });

  useWebSocketSubscription('analysis_step_error', (data) => {
    if (data.sessionId === sessionId) {
      updateStepStatus(data.stepId, 'error', data);
    }
  });

  // Update progress data from WebSocket messages
  const updateProgressData = (data: any) => {
    setProgressData(prevData => {
      const updatedSteps = ANALYSIS_WORKFLOW_STEPS.map(stepTemplate => {
        const existingStep = prevData?.steps.find(s => s.id === stepTemplate.id);
        const stepUpdate = data.steps?.[stepTemplate.id];
        
        return {
          ...stepTemplate,
          status: stepUpdate?.status || existingStep?.status || 'waiting',
          progress: stepUpdate?.progress || existingStep?.progress || 0,
          startTime: stepUpdate?.startTime || existingStep?.startTime,
          endTime: stepUpdate?.endTime || existingStep?.endTime,
          duration: stepUpdate?.duration || existingStep?.duration,
          errorMessage: stepUpdate?.errorMessage || existingStep?.errorMessage,
          subSteps: stepUpdate?.subSteps || existingStep?.subSteps || []
        } as AnalysisStep;
      });

      return {
        sessionId,
        topic: data.topic || prevData?.topic || '',
        status: data.status || prevData?.status || 'initializing',
        currentStep: data.currentStep || prevData?.currentStep || 'session_initialization',
        overallProgress: data.overallProgress || prevData?.overallProgress || 0,
        steps: updatedSteps,
        estimatedTimeRemaining: data.estimatedTimeRemaining || prevData?.estimatedTimeRemaining,
        statistics: data.statistics || prevData?.statistics
      };
    });

    setLastUpdateTime(new Date().toLocaleTimeString());
  };

  // Update specific step status
  const updateStepStatus = (stepId: string, status: AnalysisStep['status'], data?: any) => {
    setProgressData(prevData => {
      if (!prevData) return null;

      const updatedSteps = prevData.steps.map(step => {
        if (step.id === stepId) {
          return {
            ...step,
            status,
            endTime: status === 'finish' ? new Date().toISOString() : step.endTime,
            duration: data?.duration || step.duration,
            errorMessage: data?.errorMessage || step.errorMessage,
            progress: status === 'finish' ? 100 : data?.progress || step.progress
          };
        }
        return step;
      });

      return { ...prevData, steps: updatedSteps };
    });
  };

  // Calculate overall statistics
  const overallStatistics = useMemo(() => {
    if (!progressData) return null;

    const completedSteps = progressData.steps.filter(s => s.status === 'finish').length;
    const errorSteps = progressData.steps.filter(s => s.status === 'error').length;
    const runningSteps = progressData.steps.filter(s => s.status === 'process').length;
    
    const totalDuration = progressData.steps
      .filter(s => s.duration)
      .reduce((sum, s) => sum + (s.duration || 0), 0);

    return {
      totalSteps: progressData.steps.length,
      completedSteps,
      errorSteps,
      runningSteps,
      totalDurationSeconds: totalDuration,
      completionRate: (completedSteps / progressData.steps.length) * 100,
      hasErrors: errorSteps > 0
    };
  }, [progressData]);

  // Get current step details
  const currentStepDetails = useMemo(() => {
    if (!progressData) return null;
    
    return progressData.steps.find(s => s.id === progressData.currentStep);
  }, [progressData]);

  // Manual refresh function
  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call to refresh progress data
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };

  const getStepIcon = (step: AnalysisStep) => {
    switch (step.status) {
      case 'finish':
        return <CheckCircleOutlined sx={{ color: '#52c41a' }} />;
      case 'error':
        return <ErrorOutlined sx={{ color: '#ff4d4f' }} />;
      case 'process':
        return <CircularProgress size={20} sx={{ color: '#1890ff' }} />;
      default:
        return <ScheduleOutlined sx={{ color: '#8c8c8c' }} />;
    }
  };

  const getStepStatus = (step: AnalysisStep): 'wait' | 'process' | 'finish' | 'error' => {
    switch (step.status) {
      case 'finish':
        return 'finish';
      case 'error':
        return 'error';
      case 'process':
        return 'process';
      default:
        return 'wait';
    }
  };

  if (!progressData) {
    return (
      <Card 
        sx={{ 
          background: '#1a1a35', 
          border: '1px solid #3d3d56',
          mb: 2
        }}
      >
        <CardContent sx={{ p: 5, textAlign: 'center' }}>
          <CircularProgress sx={{ color: '#1890ff', mb: 2 }} />
          <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
            Loading analysis progress...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ backgroundColor: '#0f0f23' }}>
      {/* Header with overall progress */}
      <Card 
        sx={{ 
          background: '#1a1a35', 
          border: '1px solid #3d3d56', 
          mb: 2 
        }}
      >
        <CardContent sx={{ p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Stack spacing={1}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                    Strategic Analysis Progress
                  </Typography>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip 
                      label={progressData.status.toUpperCase()} 
                      color={progressData.status === 'completed' ? 'success' : progressData.status === 'error' ? 'error' : 'primary'}
                      size="small"
                    />
                    {autoRefresh && (
                      <IconButton 
                        size="small"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                      >
                        <RefreshOutlined sx={{ color: '#b8b8cc' }} />
                      </IconButton>
                    )}
                  </Stack>
                </Box>
                
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  Topic: {progressData.topic} • Session: {sessionId.substring(0, 8)}...
                </Typography>
                
                <LinearProgress
                  variant="determinate"
                  value={progressData.overallProgress}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: '#3d3d56',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: progressData.status === 'error' ? '#ff4d4f' : progressData.status === 'completed' ? '#52c41a' : '#1890ff',
                    },
                  }}
                />
              </Stack>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Stack spacing={1} sx={{ textAlign: { xs: 'left', md: 'right' } }}>
                <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                  Last Update: {lastUpdateTime}
                </Typography>
                {progressData.estimatedTimeRemaining && (
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    ETA: {Math.round(progressData.estimatedTimeRemaining / 60)} min
                  </Typography>
                )}
              </Stack>
            </Grid>
          </Grid>

          {/* Statistics Row */}
          {overallStatistics && (
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid item xs={6} sm={3}>
                <Paper sx={{ p: 1, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Completed</Typography>
                  <Typography variant="h6" sx={{ color: '#52c41a' }}>
                    {overallStatistics.completedSteps}/{overallStatistics.totalSteps}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper sx={{ p: 1, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Success Rate</Typography>
                  <Typography variant="h6" sx={{ color: '#1890ff' }}>
                    {overallStatistics.completionRate.toFixed(1)}%
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper sx={{ p: 1, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Duration</Typography>
                  <Typography variant="h6" sx={{ color: '#fa8c16' }}>
                    {Math.round(overallStatistics.totalDurationSeconds)}s
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper sx={{ p: 1, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Errors</Typography>
                  <Typography variant="h6" sx={{ color: overallStatistics.hasErrors ? '#ff4d4f' : '#52c41a' }}>
                    {overallStatistics.errorSteps}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          )}

          {overallStatistics?.hasErrors && (
            <Alert
              severity="warning"
              sx={{ 
                mt: 2, 
                backgroundColor: '#2d1b0e', 
                border: '1px solid #ad6800',
                color: '#e8e8f0'
              }}
            >
              Some steps encountered errors. Check individual step details below.
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Current Step Details */}
      {currentStepDetails && currentStepDetails.status === 'process' && (
        <Card 
          sx={{ 
            background: '#1a1a35', 
            border: '1px solid #3d3d56', 
            mb: 2 
          }}
        >
          <CardContent sx={{ p: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <CircularProgress size={20} sx={{ color: '#1890ff' }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Current Step
              </Typography>
            </Stack>
            <Stack spacing={1}>
              <Typography variant="subtitle1" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                {currentStepDetails.title}
              </Typography>
              <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                {currentStepDetails.description}
              </Typography>
              
              {currentStepDetails.progress !== undefined && (
                <LinearProgress
                  variant="determinate"
                  value={currentStepDetails.progress}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: '#3d3d56',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#1890ff',
                    },
                  }}
                />
              )}

              {currentStepDetails.subSteps && currentStepDetails.subSteps.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Sub-steps:</Typography>
                  <Stack spacing={0.5} sx={{ mt: 0.5 }}>
                    {currentStepDetails.subSteps.map((subStep, index) => (
                      <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" sx={{ color: '#e8e8f0' }}>
                          {subStep.name}
                        </Typography>
                        <Chip 
                          label={subStep.status}
                          size="small"
                          color={subStep.status === 'completed' ? 'success' : subStep.status === 'error' ? 'error' : subStep.status === 'running' ? 'primary' : 'default'}
                          sx={{ fontSize: '10px', height: '20px' }}
                        />
                      </Box>
                    ))}
                  </Stack>
                </Box>
              )}
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Main Steps Display */}
      <Card 
        sx={{ 
          background: '#1a1a35', 
          border: '1px solid #3d3d56' 
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 3 }}>
            <InfoOutlined sx={{ color: '#1890ff' }} />
            <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
              Analysis Workflow
            </Typography>
            <Tooltip title="Click on steps to view detailed information">
              <IconButton size="small">
                <InfoOutlined sx={{ color: '#b8b8cc' }} />
              </IconButton>
            </Tooltip>
          </Stack>

          <Stepper 
            orientation="vertical"
            activeStep={progressData.steps.findIndex(s => s.id === progressData.currentStep)}
            sx={{
              '& .MuiStepLabel-label': {
                color: '#e8e8f0',
                '&.Mui-active': {
                  color: '#1890ff',
                },
                '&.Mui-completed': {
                  color: '#52c41a',
                },
              },
              '& .MuiStepLabel-labelContainer': {
                '& .MuiStepLabel-iconContainer': {
                  '& .MuiStepIcon-root': {
                    color: '#3d3d56',
                    '&.Mui-active': {
                      color: '#1890ff',
                    },
                    '&.Mui-completed': {
                      color: '#52c41a',
                    },
                  },
                },
              },
            }}
          >
            {progressData.steps.map((step, index) => (
              <Step key={step.id} completed={step.status === 'finish'}>
                <StepLabel
                  StepIconComponent={() => getStepIcon(step)}
                  onClick={() => onStepClick?.(step.id)}
                  sx={{ cursor: onStepClick ? 'pointer' : 'default' }}
                >
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="subtitle1" sx={{ 
                      color: step.status === 'error' ? '#ff4d4f' : '#e8e8f0',
                      fontWeight: step.status === 'process' ? 'bold' : 'normal'
                    }}>
                      {step.title}
                    </Typography>
                    {step.duration && (
                      <Chip 
                        label={`${step.duration}s`} 
                        size="small"
                        sx={{ fontSize: '10px', height: '20px' }}
                      />
                    )}
                  </Stack>
                </StepLabel>
                <StepContent>
                  <Stack spacing={2}>
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                      {step.description}
                    </Typography>
                    
                    {step.status === 'process' && step.progress !== undefined && (
                      <LinearProgress
                        variant="determinate"
                        value={step.progress}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#3d3d56',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: '#1890ff',
                          },
                        }}
                      />
                    )}
                    
                    {step.errorMessage && (
                      <Alert
                        severity="error"
                        size="small"
                        sx={{ backgroundColor: '#2d1418', border: '1px solid #a8071a' }}
                      >
                        {step.errorMessage}
                      </Alert>
                    )}
                    
                    {showDetailedView && step.details && step.status !== 'waiting' && (
                      <Accordion sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                        <AccordionSummary expandIcon={<ExpandMoreOutlined sx={{ color: '#b8b8cc' }} />}>
                          <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                            Step Details
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Stack spacing={0.5}>
                            {step.details.slice(0, 5).map((detail, detailIndex) => (
                              <Typography key={detailIndex} variant="caption" sx={{ color: '#8c8ca0' }}>
                                • {detail}
                              </Typography>
                            ))}
                            {step.details.length > 5 && (
                              <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                                ... and {step.details.length - 5} more
                              </Typography>
                            )}
                          </Stack>
                        </AccordionDetails>
                      </Accordion>
                    )}
                    
                    {step.startTime && (
                      <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                        Started: {new Date(step.startTime).toLocaleTimeString()}
                        {step.endTime && ` • Completed: ${new Date(step.endTime).toLocaleTimeString()}`}
                      </Typography>
                    )}
                  </Stack>
                </StepContent>
              </Step>
            ))}
          </Stepper>

          {/* Analysis Statistics */}
          {progressData.statistics && (
            <Box sx={{ mt: 4, pt: 2, borderTop: '1px solid #3d3d56' }}>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                Analysis Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Total Layers</Typography>
                    <Typography variant="h6" sx={{ color: '#1890ff' }}>
                      {progressData.statistics.totalLayers}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Completed Layers</Typography>
                    <Typography variant="h6" sx={{ color: '#52c41a' }}>
                      {progressData.statistics.completedLayers}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Strategic Factors</Typography>
                    <Typography variant="h6" sx={{ color: '#fa8c16' }}>
                      {progressData.statistics.completedFactors}/{progressData.statistics.totalFactors}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Evidence Chunks</Typography>
                    <Typography variant="h6" sx={{ color: '#722ed1' }}>
                      {progressData.statistics.evidenceChunks}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Patterns Triggered</Typography>
                    <Typography variant="h6" sx={{ color: '#13c2c2' }}>
                      {progressData.statistics.patternsTrigger}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalysisProgressStepper;
