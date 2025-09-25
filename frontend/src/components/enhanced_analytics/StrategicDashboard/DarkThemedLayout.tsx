// frontend/src/components/enhanced_analytics/StrategicDashboard/DarkThemedLayout.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Badge,
  Menu,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  LinearProgress,
  Tooltip,
  useTheme,
  useMediaQuery,
  Divider,
  Button,
  Stack
} from '@mui/material';
import {
  DashboardOutlined,
  BarChartOutlined,
  StorageOutlined,
  SettingsOutlined,
  AccountCircleOutlined,
  NotificationsOutlined,
  MenuOutlined,
  FullscreenOutlined,
  FileDownloadOutlined,
  WifiOutlined,
  WifiOffOutlined
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useWebSocketConnection } from '../../../hooks/useWebSocketConnection';
import { useAuthContext } from '../../../contexts/AuthContext';
import NotificationSystem from '../RealTimeUpdates/NotificationSystem';

// Dark theme styled components
const DarkAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: '#1a1a35',
  borderBottom: '1px solid #3d3d56',
  boxShadow: 'none',
}));

const DarkDrawer = styled(Drawer)(({ theme }) => ({
  '& .MuiDrawer-paper': {
    backgroundColor: '#1a1a35',
    borderRight: '1px solid #3d3d56',
    width: 280,
    color: '#e8e8f0',
  },
}));

const DarkListItemButton = styled(ListItemButton)(({ theme }) => ({
  margin: '4px 8px',
  borderRadius: '6px',
  '&:hover': {
    backgroundColor: '#ffffff10',
  },
  '&.Mui-selected': {
    background: 'linear-gradient(135deg, #1890ff20 0%, #1890ff10 100%)',
    border: '1px solid #1890ff40',
    '&:hover': {
      backgroundColor: '#1890ff30',
    },
  },
}));

interface StrategicLayoutProps {
  children: React.ReactNode;
  activeKey?: string;
  onMenuSelect?: (key: string) => void;
  showNotifications?: boolean;
}

interface AnalysisStatus {
  sessionId: string;
  topic: string;
  progress: number;
  status: 'running' | 'completed' | 'error';
  lastUpdate: string;
}

