import React, { useState, createContext, useContext } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Chip
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft,
  Dashboard,
  Analytics,
  Insights,
  AccountCircle,
  Logout,
  TrendingUp,
  AnalyticsOutlined
} from '@mui/icons-material';
import ListItemButton from '@mui/material/ListItemButton';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 280;

// Create Sidebar Context
interface SidebarContextType {
  desktopOpen: boolean;
  toggleSidebar: () => void;
  drawerWidth: number;
  actualDrawerWidth: number;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
};

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [desktopOpen, setDesktopOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleDesktopDrawerToggle = () => {
    setDesktopOpen(!desktopOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleProfileMenuClose();
    navigate('/login');
  };

  const menuItems = [
    { text: 'Home', icon: <Dashboard />, path: '/' },
    { text: 'Dashboard', icon: <Analytics />, path: '/dashboard' },
    { text: 'Pergola Intelligence', icon: <Insights />, path: '/pergola-intelligence' },
    { text: 'Pergola Analysis', icon: <TrendingUp />, path: '/migrated/v2_analysis_20250905_185553_d5654178' },
    { text: 'Advanced Analysis', icon: <AnalyticsOutlined />, path: '/analysis/v2_analysis_20250905_185553_d5654178/advanced' },
  ];

  const drawer = (
    <Box sx={{ height: '100%', backgroundColor: '#1a1a35', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ justifyContent: 'space-between', px: 2 }}>
        <Typography variant="h6" noWrap component="div" sx={{ color: '#e8e8f0', fontWeight: 700 }}>
          Validatus
        </Typography>
        <IconButton
          color="inherit"
          aria-label="close drawer"
          onClick={handleDesktopDrawerToggle}
          sx={{ 
            display: { xs: 'none', sm: 'block' },
            color: '#b8b8cc',
            '&:hover': {
              backgroundColor: '#ffffff10'
            }
          }}
        >
          <ChevronLeft />
        </IconButton>
      </Toolbar>
      <Divider sx={{ borderColor: '#3d3d56' }} />
      <List sx={{ flex: 1, overflow: 'auto' }}>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            sx={{
              margin: '4px 8px',
              borderRadius: 2,
              padding: 0,
            }}
          >
            <ListItemButton
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 2,
                backgroundColor: location.pathname === item.path ? '#1890ff20' : 'transparent',
                '&:hover': {
                  backgroundColor: location.pathname === item.path ? '#1890ff30' : '#ffffff10',
                },
              }}
            >
            <ListItemIcon sx={{ color: location.pathname === item.path ? '#1890ff' : '#b8b8cc' }}>
              {item.icon}
            </ListItemIcon>
              <ListItemText 
                primary={item.text} 
                sx={{ 
                  '& .MuiListItemText-primary': { 
                    color: location.pathname === item.path ? '#1890ff' : '#e8e8f0',
                    fontWeight: location.pathname === item.path ? 600 : 400
                  } 
                }} 
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  const sidebarContextValue: SidebarContextType = {
    desktopOpen,
    toggleSidebar: handleDesktopDrawerToggle,
    drawerWidth,
    actualDrawerWidth: desktopOpen ? drawerWidth : 0
  };

  return (
    <SidebarContext.Provider value={sidebarContextValue}>
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: desktopOpen ? `calc(100% - ${drawerWidth}px)` : '100%' },
          ml: { sm: desktopOpen ? `${drawerWidth}px` : 0 },
          backgroundColor: '#1a1a35',
          borderBottom: '1px solid #3d3d56',
          boxShadow: 'none',
          transition: theme => theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          {!desktopOpen && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDesktopDrawerToggle}
              sx={{ mr: 2, display: { xs: 'none', sm: 'block' } }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, color: '#e8e8f0' }}>
            Strategic Analysis Platform
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label="Demo Mode" 
              size="small"
              sx={{
                backgroundColor: '#52c41a20',
                color: '#52c41a',
                fontWeight: 500
              }}
            />
            
            <IconButton
              size="large"
              edge="end"
              aria-label="account of current user"
              aria-haspopup="true"
              onClick={handleProfileMenuOpen}
              color="inherit"
            >
              <Avatar 
                sx={{ 
                  width: 32, 
                  height: 32, 
                  backgroundColor: '#1890ff',
                  fontSize: '1rem'
                }}
              >
                {user?.name?.charAt(0) || 'U'}
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        PaperProps={{
          sx: {
            backgroundColor: '#1a1a35',
            border: '1px solid #3d3d56',
            '& .MuiMenuItem-root': {
              color: '#e8e8f0',
              '&:hover': {
                backgroundColor: '#252547'
              }
            }
          }
        }}
      >
        <MenuItem onClick={handleProfileMenuClose}>
          <ListItemIcon>
            <AccountCircle sx={{ color: '#b8b8cc' }} />
          </ListItemIcon>
          <Box>
            <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
              {user?.name || 'Demo User'}
            </Typography>
            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
              {user?.email || 'demo@validatus.com'}
            </Typography>
          </Box>
        </MenuItem>
        <Divider sx={{ borderColor: '#3d3d56' }} />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout sx={{ color: '#ff4d4f' }} />
          </ListItemIcon>
          Sign Out
        </MenuItem>
      </Menu>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="Main navigation"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundColor: '#1a1a35',
              borderRight: '1px solid #3d3d56'
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="persistent"
          open={desktopOpen}
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundColor: '#1a1a35',
              borderRight: '1px solid #3d3d56',
              transition: theme => theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
              }),
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: desktopOpen ? `calc(100% - ${drawerWidth}px)` : '100%' },
          backgroundColor: '#0f0f23',
          minHeight: '100vh',
          transition: theme => theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          overflow: 'hidden', // Prevent horizontal scroll
          boxSizing: 'border-box', // Ensure proper box model
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
    </SidebarContext.Provider>
  );
};

export default MainLayout;