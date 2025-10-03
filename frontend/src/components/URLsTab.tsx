import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Paper,
  Link,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Link as LinkIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiClient } from '../services/apiClient';
import { topicService } from '../services/topicService';

interface Topic {
  session_id: string;
  topic: string;
  description: string;
  status: string;
  initial_urls: string[];
  updated_at: string;
  metadata?: any;
}

interface TopicURLs {
  session_id: string;
  topic: string;
  urls: string[];
  url_count: number;
  last_updated: string;
  metadata?: any;
}

interface URLsTabProps {
  refreshTrigger?: number;
}

const URLsTab: React.FC<URLsTabProps> = ({ refreshTrigger }) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [topicURLs, setTopicURLs] = useState<TopicURLs | null>(null);
  const [loading, setLoading] = useState(false);
  const [urlLoading, setUrlLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [collecting, setCollecting] = useState(false);
  const [showUrlDialog, setShowUrlDialog] = useState(false);
  const [newUrl, setNewUrl] = useState('');

  // Load topics on component mount and when component becomes visible
  useEffect(() => {
    loadTopics();
  }, []);

  // Refresh topics when refreshTrigger changes (when tab becomes active)
  useEffect(() => {
    if (refreshTrigger !== undefined) {
      loadTopics();
    }
  }, [refreshTrigger]);

  const loadTopics = async () => {
    try {
      setLoading(true);
      setError(null);
      const topicsData = await topicService.listTopics();
      setTopics(topicsData.topics || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  const loadTopicURLs = async (topic: Topic) => {
    try {
      setUrlLoading(true);
      setError(null);
      const response = await apiClient.get(`/api/v3/topics/${topic.session_id}/urls`);
      setTopicURLs(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load URLs');
    } finally {
      setUrlLoading(false);
    }
  };

  const collectURLs = async (topic: Topic) => {
    try {
      setCollecting(true);
      setError(null);
      
      const response = await apiClient.post(`/api/v3/topics/${topic.session_id}/collect-urls`);
      
      // Reload topic URLs after collection
      await loadTopicURLs(topic);
      
      // Reload topics to update status
      await loadTopics();
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to collect URLs');
      throw err;
    } finally {
      setCollecting(false);
    }
  };

  const addManualURL = async () => {
    if (!newUrl || !selectedTopic) return;
    
    try {
      // For now, we'll just add to the local state
      // In a real implementation, you'd call an API to update the topic
      if (topicURLs) {
        const updatedURLs = [...topicURLs.urls, newUrl];
        setTopicURLs({
          ...topicURLs,
          urls: updatedURLs,
          url_count: updatedURLs.length
        });
      }
      setNewUrl('');
      setShowUrlDialog(false);
    } catch (err: any) {
      setError(err.message || 'Failed to add URL');
    }
  };

  const clearDuplicates = () => {
    // Remove duplicate topics based on topic name and description
    const uniqueTopics = topics.filter((topic, index, self) => 
      index === self.findIndex(t => 
        t.topic === topic.topic && 
        t.description === topic.description &&
        t.session_id === topic.session_id
      )
    );
    setTopics(uniqueTopics);
  };

  const handleTopicSelect = (topic: Topic) => {
    setSelectedTopic(topic);
    loadTopicURLs(topic);
  };

  const handleCollectURLs = async (topic: Topic) => {
    try {
      const result = await collectURLs(topic);
      // Success message could be shown here
    } catch (err) {
      // Error is already set in collectURLs
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'created': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon />;
      case 'in_progress': return <ScheduleIcon />;
      case 'created': return <AddIcon />;
      default: return <ErrorIcon />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ color: '#e8e8f0', mb: 3, fontWeight: 600 }}>
        URL Collection & Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Topics List */}
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            backgroundColor: '#1a1a2e', 
            border: '1px solid #2d2d44',
            height: '100%'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  Select Topic ({topics.length} topics)
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {topics.length > 0 && (
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={clearDuplicates}
                      sx={{ 
                        borderColor: '#ff4d4f',
                        color: '#ff4d4f',
                        '&:hover': {
                          borderColor: '#ff7875',
                          backgroundColor: 'rgba(255, 77, 79, 0.04)'
                        }
                      }}
                    >
                      Clear Duplicates
                    </Button>
                  )}
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<RefreshIcon />}
                    onClick={loadTopics}
                    disabled={loading}
                    sx={{ 
                      borderColor: '#1890ff',
                      color: '#1890ff',
                      '&:hover': {
                        borderColor: '#40a9ff',
                        backgroundColor: 'rgba(24, 144, 255, 0.04)'
                      }
                    }}
                  >
                    {loading ? 'Refreshing...' : 'Refresh'}
                  </Button>
                </Box>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {topics.map((topic) => (
                    <ListItem
                      key={topic.session_id}
                      button
                      onClick={() => handleTopicSelect(topic)}
                      selected={selectedTopic?.session_id === topic.session_id}
                      sx={{
                        borderRadius: 1,
                        mb: 1,
                        backgroundColor: selectedTopic?.session_id === topic.session_id ? '#2d2d44' : 'transparent',
                        '&:hover': {
                          backgroundColor: '#2d2d44'
                        }
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" sx={{ color: '#e8e8f0' }}>
                              {topic.topic}
                            </Typography>
                            <Chip
                              icon={getStatusIcon(topic.status)}
                              label={topic.status}
                              size="small"
                              color={getStatusColor(topic.status) as any}
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                              {topic.description}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#888' }}>
                              {topic.initial_urls.length} URLs • Updated: {new Date(topic.updated_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                  {topics.length === 0 && (
                    <Typography variant="body2" sx={{ color: '#888', textAlign: 'center', py: 2 }}>
                      No topics found. Create a topic first.
                    </Typography>
                  )}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* URL Management */}
        <Grid item xs={12} md={8}>
          <Card sx={{ 
            backgroundColor: '#1a1a2e', 
            border: '1px solid #2d2d44',
            height: '100%'
          }}>
            <CardContent>
              {selectedTopic ? (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Box>
                      <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                        {selectedTopic.topic}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                        {selectedTopic.description}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="contained"
                        startIcon={<SearchIcon />}
                        onClick={() => handleCollectURLs(selectedTopic)}
                        disabled={collecting}
                        sx={{ backgroundColor: '#1890ff' }}
                      >
                        {collecting ? 'Collecting...' : 'Collect URLs'}
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<AddIcon />}
                        onClick={() => setShowUrlDialog(true)}
                      >
                        Add URL
                      </Button>
                    </Box>
                  </Box>

                  {urlLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                      <CircularProgress />
                    </Box>
                  ) : topicURLs ? (
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                          Collected URLs
                        </Typography>
                        <Badge badgeContent={topicURLs.url_count} color="primary">
                          <LinkIcon sx={{ color: '#1890ff' }} />
                        </Badge>
                      </Box>

                      <Paper sx={{ 
                        backgroundColor: '#0f0f1a', 
                        border: '1px solid #2d2d44',
                        maxHeight: 400,
                        overflow: 'auto'
                      }}>
                        <List>
                          {topicURLs.urls.map((url, index) => (
                            <ListItem
                              key={index}
                              sx={{
                                borderBottom: '1px solid #2d2d44',
                                '&:last-child': { borderBottom: 'none' }
                              }}
                            >
                              <ListItemText
                                primary={
                                  <Link
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    sx={{
                                      color: '#1890ff',
                                      textDecoration: 'none',
                                      '&:hover': { textDecoration: 'underline' }
                                    }}
                                  >
                                    {url}
                                  </Link>
                                }
                              />
                              <ListItemSecondaryAction>
                                <Tooltip title="Open URL">
                                  <IconButton
                                    edge="end"
                                    onClick={() => window.open(url, '_blank')}
                                    sx={{ color: '#1890ff' }}
                                  >
                                    <VisibilityIcon />
                                  </IconButton>
                                </Tooltip>
                              </ListItemSecondaryAction>
                            </ListItem>
                          ))}
                          {topicURLs.urls.length === 0 && (
                            <Box sx={{ p: 3, textAlign: 'center' }}>
                              <Typography variant="body2" sx={{ color: '#888' }}>
                                No URLs collected yet. Click "Collect URLs" to start.
                              </Typography>
                            </Box>
                          )}
                        </List>
                      </Paper>

                      <Typography variant="caption" sx={{ color: '#888', mt: 2, display: 'block' }}>
                        Last updated: {new Date(topicURLs.last_updated).toLocaleString()}
                      </Typography>
                    </Box>
                  ) : (
                    <Alert severity="info">
                      Select a topic to view and manage URLs
                    </Alert>
                  )}
                </Box>
              ) : (
                <Alert severity="info">
                  Select a topic from the list to view and manage URLs
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add URL Dialog */}
      <Dialog open={showUrlDialog} onClose={() => setShowUrlDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: '#e8e8f0', backgroundColor: '#1a1a2e' }}>
          Add Manual URL
        </DialogTitle>
        <DialogContent sx={{ backgroundColor: '#1a1a2e' }}>
          <TextField
            autoFocus
            margin="dense"
            label="URL"
            type="url"
            fullWidth
            variant="outlined"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: '#e8e8f0',
                '& fieldset': { borderColor: '#2d2d44' },
                '&:hover fieldset': { borderColor: '#1890ff' },
                '&.Mui-focused fieldset': { borderColor: '#1890ff' }
              },
              '& .MuiInputLabel-root': { color: '#b8b8cc' }
            }}
          />
        </DialogContent>
        <DialogActions sx={{ backgroundColor: '#1a1a2e' }}>
          <Button onClick={() => setShowUrlDialog(false)} sx={{ color: '#b8b8cc' }}>
            Cancel
          </Button>
          <Button 
            onClick={addManualURL} 
            variant="contained"
            sx={{ backgroundColor: '#1890ff' }}
          >
            Add URL
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default URLsTab;
