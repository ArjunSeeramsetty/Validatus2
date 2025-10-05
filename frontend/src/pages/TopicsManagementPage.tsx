import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Paper,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Topic as TopicIcon,
  Search as SearchIcon,
  Link as LinkIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { enqueueSnackbar } from 'notistack';
import { topicService } from '../services/topicService';

interface TopicConfig {
  session_id: string;
  topic: string;
  description: string;
  search_queries: string[];
  initial_urls: string[];
  analysis_type: string;
  user_id: string;
  created_at: string;
  status: string;
}

const TopicsManagementPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();

  const [topics, setTopics] = useState<TopicConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [selectedTopic, setSelectedTopic] = useState<TopicConfig | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [topicToDelete, setTopicToDelete] = useState<string | null>(null);

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    console.log('Loading topics...');
    setLoading(true);
    setError(null);

    try {
      console.log('Attempting to fetch topics from backend API...');
      const response = await topicService.listTopics(1, 50, 'created_at', 'desc');
      
      console.log('Topics API response:', response);
      
      if (response && response.topics) {
        setTopics(response.topics);
        console.log(`Successfully loaded ${response.topics.length} topics from database`);
        setRetryCount(0); // Reset retry count on success
      } else {
        console.warn('Unexpected API response format:', response);
        setTopics([]);
      }
    } catch (error: any) {
      console.error('Failed to load topics from backend:', error);
      setError(error.message || 'Failed to load topics from server');
      
      // Fallback to localStorage for demo purposes
      try {
        console.log('Attempting fallback to localStorage...');
        const storedTopics = localStorage.getItem('created_topics');
        if (storedTopics) {
          const parsedTopics = JSON.parse(storedTopics);
          setTopics(parsedTopics);
          console.log(`Loaded ${parsedTopics.length} topics from localStorage fallback`);
          setError(null); // Clear error if fallback succeeds
        } else {
          console.log('No topics found in localStorage');
        }
      } catch (localError) {
        console.error('Error loading topics from localStorage:', localError);
        enqueueSnackbar('Error loading topics', { variant: 'error' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    loadTopics();
  };

  const handleViewTopic = (topic: TopicConfig) => {
    setSelectedTopic(topic);
    setDialogOpen(true);
  };

  const handleDeleteTopic = (sessionId: string) => {
    setTopicToDelete(sessionId);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (topicToDelete) {
      try {
        const success = await topicService.deleteTopic(topicToDelete);
        if (success) {
          const updatedTopics = topics.filter(topic => topic.session_id !== topicToDelete);
          setTopics(updatedTopics);
          enqueueSnackbar('Topic deleted successfully', { variant: 'success' });
        } else {
          enqueueSnackbar('Failed to delete topic', { variant: 'error' });
        }
      } catch (error) {
        console.error('Error deleting topic:', error);
        enqueueSnackbar('Error deleting topic', { variant: 'error' });
      }
    }
    setDeleteDialogOpen(false);
    setTopicToDelete(null);
  };

  const handleNavigateToTopic = (topic: TopicConfig) => {
    // Navigate to topic creation/edit page
    navigate('/topic-creation', { state: { editTopic: topic } });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography>Loading topics from database...</Typography>
          {retryCount > 0 && (
            <Typography variant="caption" color="text.secondary">
              Retry attempt: {retryCount}
            </Typography>
          )}
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={handleRetry}>
              Retry
            </Button>
          }
        >
          <Typography variant="h6" gutterBottom>
            Failed to Load Topics
          </Typography>
          <Typography variant="body2">
            {error}
          </Typography>
          {retryCount > 0 && (
            <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
              Retry attempts: {retryCount}
            </Typography>
          )}
        </Alert>
        
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" gutterBottom>
              Debug Information
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Backend URL: {process.env.VITE_API_URL || 'https://validatus-backend-ssivkqhvhq-uc.a.run.app'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Retry Count: {retryCount}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Timestamp: {new Date().toLocaleString()}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button variant="contained" onClick={handleRetry} startIcon={<SearchIcon />}>
                Retry Loading
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => navigate('/topic-creation')}
                startIcon={<AddIcon />}
              >
                Create New Topic
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Topics Management ({topics.length})
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your analysis topics and view their configurations.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<SearchIcon />}
            onClick={loadTopics}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/topic-creation')}
          >
            Create New Topic
          </Button>
        </Box>
      </Box>

      {topics.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <TopicIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Topics Created Yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Create your first analysis topic to get started with strategic analysis.
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/topic-creation')}
            >
              Create Your First Topic
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {topics.map((topic) => (
            <Grid item xs={12} md={6} lg={4} key={topic.session_id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h2" sx={{ flexGrow: 1, mr: 1 }}>
                      {topic.topic}
                    </Typography>
                    <Chip 
                      label={topic.analysis_type} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {topic.description}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <SearchIcon sx={{ fontSize: 16, mr: 0.5 }} />
                      {topic.search_queries.length} search queries
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <LinkIcon sx={{ fontSize: 16, mr: 0.5 }} />
                      {topic.initial_urls.length} initial URLs
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                      <CalendarIcon sx={{ fontSize: 16, mr: 0.5 }} />
                      Created {formatDate(topic.created_at)}
                    </Typography>
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Chip 
                      label={topic.status} 
                      size="small" 
                      color={topic.status === 'created' ? 'success' : 'default'}
                    />
                    <Box>
                      <IconButton
                        size="small"
                        onClick={() => handleViewTopic(topic)}
                        title="View Details"
                      >
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleNavigateToTopic(topic)}
                        title="Analyze Topic"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteTopic(topic.session_id)}
                        title="Delete Topic"
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Topic Details Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>
          Topic Details: {selectedTopic?.topic}
        </DialogTitle>
        <DialogContent>
          {selectedTopic && (
            <Box>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 1 }}>
                Description
              </Typography>
              <Typography variant="body2" sx={{ mb: 3 }}>
                {selectedTopic.description}
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom>
                Analysis Type
              </Typography>
              <Chip label={selectedTopic.analysis_type} color="primary" sx={{ mb: 3 }} />
              
              <Typography variant="subtitle1" gutterBottom>
                Search Queries ({selectedTopic.search_queries.length})
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                {selectedTopic.search_queries.map((query, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                    • {query}
                  </Typography>
                ))}
              </Paper>
              
              <Typography variant="subtitle1" gutterBottom>
                Initial URLs ({selectedTopic.initial_urls.length})
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                {selectedTopic.initial_urls.map((url, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 1, wordBreak: 'break-all' }}>
                    • {url}
                  </Typography>
                ))}
              </Paper>
              
              <Typography variant="subtitle1" gutterBottom>
                Metadata
              </Typography>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Session ID:</strong> {selectedTopic.session_id}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>User ID:</strong> {selectedTopic.user_id}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Created:</strong> {formatDate(selectedTopic.created_at)}
                </Typography>
                <Typography variant="body2">
                  <strong>Status:</strong> {selectedTopic.status}
                </Typography>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              if (selectedTopic) {
                handleNavigateToTopic(selectedTopic);
              }
            }}
          >
            Analyze This Topic
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this topic? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TopicsManagementPage;
