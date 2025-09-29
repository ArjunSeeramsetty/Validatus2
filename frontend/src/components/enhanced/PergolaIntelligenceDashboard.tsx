import React, { useState, useEffect } from 'react';
import {
  Grid, Box, Typography, Card, CardContent, Chip, Button,
  CircularProgress, Alert, Tabs, Tab, TextField, InputAdornment
} from '@mui/material';
import {
  TrendingUp, Analytics, Search, FilterList, Assessment,
  Insights, Psychology, CompareArrows
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Import enhanced chart components
import MarketSizeChart from '../charts/MarketSizeChart';
import RegionalBreakdownTable from '../charts/RegionalBreakdownTable';
import CompetitorLandscape from '../charts/CompetitorLandscape';
import ConsumerJourneyFlow from '../charts/ConsumerJourneyFlow';
import TechnologyTrendsRadar from '../charts/TechnologyTrendsRadar';
import SemanticSearchInterface from '../search/SemanticSearchInterface';

interface PergolaIntelligenceData {
  market_insights: any;
  competitive_landscape: any;
  consumer_psychology: any;
  research_depth: any;
}

export default function PergolaIntelligenceDashboard() {
  const [data, setData] = useState<PergolaIntelligenceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadMarketIntelligence();
  }, []);

  const loadMarketIntelligence = async () => {
    try {
      setLoading(true);
      const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8001';
      const response = await fetch(`${baseUrl}/api/v3/pergola/market-intelligence`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setData(result.data);
      } else {
        throw new Error('Failed to load market intelligence');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>Loading Market Intelligence...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" onClick={loadMarketIntelligence}>Retry</Button>
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header Section */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Insights sx={{ fontSize: 36, color: '#1976d2', mr: 2 }} />
            <Typography variant="h4" sx={{ fontWeight: 600 }}>
              Pergola Market Intelligence Dashboard
            </Typography>
          </Box>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Comprehensive market intelligence powered by 58 research sources and vector analysis
          </Typography>

          {/* Research Depth Indicators */}
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Chip 
              icon={<Analytics />} 
              label={`${data?.research_depth?.total_sources || 58} Sources`}
              color="primary" 
              variant="outlined"
            />
            <Chip 
              icon={<Assessment />} 
              label={`${data?.research_depth?.vector_chunks || 150} Analysis Points`}
              color="secondary" 
              variant="outlined"
            />
            <Chip 
              icon={<TrendingUp />} 
              label={`${((data?.research_depth?.analysis_confidence || 0.92) * 100).toFixed(0)}% Confidence`}
              color="success" 
              variant="outlined"
            />
          </Box>
        </Box>

        {/* Navigation Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab icon={<TrendingUp />} label="Market Overview" />
            <Tab icon={<CompareArrows />} label="Competitive Intelligence" />
            <Tab icon={<Psychology />} label="Consumer Psychology" />
            <Tab icon={<Search />} label="Research Explorer" />
          </Tabs>
        </Box>

        {/* Tab Content */}
        {activeTab === 0 && (
          <motion.div
            key="market"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Grid container spacing={3}>
              {/* Market Size Chart */}
              <Grid item xs={12} lg={8}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Global Market Size & Growth</Typography>
                    <MarketSizeChart data={data?.market_insights?.market_size} />
                  </CardContent>
                </Card>
              </Grid>

              {/* Key Metrics */}
              <Grid item xs={12} lg={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Key Metrics</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="h4" color="primary" gutterBottom>
                        ${data?.market_insights?.market_size?.global_2024 || 3500}M
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        2024 Market Size
                      </Typography>
                      
                      <Typography variant="h5" color="success.main" sx={{ mt: 2 }}>
                        {data?.market_insights?.market_size?.cagr || 6.5}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        CAGR (2024-2033)
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Regional Breakdown */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Regional Market Analysis</Typography>
                    <RegionalBreakdownTable data={data?.market_insights?.regional_breakdown} />
                  </CardContent>
                </Card>
              </Grid>

              {/* Technology Trends */}
              <Grid item xs={12} lg={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Technology Adoption Trends</Typography>
                    <TechnologyTrendsRadar data={data?.market_insights?.technology_trends} />
                  </CardContent>
                </Card>
              </Grid>

              {/* Consumer Insights Preview */}
              <Grid item xs={12} lg={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Top Consumer Insights</Typography>
                    <Box sx={{ mt: 2 }}>
                      {(data?.market_insights?.consumer_insights || []).slice(0, 3).map((insight: string, index: number) => (
                        <Typography 
                          key={index} 
                          variant="body2" 
                          sx={{ mb: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}
                        >
                          {insight}...
                        </Typography>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </motion.div>
        )}

        {activeTab === 1 && (
          <motion.div
            key="competitive"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <CompetitorLandscape data={data?.competitive_landscape} />
          </motion.div>
        )}

        {activeTab === 2 && (
          <motion.div
            key="psychology"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <ConsumerJourneyFlow data={data?.consumer_psychology} />
          </motion.div>
        )}

        {activeTab === 3 && (
          <motion.div
            key="research"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <SemanticSearchInterface />
          </motion.div>
        )}
      </motion.div>
    </Box>
  );
}
