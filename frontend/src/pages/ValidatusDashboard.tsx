/**
 * Main Validatus Dashboard with Enhanced Feature Navigation
 * - Vertical stack of large feature cards for navigation
 * - Tile-based Consumer Factor Analysis (3 per row)
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Divider,
  Stack
} from '@mui/material';
import { 
  Assessment, 
  TrendingUp, 
  People, 
  Store, 
  Loyalty, 
  Star 
} from '@mui/icons-material';
import { motion } from 'framer-motion';

import BusinessCaseTab from '../components/Dashboard/BusinessCaseTab';
import EnhancedConsumerTab from '../components/Dashboard/EnhancedConsumerTab';
import MarketTab from '../components/Dashboard/MarketTab';
import ProductTab from '../components/Dashboard/ProductTab';
import BrandTab from '../components/Dashboard/BrandTab';
import ExperienceTab from '../components/Dashboard/ExperienceTab';

interface FeatureData {
  id: string;
  label: string;
  icon: React.ElementType;
  color: string;
  description: string;
  component: React.ComponentType<{ data: any }>;
}

const ValidatusDashboard: React.FC = () => {
  const [currentFeature, setCurrentFeature] = useState('business-case');
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const features: FeatureData[] = [
    {
      id: 'business-case',
      label: 'Business Case',
      icon: Assessment,
      color: '#1890ff',
      description: 'Financial projections, ROI analysis, and business metrics',
      component: BusinessCaseTab
    },
    {
      id: 'consumer',
      label: 'Consumer',
      icon: People,
      color: '#52c41a',
      description: 'Consumer behavior, preferences, and market insights',
      component: EnhancedConsumerTab
    },
    {
      id: 'market',
      label: 'Market',
      icon: TrendingUp,
      color: '#fa8c16',
      description: 'Market trends, competition, and growth opportunities',
      component: MarketTab
    },
    {
      id: 'product',
      label: 'Product',
      icon: Store,
      color: '#722ed1',
      description: 'Product features, innovation, and development roadmap',
      component: ProductTab
    },
    {
      id: 'brand',
      label: 'Brand',
      icon: Loyalty,
      color: '#eb2f96',
      description: 'Brand positioning, messaging, and market perception',
      component: BrandTab
    },
    {
      id: 'experience',
      label: 'Experience',
      icon: Star,
      color: '#13c2c2',
      description: 'User experience, customer journey, and satisfaction',
      component: ExperienceTab
    }
  ];

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const baseUrl = window.location.origin;
      
      // Try enhanced pergola API first
      try {
        const enhancedResponse = await fetch(`${baseUrl}/api/v3/pergola/dashboard-data`);
        
        if (enhancedResponse.ok) {
          const enhancedData = await enhancedResponse.json();
          if (enhancedData.status === 'success') {
            setDashboardData(enhancedData.data);
            return;
          }
        }
      } catch (enhancedError) {
        console.log('Enhanced API not available, falling back to standard API');
      }
      
      // Fallback to original dashboard API
      const response = await fetch(`${baseUrl}/api/v3/dashboard/v2_analysis_20250905_185553_d5654178/overview`);
      const result = await response.json();
      if (result.success) {
        setDashboardData(result.data);
      } else {
        console.error('Failed to load dashboard data:', result);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Fallback to migrated data
      try {
        const baseUrl = window.location.origin;
        const fallbackResponse = await fetch(`${baseUrl}/api/v3/migrated/results/v2_analysis_20250905_185553_d5654178`);
        const fallbackData = await fallbackResponse.json();
        setDashboardData(fallbackData);
      } catch (fallbackError) {
        console.error('Fallback data load also failed:', fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFeatureChange = (featureId: string) => {
    console.log('🟢 Feature changing to:', featureId);
    setCurrentFeature(featureId);
  };

  const currentFeatureData = features.find(feature => feature.id === currentFeature);
  const CurrentComponent = currentFeatureData?.component || BusinessCaseTab;

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#0f0f1a'
      }}>
        <Typography sx={{ color: '#e8e8f0' }}>Loading Dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      backgroundColor: '#0f0f1a', 
      minHeight: '100vh',
      p: 3
    }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            color: '#e8e8f0', 
            fontWeight: 700,
            mb: 1
          }}
        >
          Strategic Analysis Dashboard
        </Typography>
        <Typography 
          variant="subtitle1" 
          sx={{ color: '#b8b8cc' }}
        >
          Pergola Market Analysis - Live Interactive Results
        </Typography>
      </Box>

      {/* Main Dashboard Container */}
      <Paper sx={{ 
        backgroundColor: '#1a1a35',
        border: '1px solid #3d3d56',
        borderRadius: 2,
        overflow: 'hidden'
      }}>
        {/* Feature Navigation Cards - Vertical Stack */}
        <Box sx={{ 
          p: 3,
          backgroundColor: '#252547',
          borderBottom: '1px solid #3d3d56'
        }}>
          <Typography 
            variant="h6" 
            sx={{ 
              color: '#e8e8f0', 
              mb: 3,
              fontWeight: 600
            }}
          >
            Analysis Modules
          </Typography>
          
          <Stack spacing={2}>
            {features.map((feature, index) => (
              <motion.div
                key={feature.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    borderLeft: currentFeature === feature.id ? `5px solid ${feature.color}` : '5px solid transparent',
                    backgroundColor: currentFeature === feature.id ? `${feature.color}15` : '#1a1a35',
                    border: `1px solid ${currentFeature === feature.id ? feature.color : '#3d3d56'}`,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: `${feature.color}10`,
                      border: `1px solid ${feature.color}`,
                      transform: 'translateX(4px)',
                    }
                  }}
                  onClick={() => handleFeatureChange(feature.id)}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{
                        p: 1.5,
                        backgroundColor: currentFeature === feature.id ? `${feature.color}30` : '#3d3d56',
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.2s ease'
                      }}>
                        <feature.icon sx={{ 
                          color: currentFeature === feature.id ? feature.color : '#b8b8cc',
                          fontSize: 28,
                          transition: 'color 0.2s ease'
                        }} />
                      </Box>
                      
                      <Box sx={{ flex: 1 }}>
                        <Typography 
                          variant="h6" 
                          sx={{ 
                            color: currentFeature === feature.id ? feature.color : '#e8e8f0',
                            fontWeight: currentFeature === feature.id ? 700 : 600,
                            mb: 0.5,
                            transition: 'color 0.2s ease'
                          }}
                        >
                          {feature.label}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: '#b8b8cc',
                            lineHeight: 1.4
                          }}
                        >
                          {feature.description}
                        </Typography>
                      </Box>

                      {/* Selection Indicator */}
                      {currentFeature === feature.id && (
                        <Box sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          backgroundColor: feature.color,
                          animation: 'pulse 2s infinite'
                        }} />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </Stack>
        </Box>

        <Divider sx={{ borderColor: '#3d3d56' }} />

        {/* Feature Content */}
        <Box sx={{ backgroundColor: '#1a1a35', minHeight: '600px' }}>
          <motion.div
            key={currentFeature}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Box sx={{ p: 3 }}>
              <CurrentComponent data={dashboardData} />
            </Box>
          </motion.div>
        </Box>
      </Paper>
    </Box>
  );
};

export default ValidatusDashboard;
