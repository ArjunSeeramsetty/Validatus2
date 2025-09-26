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
  Paper,
  Button
} from '@mui/material';
import { ExpandMore, Analytics, TrendingUp, Assessment, Speed, Refresh } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiClient } from '../services/apiClient';

const ActionLayerDemoPage: React.FC = () => {
  const sessionId = 'v2_analysis_20250905_185553_d5654178';
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedPanel, setExpandedPanel] = useState<string | false>('scores');

  useEffect(() => {
    const loadActionLayerData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get(`/api/v3/migrated/action-layer/${sessionId}`);
        setData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load Action Layer data');
      } finally {
        setLoading(false);
      }
    };

    loadActionLayerData();
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

  const retryLoad = () => {
    setLoading(true);
    setError(null);
    // Retry logic would go here
    setTimeout(() => setLoading(false), 1000);
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
        <Button variant="contained" onClick={retryLoad} startIcon={<Refresh />}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!data) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="warning">
          No Action Layer data available for Pergola Market
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
            <Analytics sx={{ fontSize: 32, color: '#1890ff', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              Action Layer Demo: Pergola Market
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Chip 
              label={`Session: ${sessionId}`}
              sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }}
            />
            <Chip 
              label="Action Layer Calculator"
              sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
            />
            <Chip 
              label="Pergola Market"
              sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }}
            />
          </Box>
          <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
            Interactive demonstration of Action Layer calculations and strategic assessments
          </Typography>
        </Box>

        {/* Action Layer Scores */}
        <Accordion 
          expanded={expandedPanel === 'scores'} 
          onChange={handlePanelChange('scores')}
          sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUp sx={{ color: '#52c41a', mr: 2 }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Action Layer Scores
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {Object.entries(data).map(([key, value]: [string, any]) => {
                // Skip non-score data for this section
                if (typeof value !== 'object' || Array.isArray(value)) return null;
                
                return (
                  <Grid item xs={12} md={6} key={key}>
                    <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                          {key.replace(/_/g, ' ').toUpperCase()}
                        </Typography>
                        {typeof value === 'object' && value !== null ? (
                          <Box>
                            {Object.entries(value).map(([subKey, subValue]: [string, any]) => (
                              <Box key={subKey} sx={{ mb: 2 }}>
                                <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 0.5 }}>
                                  {subKey.replace(/_/g, ' ').toUpperCase()}
                                </Typography>
                                <Typography variant="h6" sx={{ color: getScoreColor(typeof subValue === 'number' ? subValue : 0) }}>
                                  {typeof subValue === 'number' ? subValue.toFixed(2) : String(subValue)}
                                </Typography>
                              </Box>
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="h4" sx={{ color: getScoreColor(typeof value === 'number' ? value : 0) }}>
                            {typeof value === 'number' ? value.toFixed(2) : String(value)}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Detailed Calculations */}
        <Accordion 
          expanded={expandedPanel === 'calculations'} 
          onChange={handlePanelChange('calculations')}
          sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Assessment sx={{ color: '#1890ff', mr: 2 }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Detailed Calculations
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper} sx={{ backgroundColor: '#252547' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Metric</TableCell>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Value</TableCell>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Category</TableCell>
                    <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(data).map(([key, value]: [string, any]) => (
                    <TableRow key={key}>
                      <TableCell sx={{ color: '#e8e8f0' }}>
                        {key.replace(/_/g, ' ').toUpperCase()}
                      </TableCell>
                      <TableCell sx={{ color: '#1890ff' }}>
                        {typeof value === 'object' ? JSON.stringify(value).substring(0, 50) + '...' : String(value)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={typeof value === 'number' ? 'Numeric' : 'Object'}
                          sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label="Calculated"
                          sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>

        {/* Raw Data View */}
        <Accordion 
          expanded={expandedPanel === 'raw'} 
          onChange={handlePanelChange('raw')}
          sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Speed sx={{ color: '#fa8c16', mr: 2 }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Raw Action Layer Data
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
              <CardContent>
                <pre style={{ 
                  color: '#e8e8f0', 
                  fontSize: '0.85rem', 
                  overflow: 'auto', 
                  maxHeight: '400px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {JSON.stringify(data, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </AccordionDetails>
        </Accordion>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                  Data Points
                </Typography>
                <Typography variant="h3" sx={{ color: '#1890ff' }}>
                  {Object.keys(data).length}
                </Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  Action Layer metrics calculated
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                  Analysis Status
                </Typography>
                <Typography variant="h3" sx={{ color: '#52c41a' }}>
                  Complete
                </Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  All calculations processed
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                  Market Focus
                </Typography>
                <Typography variant="h3" sx={{ color: '#fa8c16' }}>
                  Pergola
                </Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  Outdoor living market analysis
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </motion.div>
    </Box>
  );
};

export default ActionLayerDemoPage;