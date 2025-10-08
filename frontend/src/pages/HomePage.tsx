import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid,
  Button,
  Chip,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  ListItemButton,
  ListItemIcon,
  IconButton,
  Divider,
  Fab
} from '@mui/material';
import { 
  TrendingUp, 
  Insights,
  Topic as TopicIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  CalendarToday as CalendarIcon,
  Search as SearchIcon,
  Link as LinkIcon,
  Dashboard as DashboardIcon,
  AnalyticsOutlined
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { enqueueSnackbar } from 'notistack';
import ValidatusDashboard from './ValidatusDashboard';
import PergolaIntelligenceDashboard from '../components/enhanced/PergolaIntelligenceDashboard';
import PergolaAnalysisPage from './PergolaAnalysisPage';
import AdvancedAnalysisDashboard from './AdvancedAnalysisDashboard';
import URLsTab from '../components/URLsTab';
import { topicService, TopicConfig } from '../services/topicService';


const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState(0);
  const [topics, setTopics] = useState<TopicConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [dashboardView, setDashboardView] = useState('dashboard'); // 'dashboard', 'pergola-intelligence', 'pergola-analysis', 'advanced-analysis'

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    try {
      setLoading(true);
      // Try to load from backend first
      const response = await topicService.listTopics(1, 50, 'created_at', 'desc');
      setTopics(response.topics);
      
      // Check if there are topics in localStorage to migrate
      const localTopics = topicService.getTopicsFromLocalStorage();
      if (localTopics.length > 0) {
        try {
          const migrationResult = await topicService.migrateFromLocalStorage(localTopics);
          if (migrationResult.migrated_count > 0) {
            enqueueSnackbar(
              `Migrated ${migrationResult.migrated_count} topics from local storage`, 
              { variant: 'success' }
            );
            // Reload topics after migration
            const updatedResponse = await topicService.listTopics(1, 50, 'created_at', 'desc');
            setTopics(updatedResponse.topics);
            // Clear localStorage after successful migration
            topicService.clearTopicsFromLocalStorage();
          }
        } catch (migrationError) {
          console.error('Migration failed:', migrationError);
          enqueueSnackbar('Topics could not be migrated to the server — working offline with local topics. Please check your network or retry from Settings.', { 
            variant: 'warning',
            action: (
              <Button color="inherit" size="small" onClick={handleMigrateTopics}>
                Retry
              </Button>
            )
          });
          // Fallback to localStorage topics
          setTopics(localTopics);
        }
      }
    } catch (error) {
      console.error('Error loading topics from backend:', error);
      enqueueSnackbar('Failed to load topics from server', { variant: 'error' });
      
      // Fallback to localStorage
      try {
        const localTopics = topicService.getTopicsFromLocalStorage();
        setTopics(localTopics);
        if (localTopics.length > 0) {
          enqueueSnackbar('Loaded topics from local storage', { variant: 'info' });
        }
      } catch (localError) {
        console.error('Error loading topics from localStorage:', localError);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTopic = async (sessionId: string) => {
    try {
      const success = await topicService.deleteTopic(sessionId);
      if (success) {
        const updatedTopics = topics.filter(topic => topic.session_id !== sessionId);
        setTopics(updatedTopics);
        enqueueSnackbar('Topic deleted successfully', { variant: 'success' });
      } else {
        enqueueSnackbar('Topic not found', { variant: 'error' });
      }
    } catch (error: any) {
      console.error('Error deleting topic:', error);
      enqueueSnackbar(error.message || 'Error deleting topic', { variant: 'error' });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    if (newValue === 0) { // Topics tab
      loadTopics();
    } else if (newValue === 1) { // Dashboard tab
      setDashboardView('dashboard'); // Reset to default dashboard view
    }
  };


  return (
    <Box sx={{ p: 4, width: '100%', maxWidth: 'none' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h3" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 2 }}>
            Validatus Strategic Analysis Platform
          </Typography>
          <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 3 }}>
            Advanced business intelligence and strategic analysis tools
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Chip label="Strategic Analysis" sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }} />
            <Chip label="Action Layer Calculator" sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }} />
            <Chip label="Sequential Workflow" sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }} />
          </Box>
        </Box>

        {/* Tabs */}
        <Box sx={{ mb: 4 }}>
          <Paper sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
            <Tabs 
              value={activeTab} 
              onChange={handleTabChange}
              sx={{
                '& .MuiTab-root': {
                  color: '#b8b8cc',
                  '&.Mui-selected': {
                    color: '#1890ff',
                  },
                },
                '& .MuiTabs-indicator': {
                  backgroundColor: '#1890ff',
                },
              }}
            >
              <Tab 
                label="Topics" 
                icon={<TopicIcon />} 
                iconPosition="start"
                sx={{ minHeight: 60 }}
              />
              <Tab 
                label="URLs" 
                icon={<LinkIcon />} 
                iconPosition="start"
                sx={{ minHeight: 60 }}
              />
              <Tab 
                label="Dashboard" 
                icon={<DashboardIcon />} 
                iconPosition="start"
                sx={{ minHeight: 60 }}
              />
            </Tabs>
          </Paper>
        </Box>

        {/* Tab Content */}
        {activeTab === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Topics Tab */}
            <Paper sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  My Topics
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/topic-creation')}
                  sx={{
                    backgroundColor: '#1890ff',
                    '&:hover': {
                      backgroundColor: '#1890ff',
                      opacity: 0.9
                    }
                  }}
                >
                  Create New Topic
                </Button>
              </Box>

              {topics.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  <TopicIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" gutterBottom sx={{ color: '#e8e8f0' }}>
                    No Topics Created Yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Create your first analysis topic to get started with strategic analysis.
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/topic-creation')}
                    sx={{
                      backgroundColor: '#1890ff',
                      '&:hover': {
                        backgroundColor: '#1890ff',
                        opacity: 0.9
                      }
                    }}
                  >
                    Create Your First Topic
                  </Button>
                </Box>
              ) : (
                <List sx={{ bgcolor: 'transparent' }}>
                  {topics.map((topic, index) => (
                    <React.Fragment key={topic.session_id}>
                      <ListItem
                        sx={{
                          bgcolor: 'transparent',
                          borderRadius: 2,
                          mb: 1,
                          border: '1px solid #3d3d56',
                          '&:hover': {
                            bgcolor: '#2a2a45',
                          }
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                          <Chip 
                            label={topic.analysis_type} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                            sx={{ mr: 2 }}
                          />
                        </Box>
                        <ListItemText
                          primary={
                            <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 500 }}>
                              {topic.topic}
                            </Typography>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                                {topic.description}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  <SearchIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                  <Typography variant="caption" color="text.secondary">
                                    {(topic.search_queries || []).length} queries
                                  </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  <LinkIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                  <Typography variant="caption" color="text.secondary">
                                    {(topic.initial_urls || []).length} URLs
                                  </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  <CalendarIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                  <Typography variant="caption" color="text.secondary">
                                    {formatDate(topic.created_at)}
                                  </Typography>
                                </Box>
                                <Chip 
                                  label={topic.status} 
                                  size="small" 
                                  color={topic.status === 'created' ? 'success' : 'default'}
                                  variant="outlined"
                                />
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                              size="small"
                              onClick={() => navigate('/topic-creation', { state: { editTopic: topic } })}
                              title="Edit Topic"
                              sx={{ color: '#1890ff' }}
                            >
                              <EditIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => navigate('/topics')}
                              title="View Details"
                              sx={{ color: '#52c41a' }}
                            >
                              <VisibilityIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => handleDeleteTopic(topic.session_id)}
                              title="Delete Topic"
                              sx={{ color: '#ff4d4f' }}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < topics.length - 1 && <Divider sx={{ bgcolor: '#3d3d56' }} />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </Paper>
          </motion.div>
        )}

        {activeTab === 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* URLs Tab */}
            <URLsTab refreshTrigger={activeTab} />
          </motion.div>
        )}

        {activeTab === 2 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Dashboard Tab - Full Dashboard Experience */}
            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, minHeight: '80vh', width: '100%' }}>
              {/* Left Sidebar Navigation */}
              <Box
                sx={{
                  width: { xs: '100%', md: 280 },
                  backgroundColor: '#1a1a35',
                  border: '1px solid #3d3d56',
                  borderRadius: 2,
                  p: 2,
                  mr: { xs: 0, md: 3 },
                  mb: { xs: 3, md: 0 },
                  height: 'fit-content',
                  position: { xs: 'relative', md: 'sticky' },
                  top: 0,
                  flexShrink: 0
                }}
              >
                <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 2 }}>
                  Dashboard Navigation
                </Typography>
                <Divider sx={{ borderColor: '#3d3d56', mb: 2 }} />
                <List sx={{ p: 0 }}>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemButton
                      onClick={() => setDashboardView('dashboard')}
                      sx={{
                        borderRadius: 2,
                        backgroundColor: dashboardView === 'dashboard' ? '#1890ff20' : 'transparent',
                        '&:hover': {
                          backgroundColor: '#1890ff20',
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: dashboardView === 'dashboard' ? '#1890ff' : '#b8b8cc' }}>
                        <DashboardIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          <Typography 
                            sx={{ 
                              color: dashboardView === 'dashboard' ? '#1890ff' : '#e8e8f0',
                              fontWeight: dashboardView === 'dashboard' ? 600 : 400
                            }}
                          >
                            Dashboard
                          </Typography>
                        }
                      />
                    </ListItemButton>
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemButton
                      onClick={() => setDashboardView('pergola-intelligence')}
                      sx={{
                        borderRadius: 2,
                        backgroundColor: dashboardView === 'pergola-intelligence' ? '#1890ff20' : 'transparent',
                        '&:hover': {
                          backgroundColor: '#1890ff20',
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: dashboardView === 'pergola-intelligence' ? '#1890ff' : '#b8b8cc' }}>
                        <Insights />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          <Typography 
                            sx={{ 
                              color: dashboardView === 'pergola-intelligence' ? '#1890ff' : '#e8e8f0',
                              fontWeight: dashboardView === 'pergola-intelligence' ? 600 : 400
                            }}
                          >
                            Pergola Intelligence
                          </Typography>
                        }
                      />
                    </ListItemButton>
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemButton
                      onClick={() => setDashboardView('pergola-analysis')}
                      sx={{
                        borderRadius: 2,
                        backgroundColor: dashboardView === 'pergola-analysis' ? '#1890ff20' : 'transparent',
                        '&:hover': {
                          backgroundColor: '#1890ff20',
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: dashboardView === 'pergola-analysis' ? '#1890ff' : '#b8b8cc' }}>
                        <TrendingUp />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          <Typography 
                            sx={{ 
                              color: dashboardView === 'pergola-analysis' ? '#1890ff' : '#e8e8f0',
                              fontWeight: dashboardView === 'pergola-analysis' ? 600 : 400
                            }}
                          >
                            Pergola Analysis
                          </Typography>
                        }
                      />
                    </ListItemButton>
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemButton
                      onClick={() => setDashboardView('advanced-analysis')}
                      sx={{
                        borderRadius: 2,
                        backgroundColor: dashboardView === 'advanced-analysis' ? '#1890ff20' : 'transparent',
                        '&:hover': {
                          backgroundColor: '#1890ff20',
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: dashboardView === 'advanced-analysis' ? '#1890ff' : '#b8b8cc' }}>
                        <AnalyticsOutlined />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          <Typography 
                            sx={{ 
                              color: dashboardView === 'advanced-analysis' ? '#1890ff' : '#e8e8f0',
                              fontWeight: dashboardView === 'advanced-analysis' ? 600 : 400
                            }}
                          >
                            Advanced Analysis
                          </Typography>
                        }
                      />
                    </ListItemButton>
                  </ListItem>
                </List>
              </Box>

              {/* Main Dashboard Content - Full Width */}
              <Box sx={{ flexGrow: 1, minWidth: 0, width: '100%' }}>
                {dashboardView === 'dashboard' && <ValidatusDashboard />}
                {dashboardView === 'pergola-intelligence' && <PergolaIntelligenceDashboard />}
                {dashboardView === 'pergola-analysis' && (
                  <Box sx={{ p: 3, width: '100%' }}>
                    <PergolaAnalysisPage />
                  </Box>
                )}
                {dashboardView === 'advanced-analysis' && (
                  <Box sx={{ p: 3, width: '100%' }}>
                    <AdvancedAnalysisDashboard />
                  </Box>
                )}
              </Box>
            </Box>
          </motion.div>
        )}


        {/* Quick Stats */}
        <Box sx={{ mt: 6, textAlign: 'center' }}>
          <Typography variant="h5" sx={{ color: '#e8e8f0', mb: 3 }}>
            Platform Overview
          </Typography>
          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Typography variant="h4" sx={{ color: '#1890ff', fontWeight: 600 }}>
                    2
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Main Sections
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Typography variant="h4" sx={{ color: '#52c41a', fontWeight: 600 }}>
                    1
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Market Analysis
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Typography variant="h4" sx={{ color: '#fa8c16', fontWeight: 600 }}>
                    100%
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Strategic Coverage
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </motion.div>
    </Box>
  );
};

export default HomePage;
