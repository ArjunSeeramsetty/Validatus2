/**
 * Scoring Tab Component - Strategic analysis scoring and results
 * 🆕 NEW COMPONENT: Integrates with existing AdvancedStrategyAnalysisEngine
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Assessment,
  PlayArrow,
  CheckCircle,
  Warning,
  Info,
  ExpandMore,
  Timeline,
  TrendingUp,
  Business,
  Star
} from '@mui/icons-material';
import { apiClient } from '../services/apiClient';

const ScoringTab: React.FC = () => {
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [scoring, setScoring] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<any>(null);
  const [scoringResults, setScoringResults] = useState<any>(null);
  const [showResultsDialog, setShowResultsDialog] = useState(false);

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    setLoading(true);
    setError(null);

    try {
      // ✅ USING NEW API: /api/v3/scoring/topics
      const response = await apiClient.get('/api/v3/scoring/topics');
      if (response.data.success) {
        setTopics(response.data.topics);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  const startScoring = async (sessionId: string) => {
    setScoring(sessionId);
    setError(null);

    try {
      // ✅ USING NEW API: /api/v3/scoring/{session_id}/start
      const response = await apiClient.post(`/api/v3/scoring/${sessionId}/start`);

      if (response.data.success) {
        // Reload topics
        await loadTopics();
        // Load and show results
        await loadScoringResults(sessionId);
      } else {
        throw new Error(response.data.error || 'Scoring failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start scoring');
    } finally {
      setScoring(null);
    }
  };

  const loadScoringResults = async (sessionId: string) => {
    try {
      // ✅ USING NEW API: /api/v3/scoring/{session_id}/results
      const response = await apiClient.get(`/api/v3/scoring/${sessionId}/results`);

      if (response.data.has_results) {
        setScoringResults(response.data);
        const topic = topics.find(t => t.session_id === sessionId);
        if (topic) {
          setSelectedTopic(topic);
          setShowResultsDialog(true);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load results');
    }
  };

  const getStatusChip = (status: string, hasContent: boolean) => {
    if (!hasContent) {
      return <Chip label="No Content" color="default" size="small" icon={<Warning />} />;
    }

    switch (status) {
      case 'never_scored':
        return <Chip label="Ready to Score" color="warning" size="small" icon={<Info />} />;
      case 'needs_update':
        return <Chip label="Needs Update" color="error" size="small" icon={<Warning />} />;
      case 'up_to_date':
        return <Chip label="Up to Date" color="success" size="small" icon={<CheckCircle />} />;
      case 'no_content':
        return <Chip label="Collect URLs First" color="default" size="small" icon={<Warning />} />;
      default:
        return <Chip label="Unknown" color="default" size="small" />;
    }
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1) + '%';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString() + ' ' +
      new Date(dateString).toLocaleTimeString();
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#52c41a';
    if (score >= 0.4) return '#faad14';
    return '#ff4d4f';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2, color: '#e8e8f0' }}>Loading topics...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ color: '#e8e8f0', mb: 1, display: 'flex', alignItems: 'center' }}>
          <Assessment sx={{ mr: 1 }} />
          Strategic Scoring Analysis
        </Typography>
        <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
          Execute comprehensive strategic analysis using advanced Monte Carlo simulation and factor scoring.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper} sx={{ backgroundColor: '#1a1a2e' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: '#e8e8f0' }}>Topic</TableCell>
              <TableCell sx={{ color: '#e8e8f0' }}>Content Status</TableCell>
              <TableCell sx={{ color: '#e8e8f0' }}>Scoring Status</TableCell>
              <TableCell sx={{ color: '#e8e8f0' }}>Last Scored</TableCell>
              <TableCell sx={{ color: '#e8e8f0' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {topics.map((topic) => (
              <TableRow key={topic.session_id} sx={{ '&:hover': { backgroundColor: '#2d2d44' } }}>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2" sx={{ color: '#e8e8f0' }}>
                      {topic.topic}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#888' }}>
                      {topic.description?.substring(0, 60)}...
                    </Typography>
                  </Box>
                </TableCell>

                <TableCell>
                  <Box>
                    <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                      {topic.content_statistics.total_items} URLs
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#888' }}>
                      Quality: {(topic.content_statistics.average_quality * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                </TableCell>

                <TableCell>
                  {getStatusChip(
                    topic.scoring_information.scoring_status,
                    topic.content_statistics.has_content
                  )}
                </TableCell>

                <TableCell>
                  {topic.scoring_information.last_scored ? (
                    <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                      {formatDate(topic.scoring_information.last_scored)}
                    </Typography>
                  ) : (
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      Never
                    </Typography>
                  )}
                </TableCell>

                <TableCell>
                  <Box display="flex" gap={1}>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => startScoring(topic.session_id)}
                      disabled={!topic.scoring_information.ready_for_scoring || scoring === topic.session_id}
                      startIcon={scoring === topic.session_id ? <CircularProgress size={16} /> : <PlayArrow />}
                      sx={{ backgroundColor: '#1890ff' }}
                    >
                      {scoring === topic.session_id ? 'Analyzing...' : 'Start Scoring'}
                    </Button>

                    {topic.scoring_information.has_scores && (
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => loadScoringResults(topic.session_id)}
                        startIcon={<Assessment />}
                        sx={{ borderColor: '#1890ff', color: '#1890ff' }}
                      >
                        View Results
                      </Button>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {topics.length === 0 && !loading && (
        <Box textAlign="center" py={6}>
          <Assessment sx={{ fontSize: 64, color: '#888', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 1 }}>
            No Topics Found
          </Typography>
          <Typography variant="body2" sx={{ color: '#888' }}>
            Create some topics with collected URLs to see them here for scoring.
          </Typography>
        </Box>
      )}

      {/* Scoring Results Dialog */}
      <Dialog
        open={showResultsDialog}
        onClose={() => setShowResultsDialog(false)}
        maxWidth="lg"
        fullWidth
        disableRestoreFocus
        PaperProps={{ sx: { backgroundColor: '#1a1a2e', color: '#e8e8f0' } }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid #2d2d44' }}>
          <Box display="flex" alignItems="center">
            <Assessment sx={{ mr: 1 }} />
            Strategic Analysis Results: {selectedTopic?.topic}
          </Box>
        </DialogTitle>

        <DialogContent dividers sx={{ borderColor: '#2d2d44' }}>
          {scoringResults && scoringResults.results && (
            <Box>
              {/* Overall Score Card */}
              <Card sx={{ mb: 3, backgroundColor: '#0f0f1a', border: '1px solid #2d2d44' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ color: '#e8e8f0' }}>
                    Overall Business Case Score
                  </Typography>
                  <Box display="flex" justifyContent="center" alignItems="center" py={3}>
                    <Box textAlign="center">
                      <Typography
                        variant="h1"
                        sx={{
                          color: getScoreColor(scoringResults.results.business_case_score || 0.5),
                          fontWeight: 'bold'
                        }}
                      >
                        {formatScore(scoringResults.results.business_case_score || 0.5)}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#888' }}>
                        Strategic Attractiveness
                      </Typography>
                    </Box>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={4} textAlign="center">
                      <Typography variant="h6" sx={{ color: '#1890ff' }}>
                        {scoringResults.results.scenarios?.length || 0}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                        Scenarios Analyzed
                      </Typography>
                    </Grid>
                    <Grid item xs={4} textAlign="center">
                      <Typography variant="h6" sx={{ color: '#52c41a' }}>
                        {scoringResults.results.confidence ? 
                          (scoringResults.results.confidence * 100).toFixed(0) : 80}%
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                        Confidence Level
                      </Typography>
                    </Grid>
                    <Grid item xs={4} textAlign="center">
                      <Typography variant="h6" sx={{ color: '#fa8c16' }}>
                        {scoringResults.results.analysis_metadata?.runs || 'N/A'}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                        Simulation Runs
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              {/* Scenarios */}
              {scoringResults.results.scenarios && scoringResults.results.scenarios.length > 0 && (
                <Accordion sx={{ backgroundColor: '#1a1a2e', mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      Strategic Scenarios ({scoringResults.results.scenarios.length})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      {scoringResults.results.scenarios.map((scenario: any, index: number) => (
                        <Grid item xs={12} md={6} key={index}>
                          <Card variant="outlined" sx={{ backgroundColor: '#0f0f1a', borderColor: '#2d2d44' }}>
                            <CardContent>
                              <Typography variant="subtitle1" sx={{ color: '#1890ff', mb: 1 }}>
                                {scenario.name || `Scenario ${index + 1}`}
                              </Typography>

                              <Box sx={{ mb: 2 }}>
                                <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                                  Probability
                                </Typography>
                                <LinearProgress
                                  variant="determinate"
                                  value={(scenario.probability || 0.33) * 100}
                                  sx={{
                                    mt: 0.5,
                                    '& .MuiLinearProgress-bar': {
                                      backgroundColor: '#1890ff'
                                    }
                                  }}
                                />
                                <Typography variant="body2" sx={{ color: '#e8e8f0', mt: 0.5 }}>
                                  {((scenario.probability || 0.33) * 100).toFixed(1)}%
                                </Typography>
                              </Box>

                              {scenario.narrative && (
                                <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                                  {scenario.narrative}
                                </Typography>
                              )}

                              {scenario.kpis && (
                                <Box sx={{ mt: 2 }}>
                                  <Typography variant="caption" sx={{ color: '#888' }}>
                                    Key Metrics:
                                  </Typography>
                                  {Object.entries(scenario.kpis).slice(0, 3).map(([key, value]: any) => (
                                    <Typography key={key} variant="caption" display="block" sx={{ color: '#b8b8cc' }}>
                                      • {key}: {typeof value === 'number' ? value.toFixed(2) : value}
                                    </Typography>
                                  ))}
                                </Box>
                              )}
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Driver Sensitivities */}
              {scoringResults.results.driver_sensitivities && 
               Object.keys(scoringResults.results.driver_sensitivities).length > 0 && (
                <Accordion sx={{ backgroundColor: '#1a1a2e', mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      Driver Sensitivities
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell sx={{ color: '#b8b8cc' }}>Driver</TableCell>
                            <TableCell sx={{ color: '#b8b8cc' }}>Impact</TableCell>
                            <TableCell sx={{ color: '#b8b8cc' }}>Sensitivity</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {Object.entries(scoringResults.results.driver_sensitivities).map(([driver, sensitivity]: any) => (
                            <TableRow key={driver}>
                              <TableCell sx={{ color: '#e8e8f0' }}>
                                {driver.replace(/_/g, ' ')}
                              </TableCell>
                              <TableCell>
                                <LinearProgress
                                  variant="determinate"
                                  value={Math.min(100, Math.abs(sensitivity))}
                                  sx={{
                                    '& .MuiLinearProgress-bar': {
                                      backgroundColor: sensitivity > 0 ? '#52c41a' : '#ff4d4f'
                                    }
                                  }}
                                />
                              </TableCell>
                              <TableCell sx={{ color: '#e8e8f0' }}>
                                {sensitivity.toFixed(2)}%
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Financial Projections */}
              {scoringResults.results.financial_projections && (
                <Accordion sx={{ backgroundColor: '#1a1a2e' }}>
                  <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      Financial Projections
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      {Object.entries(scoringResults.results.financial_projections).map(([key, value]: any) => (
                        <Grid item xs={6} sm={4} key={key}>
                          <Paper sx={{ p: 2, backgroundColor: '#0f0f1a' }}>
                            <Typography variant="caption" sx={{ color: '#888' }}>
                              {key.replace(/_/g, ' ').toUpperCase()}
                            </Typography>
                            <Typography variant="h6" sx={{ color: '#52c41a' }}>
                              {typeof value === 'number' ? `$${value.toLocaleString()}` : value}
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Analysis Metadata */}
              <Card sx={{ mt: 2, backgroundColor: '#0f0f1a', border: '1px solid #2d2d44' }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom sx={{ color: '#e8e8f0' }}>
                    Analysis Metadata
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: '#888' }}>Scored At:</Typography>
                      <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                        {formatDate(scoringResults.scored_at)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: '#888' }}>Analysis Type:</Typography>
                      <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                        {scoringResults.results.analysis_metadata?.analysis_type || 'Comprehensive'}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ borderTop: '1px solid #2d2d44' }}>
          <Button onClick={() => setShowResultsDialog(false)} sx={{ color: '#b8b8cc' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScoringTab;
