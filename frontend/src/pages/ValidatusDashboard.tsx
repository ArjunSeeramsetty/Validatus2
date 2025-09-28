/**
 * Main Validatus Dashboard matching Figma design
 * Implements Business Case Calculator + Segment Analysis Tabs
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { 
  Assessment, 
  TrendingUp, 
  People, 
  Store, 
  Loyalty, 
  Star 
} from '@mui/icons-material';

import BusinessCaseTab from '../components/Dashboard/BusinessCaseTab';
import ConsumerTab from '../components/Dashboard/ConsumerTab';
import MarketTab from '../components/Dashboard/MarketTab';
import ProductTab from '../components/Dashboard/ProductTab';
import BrandTab from '../components/Dashboard/BrandTab';
import ExperienceTab from '../components/Dashboard/ExperienceTab';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ width: '100%' }}>
    {value === index && <Box sx={{ p: 0 }}>{children}</Box>}
  </div>
);

const ValidatusDashboard: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const tabs = [
    { label: 'Business Case', icon: Assessment, color: '#1890ff' },
    { label: 'Consumer', icon: People, color: '#52c41a' },
    { label: 'Market', icon: TrendingUp, color: '#fa8c16' },
    { label: 'Product', icon: Store, color: '#722ed1' },
    { label: 'Brand', icon: Loyalty, color: '#eb2f96' },
    { label: 'Experience', icon: Star, color: '#13c2c2' }
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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    console.log('🟢 Tab changing to:', newValue);
    setCurrentTab(newValue);
  };

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
        {/* Tab Navigation */}
        <Box sx={{ 
          borderBottom: '1px solid #3d3d56',
          backgroundColor: '#252547'
        }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                color: '#b8b8cc',
                fontWeight: 600,
                textTransform: 'none',
                fontSize: '1rem',
                minHeight: 64,
                '&.Mui-selected': {
                  color: tabs[currentTab]?.color || '#1890ff'
                }
              },
              '& .MuiTabs-indicator': {
                backgroundColor: tabs[currentTab]?.color || '#1890ff',
                height: 3
              }
            }}
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                label={tab.label}
                icon={<tab.icon />}
                iconPosition="start"
                sx={{
                  '& .MuiSvgIcon-root': {
                    color: currentTab === index ? tab.color : '#b8b8cc'
                  }
                }}
              />
            ))}
          </Tabs>
        </Box>

        {/* Tab Content */}
        <Box sx={{ backgroundColor: '#1a1a35' }}>
          <TabPanel value={currentTab} index={0}>
            <Box sx={{ backgroundColor: 'yellow', color: 'black', p: 2, mb: 2 }}>
              🟡 TAB 0 (Business Case) - currentTab: {currentTab}
            </Box>
            <BusinessCaseTab data={dashboardData} />
          </TabPanel>
          
          <TabPanel value={currentTab} index={1}>
            <ConsumerTab data={dashboardData} />
          </TabPanel>
          
          <TabPanel value={currentTab} index={2}>
            <MarketTab data={dashboardData} />
          </TabPanel>
          
          <TabPanel value={currentTab} index={3}>
            <ProductTab data={dashboardData} />
          </TabPanel>
          
          <TabPanel value={currentTab} index={4}>
            <BrandTab data={dashboardData} />
          </TabPanel>
          
          <TabPanel value={currentTab} index={5}>
            <ExperienceTab data={dashboardData} />
          </TabPanel>
        </Box>
      </Paper>
    </Box>
  );
};

export default ValidatusDashboard;
