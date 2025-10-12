/**
 * Results Tab - Main container for comprehensive analysis results
 * Displays Market, Consumer, Product, Brand, and Experience analysis
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
  Button
} from '@mui/material';
import { 
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  Category as CategoryIcon,
  Loyalty as LoyaltyIcon,
  Stars as StarsIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

import { useAnalysis } from '../hooks/useAnalysis';
import MarketResults from './results/MarketResults';
import ConsumerResults from './results/ConsumerResults';
import ProductResults from './results/ProductResults';
import BrandResults from './results/BrandResults';
import ExperienceResults from './results/ExperienceResults';

interface ResultsTabProps {
  sessionId: string;
}

const ResultsTab: React.FC<ResultsTabProps> = ({ sessionId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const { analysisData, loading, error, fetchCompleteAnalysis, resetAnalysis } = useAnalysis();

  useEffect(() => {
    if (sessionId) {
      console.log('Fetching analysis for session:', sessionId);
      fetchCompleteAnalysis(sessionId).catch(err => {
        console.error('Failed to fetch analysis:', err);
      });
    }
    
    return () => {
      // Cleanup on unmount
      resetAnalysis();
    };
  }, [sessionId]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    if (sessionId) {
      fetchCompleteAnalysis(sessionId);
    }
  };

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
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
              Analysis Results: {analysisData.topic_name}
            </Typography>
            <Typography variant="caption" sx={{ color: '#888' }}>
              Generated: {new Date(analysisData.analysis_timestamp).toLocaleString()}
            </Typography>
          </Box>
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
        {activeTab === 0 && <MarketResults data={analysisData.market} />}
        {activeTab === 1 && <ConsumerResults data={analysisData.consumer} />}
        {activeTab === 2 && <ProductResults data={analysisData.product} />}
        {activeTab === 3 && <BrandResults data={analysisData.brand} />}
        {activeTab === 4 && <ExperienceResults data={analysisData.experience} />}
      </Box>
    </Box>
  );
};

export default ResultsTab;

