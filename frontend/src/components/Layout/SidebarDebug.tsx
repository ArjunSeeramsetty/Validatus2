/**
 * Debug component to show sidebar state
 * Use this temporarily to verify sidebar context is working
 */
import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { useSidebar } from './MainLayout';

const SidebarDebug: React.FC = () => {
  const { desktopOpen, drawerWidth, actualDrawerWidth } = useSidebar();

  return (
    <Box sx={{ 
      position: 'fixed', 
      bottom: 16, 
      right: 16,
      p: 2,
      backgroundColor: '#1a1a35',
      border: '1px solid #3d3d56',
      borderRadius: 2,
      zIndex: 9999
    }}>
      <Typography variant="caption" sx={{ color: '#b8b8cc', display: 'block', mb: 1 }}>
        Sidebar Debug
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        <Chip 
          label={`Main: ${desktopOpen ? 'Open' : 'Closed'}`}
          size="small"
          color={desktopOpen ? 'success' : 'warning'}
        />
        <Chip 
          label={`Base: ${drawerWidth}px`}
          size="small"
          color="info"
        />
        <Chip 
          label={`Actual: ${actualDrawerWidth}px`}
          size="small"
          color="primary"
        />
      </Box>
    </Box>
  );
};

export default SidebarDebug;
