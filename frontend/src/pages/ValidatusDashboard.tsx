/**
 * Enhanced Validatus Dashboard with:
 * - Collapsible side menu
 * - Vertical tab navigation
 * - Tile-based Consumer Factor Analysis
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Toolbar,
  AppBar,
  CssBaseline
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  People,
  Store,
  Loyalty,
  Star,
  Menu,
  ChevronLeft
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

import BusinessCaseTab from '../components/Dashboard/BusinessCaseTab';
import EnhancedConsumerTab from '../components/Dashboard/EnhancedConsumerTab';
import MarketTab from '../components/Dashboard/MarketTab';
import ProductTab from '../components/Dashboard/ProductTab';
import BrandTab from '../components/Dashboard/BrandTab';
import ExperienceTab from '../components/Dashboard/ExperienceTab';

const drawerWidth = 280;

interface TabData {
  id: string;
  label: string;
  icon: React.ElementType;
  color: string;
  component: React.ComponentType<{ data: any }>;
}

const ValidatusDashboard: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('business-case');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sideMenuOpen, setSideMenuOpen] = useState(true);

  const tabs: TabData[] = [
    {
      id: 'business-case',
      label: 'Business Case',
      icon: Assessment,
      color: '#1890ff',
      component: BusinessCaseTab
    },
    {
      id: 'consumer',
      label: 'Consumer',
      icon: People,
      color: '#52c41a',
      component: EnhancedConsumerTab
    },
    {
      id: 'market',
      label: 'Market',
      icon: TrendingUp,
      color: '#fa8c16',
      component: MarketTab
    },
    {
      id: 'product',
      label: 'Product',
      icon: Store,
      color: '#722ed1',
      component: ProductTab
    },
    {
      id: 'brand',
      label: 'Brand',
      icon: Loyalty,
      color: '#eb2f96',
      component: BrandTab
    },
    {
      id: 'experience',
      label: 'Experience',
      icon: Star,
      color: '#13c2c2',
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

  const handleTabChange = (tabId: string) => {
    console.log('🟢 Tab changing to:', tabId);
    setCurrentTab(tabId);
  };

  const toggleSideMenu = () => {
    setSideMenuOpen(!sideMenuOpen);
  };

  const currentTabData = tabs.find(tab => tab.id === currentTab);
  const CurrentComponent = currentTabData?.component || BusinessCaseTab;

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#0f0f1a'
      }}>
        <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
          Loading Dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', backgroundColor: '#0f0f1a', minHeight: '100vh' }}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: sideMenuOpen ? `calc(100% - ${drawerWidth}px)` : '100%',
          ml: sideMenuOpen ? `${drawerWidth}px` : 0,
          backgroundColor: '#1a1a35',
          borderBottom: '1px solid #3d3d56',
          transition: theme => theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle menu"
            onClick={toggleSideMenu}
            edge="start"
            sx={{ mr: 2 }}
          >
            {sideMenuOpen ? <ChevronLeft /> : <Menu />}
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 700 }}>
              Strategic Analysis Dashboard
            </Typography>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              Pergola Market Analysis - Live Interactive Results
            </Typography>
          </Box>

          {/* Current Tab Indicator */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center',
            backgroundColor: `${currentTabData?.color}20`,
            px: 2,
            py: 1,
            borderRadius: 1,
            border: `1px solid ${currentTabData?.color}40`
          }}>
            {currentTabData?.icon && (
              <currentTabData.icon sx={{ color: currentTabData.color, mr: 1 }} />
            )}
            <Typography sx={{ color: currentTabData?.color, fontWeight: 600 }}>
              {currentTabData?.label}
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Side Navigation Drawer */}
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            backgroundColor: '#252547',
            borderRight: '1px solid #3d3d56',
          },
        }}
        variant="persistent"
        anchor="left"
        open={sideMenuOpen}
      >
        <Toolbar />
        
        <Box sx={{ overflow: 'auto', mt: 2 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              px: 2, 
              pb: 1, 
              color: '#b8b8cc',
              textTransform: 'uppercase',
              fontSize: '0.75rem',
              letterSpacing: 1
            }}
          >
            Analysis Modules
          </Typography>
          
          <List>
            {tabs.map((tab, index) => (
              <motion.div
                key={tab.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ListItem
                  button
                  selected={currentTab === tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  sx={{
                    mx: 1,
                    mb: 1,
                    borderRadius: 2,
                    '&.Mui-selected': {
                      backgroundColor: `${tab.color}20`,
                      borderLeft: `4px solid ${tab.color}`,
                      '&:hover': {
                        backgroundColor: `${tab.color}25`,
                      }
                    },
                    '&:hover': {
                      backgroundColor: `${tab.color}10`,
                    }
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    <tab.icon 
                      sx={{ 
                        color: currentTab === tab.id ? tab.color : '#b8b8cc',
                        transition: 'color 0.2s ease'
                      }} 
                    />
                  </ListItemIcon>
                  <ListItemText 
                    primary={tab.label}
                    sx={{
                      '& .MuiListItemText-primary': {
                        color: currentTab === tab.id ? tab.color : '#e8e8f0',
                        fontWeight: currentTab === tab.id ? 600 : 400,
                        transition: 'color 0.2s ease'
                      }
                    }}
                  />
                </ListItem>
              </motion.div>
            ))}
          </List>

          <Divider sx={{ mt: 2, borderColor: '#3d3d56' }} />

          {/* Navigation Stats */}
          <Box sx={{ p: 2, mt: 2 }}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 2 }}>
              Quick Stats
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                p: 1,
                backgroundColor: '#1a1a35',
                borderRadius: 1
              }}>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  Modules
                </Typography>
                <Typography variant="body2" sx={{ color: '#1890ff', fontWeight: 600 }}>
                  {tabs.length}
                </Typography>
              </Box>
              
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                p: 1,
                backgroundColor: '#1a1a35',
                borderRadius: 1
              }}>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  Analysis
                </Typography>
                <Typography variant="body2" sx={{ color: '#52c41a', fontWeight: 600 }}>
                  Live
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: sideMenuOpen ? `calc(100% - ${drawerWidth}px)` : '100%',
          transition: theme => theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar />
        
        {/* Tab Content with Animation */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            style={{ height: '100%' }}
          >
            <Box sx={{
              backgroundColor: '#1a1a35',
              borderRadius: 2,
              border: '1px solid #3d3d56',
              p: 3,
              minHeight: 'calc(100vh - 150px)'
            }}>
              <CurrentComponent data={dashboardData} />
            </Box>
          </motion.div>
        </AnimatePresence>
      </Box>
    </Box>
  );
};

export default ValidatusDashboard;
