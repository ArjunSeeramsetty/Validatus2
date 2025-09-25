import React, { useState } from 'react';
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
  Dashboard,
  Topic,
  Analytics,
  Assessment,
  Settings,
  AccountCircle,
  Logout,
  TrendingUp
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 280;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
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
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'Topic Management', icon: <Topic />, path: '/topics' },
    { text: 'Analysis Sessions', icon: <Analytics />, path: '/analysis' },
    { text: 'Results', icon: <Assessment />, path: '/results' },
    { text: 'Enhanced Analytics', icon: <TrendingUp />, path: '/enhanced-analytics' },
    { text: 'Settings', icon: <Settings />, path: '/settings' },
  ];

  const drawer = (
    <Box sx={{ height: '100%', backgroundColor: '#1a1a35' }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ color: '#e8e8f0', fontWeight: 700 }}>
          Validatus
        </Typography>
      </Toolbar>
      <Divider sx={{ borderColor: '#3d3d56' }} />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => navigate(item.path)}
            sx={{
              margin: '4px 8px',
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
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          backgroundColor: '#1a1a35',
          borderBottom: '1px solid #3d3d56',
          boxShadow: 'none',
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
        aria-label="mailbox folders"
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
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundColor: '#1a1a35',
              borderRight: '1px solid #3d3d56'
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: '#0f0f23',
          minHeight: '100vh'
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout;