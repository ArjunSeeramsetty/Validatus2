/**
 * Sequential Analysis Workflow Page
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  CircularProgress,
  Alert,
  LinearProgress,
  Chip,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  PlayArrow,
  CheckCircle,
  Error,
  ExpandMore,
  Timeline,
  Assessment,
  Analytics,
  Refresh,
  Download
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';

import { useSequentialAnalysis } from '../hooks/useSequentialAnalysis';

const steps = [
  {
    label: 'Stage 1: Strategic Analysis',
    description: 'Knowledge acquisition and strategic layer scoring'
  },
  {
    label: 'Stage 2: RAG Query',
    description: 'Semantic search and evidence gathering'
  },
  {
    label: 'Stage 3: Action Layer',
    description: 'Formula calculations and action items'
  }
];

const SequentialAnalysisPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const {
    sessionId,
    currentStage,
    loading,
    error,
    sessionOverview,
    stage1Results,
    stage2Results,
    stage3Results,
    createSession,
    startStage1,
    checkStage1Status,
    getStage1Results,
    startStage2,
    checkStage2Status,
    getStage2Results,
    startStage3,
    checkStage3Status,
    getStage3Results,
    getSessionOverview,
    reset
  } = useSequentialAnalysis();

  const [activeStep, setActiveStep] = useState(0);
  const [stage2Query, setStage2Query] = useState('');
  const [stageStatuses, setStageStatuses] = useState<Record<number, any>>({});
  const [pollingIntervals, setPollingIntervals] = useState<Record<number, NodeJS.Timeout>>({});

  // Initialize session on component mount
  useEffect(() => {
    if (topicId && !sessionId) {
      handleCreateSession();
    }
    
    return () => {
      // Clean up polling intervals
      Object.values(pollingIntervals).forEach(clearInterval);
    };
  }, [topicId]);

  // Polling for stage status
  const startPolling = useCallback((stage: number, statusChecker: () => Promise<any>) => {
    if (pollingIntervals[stage]) {
      clearInterval(pollingIntervals[stage]);
    }

    const interval = setInterval(async () => {
      try {
        const status = await statusChecker();
        setStageStatuses(prev => ({ ...prev, [stage]: status }));
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          setPollingIntervals(prev => ({ ...prev, [stage]: undefined as any }));
          
          if (status.status === 'completed') {
            // Fetch results when completed
            if (stage === 1) await getStage1Results();
            else if (stage === 2) await getStage2Results();
            else if (stage === 3) await getStage3Results();
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000);

    setPollingIntervals(prev => ({ ...prev, [stage]: interval }));
  }, [pollingIntervals, getStage1Results, getStage2Results, getStage3Results]);

  const handleCreateSession = async () => {
    try {
      await createSession(topicId!, 'current-user'); // TODO: Get actual user ID
      setActiveStep(0);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleStartStage1 = async () => {
    try {
      await startStage1();
      setActiveStep(1);
      startPolling(1, checkStage1Status);
    } catch (err) {
      console.error('Failed to start Stage 1:', err);
    }
  };

  const handleStartStage2 = async () => {
    if (!stage2Query.trim()) {
      alert('Please enter a query for Stage 2');
      return;
    }

    try {
      await startStage2(stage2Query);
      setActiveStep(2);
      startPolling(2, checkStage2Status);
    } catch (err) {
      console.error('Failed to start Stage 2:', err);
    }
  };

  const handleStartStage3 = async () => {
    try {
      await startStage3();
      setActiveStep(3);
      startPolling(3, checkStage3Status);
    } catch (err) {
      console.error('Failed to start Stage 3:', err);
    }
  };

  const getStageIcon = (stage: number) => {
    const status = stageStatuses[stage]?.status;
    
    if (status === 'completed') return <CheckCircle sx={{ color: '#52c41a' }} />;
    if (status === 'failed') return <Error sx={{ color: '#ff4d4f' }} />;
    if (status === 'running') return <CircularProgress size={20} />;
    return stage === 1 ? <Timeline /> : stage === 2 ? <Assessment /> : <Analytics />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#52c41a';
      case 'running': return '#1890ff';
      case 'failed': return '#ff4d4f';
      default: return '#d9d9d9';
    }
  };

  if (!topicId) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">No topic ID provided</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Timeline sx={{ fontSize: 32, color: '#1890ff', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              Sequential Analysis Workflow
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: '#b8b8cc', mb: 2 }}>
            Execute Stage 1 → Stage 2 → Stage 3 analysis with human control between each stage
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip 
              label={`Topic: ${topicId}`} 
              sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} 
            />
            {sessionId && (
              <Chip 
                label={`Session: ${sessionId}`} 
                sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }} 
              />
            )}
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}

        {/* Stepper */}
        <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', mb: 4 }}>
          <CardContent>
            <Stepper activeStep={activeStep} orientation="vertical">
              {/* Stage 1 */}
              <Step>
                <StepLabel 
                  icon={getStageIcon(1)}
                  sx={{ 
                    '.MuiStepLabel-label': { color: '#e8e8f0' },
                    '.MuiStepLabel-label.Mui-active': { color: '#1890ff' }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      {steps[0].label}
                    </Typography>
                    {stageStatuses[1] && (
                      <Chip 
                        size="small"
                        label={stageStatuses[1].status}
                        sx={{ 
                          backgroundColor: `${getStatusColor(stageStatuses[1].status)}20`,
                          color: getStatusColor(stageStatuses[1].status)
                        }}
                      />
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    {steps[0].description}
                  </Typography>
                </StepLabel>
                <StepContent>
                  {!sessionId ? (
                    <Button 
                      variant="contained" 
                      onClick={handleCreateSession}
                      disabled={loading}
                      sx={{ mt: 2 }}
                    >
                      Create Analysis Session
                    </Button>
                  ) : !stageStatuses[1] || stageStatuses[1].status === 'pending' ? (
                    <Button
                      variant="contained"
                      startIcon={<PlayArrow />}
                      onClick={handleStartStage1}
                      disabled={loading}
                      sx={{ mt: 2 }}
                    >
                      Start Strategic Analysis
                    </Button>
                  ) : stageStatuses[1].status === 'running' ? (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                        Running strategic analysis...
                      </Typography>
                      <LinearProgress 
                        variant="indeterminate"
                        sx={{ 
                          backgroundColor: '#3d3d56',
                          '& .MuiLinearProgress-bar': { backgroundColor: '#1890ff' }
                        }}
                      />
                    </Box>
                  ) : stageStatuses[1].status === 'completed' && stage1Results ? (
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="success" sx={{ mb: 2 }}>
                        Stage 1 completed successfully!
                      </Alert>
                      <Accordion sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography sx={{ color: '#e8e8f0' }}>View Strategic Analysis Results</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography variant="subtitle2" sx={{ color: '#1890ff', mb: 1 }}>
                            Strategic Layers:
                          </Typography>
                          {stage1Results.strategic_layers && Object.entries(stage1Results.strategic_layers).map(([layer, data]: [string, any]) => (
                            <Box key={layer} sx={{ mb: 1 }}>
                              <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                                {layer}: {data.score}% (Confidence: {(data.confidence * 100).toFixed(0)}%)
                              </Typography>
                            </Box>
                          ))}
                        </AccordionDetails>
                      </Accordion>
                    </Box>
                  ) : null}
                </StepContent>
              </Step>

              {/* Stage 2 */}
              <Step>
                <StepLabel 
                  icon={getStageIcon(2)}
                  sx={{ 
                    '.MuiStepLabel-label': { color: '#e8e8f0' },
                    '.MuiStepLabel-label.Mui-active': { color: '#1890ff' }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      {steps[1].label}
                    </Typography>
                    {stageStatuses[2] && (
                      <Chip 
                        size="small"
                        label={stageStatuses[2].status}
                        sx={{ 
                          backgroundColor: `${getStatusColor(stageStatuses[2].status)}20`,
                          color: getStatusColor(stageStatuses[2].status)
                        }}
                      />
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    {steps[1].description}
                  </Typography>
                </StepLabel>
                <StepContent>
                  {stageStatuses[1]?.status === 'completed' && (
                    <>
                      {(!stageStatuses[2] || stageStatuses[2].status === 'pending') && (
                        <Box sx={{ mt: 2 }}>
                          <TextField
                            fullWidth
                            multiline
                            minRows={2}
                            placeholder="Enter your semantic search query..."
                            value={stage2Query}
                            onChange={(e) => setStage2Query(e.target.value)}
                            sx={{
                              mb: 2,
                              '& .MuiOutlinedInput-root': {
                                backgroundColor: '#252547',
                                '& fieldset': { borderColor: '#3d3d56' },
                                '&:hover fieldset': { borderColor: '#1890ff' },
                                '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                              },
                              '& .MuiInputBase-input': { color: '#e8e8f0' }
                            }}
                          />
                          <Button
                            variant="contained"
                            startIcon={<Assessment />}
                            onClick={handleStartStage2}
                            disabled={loading || !stage2Query.trim()}
                          >
                            Start RAG Query Analysis
                          </Button>
                        </Box>
                      )}
                      
                      {stageStatuses[2]?.status === 'running' && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                            Running semantic search: "{stage2Query}"
                          </Typography>
                          <LinearProgress 
                            variant="indeterminate"
                            sx={{ 
                              backgroundColor: '#3d3d56',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#52c41a' }
                            }}
                          />
                        </Box>
                      )}
                      
                      {stageStatuses[2]?.status === 'completed' && stage2Results && (
                        <Box sx={{ mt: 2 }}>
                          <Alert severity="success" sx={{ mb: 2 }}>
                            Stage 2 completed! Found {stage2Results.total_results} results.
                          </Alert>
                          <Accordion sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                            <AccordionSummary expandIcon={<ExpandMore />}>
                              <Typography sx={{ color: '#e8e8f0' }}>View RAG Query Results</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <List>
                                {stage2Results.results.slice(0, 3).map((result, index) => (
                                  <ListItem key={index} sx={{ backgroundColor: '#1a1a35', mb: 1, borderRadius: 1 }}>
                                    <ListItemText
                                      primary={result.content.substring(0, 100) + '...'}
                                      secondary={`Similarity: ${(result.similarity_score * 100).toFixed(1)}%`}
                                      sx={{
                                        '& .MuiListItemText-primary': { color: '#e8e8f0' },
                                        '& .MuiListItemText-secondary': { color: '#b8b8cc' }
                                      }}
                                    />
                                  </ListItem>
                                ))}
                              </List>
                            </AccordionDetails>
                          </Accordion>
                        </Box>
                      )}
                    </>
                  )}
                </StepContent>
              </Step>

              {/* Stage 3 */}
              <Step>
                <StepLabel 
                  icon={getStageIcon(3)}
                  sx={{ 
                    '.MuiStepLabel-label': { color: '#e8e8f0' },
                    '.MuiStepLabel-label.Mui-active': { color: '#1890ff' }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      {steps[2].label}
                    </Typography>
                    {stageStatuses[3] && (
                      <Chip 
                        size="small"
                        label={stageStatuses[3].status}
                        sx={{ 
                          backgroundColor: `${getStatusColor(stageStatuses[3].status)}20`,
                          color: getStatusColor(stageStatuses[3].status)
                        }}
                      />
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    {steps[2].description}
                  </Typography>
                </StepLabel>
                <StepContent>
                  {stageStatuses[2]?.status === 'completed' && (
                    <>
                      {(!stageStatuses[3] || stageStatuses[3].status === 'pending') && (
                        <Button
                          variant="contained"
                          startIcon={<Analytics />}
                          onClick={handleStartStage3}
                          disabled={loading}
                          sx={{ mt: 2 }}
                        >
                          Start Action Layer Calculations
                        </Button>
                      )}
                      
                      {stageStatuses[3]?.status === 'running' && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                            Computing action layer formulas and generating insights...
                          </Typography>
                          <LinearProgress 
                            variant="indeterminate"
                            sx={{ 
                              backgroundColor: '#3d3d56',
                              '& .MuiLinearProgress-bar': { backgroundColor: '#fa8c16' }
                            }}
                          />
                        </Box>
                      )}
                      
                      {stageStatuses[3]?.status === 'completed' && stage3Results && (
                        <Box sx={{ mt: 2 }}>
                          <Alert severity="success" sx={{ mb: 2 }}>
                            🎉 All stages completed! Strategic analysis finished successfully.
                          </Alert>
                          
                          <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                              <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                                <Typography variant="subtitle1" sx={{ color: '#fa8c16', mb: 1 }}>
                                  Overall Score
                                </Typography>
                                <Typography variant="h3" sx={{ color: '#e8e8f0' }}>
                                  {(stage3Results.overall_score * 100).toFixed(1)}%
                                </Typography>
                              </Paper>
                            </Grid>
                            
                            <Grid item xs={12} md={6}>
                              <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                                <Typography variant="subtitle1" sx={{ color: '#52c41a', mb: 1 }}>
                                  Action Items
                                </Typography>
                                <Typography variant="h3" sx={{ color: '#e8e8f0' }}>
                                  {stage3Results.action_items.length}
                                </Typography>
                              </Paper>
                            </Grid>
                          </Grid>
                          
                          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                            <Button
                              variant="contained"
                              startIcon={<Download />}
                              sx={{ backgroundColor: '#52c41a' }}
                            >
                              Export Results
                            </Button>
                            <Button
                              variant="outlined"
                              onClick={() => window.open(`/action-layer/${sessionId}`, '_blank')}
                              sx={{ borderColor: '#1890ff', color: '#1890ff' }}
                            >
                              View Action Layer Demo
                            </Button>
                          </Box>
                        </Box>
                      )}
                    </>
                  )}
                </StepContent>
              </Step>
            </Stepper>
          </CardContent>
        </Card>

        {/* Session Overview */}
        {sessionOverview && (
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                Session Overview
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip label={`Status: ${sessionOverview.overall_status}`} />
                <Chip label={`Current Stage: ${sessionOverview.current_stage}`} />
                <Chip label={`Created: ${new Date(sessionOverview.created_at).toLocaleString()}`} />
              </Box>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </Box>
  );
};

export default SequentialAnalysisPage;
