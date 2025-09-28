/**
 * Main Validatus Dashboard with Enhanced Feature Navigation
 * - Vertical stack of large feature cards for navigation
 * - Tile-based Consumer Factor Analysis (3 per row)
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
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
      display: 'flex',
      width: '100%',
      maxWidth: '100%'
    }}>
      {/* Left Sidebar - Feature Navigation */}
      <Box sx={{
        width: { xs: 280, sm: 280, md: 300, lg: 320, xl: 340 },
        backgroundColor: '#252547',
        borderRight: '1px solid #3d3d56',
        minHeight: '100vh',
        position: 'sticky',
        top: 0,
        flexShrink: 0
      }}>
        {/* Header */}
        <Box sx={{ p: 3, borderBottom: '1px solid #3d3d56' }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: '#e8e8f0', 
              fontWeight: 700,
              mb: 1
            }}
          >
            Dashboard
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ color: '#b8b8cc' }}
          >
            Analysis Modules
          </Typography>
        </Box>

        {/* Feature Navigation List */}
        <Box sx={{ p: 2 }}>
          <List sx={{ p: 0 }}>
            {features.map((feature, index) => (
              <motion.div
                key={feature.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ListItem
                  button
                  selected={currentFeature === feature.id}
                  onClick={() => handleFeatureChange(feature.id)}
                  sx={{
                    mb: 1,
                    borderRadius: 2,
                    borderLeft: currentFeature === feature.id ? `4px solid ${feature.color}` : '4px solid transparent',
                    backgroundColor: currentFeature === feature.id ? `${feature.color}20` : 'transparent',
                    '&.Mui-selected': {
                      backgroundColor: `${feature.color}20`,
                      '&:hover': {
                        backgroundColor: `${feature.color}25`,
                      }
                    },
                    '&:hover': {
                      backgroundColor: currentFeature === feature.id ? `${feature.color}25` : `${feature.color}10`,
                    },
                    transition: 'all 0.2s ease'
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 48 }}>
                    <feature.icon sx={{ 
                      color: currentFeature === feature.id ? feature.color : '#b8b8cc',
                      fontSize: 24,
                      transition: 'color 0.2s ease'
                    }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary={feature.label}
                    secondary={feature.description}
                    sx={{
                      '& .MuiListItemText-primary': {
                        color: currentFeature === feature.id ? feature.color : '#e8e8f0',
                        fontWeight: currentFeature === feature.id ? 600 : 400,
                        fontSize: '1rem',
                        transition: 'color 0.2s ease'
                      },
                      '& .MuiListItemText-secondary': {
                        color: '#b8b8cc',
                        fontSize: '0.8rem',
                        lineHeight: 1.3,
                        mt: 0.5
                      }
                    }}
                  />
                </ListItem>
              </motion.div>
            ))}
          </List>
        </Box>

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
      </Box>

      {/* Main Content Area */}
      <Box sx={{ 
        flex: 1,
        backgroundColor: '#1a1a35',
        minHeight: '100vh',
        width: '100%',
        overflow: 'auto',
        position: 'relative'
      }}>
        {/* Content Header */}
        <Box sx={{ 
          p: 3,
          borderBottom: '1px solid #3d3d56',
          backgroundColor: '#252547'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{
              p: 1,
              backgroundColor: `${currentFeatureData?.color}30`,
              borderRadius: 2
            }}>
              {currentFeatureData?.icon && (
                <currentFeatureData.icon sx={{ 
                  color: currentFeatureData.color, 
                  fontSize: 28 
                }} />
              )}
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
                {currentFeatureData?.label}
              </Typography>
              <Typography 
                variant="subtitle1" 
                sx={{ color: '#b8b8cc' }}
              >
                {currentFeatureData?.description}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Feature Content */}
        <Box sx={{ 
          width: '100%',
          maxWidth: '100%'
        }}>
          <motion.div
            key={currentFeature}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <CurrentComponent data={dashboardData} />
          </motion.div>
        </Box>
      </Box>
    </Box>
  );
};

export default ValidatusDashboard;
