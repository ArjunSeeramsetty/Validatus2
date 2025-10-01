import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Alert, 
  Card, 
  CardContent, 
  Chip,
  Grid,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  Paper
} from '@mui/material';
import { ExpandMore, TrendingUp, Assessment } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiClient } from '../services/apiClient';

const PergolaAnalysisPage: React.FC = () => {
  const sessionId = 'v2_analysis_20250905_185553_d5654178';
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedPanel, setExpandedPanel] = useState<string | false>('strategic');

  useEffect(() => {
    const loadPergolaData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get(`/api/v3/migrated/results/${sessionId}`);
        setResult(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load Pergola analysis data');
      } finally {
        setLoading(false);
      }
    };

    loadPergolaData();
  }, []);

  const handlePanelChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  const getScoreLevel = (score: number) => {
    if (score >= 80) return 'High';
    if (score >= 60) return 'Medium';
    return 'Low';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2, color: '#e8e8f0' }}>
          Loading Pergola Market Analysis...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!result) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="warning">
          No analysis data available for Pergola Market
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1400, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TrendingUp sx={{ fontSize: 32, color: '#1890ff', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              Pergola Market Strategic Analysis
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Chip 
              label={`Session: ${sessionId}`}
              sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }}
            />
            <Chip 
              label={`Status: ${result.status || 'Completed'}`}
              sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
            />
            <Chip 
              label="Migrated Data"
              sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }}
            />
          </Box>
          <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
            Topic: {result.topic || 'Build a business case for the pergola market outdoor living'}
          </Typography>
        </Box>

        {/* Strategic Layers Analysis */}
        <Accordion 
          expanded={expandedPanel === 'strategic'} 
          onChange={handlePanelChange('strategic')}
          sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Assessment sx={{ color: '#52c41a', mr: 2 }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Strategic Layers Analysis
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {result.strategic_layers && Object.entries(result.strategic_layers).map(([layer, data]: [string, any]) => (
                <Grid item xs={12} md={6} key={layer}>
                  <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                        {layer}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                        <Typography variant="h4" sx={{ color: getScoreColor(data.score) }}>
                          {data.score}%
                        </Typography>
                        <Chip
                          size="small"
                          label={getScoreLevel(data.score)}
                          sx={{ 
                            backgroundColor: `${getScoreColor(data.score)}20`,
                            color: getScoreColor(data.score)
                          }}
                        />
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={data.score} 
                        sx={{ 
                          height: 6, 
                          borderRadius: 3,
                          backgroundColor: '#3d3d56',
                          '& .MuiLinearProgress-bar': { backgroundColor: getScoreColor(data.score) }
                        }} 
                      />
                      <Typography variant="body2" sx={{ color: '#b8b8cc', mt: 1 }}>
                        Confidence: {(data.confidence * 100).toFixed(0)}%
                      </Typography>
                      {data.insights && data.insights.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" sx={{ color: '#e8e8f0', mb: 1 }}>
                            Key Insights:
                          </Typography>
                          {data.insights.map((insight: string, index: number) => (
                            <Typography key={index} variant="body2" sx={{ color: '#b8b8cc', fontSize: '0.85rem' }}>
                              • {insight}
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

        {/* Action Layer Data */}
        {result.action_layer_data && (
          <Accordion 
            expanded={expandedPanel === 'action'} 
            onChange={handlePanelChange('action')}
            sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
          >
            <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Assessment sx={{ color: '#1890ff', mr: 2 }} />
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  Action Layer Calculations
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {/* Essential Metrics */}
              {result.action_layer_data.essential_metrics && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 2 }}>
                    Essential Metrics
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(result.action_layer_data.essential_metrics).map(([key, value]: [string, any]) => (
                      <Grid item xs={12} sm={6} md={4} key={key}>
                        <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                          <CardContent>
                            <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                              {key.replace(/_/g, ' ').toUpperCase()}
                            </Typography>
                            <Typography variant="h6" sx={{ color: getScoreColor(typeof value === 'number' ? value : 0) }}>
                              {typeof value === 'number' ? (isNaN(value) ? 'N/A' : value.toFixed(2)) : (value || 'N/A')}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* Growth Scenarios */}
              {result.action_layer_data.growth_scenarios && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 2 }}>
                    Growth Scenarios
                  </Typography>
                  <TableContainer component={Paper} sx={{ backgroundColor: '#252547' }}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Scenario</TableCell>
                          <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Growth Rate</TableCell>
                          <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Revenue Impact</TableCell>
                          <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Risk Level</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(result.action_layer_data.growth_scenarios).map(([scenario, data]: [string, any]) => (
                          <TableRow key={scenario}>
                            <TableCell sx={{ color: '#e8e8f0' }}>{scenario}</TableCell>
                            <TableCell sx={{ color: '#52c41a' }}>
                              {typeof data.growth_rate === 'number' ? `${(data.growth_rate * 100).toFixed(1)}%` : 'N/A'}
                            </TableCell>
                            <TableCell sx={{ color: '#1890ff' }}>
                              {typeof data.revenue_impact === 'number' ? `$${data.revenue_impact.toLocaleString()}` : 'N/A'}
                            </TableCell>
                            <TableCell>
                              <Chip
                                size="small"
                                label={data.risk_level || 'Medium'}
                                sx={{ 
                                  backgroundColor: data.risk_level === 'Low' ? '#52c41a20' : 
                                                 data.risk_level === 'High' ? '#ff4d4f20' : '#fa8c1620',
                                  color: data.risk_level === 'Low' ? '#52c41a' : 
                                         data.risk_level === 'High' ? '#ff4d4f' : '#fa8c16'
                                }}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}

              {/* Action Layer Scores */}
              {result.action_layer_data.action_layer_scores && (
                <Box>
                  <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 2 }}>
                    Action Layer Scores
                  </Typography>
                  {Object.entries(result.action_layer_data.action_layer_scores).map(([category, scores]: [string, any]) => (
                    <Box key={category} sx={{ mb: 3 }}>
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                        {category.replace(/_/g, ' ').toUpperCase()}
                      </Typography>
                      <Grid container spacing={2}>
                        {Array.isArray(scores) ? scores.map((score: any, index: number) => (
                          <Grid item xs={12} sm={6} md={4} key={score.score_id || index}>
                            <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                              <CardContent>
                                <Typography variant="subtitle2" sx={{ color: '#e8e8f0', mb: 1 }}>
                                  {score.score_name || 'Score'}
                                </Typography>
                                <Typography variant="h5" sx={{ color: getScoreColor(score.score_value || 0) }}>
                                  {typeof score.score_value === 'number' ? score.score_value.toFixed(1) : 'N/A'}
                                </Typography>
                                <Typography variant="body2" sx={{ color: '#b8b8cc', mt: 1, fontSize: '0.8rem' }}>
                                  {score.description || 'No description'}
                                </Typography>
                                <Typography variant="body2" sx={{ color: '#b8b8cc', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                                  Formula: {score.formula || 'N/A'}
                                </Typography>
                                <Chip
                                  size="small"
                                  label={score.category || 'Uncategorized'}
                                  sx={{ mt: 1, backgroundColor: '#1890ff20', color: '#1890ff' }}
                                />
                              </CardContent>
                            </Card>
                          </Grid>
                        )) : (
                          <Grid item xs={12} sm={6} md={4} key={category}>
                            <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                              <CardContent>
                                <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                                  {category.replace(/_/g, ' ').toUpperCase()}
                                </Typography>
                                <Typography variant="h5" sx={{ color: getScoreColor(typeof scores === 'number' ? scores : 0) }}>
                                  {typeof scores === 'number' ? scores.toFixed(1) : String(scores)}
                                </Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                        )}
                      </Grid>
                    </Box>
                  ))}
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Key Insights */}
        {result.key_insights && result.key_insights.length > 0 && (
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', mb: 4 }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
                Key Insights
              </Typography>
              <Grid container spacing={2}>
                {result.key_insights.map((insight: any, index: number) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                      <CardContent>
                        <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 1 }}>
                          {insight.title || `Insight ${index + 1}`}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                          {typeof insight === 'string' ? insight : (insight.description || insight.insight || 'No description available')}
                        </Typography>
                        {insight.confidence && (
                          <Chip
                            size="small"
                            label={`${(insight.confidence * 100).toFixed(0)}% confidence`}
                            sx={{ mt: 1, backgroundColor: '#52c41a20', color: '#52c41a' }}
                          />
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Strategic Recommendations */}
        {result.strategic_recommendations && result.strategic_recommendations.length > 0 && (
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
                Strategic Recommendations
              </Typography>
              <Grid container spacing={2}>
                {result.strategic_recommendations.map((recommendation: any, index: number) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                      <CardContent>
                        <Typography variant="subtitle1" sx={{ color: '#e8e8f0', mb: 1 }}>
                          {recommendation.title || `Recommendation ${index + 1}`}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                          {typeof recommendation === 'string' ? recommendation : (recommendation.description || recommendation.recommendation || 'No description available')}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          {recommendation.priority && (
                            <Chip
                              size="small"
                              label={recommendation.priority}
                              sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }}
                            />
                          )}
                          {recommendation.impact && (
                            <Chip
                              size="small"
                              label={recommendation.impact}
                              sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
                            />
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </Box>
  );
};

export default PergolaAnalysisPage;
