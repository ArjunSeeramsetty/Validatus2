/**
 * Responsive container that adjusts to main sidebar state
 * Use this for all pages to ensure proper space utilization
 */
import React from 'react';
import { Box, Container, useTheme, useMediaQuery } from '@mui/material';
import { useSidebar } from './MainLayout';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  fullWidth?: boolean;
  padding?: number | string;
}

const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({ 
  children, 
  maxWidth = 'xl',
  fullWidth = true,
  padding = 3
}) => {
  const { desktopOpen } = useSidebar();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{
      width: '100%',
      minHeight: 'calc(100vh - 64px)', // Account for AppBar height
      backgroundColor: '#0f0f23',
      transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
    }}>
      <Container
        maxWidth={maxWidth}
        sx={{
          width: '100%',
          maxWidth: fullWidth ? '100%' : undefined,
          px: isMobile ? 2 : padding,
          py: padding,
          transition: theme.transitions.create('padding', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

export default ResponsiveContainer;