const StrategicDarkLayout: React.FC<StrategicLayoutProps> = ({
  children,
  activeKey = 'dashboard',
  onMenuSelect,
  showNotifications = true
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('lg'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchor, setNotificationAnchor] = useState<null | HTMLElement>(null);
  
  const { user } = useAuthContext();
  const { connectionStatus, lastMessage } = useWebSocketConnection();

  // Handle WebSocket messages for real-time updates
  useEffect(() => {
    if (lastMessage) {
      try {
        const message = JSON.parse(lastMessage.data);
        
        if (message.type === 'analysis_progress') {
          setAnalysisStatus(prev => {
            const existing = prev.find(s => s.sessionId === message.sessionId);
            if (existing) {
              return prev.map(s => 
                s.sessionId === message.sessionId 
                  ? { ...s, ...message.data, lastUpdate: new Date().toISOString() }
                  : s
              );
            }
            return [...prev, { ...message.data, lastUpdate: new Date().toISOString() }];
          });
        } else if (message.type === 'notification') {
          setNotifications(prev => [message, ...prev.slice(0, 49)]);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Strategic Command Center',
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: 'Advanced Analytics',
      children: [
        { key: 'factor-analysis', label: 'F1-F28 Factor Analysis' },
        { key: 'pattern-recognition', label: 'Pattern Recognition' },
        { key: 'monte-carlo', label: 'Monte Carlo Simulation' },
        { key: 'bayesian-blending', label: 'Bayesian Data Blending' },
      ],
    },
    {
      key: 'knowledge',
      icon: <StorageOutlined />,
      label: 'Knowledge Management',
      children: [
        { key: 'topic-stores', label: 'Topic Vector Stores' },
        { key: 'evidence-correlation', label: 'Evidence Correlation' },
        { key: 'hybrid-search', label: 'Hybrid Vector Search' },
      ],
    },
    {
      key: 'sessions',
      icon: <BarChartOutlined />,
      label: 'Analysis Sessions',
    },
    {
      key: 'settings',
      icon: <SettingsOutlined />,
      label: 'Configuration',
    },
  ];

  const handleMenuClick = useCallback((key: string) => {
    onMenuSelect?.(key);
    if (isMobile) {
      setMobileOpen(false);
    }
  }, [onMenuSelect, isMobile]);

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchor(null);
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo Section */}
      <Box
        sx={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #3d3d56',
          px: 2,
        }}
      >
        <Typography variant="h5" sx={{ color: '#1890ff', fontWeight: 'bold' }}>
          Validatus
        </Typography>
      </Box>

      {/* Menu Items */}
      <List sx={{ flex: 1, py: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.key} disablePadding>
            <DarkListItemButton
              selected={activeKey === item.key}
              onClick={() => handleMenuClick(item.key)}
            >
              <ListItemIcon sx={{ color: '#e8e8f0', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: '14px',
                  color: '#e8e8f0',
                }}
              />
            </DarkListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Analysis Status Indicator */}
      {analysisStatus.length > 0 && (
        <Box sx={{ p: 2, borderTop: '1px solid #3d3d56' }}>
          <Typography variant="caption" sx={{ color: '#b8b8cc', mb: 1, display: 'block' }}>
            Active Analyses
          </Typography>
          {analysisStatus.slice(0, 3).map((status) => (
            <Box key={status.sessionId} sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Typography variant="caption" sx={{ color: '#e8e8f0' }}>
                  {status.topic.substring(0, 15)}...
                </Typography>
                <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                  {status.progress}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={status.progress}
                sx={{
                  height: 2,
                  backgroundColor: '#3d3d56',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: status.status === 'error' ? '#ff4d4f' : '#1890ff',
                  },
                }}
              />
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh', backgroundColor: '#0f0f23' }}>
      {/* Desktop Sidebar */}
      <DarkDrawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? mobileOpen : true}
        onClose={() => setMobileOpen(false)}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
      >
        {drawerContent}
      </DarkDrawer>

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <DarkAppBar position="static" elevation={0}>
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Stack direction="row" alignItems="center" spacing={2}>
              <IconButton
                edge="start"
                color="inherit"
                onClick={() => setMobileOpen(true)}
                sx={{ display: { lg: 'none' } }}
              >
                <MenuOutlined />
              </IconButton>
              
              {/* Connection Status */}
              <Stack direction="row" alignItems="center" spacing={1}>
                {connectionStatus === 'connected' ? (
                  <WifiOutlined sx={{ color: '#52c41a', fontSize: 16 }} />
                ) : (
                  <WifiOffOutlined sx={{ color: '#ff4d4f', fontSize: 16 }} />
                )}
                <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                  {connectionStatus === 'connected' ? 'Live' : 'Offline'}
                </Typography>
              </Stack>
            </Stack>

            <Stack direction="row" alignItems="center" spacing={1}>
              <IconButton color="inherit" onClick={toggleFullscreen}>
                <FullscreenOutlined />
              </IconButton>
              
              <IconButton color="inherit">
                <FileDownloadOutlined />
              </IconButton>

              {showNotifications && (
                <>
                  <IconButton color="inherit" onClick={handleNotificationMenuOpen}>
                    <Badge badgeContent={notifications.length} color="error">
                      <NotificationsOutlined />
                    </Badge>
                  </IconButton>
                  <Menu
                    anchorEl={notificationAnchor}
                    open={Boolean(notificationAnchor)}
                    onClose={handleNotificationMenuClose}
                    PaperProps={{
                      sx: {
                        backgroundColor: '#1a1a35',
                        border: '1px solid #3d3d56',
                        maxHeight: 300,
                        width: 300,
                      }
                    }}
                  >
                    {notifications.slice(0, 5).map((notif, index) => (
                      <MenuItem key={index} onClick={handleNotificationMenuClose}>
                        <Box>
                          <Typography variant="body2" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                            {notif.title}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                            {notif.message}
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))}
                  </Menu>
                </>
              )}

              <IconButton color="inherit" onClick={handleUserMenuOpen}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#1890ff' }}>
                  <AccountCircleOutlined />
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleUserMenuClose}
                PaperProps={{
                  sx: {
                    backgroundColor: '#1a1a35',
                    border: '1px solid #3d3d56',
                  }
                }}
              >
                <MenuItem onClick={handleUserMenuClose}>
                  <ListItemIcon>
                    <AccountCircleOutlined sx={{ color: '#e8e8f0' }} />
                  </ListItemIcon>
                  <ListItemText primary="User Profile" sx={{ color: '#e8e8f0' }} />
                </MenuItem>
                <MenuItem onClick={handleUserMenuClose}>
                  <ListItemIcon>
                    <SettingsOutlined sx={{ color: '#e8e8f0' }} />
                  </ListItemIcon>
                  <ListItemText primary="Preferences" sx={{ color: '#e8e8f0' }} />
                </MenuItem>
                <Divider sx={{ backgroundColor: '#3d3d56' }} />
                <MenuItem onClick={handleUserMenuClose}>
                  <ListItemText primary="Sign Out" sx={{ color: '#e8e8f0' }} />
                </MenuItem>
              </Menu>
            </Stack>
          </Toolbar>
        </DarkAppBar>

        {/* Main Content Area */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            backgroundColor: '#0f0f23',
            overflow: 'auto',
          }}
        >
          {children}
        </Box>
      </Box>

      {/* Notification System */}
      {showNotifications && (
        <NotificationSystem 
          notifications={notifications}
          onDismiss={(index) => {
            setNotifications(prev => prev.filter((_, i) => i !== index));
          }}
        />
      )}
    </Box>
  );
};

export default StrategicDarkLayout;
