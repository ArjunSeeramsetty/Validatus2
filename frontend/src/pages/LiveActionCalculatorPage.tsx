import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Card, 
  CardContent, 
  CircularProgress, 
  List, 
  ListItem, 
  ListItemText,
  Grid,
  Chip,
  Alert,
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
  Divider
} from '@mui/material';
import { ExpandMore, Analytics, TrendingUp, Assessment, Search } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiClient } from '../services/apiClient';

interface CalculationResult {
  financial_metrics: {
    unit_price: number;
    unit_cost: number;
    unit_margin: number;
    margin_percent: number;
    expected_volume: number;
    total_revenue: number;
    total_cost: number;
    total_profit: number;
    adjusted_margin: number;
    adjusted_profit: number;
  };
  live_evidence: {
    query: string;
    results_count: number;
    relevance_score: number;
    evidence_adjustment: number;
    results: Array<{
      title: string;
      snippet: string;
      link: string;
    }>;
  };
  risk_assessment: {
    market_volatility: number;
    competition_risk: number;
    supply_chain_risk: number;
  };
  opportunity_analysis: {
    market_growth: number;
    innovation_potential: number;
    scalability: number;
  };
  recommendations: string[];
  calculation_timestamp?: number;
}

const LiveActionCalculatorPage: React.FC = () => {
  const [price, setPrice] = useState('');
  const [cost, setCost] = useState('');
  const [volume, setVolume] = useState('1000');
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedPanel, setExpandedPanel] = useState<string | false>('financial');

  const handleCalculate = async () => {
    if (!price || !cost || !query) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiClient.post('/api/v3/analysis/live-calculate', {
        client_inputs: {
          unit_price: parseFloat(price),
          unit_cost: parseFloat(cost),
          expected_volume: parseFloat(volume)
        },
        query
      });

      setResult(response.data.calculation_result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePanelChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#52c41a';
    if (score >= 0.4) return '#fa8c16';
    return '#ff4d4f';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

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
            <Analytics sx={{ fontSize: 32, color: '#1890ff', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              Live Action Layer Calculator
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: '#b8b8cc', mb: 3 }}>
            Real-time business calculations enhanced with live web search data
          </Typography>
        </Box>

        {/* Input Form */}
        <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', mb: 4 }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
              Business Inputs
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Unit Price ($)"
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: '#e8e8f0',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputLabel-root': { color: '#b8b8cc' }
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Unit Cost ($)"
                  type="number"
                  value={cost}
                  onChange={(e) => setCost(e.target.value)}
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: '#e8e8f0',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputLabel-root': { color: '#b8b8cc' }
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Expected Volume"
                  type="number"
                  value={volume}
                  onChange={(e) => setVolume(e.target.value)}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: '#e8e8f0',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputLabel-root': { color: '#b8b8cc' }
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Live Evidence Query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., 'pergola market trends 2024' or 'outdoor living industry growth'"
                  required
                  multiline
                  rows={2}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: '#e8e8f0',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputLabel-root': { color: '#b8b8cc' }
                  }}
                />
              </Grid>
            </Grid>
            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={handleCalculate}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <Search />}
                sx={{
                  backgroundColor: '#1890ff',
                  '&:hover': { backgroundColor: '#1890ff', opacity: 0.9 }
                }}
              >
                {loading ? 'Calculating...' : 'Calculate with Live Data'}
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Results Display */}
        {result && (
          <Box>
            {/* Financial Metrics */}
            <Accordion 
              expanded={expandedPanel === 'financial'} 
              onChange={handlePanelChange('financial')}
              sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
            >
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUp sx={{ color: '#52c41a', mr: 2 }} />
                  <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                    Financial Metrics
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                          Unit Economics
                        </Typography>
                        <TableContainer>
                          <Table size="small">
                            <TableBody>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Unit Price</TableCell>
                                <TableCell sx={{ color: '#e8e8f0' }}>{formatCurrency(result.financial_metrics.unit_price)}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Unit Cost</TableCell>
                                <TableCell sx={{ color: '#e8e8f0' }}>{formatCurrency(result.financial_metrics.unit_cost)}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Unit Margin</TableCell>
                                <TableCell sx={{ color: '#52c41a' }}>{formatCurrency(result.financial_metrics.unit_margin)}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Margin %</TableCell>
                                <TableCell sx={{ color: '#52c41a' }}>{result.financial_metrics.margin_percent.toFixed(1)}%</TableCell>
                              </TableRow>
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                          Volume Projections
                        </Typography>
                        <TableContainer>
                          <Table size="small">
                            <TableBody>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Expected Volume</TableCell>
                                <TableCell sx={{ color: '#e8e8f0' }}>{result.financial_metrics.expected_volume.toLocaleString()}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Total Revenue</TableCell>
                                <TableCell sx={{ color: '#1890ff' }}>{formatCurrency(result.financial_metrics.total_revenue)}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Total Cost</TableCell>
                                <TableCell sx={{ color: '#ff4d4f' }}>{formatCurrency(result.financial_metrics.total_cost)}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell sx={{ color: '#b8b8cc' }}>Total Profit</TableCell>
                                <TableCell sx={{ color: '#52c41a' }}>{formatCurrency(result.financial_metrics.total_profit)}</TableCell>
                              </TableRow>
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Live Evidence */}
            <Accordion 
              expanded={expandedPanel === 'evidence'} 
              onChange={handlePanelChange('evidence')}
              sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
            >
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Search sx={{ color: '#1890ff', mr: 2 }} />
                  <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                    Live Evidence ({result.live_evidence.results_count} results)
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ mb: 3 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                        <CardContent>
                          <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                            Relevance Score
                          </Typography>
                          <Typography variant="h4" sx={{ color: getScoreColor(result.live_evidence.relevance_score) }}>
                            {formatPercent(result.live_evidence.relevance_score)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                        <CardContent>
                          <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                            Evidence Adjustment
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#1890ff' }}>
                            {formatPercent(result.live_evidence.evidence_adjustment - 1)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                        <CardContent>
                          <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                            Adjusted Profit
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#52c41a' }}>
                            {formatCurrency(result.financial_metrics.adjusted_profit)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
                <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                  Search Results
                </Typography>
                <List>
                  {result.live_evidence.results.map((item, index) => (
                    <ListItem key={index} sx={{ backgroundColor: '#252547', mb: 1, borderRadius: 1 }}>
                      <ListItemText
                        primary={
                          <Typography variant="subtitle1" sx={{ color: '#e8e8f0' }}>
                            {item.title}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                              {item.snippet}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#1890ff' }}>
                              {item.link}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>

            {/* Risk & Opportunity Analysis */}
            <Accordion 
              expanded={expandedPanel === 'analysis'} 
              onChange={handlePanelChange('analysis')}
              sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
            >
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Assessment sx={{ color: '#fa8c16', mr: 2 }} />
                  <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                    Risk & Opportunity Analysis
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                          Risk Assessment
                        </Typography>
                        {Object.entries(result.risk_assessment).map(([key, value]) => (
                          <Box key={key} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                                {key.replace(/_/g, ' ').toUpperCase()}
                              </Typography>
                              <Typography variant="body2" sx={{ color: getScoreColor(1 - value) }}>
                                {formatPercent(value)}
                              </Typography>
                            </Box>
                            <Box sx={{ width: '100%', height: 4, backgroundColor: '#3d3d56', borderRadius: 2 }}>
                              <Box 
                                sx={{ 
                                  width: `${value * 100}%`, 
                                  height: '100%', 
                                  backgroundColor: getScoreColor(1 - value),
                                  borderRadius: 2
                                }} 
                              />
                            </Box>
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                          Opportunity Analysis
                        </Typography>
                        {Object.entries(result.opportunity_analysis).map(([key, value]) => (
                          <Box key={key} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                                {key.replace(/_/g, ' ').toUpperCase()}
                              </Typography>
                              <Typography variant="body2" sx={{ color: getScoreColor(value) }}>
                                {formatPercent(value)}
                              </Typography>
                            </Box>
                            <Box sx={{ width: '100%', height: 4, backgroundColor: '#3d3d56', borderRadius: 2 }}>
                              <Box 
                                sx={{ 
                                  width: `${value * 100}%`, 
                                  height: '100%', 
                                  backgroundColor: getScoreColor(value),
                                  borderRadius: 2
                                }} 
                              />
                            </Box>
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
                    Strategic Recommendations
                  </Typography>
                  <Grid container spacing={2}>
                    {result.recommendations.map((recommendation, index) => (
                      <Grid item xs={12} md={6} key={index}>
                        <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                              <Chip
                                size="small"
                                label={`${index + 1}`}
                                sx={{ 
                                  backgroundColor: '#1890ff20', 
                                  color: '#1890ff',
                                  mr: 2,
                                  minWidth: 24
                                }}
                              />
                              <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                                {recommendation}
                              </Typography>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            )}
          </Box>
        )}
      </motion.div>
    </Box>
  );
};

export default LiveActionCalculatorPage;
