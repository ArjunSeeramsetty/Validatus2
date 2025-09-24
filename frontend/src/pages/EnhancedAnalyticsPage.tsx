// frontend/src/pages/EnhancedAnalyticsPage.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Stack,
  Button,
  Paper,
  Grid,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  DashboardOutlined,
  TrendingUpOutlined,
  BubbleChartOutlined,
  AnalyticsOutlined,
  RefreshOutlined
} from '@mui/icons-material';
import StrategicDarkLayout from '../components/enhanced_analytics/StrategicDashboard/DarkThemedLayout';
import FactorVisualization from '../components/enhanced_analytics/StrategicDashboard/FactorVisualization';
import MonteCarloSimulation from '../components/enhanced_analytics/InteractiveCharts/MonteCarloSimulation';
import AnalysisProgressStepper from '../components/enhanced_analytics/RealTimeUpdates/AnalysisProgressStepper';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `analytics-tab-${index}`,
    'aria-controls': `analytics-tabpanel-${index}`,
  };
}

interface EnhancedAnalyticsPageProps {
  sessionId?: string;
  topic?: string;
}

const EnhancedAnalyticsPage: React.FC<EnhancedAnalyticsPageProps> = ({
  sessionId = 'demo-session-001',
  topic = 'AI-Powered Strategic Analysis Platform'
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [factorResults, setFactorResults] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const { sendMessage } = useWebSocketConnection();

  // Mock factor results for demonstration
  const generateMockFactorResults = () => {
    const factors = [
      'F1_market_size', 'F2_market_growth', 'F3_market_maturity', 'F4_competitive_intensity',
      'F5_barrier_to_entry', 'F6_regulatory_environment', 'F7_economic_sensitivity',
      'F8_product_differentiation', 'F9_innovation_capability', 'F10_quality_reliability',
      'F11_scalability_potential', 'F12_customer_stickiness', 'F13_pricing_power',
      'F14_lifecycle_position', 'F15_revenue_growth', 'F16_profitability_margins',
      'F17_cash_flow_generation', 'F18_capital_efficiency', 'F19_financial_stability',
      'F20_cost_structure', 'F21_working_capital', 'F22_brand_strength',
      'F23_management_quality', 'F24_strategic_positioning', 'F25_operational_excellence',
      'F26_digital_transformation', 'F27_sustainability_esg', 'F28_strategic_flexibility'
    ];

    const results: Record<string, any> = {};
    
    factors.forEach((factor, index) => {
      const rawScore = Math.random() * 100;
      const normalizedScore = Math.min(Math.max(rawScore / 100, 0.1), 0.95);
      const confidence = Math.min(Math.max(0.6 + Math.random() * 0.3, 0.6), 0.95);
      
      results[factor] = {
        formula_name: factor,
        raw_score: rawScore,
        normalized_score: normalizedScore,
        confidence: confidence,
        calculation_steps: [
          { step: 'Data Collection', value: Math.random() * 100 },
          { step: 'Normalization', value: normalizedScore },
          { step: 'Weight Application', value: Math.random() * 0.2 + 0.1 },
          { step: 'Final Score', value: normalizedScore }
        ],
        metadata: {
          weight: Math.random() * 0.15 + 0.05,
          description: `Strategic factor ${index + 1} analysis`,
          calculation_timestamp: new Date().toISOString()
        }
      };
    });

    return results;
  };

  useEffect(() => {
    // Load initial factor results
    setFactorResults(generateMockFactorResults());
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    setIsLoading(true);
    setFactorResults(generateMockFactorResults());
    setLastRefresh(new Date());
    
    // Send refresh message to backend
    sendMessage(JSON.stringify({
      type: 'refresh_analysis',
      sessionId,
      timestamp: new Date().toISOString()
    }));

    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  };

  const handleFactorSelect = (factorId: string) => {
    console.log('Selected factor:', factorId);
    // Navigate to detailed factor analysis or show modal
  };

  const handleMenuSelect = (key: string) => {
    console.log('Menu selected:', key);
    // Handle navigation based on menu selection
    switch (key) {
      case 'dashboard':
        setActiveTab(0);
        break;
      case 'factor-analysis':
        setActiveTab(1);
        break;
      case 'monte-carlo':
        setActiveTab(2);
        break;
      case 'pattern-recognition':
        setActiveTab(3);
        break;
      default:
        break;
    }
  };

  return (
    <StrategicDarkLayout
      activeKey="analytics"
      onMenuSelect={handleMenuSelect}
      showNotifications={true}
    >
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Box>
              <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 'bold', mb: 1 }}>
                Enhanced Analytics Dashboard
              </Typography>
              <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
                Advanced strategic analysis with real-time insights and comprehensive factor evaluation
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={<RefreshOutlined />}
              onClick={handleRefresh}
              disabled={isLoading}
              sx={{ 
                borderColor: '#1890ff', 
                color: '#1890ff',
                '&:hover': {
                  borderColor: '#1890ff',
                  backgroundColor: '#1890ff20'
                }
              }}
            >
              Refresh Analysis
            </Button>
          </Stack>

          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#1a1a35', 
            border: '1px solid #3d3d56' 
          }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={3}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Session:</Typography>
                  <Chip 
                    label={sessionId.substring(0, 12)} 
                    size="small"
                    sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }}
                  />
                </Stack>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Topic:</Typography>
                  <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                    {topic.substring(0, 30)}...
                  </Typography>
                </Stack>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Last Updated:</Typography>
                  <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                    {lastRefresh.toLocaleTimeString()}
                  </Typography>
                </Stack>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Status:</Typography>
                  <Chip 
                    label="Live" 
                    color="success" 
                    size="small"
                    sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
                  />
                </Stack>
              </Grid>
            </Grid>
          </Paper>
        </Box>

        {/* Navigation Tabs */}
        <Paper sx={{ 
          backgroundColor: '#1a1a35', 
          border: '1px solid #3d3d56',
          mb: 3
        }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                color: '#b8b8cc',
                '&.Mui-selected': {
                  color: '#1890ff',
                },
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#1890ff',
              },
            }}
          >
            <Tab 
              icon={<DashboardOutlined />} 
              label="Overview" 
              {...a11yProps(0)} 
            />
            <Tab 
              icon={<TrendingUpOutlined />} 
              label="F1-F28 Factors" 
              {...a11yProps(1)} 
            />
            <Tab 
              icon={<BubbleChartOutlined />} 
              label="Monte Carlo" 
              {...a11yProps(2)} 
            />
            <Tab 
              icon={<AnalyticsOutlined />} 
              label="Progress" 
              {...a11yProps(3)} 
            />
          </Tabs>
        </Paper>

        {/* Tab Content */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <Paper sx={{ 
                p: 3, 
                backgroundColor: '#1a1a35', 
                border: '1px solid #3d3d56',
                height: 400
              }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                  Strategic Analysis Overview
                </Typography>
                <Alert severity="info" sx={{ 
                  backgroundColor: '#252547', 
                  border: '1px solid #3d3d56',
                  color: '#e8e8f0'
                }}>
                  Select a specific analysis tab to view detailed insights and visualizations.
                  All analysis components are integrated with real-time WebSocket updates.
                </Alert>
              </Paper>
            </Grid>
            <Grid item xs={12} lg={4}>
              <Paper sx={{ 
                p: 3, 
                backgroundColor: '#1a1a35', 
                border: '1px solid #3d3d56',
                height: 400
              }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                  Quick Stats
                </Typography>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Total Factors</Typography>
                    <Typography variant="h5" sx={{ color: '#1890ff' }}>28</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Analysis Layers</Typography>
                    <Typography variant="h5" sx={{ color: '#52c41a' }}>10</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: '#b8b8cc' }}>Simulation Iterations</Typography>
                    <Typography variant="h5" sx={{ color: '#fa8c16' }}>10,000</Typography>
                  </Box>
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <FactorVisualization
            factorResults={factorResults}
            sessionId={sessionId}
            isLoading={isLoading}
            showDetailedView={true}
            onFactorSelect={handleFactorSelect}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <MonteCarloSimulation
            sessionId={sessionId}
            factorResults={factorResults}
            initialValue={100}
            autoStart={false}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <AnalysisProgressStepper
            sessionId={sessionId}
            showDetailedView={true}
            autoRefresh={true}
          />
        </TabPanel>

        {/* Loading Overlay */}
        {isLoading && (
          <Box
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(15, 15, 35, 0.8)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 9999,
            }}
          >
            <Stack spacing={2} alignItems="center">
              <CircularProgress size={60} sx={{ color: '#1890ff' }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Refreshing Analysis...
              </Typography>
            </Stack>
          </Box>
        )}
      </Container>
    </StrategicDarkLayout>
  );
};

export default EnhancedAnalyticsPage;
