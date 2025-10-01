/**
 * Advanced Strategy Analysis Dashboard
 * Implements the complete Figma design with Monte Carlo results
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Tab,
  Tabs,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  Download,
  Insights
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';

// Custom components
import BusinessCaseScoreCard from '../components/Analysis/BusinessCaseScoreCard';
import ScenarioGrid from '../components/Analysis/ScenarioGrid';
import DriverSensitivityChart from '../components/Analysis/DriverSensitivityChart';
import SimulationDistribution from '../components/Analysis/SimulationDistribution';
import AssumptionsPanel from '../components/Analysis/AssumptionsPanel';
import EvidenceExplorer from '../components/Analysis/EvidenceExplorer';
import { apiClient } from '../services/apiClient';

interface AdvancedAnalysisResults {
  business_case_score: {
    score: number;
    confidence_band: [number, number];
    components: Record<string, number>;
  };
  scenarios: Array<{
    name: string;
    probability: number;
    kpis: Record<string, number>;
    narrative: string;
    key_drivers: string[];
    risk_level: string;
  }>;
  driver_sensitivities: Record<string, number>;
  simulation_metadata: {
    runs: number;
    confidence_level: number;
  };
  financial_projections?: Record<string, any>;
  assumptions?: Record<string, any>;
}

interface AdvancedAnalysisDashboardProps {
  sessionId?: string;
}

const AdvancedAnalysisDashboard: React.FC<AdvancedAnalysisDashboardProps> = ({ sessionId: propSessionId }) => {
  const { sessionId: paramSessionId } = useParams<{ sessionId: string }>();
  // Use prop sessionId if provided (for HomePage), otherwise use URL param
  const sessionId = propSessionId || paramSessionId || 'v2_analysis_20250905_185553_d5654178';
  
  const [results, setResults] = useState<AdvancedAnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [sensitivityValues, setSensitivityValues] = useState<Record<string, number>>({});

  useEffect(() => {
    if (sessionId) {
      loadAdvancedResults();
    }
  }, [sessionId]);

  const loadAdvancedResults = async () => {
    if (!sessionId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(`/api/v3/analysis/${sessionId}/scenarios`);
      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load analysis results');
    } finally {
      setLoading(false);
    }
  };

  const handleSensitivityChange = async (driver: string, value: number) => {
    if (!sessionId) return;
    
    setSensitivityValues(prev => ({ ...prev, [driver]: value }));
    
    // Debounced API call for real-time sensitivity analysis
    const adjustments = { ...sensitivityValues, [driver]: value };
    
    try {
      const response = await apiClient.post(`/api/v3/analysis/${sessionId}/sensitivity`, {
        scenario_adjustments: adjustments
      });
      
      // Update results with sensitivity analysis
      if (response.data.adjusted_results) {
        setResults(prev => ({
          ...prev!,
          ...response.data.adjusted_results
        }));
      }
    } catch (error) {
      console.error('Sensitivity analysis failed:', error);
    }
  };

  const handleExport = async (format: string = 'json') => {
    if (!sessionId) return;
    
    try {
      const response = await apiClient.get(`/api/v3/analysis/${sessionId}/export?format=${format}`);
      
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(response.data.data, null, 2)], {
          type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis_results_${sessionId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '50vh',
        flexDirection: 'column',
        gap: 2
      }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
          Loading Advanced Analysis...
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
        <Button variant="contained" onClick={loadAdvancedResults}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!results) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="warning">
          No analysis results found for session {sessionId}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, backgroundColor: '#0f0f1a', minHeight: '100vh' }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h3" sx={{ color: '#e8e8f0', fontWeight: 700, mb: 1 }}>
              Strategic Analysis Results
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={`${results.simulation_metadata.runs.toLocaleString()} Monte Carlo Runs`}
                sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }}
              />
              <Chip 
                label={`${(results.simulation_metadata.confidence_level * 100)}% Confidence`}
                sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
              />
              <Chip 
                label={`Session: ${sessionId}`}
                sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }}
              />
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={() => handleExport('json')}
              sx={{ borderColor: '#3d3d56', color: '#e8e8f0' }}
            >
              Export Report
            </Button>
            <Button
              variant="contained"
              startIcon={<Insights />}
              sx={{ backgroundColor: '#1890ff' }}
            >
              Deep Dive
            </Button>
          </Box>
        </Box>
      </motion.div>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Business Case Score - Top Left */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <BusinessCaseScoreCard 
              score={results.business_case_score}
              height={280}
            />
          </motion.div>
        </Grid>

        {/* Driver Sensitivity - Top Center */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', height: 280 }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                  Driver Sensitivity Analysis
                </Typography>
                <DriverSensitivityChart 
                  sensitivities={results.driver_sensitivities}
                  onDriverChange={handleSensitivityChange}
                />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Scenario Grid - Middle */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <ScenarioGrid 
              scenarios={results.scenarios}
              onScenarioSelect={(scenario) => console.log('Selected:', scenario)}
            />
          </motion.div>
        </Grid>

        {/* Simulation Distribution - Bottom Left */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
              <CardContent>
                <Tabs 
                  value={selectedTab} 
                  onChange={(_, newValue) => setSelectedTab(newValue)}
                  sx={{ mb: 2 }}
                >
                  <Tab label="ROI Distribution" sx={{ color: '#b8b8cc' }} />
                  <Tab label="Adoption Curves" sx={{ color: '#b8b8cc' }} />
                  <Tab label="Financial Metrics" sx={{ color: '#b8b8cc' }} />
                </Tabs>
                
                <SimulationDistribution 
                  data={results}
                  selectedMetric={['roi', 'adoption', 'financial'][selectedTab]}
                />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Assumptions & Evidence - Bottom Right */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <AssumptionsPanel sessionId={sessionId!} />
              <EvidenceExplorer sessionId={sessionId!} />
            </Box>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvancedAnalysisDashboard;
