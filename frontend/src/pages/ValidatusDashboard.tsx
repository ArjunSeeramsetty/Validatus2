// frontend/src/pages/ValidatusDashboard.tsx

import React, { useState, useEffect, lazy, Suspense } from 'react';
import {
  Box,
  Typography,
  Card,
  Stack,
  Chip,
  useTheme,
  useMediaQuery,
  Tabs,
  Tab,
  CircularProgress
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  People,
  Store,
  Loyalty,
  Star
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Lazy load components for better performance
const BusinessCaseTab = lazy(() => import('../components/Dashboard/BusinessCaseTab'));
const EnhancedConsumerTab = lazy(() => import('../components/Dashboard/EnhancedConsumerTab'));
const MarketTab = lazy(() => import('../components/Dashboard/MarketTab'));
const ProductTab = lazy(() => import('../components/Dashboard/ProductTab'));
const BrandTab = lazy(() => import('../components/Dashboard/BrandTab'));
const ExperienceTab = lazy(() => import('../components/Dashboard/ExperienceTab'));

interface FeatureData {
  id: string;
  label: string;
  icon: React.ReactElement;
  color: string;
  description: string;
  component: React.ComponentType<{ data: any }>;
}

const features: FeatureData[] = [
  {
    id: 'business-case',
    label: 'Business Case',
    icon: <Assessment />,
    color: '#1890ff',
    description: 'Financial projections, ROI analysis, and business metrics',
    component: BusinessCaseTab
  },
  {
    id: 'consumer',
    label: 'Consumer',
    icon: <People />,
    color: '#52c41a',
    description: 'Consumer behavior, preferences, and market insights',
    component: EnhancedConsumerTab
  },
  {
    id: 'market',
    label: 'Market',
    icon: <TrendingUp />,
    color: '#fa8c16',
    description: 'Market trends, competition, and growth opportunities',
    component: MarketTab
  },
  {
    id: 'product',
    label: 'Product',
    icon: <Store />,
    color: '#722ed1',
    description: 'Product features, innovation, and development roadmap',
    component: ProductTab
  },
  {
    id: 'brand',
    label: 'Brand',
    icon: <Loyalty />,
    color: '#eb2f96',
    description: 'Brand positioning, messaging, and market perception',
    component: BrandTab
  },
  {
    id: 'experience',
    label: 'Experience',
    icon: <Star />,
    color: '#13c2c2',
    description: 'User experience, customer journey, and satisfaction',
    component: ExperienceTab
  }
];

const ValidatusDashboard: React.FC = () => {
  const [currentFeature, setCurrentFeature] = useState('business-case');
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    const baseUrl = (import.meta as any).env?.VITE_API_URL || 'https://validatus-backend-ssivkqhvhq-uc.a.run.app';
    
    // Parallel API calls for better performance - try all endpoints simultaneously
    const apiPromises = [
      fetch(`${baseUrl}/api/v3/pergola/dashboard-data`).catch(() => null),
      fetch(`${baseUrl}/api/v3/dashboard/v2_analysis_20250905_185553_d5654178/overview`).catch(() => null),
      fetch(`${baseUrl}/api/v3/migrated/results/v2_analysis_20250905_185553_d5654178`).catch(() => null)
    ];
    
    try {
      const [enhancedResponse, dashboardResponse, migratedResponse] = await Promise.allSettled(apiPromises);
      
      // Process responses in order of preference
      if (enhancedResponse.status === 'fulfilled' && enhancedResponse.value?.ok) {
        try {
          const enhancedData = await enhancedResponse.value.json();
          if (enhancedData.status === 'success') {
            setDashboardData(enhancedData.data);
            return;
          }
        } catch (e) {
          console.warn('Enhanced API response parsing failed');
        }
      }
      
      if (dashboardResponse.status === 'fulfilled' && dashboardResponse.value?.ok) {
        try {
          const dashboardData = await dashboardResponse.value.json();
          if (dashboardData.success) {
            setDashboardData(dashboardData.data);
            return;
          }
        } catch (e) {
          console.warn('Dashboard API response parsing failed');
        }
      }
      
      if (migratedResponse.status === 'fulfilled' && migratedResponse.value?.ok) {
        try {
          const migratedData = await migratedResponse.value.json();
          setDashboardData(migratedData);
          return;
        } catch (e) {
          console.warn('Migrated API response parsing failed');
        }
      }
      
      // If all APIs fail, set empty data
      setDashboardData({});
      console.warn('All API endpoints failed, using empty data');
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setDashboardData({});
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          height: 'calc(100vh - 64px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#0f0f1a'
        }}
      >
        <Typography color="textSecondary">Loading...</Typography>
      </Box>
    );
  }

  // Always show vertical navigation for analysis modules
  const showVerticalNav = !isMobile;

  const CurrentComponent = features.find(f => f.id === currentFeature)?.component!;

  return (
    <Box
      sx={{
        display: 'flex',
        width: '100%',
        minHeight: 'calc(100vh - 64px)',
        backgroundColor: '#0f0f1a'
      }}
    >
      {/* Vertical Navigation - Always visible on desktop */}
      {showVerticalNav && (
        <Stack 
          spacing={1} 
          sx={{ 
            width: 280, 
            p: 2, 
            backgroundColor: '#252547', 
            minHeight: 'calc(100vh - 64px)',
            borderRight: '1px solid #3d3d56',
            position: 'relative',
            flexShrink: 0
          }}
        >
          <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 700, mb: 1 }}>Dashboard</Typography>
          <Typography variant="caption" sx={{ color: '#b8b8cc' }} gutterBottom>
            Analysis Modules
          </Typography>
          {features.map((f, index) => (
            <motion.div
              key={f.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card
                onClick={() => setCurrentFeature(f.id)}
                sx={{
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  p: 2,
                  bgcolor: currentFeature === f.id ? `${f.color}20` : 'transparent',
                  borderLeft: currentFeature === f.id ? `4px solid ${f.color}` : '4px solid transparent',
                  border: '1px solid transparent',
                  borderRadius: 2,
                  mb: 1,
                  transition: 'all 0.2s ease',
                  '&:hover': { 
                    bgcolor: currentFeature === f.id ? `${f.color}25` : `${f.color}10`,
                    borderColor: f.color
                  }
                }}
              >
                <Box sx={{ color: currentFeature === f.id ? f.color : '#b8b8cc', mr: 2, transition: 'color 0.2s ease' }}>
                  {f.icon}
                </Box>
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ 
                      color: currentFeature === f.id ? f.color : '#e8e8f0',
                      fontWeight: currentFeature === f.id ? 600 : 400,
                      transition: 'color 0.2s ease'
                    }}
                  >
                    {f.label}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc', fontSize: '0.75rem' }}>
                    {f.description}
                  </Typography>
                </Box>
              </Card>
            </motion.div>
          ))}
          
          {/* Footer Stats */}
          <Box sx={{ 
            position: 'absolute', 
            bottom: 0, 
            left: 0, 
            right: 0, 
            p: 2,
            borderTop: '1px solid #3d3d56',
            backgroundColor: '#1a1a35'
          }}>
            <Typography variant="caption" sx={{ color: '#b8b8cc', display: 'block', mb: 1 }}>
              Analysis Status
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                Modules: {features.length}
              </Typography>
              <Box sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: '#52c41a',
                animation: 'pulse 2s infinite'
              }} />
            </Box>
          </Box>
        </Stack>
      )}

      {/* Content Area - Always uses vertical navigation on desktop */}
      {showVerticalNav ? (
        /* Side-by-side layout with vertical navigation */
        <Box
          sx={{
            flex: 1,
            p: 3,
            backgroundColor: '#1a1a35',
            overflowY: 'auto',
            overflowX: 'hidden',
            width: '100%',
            minHeight: 'calc(100vh - 64px)'
          }}
        >
          {/* Content Header */}
          <Box sx={{ 
            mb: 3,
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}>
            <Box sx={{
              p: 1.5,
              backgroundColor: `${features.find(f => f.id === currentFeature)?.color}30`,
              borderRadius: 2
            }}>
              {features.find(f => f.id === currentFeature)?.icon}
            </Box>
            <Box>
              <Typography 
                variant="h4" 
                sx={{ 
                  color: '#e8e8f0', 
                  fontWeight: 700,
                  mb: 0.5
                }}
              >
                {features.find(f => f.id === currentFeature)?.label}
              </Typography>
              <Typography 
                variant="subtitle1" 
                sx={{ color: '#b8b8cc' }}
              >
                {features.find(f => f.id === currentFeature)?.description}
              </Typography>
            </Box>
            <Chip
              label="Live Data"
              size="small"
              sx={{
                backgroundColor: '#52c41a20',
                color: '#52c41a',
                fontWeight: 500,
                ml: 'auto'
              }}
            />
          </Box>

          <AnimatePresence mode="wait">
            <motion.div
              key={currentFeature}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4 }}
            >
              <Box sx={{ width: '100%' }}>
                <Suspense fallback={
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                    <CircularProgress sx={{ color: '#1890ff' }} />
                  </Box>
                }>
                  <CurrentComponent data={dashboardData} />
                </Suspense>
              </Box>
            </motion.div>
          </AnimatePresence>
        </Box>
      ) : (
        /* Mobile layout with horizontal tabs */
        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* Horizontal Tabs for mobile */}
          <Tabs
            value={currentFeature}
            onChange={(_, v) => setCurrentFeature(v)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ 
              px: 2,
              backgroundColor: '#252547',
              '& .MuiTab-root': {
                color: '#b8b8cc',
                minHeight: 48,
                '&.Mui-selected': {
                  color: '#e8e8f0'
                }
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#1890ff'
              }
            }}
          >
            {features.map(f => (
              <Tab
                key={f.id}
                value={f.id}
                label={f.label}
                icon={f.icon}
                iconPosition="start"
                sx={{
                  pl: 2,
                  pr: 2,
                  color: currentFeature === f.id ? f.color : '#b8b8cc',
                  '&.Mui-selected': {
                    color: f.color
                  }
                }}
              />
            ))}
          </Tabs>

          {/* Content below tabs for mobile */}
          <Box
            sx={{
              flex: 1,
              p: 3,
              backgroundColor: '#1a1a35',
              overflowY: 'auto',
              overflowX: 'hidden',
              width: '100%',
              minHeight: 'calc(100vh - 112px)' // Account for header + tabs
            }}
          >
            {/* Content Header */}
            <Box sx={{ 
              mb: 3,
              display: 'flex',
              alignItems: 'center',
              gap: 2
            }}>
              <Box sx={{
                p: 1.5,
                backgroundColor: `${features.find(f => f.id === currentFeature)?.color}30`,
                borderRadius: 2
              }}>
                {features.find(f => f.id === currentFeature)?.icon}
              </Box>
              <Box>
                <Typography 
                  variant="h4" 
                  sx={{ 
                    color: '#e8e8f0', 
                    fontWeight: 700,
                    mb: 0.5
                  }}
                >
                  {features.find(f => f.id === currentFeature)?.label}
                </Typography>
                <Typography 
                  variant="subtitle1" 
                  sx={{ color: '#b8b8cc' }}
                >
                  {features.find(f => f.id === currentFeature)?.description}
                </Typography>
              </Box>
              <Chip
                label="Live Data"
                size="small"
                sx={{
                  backgroundColor: '#52c41a20',
                  color: '#52c41a',
                  fontWeight: 500,
                  ml: 'auto'
                }}
              />
            </Box>

            <AnimatePresence mode="wait">
              <motion.div
                key={currentFeature}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.4 }}
              >
                <Box sx={{ width: '100%' }}>
                  <Suspense fallback={
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                      <CircularProgress sx={{ color: '#1890ff' }} />
                    </Box>
                  }>
                    <CurrentComponent data={dashboardData} />
                  </Suspense>
                </Box>
              </motion.div>
            </AnimatePresence>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ValidatusDashboard;