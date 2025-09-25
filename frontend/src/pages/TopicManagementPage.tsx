import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert
} from '@mui/material';
import {
  Add,
  Topic,
  Link,
  CheckCircle,
  Schedule,
  Error,
  Edit,
  Delete,
  Refresh
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTopics } from '../hooks/useAnalysisData';
import { useAuth } from '../contexts/AuthContext';

const TopicManagementPage: React.FC = () => {
  const { topics, loading, error, refetch, createTopic } = useTopics();
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [newTopic, setNewTopic] = useState({
    name: '',
    description: '',
    urls: [''],
    searchQueries: ['']
  });
  const [creating, setCreating] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  const handleAddUrl = () => {
    setNewTopic(prev => ({
      ...prev,
      urls: [...prev.urls, '']
    }));
  };

  const handleUrlChange = (index: number, value: string) => {
    setNewTopic(prev => ({
      ...prev,
      urls: prev.urls.map((url, i) => i === index ? value : url)
    }));
  };

  const handleRemoveUrl = (index: number) => {
    setNewTopic(prev => ({
      ...prev,
      urls: prev.urls.filter((_, i) => i !== index)
    }));
  };

  const handleAddSearchQuery = () => {
    setNewTopic(prev => ({
      ...prev,
      searchQueries: [...prev.searchQueries, '']
    }));
  };

  const handleSearchQueryChange = (index: number, value: string) => {
    setNewTopic(prev => ({
      ...prev,
      searchQueries: prev.searchQueries.map((query, i) => i === index ? value : query)
    }));
  };

  const handleRemoveSearchQuery = (index: number) => {
    setNewTopic(prev => ({
      ...prev,
      searchQueries: prev.searchQueries.filter((_, i) => i !== index)
    }));
  };

  const handleCreateTopic = async () => {
    if (!newTopic.name.trim()) {
      setAlert({ type: 'error', message: 'Topic name is required' });
      return;
    }

    const validUrls = newTopic.urls.filter(url => url.trim());
    if (validUrls.length === 0) {
      setAlert({ type: 'error', message: 'At least one URL is required' });
      return;
    }

    try {
      setCreating(true);
      const validSearchQueries = newTopic.searchQueries.filter(query => query.trim());
      
      await createTopic(
        newTopic.name.trim(),
        validUrls,
        validSearchQueries.length > 0 ? validSearchQueries : undefined
      );

      setAlert({ type: 'success', message: `Topic "${newTopic.name}" created successfully!` });
      setOpen(false);
      setNewTopic({
        name: '',
        description: '',
        urls: [''],
        searchQueries: ['']
      });
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message });
    } finally {
      setCreating(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle sx={{ color: '#52c41a' }} />;
      case 'processing': return <Schedule sx={{ color: '#fa8c16' }} />;
      case 'inactive': return <Error sx={{ color: '#ff4d4f' }} />;
      default: return <Topic sx={{ color: '#8c8ca0' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#52c41a';
      case 'processing': return '#fa8c16';
      case 'inactive': return '#ff4d4f';
      default: return '#8c8ca0';
    }
  };

  if (loading && topics.length === 0) {
    return (
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <LinearProgress sx={{ mb: 2, width: 300 }} />
          <Typography sx={{ color: '#b8b8cc' }}>Loading topics...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0f0f23' }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 1 }}>
              Topic Management
            </Typography>
            <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
              Create and manage analysis topics for strategic insights
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={refetch}
              disabled={loading}
              sx={{
                borderColor: '#1890ff',
                color: '#1890ff',
                '&:hover': { borderColor: '#40a9ff', backgroundColor: '#1890ff20' }
              }}
            >
              Refresh
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpen(true)}
              sx={{
                background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                }
              }}
            >
              Create Topic
            </Button>
          </Box>
        </Box>

        {/* Alert */}
        {alert && (
          <Alert 
            severity={alert.type} 
            onClose={() => setAlert(null)}
            sx={{ mb: 3 }}
          >
            {alert.message}
          </Alert>
        )}

        {/* Topics Grid */}
        <Grid container spacing={3}>
          {topics.map((topic, index) => (
            <Grid item xs={12} md={6} lg={4} key={topic.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card sx={{
                  background: '#1a1a35',
                  border: '1px solid #3d3d56',
                  borderRadius: 2,
                  height: '100%',
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 32px rgba(24, 144, 255, 0.1)'
                  }
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(topic.status)}
                        <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                          {topic.name}
                        </Typography>
                      </Box>
                      <Chip
                        label={topic.status}
                        size="small"
                        sx={{
                          backgroundColor: `${getStatusColor(topic.status)}20`,
                          color: getStatusColor(topic.status),
                          textTransform: 'capitalize',
                          fontWeight: 500
                        }}
                      />
                    </Box>

                    <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 3, lineHeight: 1.6 }}>
                      {topic.description}
                    </Typography>

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                          URLs: {topic.url_count}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                          Knowledge: {topic.knowledge_count}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                          Created: {new Date(topic.created_at).toLocaleDateString()}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton size="small" sx={{ color: '#1890ff' }}>
                            <Edit fontSize="small" />
                          </IconButton>
                          <IconButton size="small" sx={{ color: '#ff4d4f' }}>
                            <Delete fontSize="small" />
                          </IconButton>
                        </Box>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Empty State */}
        {topics.length === 0 && !loading && (
          <Box sx={{ textAlign: 'center', mt: 8 }}>
            <Topic sx={{ fontSize: 64, color: '#3d3d56', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 2 }}>
              No topics created yet
            </Typography>
            <Typography variant="body2" sx={{ color: '#8c8ca0', mb: 4 }}>
              Create your first topic to start strategic analysis
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpen(true)}
              sx={{
                background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                }
              }}
            >
              Create First Topic
            </Button>
          </Box>
        )}
      </motion.div>

      {/* Create Topic Dialog */}
      <Dialog 
        open={open} 
        onClose={() => setOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: '#1a1a35',
            border: '1px solid #3d3d56'
          }
        }}
      >
        <DialogTitle sx={{ color: '#e8e8f0' }}>
          Create New Topic
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            <TextField
              label="Topic Name"
              value={newTopic.name}
              onChange={(e) => setNewTopic(prev => ({ ...prev, name: e.target.value }))}
              fullWidth
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#252547',
                  '& fieldset': { borderColor: '#3d3d56' },
                  '&:hover fieldset': { borderColor: '#1890ff' },
                  '&.Mui-focused fieldset': { borderColor: '#1890ff' },
                },
                '& .MuiInputLabel-root': { color: '#b8b8cc' },
                '& .MuiInputBase-input': { color: '#e8e8f0' },
              }}
            />

            <TextField
              label="Description (Optional)"
              value={newTopic.description}
              onChange={(e) => setNewTopic(prev => ({ ...prev, description: e.target.value }))}
              fullWidth
              multiline
              rows={2}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#252547',
                  '& fieldset': { borderColor: '#3d3d56' },
                  '&:hover fieldset': { borderColor: '#1890ff' },
                  '&.Mui-focused fieldset': { borderColor: '#1890ff' },
                },
                '& .MuiInputLabel-root': { color: '#b8b8cc' },
                '& .MuiInputBase-input': { color: '#e8e8f0' },
              }}
            />

            {/* URLs */}
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  URLs
                </Typography>
                <Button size="small" onClick={handleAddUrl} startIcon={<Add />}>
                  Add URL
                </Button>
              </Box>
              {newTopic.urls.map((url, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <TextField
                    label={`URL ${index + 1}`}
                    value={url}
                    onChange={(e) => handleUrlChange(index, e.target.value)}
                    fullWidth
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#252547',
                        '& fieldset': { borderColor: '#3d3d56' },
                        '&:hover fieldset': { borderColor: '#1890ff' },
                        '&.Mui-focused fieldset': { borderColor: '#1890ff' },
                      },
                      '& .MuiInputLabel-root': { color: '#b8b8cc' },
                      '& .MuiInputBase-input': { color: '#e8e8f0' },
                    }}
                  />
                  {newTopic.urls.length > 1 && (
                    <IconButton onClick={() => handleRemoveUrl(index)} sx={{ color: '#ff4d4f' }}>
                      <Delete />
                    </IconButton>
                  )}
                </Box>
              ))}
            </Box>

            {/* Search Queries */}
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  Search Queries (Optional)
                </Typography>
                <Button size="small" onClick={handleAddSearchQuery} startIcon={<Add />}>
                  Add Query
                </Button>
              </Box>
              {newTopic.searchQueries.map((query, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <TextField
                    label={`Query ${index + 1}`}
                    value={query}
                    onChange={(e) => handleSearchQueryChange(index, e.target.value)}
                    fullWidth
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#252547',
                        '& fieldset': { borderColor: '#3d3d56' },
                        '&:hover fieldset': { borderColor: '#1890ff' },
                        '&.Mui-focused fieldset': { borderColor: '#1890ff' },
                      },
                      '& .MuiInputLabel-root': { color: '#b8b8cc' },
                      '& .MuiInputBase-input': { color: '#e8e8f0' },
                    }}
                  />
                  {newTopic.searchQueries.length > 1 && (
                    <IconButton onClick={() => handleRemoveSearchQuery(index)} sx={{ color: '#ff4d4f' }}>
                      <Delete />
                    </IconButton>
                  )}
                </Box>
              ))}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} sx={{ color: '#b8b8cc' }}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateTopic}
            variant="contained"
            disabled={creating}
            sx={{
              background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
              }
            }}
          >
            {creating ? 'Creating...' : 'Create Topic'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TopicManagementPage;