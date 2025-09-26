import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
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
  Paper,
  Button,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  ExpandMore,
  Analytics,
  TrendingUp,
  Assessment,
  Speed,
  Refresh
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';
import { StrategicAnalysisService, ResultsResponse } from '../services/strategicAnalysisService';

interface ActionLayerData {
  factor_scores: { [key: string]: number };
  layer_scores: { [key: string]: { score: number; confidence: number } };
  formula_calculations: { [key: string]: { result: number; formula: string; inputs: any } };
}

const ActionLayerDemoPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [actionLayerData, setActionLayerData] = useState<ActionLayerData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedPanel, setExpandedPanel] = useState<string | false>('factors');

  useEffect(() => {
    if (sessionId) {
      loadActionLayerData();
    }
  }, [sessionId]);

  const loadActionLayerData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get analysis results from existing service
      const analysisResults = await StrategicAnalysisService.getAnalysisResults(sessionId!);
      setResults(analysisResults);

      // Transform results into action layer format
      const actionData: ActionLayerData = {
        factor_scores: analysisResults.strategic_factors 
          ? Object.entries(analysisResults.strategic_factors).reduce((acc, [key, value]) => {
              acc[key] = value.score;
              return acc;
            }, {} as { [key: string]: number })
          : {},
        layer_scores: analysisResults.strategic_layers
          ? Object.entries(analysisResults.strategic_layers).reduce((acc, [key, value]) => {
              acc[key] = { score: value.score, confidence: value.confidence };
              return acc;
            }, {} as { [key: string]: { score: number; confidence: number } })
          : {},
        formula_calculations: generateMockFormulaCalculations()
      };

      setActionLayerData(actionData);
    } catch (err: any) {
      setError(err.message || 'Failed to load action layer data');
    } finally {
      setLoading(false);
    }
  };

  const generateMockFormulaCalculations = () => {
    const formulas = {
      'F1_Market_Size': { result: 85.2, formula: 'Market_TAM * Growth_Rate * Penetration', inputs: { Market_TAM: 1000, Growth_Rate: 0.12, Penetration: 0.71 }},
      'F2_Competition': { result: 72.8, formula: 'HHI_Index * (1 - Barriers_Entry) * Switching_Cost', inputs: { HHI_Index: 0.65, Barriers_Entry: 0.3, Switching_Cost: 0.8 }},
      'F3_Technology': { result: 91.5, formula: 'Tech_Readiness * Innovation_Rate * Adoption_Speed', inputs: { Tech_Readiness: 0.95, Innovation_Rate: 0.88, Adoption_Speed: 1.09 }},
      'D_Score': { result: 78.4, formula: '(F1 * 0.3 + F2 * 0.25 + F3 * 0.45) * Confidence_Weight', inputs: { F1: 85.2, F2: 72.8, F3: 91.5, Confidence_Weight: 0.92 }},
      'Risk_Score': { result: 23.7, formula: '1 - (Stability * Predictability * Mitigation)', inputs: { Stability: 0.85, Predictability: 0.78, Mitigation: 0.88 }},
      'SWOT_Score': { result: 82.1, formula: '(Strengths + Opportunities - Weaknesses - Threats) / 4', inputs: { Strengths: 88, Opportunities: 84, Weaknesses: 22, Threats: 18 }}
    };
    return formulas;
  };

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
          Loading Action Layer Analysis...
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
        <Button variant="contained" onClick={loadActionLayerData} startIcon={<Refresh />}>
          Retry
        </Button>
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
            <Analytics sx={{ fontSize: 32, color: '#1890ff', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              Action Layer Demo
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: '#b8b8cc', mb: 2 }}>
            Interactive demonstration of F1-F28 strategic factors and 18 action-layer formulas
          </Typography>
          {results && (
            <Chip 
              label={`Topic: ${results.topic}`}
              sx={{ backgroundColor: '#1890ff20', color: '#1890ff', mr: 1 }}
            />
          )}
          <Chip 
            label={`Session: ${sessionId}`}
            sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
          />
        </Box>

        {/* Strategic Factors Panel */}
        <Accordion 
          expanded={expandedPanel === 'factors'} 
          onChange={handlePanelChange('factors')}
          sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUp sx={{ color: '#1890ff', mr: 2 }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Strategic Factors (F1-F28)
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {actionLayerData && Object.entries(actionLayerData.factor_scores).map(([factor, score]) => (
                <Grid item xs={12} sm={6} md={4} key={factor}>
                  <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <CardContent>
                      <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                        {factor.replace(/_/g, ' ')}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h4" sx={{ color: getScoreColor(score), mr: 2 }}>
                          {score.toFixed(1)}
                        </Typography>
                        <Chip 
                          size="small"
                          label={getScoreLevel(score)}
                          sx={{ 
                            backgroundColor: `${getScoreColor(score)}20`,
                            color: getScoreColor(score)
                          }}
                        />
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={score} 
                        sx={{ 
                          height: 6, 
                          borderRadius: 3,
                          backgroundColor: '#3d3d56',
                          '& .MuiLinearProgress-bar': { backgroundColor: getScoreColor(score) }
                        }} 
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Strategic Layers Panel */}
        <Accordion 
          expanded={expandedPanel === 'layers'} 
          onChange={handlePanelChange('layers')}
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
              {actionLayerData && Object.entries(actionLayerData.layer_scores).map(([layer, data]) => (
                <Grid item xs={12} md={6} key={layer}>
                  <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                        {layer}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                        <Box>
                          <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Score</Typography>
                          <Typography variant="h4" sx={{ color: getScoreColor(data.score) }}>
                            {data.score}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Confidence</Typography>
                          <Typography variant="h5" sx={{ color: '#fa8c16' }}>
                            {(data.confidence * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={data.score} 
                        sx={{ 
                          height: 8, 
                          borderRadius: 4,
                          backgroundColor: '#3d3d56',
                          '& .MuiLinearProgress-bar': { backgroundColor: getScoreColor(data.score) }
                        }} 
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Formula Calculations Panel */}
        <Accordion 
          expanded={expandedPanel === 'formulas'} 
          onChange={handlePanelChange('formulas')}
          sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Speed sx={{ color: '#fa8c16', mr: 2 }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Formula Calculations (18 Action Layer Formulas)
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper} sx={{ backgroundColor: '#252547' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Formula</TableCell>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Result</TableCell>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Calculation</TableCell>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Inputs</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {actionLayerData && Object.entries(actionLayerData.formula_calculations).map(([formula, data]) => (
                    <TableRow key={formula}>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 500 }}>
                        {formula}
                      </TableCell>
                      <TableCell>
                        <Typography 
                          variant="h6" 
                          sx={{ color: getScoreColor(data.result), fontWeight: 600 }}
                        >
                          {data.result.toFixed(1)}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ color: '#b8b8cc', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                        {data.formula}
                      </TableCell>
                      <TableCell sx={{ color: '#b8b8cc', fontSize: '0.8rem' }}>
                        {Object.entries(data.inputs).map(([key, value]) => (
                          <Box key={key} sx={{ mb: 0.5 }}>
                            <strong>{key}:</strong> {typeof value === 'number' ? value.toFixed(2) : value}
                          </Box>
                        ))}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>

        {/* Action Items */}
        {results?.action_items && results.action_items.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3, fontWeight: 600 }}>
              Recommended Actions
            </Typography>
            <Grid container spacing={2}>
              {results.action_items.map((item, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                          {item.title}
                        </Typography>
                        <Chip 
                          size="small"
                          label={item.priority}
                          sx={{
                            backgroundColor: item.priority === 'high' ? '#ff4d4f20' : 
                                           item.priority === 'medium' ? '#fa8c1620' : '#52c41a20',
                            color: item.priority === 'high' ? '#ff4d4f' : 
                                   item.priority === 'medium' ? '#fa8c16' : '#52c41a'
                          }}
                        />
                      </Box>
                      <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                        {item.description}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                          <strong>Timeline:</strong> {item.timeline}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                          <strong>Owner:</strong> {item.responsible_party}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </motion.div>
    </Box>
  );
};

export default ActionLayerDemoPage;
