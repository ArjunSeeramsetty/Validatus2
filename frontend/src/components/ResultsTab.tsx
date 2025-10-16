/**
 * Results Tab - Main container for comprehensive analysis results
 * Displays Market, Consumer, Product, Brand, and Experience analysis
 * Now includes topic selector for viewing different topic results
 */

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Tabs, 
  Tab, 
  CircularProgress, 
  Alert, 
  Typography,
  Paper,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  SelectChangeEvent
} from '@mui/material';
import { 
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  Category as CategoryIcon,
  Loyalty as LoyaltyIcon,
  Stars as StarsIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  List as ListIcon
} from '@mui/icons-material';

import { useAnalysis } from '../hooks/useAnalysis';
import { apiClient } from '../services/apiClient';
import MarketResults from './Results/MarketResults';
import ConsumerResults from './Results/ConsumerResults';
import ProductResults from './Results/ProductResults';
import BrandResults from './Results/BrandResults';
import ExperienceResults from './Results/ExperienceResults';

interface ResultsTabProps {
  sessionId?: string;
}

const ResultsTab: React.FC<ResultsTabProps> = ({ sessionId: initialSessionId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [topics, setTopics] = useState<any[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string>(initialSessionId || '');
  const [loadingTopics, setLoadingTopics] = useState(false);
  const [topicsError, setTopicsError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'details'>('list');
  
  const { analysisData, loading, error, fetchCompleteAnalysis, resetAnalysis } = useAnalysis();

  // Load available topics on mount with slight delay to avoid concurrent DB operations
  useEffect(() => {
    const timer = setTimeout(() => {
      loadTopics();
    }, 300); // 300ms delay to let other initial loads complete
    
    return () => clearTimeout(timer);
  }, []);

  // Load analysis when a topic is selected
  useEffect(() => {
    if (selectedSessionId) {
      console.log('Fetching analysis for session:', selectedSessionId);
      setViewMode('details');
      
      // Add delay before fetching to avoid concurrent DB operations
      const timer = setTimeout(() => {
        fetchCompleteAnalysis(selectedSessionId).catch(err => {
          console.error('Failed to fetch analysis:', err);
        });
      }, 200);
      
      return () => clearTimeout(timer);
    }
    
    return () => {
      // Cleanup on unmount
      if (!selectedSessionId) {
        resetAnalysis();
      }
    };
  }, [selectedSessionId]);

  const loadTopics = async (retryCount = 0) => {
    setLoadingTopics(true);
    setTopicsError(null);

    try {
      const response = await apiClient.get('/api/v3/scoring/topics');
      if (response.data.success) {
        setTopics(response.data.topics);
        
        // Auto-select first topic if none selected
        if (!selectedSessionId && response.data.topics.length > 0) {
          setSelectedSessionId(response.data.topics[0].session_id);
        }
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load topics';
      
      // Check for transient database error and retry
      if (errorMessage.includes('another operation is in progress') && retryCount < 3) {
        console.log(`Database busy, retrying in ${(retryCount + 1) * 500}ms... (attempt ${retryCount + 1}/3)`);
        setTimeout(() => {
          loadTopics(retryCount + 1);
        }, (retryCount + 1) * 500); // Exponential backoff: 500ms, 1000ms, 1500ms
        return;
      }
      
      setTopicsError(errorMessage);
    } finally {
      if (retryCount === 0 || !topicsError) {
        setLoadingTopics(false);
      }
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    if (selectedSessionId) {
      fetchCompleteAnalysis(selectedSessionId);
    }
  };

  const handleTopicSelect = (sessionId: string) => {
    setSelectedSessionId(sessionId);
    setActiveTab(0); // Reset to first tab when changing topics
  };

  const handleTopicChange = (event: SelectChangeEvent<string>) => {
    handleTopicSelect(event.target.value);
  };

  const handleBackToList = () => {
    setViewMode('list');
    resetAnalysis();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#52c41a';
      case 'in_progress': return '#fa8c16';
      case 'created': return '#1890ff';
      default: return '#888';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon fontSize="small" />;
      case 'in_progress': return <ScheduleIcon fontSize="small" />;
      default: return <ScheduleIcon fontSize="small" />;
    }
  };

  // Show topics list view
  if (viewMode === 'list' || !selectedSessionId) {
    return (
      <Box sx={{ width: '100%', bgcolor: '#0a0a14', minHeight: '600px', p: 3 }}>
        <Paper sx={{ bgcolor: '#16162a', p: 3, borderRadius: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Box display="flex" alignItems="center" gap={2}>
              <ListIcon sx={{ color: '#52c41a', fontSize: 32 }} />
              <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                Select a Topic to View Results
              </Typography>
            </Box>
            <Button
              variant="outlined"
              size="small"
              onClick={loadTopics}
              startIcon={<RefreshIcon />}
              disabled={loadingTopics}
              sx={{
                color: '#52c41a',
                borderColor: '#52c41a',
                '&:hover': { bgcolor: 'rgba(82, 196, 26, 0.1)', borderColor: '#449413' }
              }}
            >
              Refresh
            </Button>
          </Box>

          {loadingTopics && (
            <Box display="flex" justifyContent="center" alignItems="center" py={8}>
              <CircularProgress sx={{ color: '#52c41a' }} />
            </Box>
          )}

          {topicsError && (
            <Alert severity="error" sx={{ bgcolor: '#2d1b1b', color: '#ff4d4f', border: '1px solid #ff4d4f', mb: 3 }}>
              {topicsError}
            </Alert>
          )}

          {!loadingTopics && !topicsError && topics.length === 0 && (
            <Alert severity="info" sx={{ bgcolor: '#1a1a2e', color: '#1890ff', border: '1px solid #1890ff' }}>
              No topics found. Create a topic and run analysis to see results here.
            </Alert>
          )}

          {!loadingTopics && topics.length > 0 && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#888', fontWeight: 'bold', borderBottom: '1px solid #2d2d44' }}>
                      Topic
                    </TableCell>
                    <TableCell sx={{ color: '#888', fontWeight: 'bold', borderBottom: '1px solid #2d2d44' }}>
                      Description
                    </TableCell>
                    <TableCell sx={{ color: '#888', fontWeight: 'bold', borderBottom: '1px solid #2d2d44' }}>
                      Status
                    </TableCell>
                    <TableCell sx={{ color: '#888', fontWeight: 'bold', borderBottom: '1px solid #2d2d44' }}>
                      Last Scored
                    </TableCell>
                    <TableCell sx={{ color: '#888', fontWeight: 'bold', borderBottom: '1px solid #2d2d44' }}>
                      Action
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topics.map((topic) => (
                    <TableRow
                      key={topic.session_id}
                      sx={{
                        '&:hover': { bgcolor: 'rgba(82, 196, 26, 0.05)' },
                        cursor: 'pointer'
                      }}
                      onClick={() => handleTopicSelect(topic.session_id)}
                    >
                      <TableCell sx={{ color: '#e8e8f0', borderBottom: '1px solid #2d2d44' }}>
                        {topic.topic}
                      </TableCell>
                      <TableCell sx={{ color: '#888', borderBottom: '1px solid #2d2d44', maxWidth: 300 }}>
                        {topic.description || 'No description'}
                      </TableCell>
                      <TableCell sx={{ borderBottom: '1px solid #2d2d44' }}>
                        <Chip
                          icon={getStatusIcon(topic.status)}
                          label={topic.status}
                          size="small"
                          sx={{
                            bgcolor: 'transparent',
                            color: getStatusColor(topic.status),
                            border: `1px solid ${getStatusColor(topic.status)}`,
                            textTransform: 'capitalize'
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: '#888', borderBottom: '1px solid #2d2d44' }}>
                        {topic.scored_at ? new Date(topic.scored_at).toLocaleDateString() : 'Not scored'}
                      </TableCell>
                      <TableCell sx={{ borderBottom: '1px solid #2d2d44' }}>
                        <Button
                          variant="contained"
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleTopicSelect(topic.session_id);
                          }}
                          sx={{
                            bgcolor: '#52c41a',
                            '&:hover': { bgcolor: '#449413' }
                          }}
                        >
                          View Results
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box 
        display="flex" 
        flexDirection="column"
        justifyContent="center" 
        alignItems="center" 
        minHeight="400px"
        sx={{ bgcolor: '#0a0a14', p: 4 }}
      >
        <CircularProgress size={60} sx={{ color: '#52c41a', mb: 3 }} />
        <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
          Generating Comprehensive Analysis...
        </Typography>
        <Typography variant="body2" sx={{ color: '#888', mt: 1 }}>
          Analyzing market, consumer, product, brand, and experience dimensions
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error" 
          sx={{ bgcolor: '#2d1b1b', color: '#ff4d4f', border: '1px solid #ff4d4f' }}
          action={
            <Button color="inherit" size="small" onClick={handleRefresh} startIcon={<RefreshIcon />}>
              Retry
            </Button>
          }
        >
          Failed to load analysis results: {error}
        </Alert>
        <Typography variant="body2" sx={{ color: '#888', mt: 2 }}>
          Make sure you have scraped content available for this topic.
        </Typography>
      </Box>
    );
  }

  if (!analysisData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info" sx={{ bgcolor: '#1a1a2e', color: '#1890ff', border: '1px solid #1890ff' }}>
          No analysis data available yet. Click Refresh to generate analysis.
        </Alert>
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button 
            variant="contained" 
            onClick={handleRefresh}
            startIcon={<RefreshIcon />}
            sx={{ bgcolor: '#52c41a', '&:hover': { bgcolor: '#449413' } }}
          >
            Generate Analysis
          </Button>
        </Box>
      </Box>
    );
  }

  // Check if analysis has actual data or is just empty defaults
  const hasRealData = analysisData && (
    (analysisData.market?.opportunities?.length > 0) ||
    (analysisData.consumer?.challenges?.length > 0) ||
    (analysisData.product?.product_features?.length > 0) ||
    (analysisData.brand?.brand_opportunities?.length > 0) ||
    (analysisData.experience?.pain_points?.length > 0)
  );

  if (!hasRealData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="warning" 
          sx={{ bgcolor: '#2d2416', color: '#fa8c16', border: '1px solid #fa8c16', mb: 3 }}
        >
          <Typography variant="h6" sx={{ mb: 1 }}>
            📊 No Analysis Results Available
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            This topic hasn't been scored yet. The Results tab displays detailed analysis from scored topics.
          </Typography>
          <Typography variant="body2" component="div">
            <strong>To view results:</strong>
            <ol style={{ marginTop: '8px', marginBottom: 0 }}>
              <li>Go to the <strong>Scoring</strong> tab</li>
              <li>Find this topic in the list</li>
              <li>Click <strong>"Start Scoring"</strong> to run v2.0 Strategic Analysis</li>
              <li>Wait for scoring to complete (15-20 minutes for comprehensive analysis)</li>
              <li>Return to this tab to view the detailed results</li>
            </ol>
          </Typography>
          <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic' }}>
            💡 <strong>Note:</strong> Results are generated from the Scoring analysis, not from raw content. 
            Make sure the topic has been scored before viewing results here.
          </Typography>
        </Alert>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button 
            variant="outlined"
            onClick={handleBackToList}
            startIcon={<ListIcon />}
            sx={{ 
              color: '#888', 
              borderColor: '#2d2d44',
              '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)', borderColor: '#52c41a', color: '#52c41a' }
            }}
          >
            Back to Topics
          </Button>
          <Button 
            variant="contained" 
            onClick={handleRefresh}
            startIcon={<RefreshIcon />}
            sx={{ bgcolor: '#52c41a', '&:hover': { bgcolor: '#449413' } }}
          >
            Try Refresh
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', bgcolor: '#0a0a14', minHeight: '600px' }}>
      {/* Header */}
      <Paper 
        sx={{ 
          bgcolor: '#16162a', 
          borderBottom: '1px solid #2d2d44', 
          p: 2,
          mb: 2
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Button
              variant="outlined"
              size="small"
              onClick={handleBackToList}
              startIcon={<ListIcon />}
              sx={{
                color: '#888',
                borderColor: '#2d2d44',
                '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)', borderColor: '#52c41a', color: '#52c41a' }
              }}
            >
              Back to List
            </Button>
            <Box>
              <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                Analysis Results: {analysisData.topic_name}
              </Typography>
              <Typography variant="caption" sx={{ color: '#888' }}>
                Generated: {new Date(analysisData.analysis_timestamp).toLocaleString()}
              </Typography>
            </Box>
          </Box>
          <Box display="flex" gap={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel sx={{ color: '#888' }}>Switch Topic</InputLabel>
              <Select
                value={selectedSessionId}
                onChange={handleTopicChange}
                label="Switch Topic"
                sx={{
                  color: '#e8e8f0',
                  '.MuiOutlinedInput-notchedOutline': { borderColor: '#2d2d44' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#52c41a' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#52c41a' },
                  '.MuiSvgIcon-root': { color: '#888' }
                }}
              >
                {topics.map((topic) => (
                  <MenuItem key={topic.session_id} value={topic.session_id}>
                    {topic.topic}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button 
              variant="outlined" 
              size="small"
              onClick={handleRefresh}
              startIcon={<RefreshIcon />}
              sx={{ 
                color: '#52c41a', 
                borderColor: '#52c41a',
                '&:hover': { bgcolor: 'rgba(82, 196, 26, 0.1)', borderColor: '#449413' }
              }}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {/* Confidence Scores */}
        {analysisData.confidence_scores && Object.keys(analysisData.confidence_scores).length > 0 && (
          <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {Object.entries(analysisData.confidence_scores).map(([dimension, score]) => (
              <Paper
                key={dimension}
                sx={{
                  bgcolor: '#1a1a2e',
                  p: 1.5,
                  minWidth: 120,
                  textAlign: 'center'
                }}
              >
                <Typography variant="caption" sx={{ color: '#888', textTransform: 'capitalize' }}>
                  {dimension}
                </Typography>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    color: score > 0.7 ? '#52c41a' : score > 0.5 ? '#fa8c16' : '#ff4d4f',
                    fontWeight: 'bold'
                  }}
                >
                  {(score * 100).toFixed(0)}%
                </Typography>
              </Paper>
            ))}
          </Box>
        )}
      </Paper>

      {/* Tabs */}
      <Paper sx={{ bgcolor: '#16162a', borderBottom: '1px solid #2d2d44' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              color: '#888',
              textTransform: 'none',
              fontSize: '1rem',
              minHeight: 64,
              '&:hover': {
                color: '#52c41a',
                bgcolor: 'rgba(82, 196, 26, 0.05)'
              },
              '&.Mui-selected': {
                color: '#52c41a',
                fontWeight: 'bold'
              }
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#52c41a',
              height: 3
            }
          }}
        >
          <Tab 
            label="Market" 
            icon={<AssessmentIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Consumer" 
            icon={<PeopleIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Product" 
            icon={<CategoryIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Brand" 
            icon={<LoyaltyIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Experience" 
            icon={<StarsIcon />} 
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      <Box sx={{ p: 3, bgcolor: '#0a0a14' }}>
        {activeTab === 0 && <MarketResults data={analysisData.market} sessionId={selectedSessionId} />}
        {activeTab === 1 && <ConsumerResults data={analysisData.consumer} sessionId={selectedSessionId} />}
        {activeTab === 2 && <ProductResults data={analysisData.product} sessionId={selectedSessionId} />}
        {activeTab === 3 && <BrandResults data={analysisData.brand} sessionId={selectedSessionId} />}
        {activeTab === 4 && <ExperienceResults data={analysisData.experience} sessionId={selectedSessionId} />}
      </Box>
    </Box>
  );
};

export default ResultsTab;

