import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayArrowIcon,
  Topic as TopicIcon,
  Description as DescriptionIcon,
  Search as SearchIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { enqueueSnackbar } from 'notistack';
import { topicService, TopicCreateRequest, TopicUpdateRequest } from '../services/topicService';

interface TopicData {
  topic: string;
  description: string;
  searchQueries: string[];
  initialUrls: string[];
  analysisType: 'pergola' | 'general' | 'custom';
}

// Map frontend analysis types to backend types
const mapAnalysisType = (frontendType: 'pergola' | 'general' | 'custom'): 'standard' | 'comprehensive' => {
  switch (frontendType) {
    case 'pergola':
      return 'comprehensive';
    case 'general':
      return 'standard';
    case 'custom':
      return 'standard';
    default:
      throw new Error(`Unexpected analysis type: ${frontendType}`);
  }
};

// Get current user ID from authentication context
const getCurrentUserId = (): string => {
  // TODO: Replace with actual authentication context
  // For now, return a demo user ID
  return 'demo_user_123';
};

const TopicCreationPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editingTopicId, setEditingTopicId] = useState<string | null>(null);

  const [topicData, setTopicData] = useState<TopicData>({
    topic: '',
    description: '',
    searchQueries: [''],
    initialUrls: [''],
    analysisType: 'pergola'
  });

  const [newQuery, setNewQuery] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'query' | 'url'>('query');

  // Handle edit mode
  useEffect(() => {
    if (location.state?.editTopic) {
      const editTopic = location.state.editTopic;
      setIsEditing(true);
      setEditingTopicId(editTopic.session_id);
      setTopicData({
        topic: editTopic.topic,
        description: editTopic.description,
        searchQueries: editTopic.search_queries,
        initialUrls: editTopic.initial_urls,
        analysisType: editTopic.analysis_type
      });
    }
  }, [location.state]);

  const pergolaPresets = {
    topic: 'Pergola Market Strategic Analysis',
    description: 'Comprehensive analysis of global pergola market trends, opportunities, and competitive landscape for strategic decision making.',
    searchQueries: [
      'pergola market size forecast 2024 2025',
      'outdoor living space trends growth',
      'bioclimatic pergola industry analysis',
      'commercial pergola hospitality applications',
      'pergola sustainability eco-friendly materials',
      'smart pergola technology integration',
      'pergola market regional analysis',
      'pergola competitive landscape analysis'
    ],
    initialUrls: [
      'https://www.verifiedmarketresearch.com/product/pergolas-market/',
      'https://www.fortunebusinessinsights.com/bioclimatic-pergola-market-112455',
      'https://www.zionmarketresearch.com/report/pergolas-market',
      'https://www.cognitivemarketresearch.com/pergolas-market-report',
      'https://www.grandviewresearch.com/industry-analysis/north-america-pergola-kits-market-report'
    ]
  };

  const handleInputChange = (field: keyof TopicData, value: any) => {
    setTopicData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
  };

  const handlePresetLoad = (preset: 'pergola') => {
    if (preset === 'pergola') {
      setTopicData(prev => ({
        ...prev,
        ...pergolaPresets,
        analysisType: 'pergola'
      }));
      enqueueSnackbar('Pergola preset loaded successfully', { variant: 'success' });
    }
  };

  const handleAddQuery = () => {
    setNewQuery('');
    setDialogType('query');
    setDialogOpen(true);
  };

  const handleAddUrl = () => {
    setNewUrl('');
    setDialogType('url');
    setDialogOpen(true);
  };

  const handleConfirmAdd = () => {
    if (dialogType === 'query' && newQuery.trim()) {
      setTopicData(prev => ({
        ...prev,
        searchQueries: [...prev.searchQueries.filter(q => q.trim()), newQuery.trim()]
      }));
      enqueueSnackbar('Search query added', { variant: 'success' });
    } else if (dialogType === 'url' && newUrl.trim()) {
      setTopicData(prev => ({
        ...prev,
        initialUrls: [...prev.initialUrls.filter(u => u.trim()), newUrl.trim()]
      }));
      enqueueSnackbar('Initial URL added', { variant: 'success' });
    }
    setDialogOpen(false);
  };

  const handleRemoveQuery = (index: number) => {
    setTopicData(prev => ({
      ...prev,
      searchQueries: prev.searchQueries.filter((_, i) => i !== index)
    }));
  };

  const handleRemoveUrl = (index: number) => {
    setTopicData(prev => ({
      ...prev,
      initialUrls: prev.initialUrls.filter((_, i) => i !== index)
    }));
  };

  const handleNext = () => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleCreateTopic = async () => {
    setLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!topicData.topic.trim()) {
        throw new Error('Topic name is required');
      }
      if (!topicData.description.trim()) {
        throw new Error('Topic description is required');
      }
      if (topicData.searchQueries.filter(q => q.trim()).length === 0) {
        throw new Error('At least one search query is required');
      }

      let createdTopic;
      
      if (isEditing && editingTopicId) {
        // Update existing topic
        const updateRequest: TopicUpdateRequest = {
          topic: topicData.topic.trim(),
          description: topicData.description.trim(),
          search_queries: topicData.searchQueries.filter(q => q.trim()),
          initial_urls: topicData.initialUrls.filter(u => u.trim()),
          analysis_type: mapAnalysisType(topicData.analysisType),
          status: 'created'
        };
        
        createdTopic = await topicService.updateTopic(editingTopicId, updateRequest);
        
        if (!createdTopic) {
          throw new Error('Topic not found or failed to update');
        }
        
        enqueueSnackbar('Topic updated successfully!', { variant: 'success' });
      } else {
        // Create new topic
        const createRequest: TopicCreateRequest = {
          topic: topicData.topic.trim(),
          description: topicData.description.trim(),
          search_queries: topicData.searchQueries.filter(q => q.trim()),
          initial_urls: topicData.initialUrls.filter(u => u.trim()),
          analysis_type: mapAnalysisType(topicData.analysisType),
          user_id: getCurrentUserId()
        };
        
        createdTopic = await topicService.createTopic(createRequest);
        enqueueSnackbar('Topic created successfully!', { variant: 'success' });
      }
      
      setSessionId(createdTopic.session_id);
      setSuccess(true);
      
      // Auto-navigate to dashboard after 3 seconds
      setTimeout(() => {
        navigate('/');
      }, 3000);

    } catch (err: any) {
      setError(err.message || `Failed to ${isEditing ? 'update' : 'create'} topic`);
      enqueueSnackbar(err.message || `Failed to ${isEditing ? 'update' : 'create'} topic`, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      label: 'Topic Information',
      description: 'Define your analysis topic and description'
    },
    {
      label: 'Search Configuration',
      description: 'Configure search queries and initial URLs'
    },
    {
      label: 'Review & Create',
      description: 'Review your configuration and create the topic'
    }
  ];

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Topic Name"
                value={topicData.topic}
                onChange={(e) => handleInputChange('topic', e.target.value)}
                placeholder="e.g., Pergola Market Strategic Analysis"
                variant="outlined"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={topicData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe the scope and objectives of your analysis..."
                multiline
                rows={4}
                variant="outlined"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Analysis Type</InputLabel>
                <Select
                  value={topicData.analysisType}
                  onChange={(e) => handleInputChange('analysisType', e.target.value)}
                  label="Analysis Type"
                >
                  <MenuItem value="pergola">Pergola Market Analysis</MenuItem>
                  <MenuItem value="general">General Market Analysis</MenuItem>
                  <MenuItem value="custom">Custom Analysis</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {topicData.analysisType === 'pergola' && (
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  startIcon={<TopicIcon />}
                  onClick={() => handlePresetLoad('pergola')}
                  fullWidth
                >
                  Load Pergola Preset
                </Button>
              </Grid>
            )}
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Search Queries</Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={handleAddQuery}
                >
                  Add Query
                </Button>
              </Box>
              <Paper variant="outlined" sx={{ maxHeight: 200, overflow: 'auto' }}>
                <List dense>
                  {topicData.searchQueries.filter(q => q.trim()).map((query, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={query} />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => handleRemoveQuery(index)}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Initial URLs (Optional)</Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={handleAddUrl}
                >
                  Add URL
                </Button>
              </Box>
              <Paper variant="outlined" sx={{ maxHeight: 200, overflow: 'auto' }}>
                <List dense>
                  {topicData.initialUrls.filter(u => u.trim()).map((url, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={url} />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => handleRemoveUrl(index)}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Topic Configuration Summary
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="primary">Topic Name:</Typography>
                    <Typography variant="body1">{topicData.topic}</Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="primary">Description:</Typography>
                    <Typography variant="body2">{topicData.description}</Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="primary">Analysis Type:</Typography>
                    <Chip label={topicData.analysisType} color="primary" size="small" />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="primary">
                      Search Queries ({topicData.searchQueries.filter(q => q.trim()).length}):
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {topicData.searchQueries.filter(q => q.trim()).map((query, index) => (
                        <Chip
                          key={index}
                          label={query}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="primary">
                      Initial URLs ({topicData.initialUrls.filter(u => u.trim()).length}):
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {topicData.initialUrls.filter(u => u.trim()).map((url, index) => (
                        <Chip
                          key={index}
                          label={url.length > 50 ? url.substring(0, 50) + '...' : url}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  if (success) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Box sx={{ textAlign: 'center' }}>
          <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom color="success.main">
            {isEditing ? 'Topic Updated Successfully!' : 'Topic Created Successfully!'}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Your topic "{topicData.topic}" has been {isEditing ? 'updated' : 'created'} and is ready for analysis.
          </Typography>
          {sessionId && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Session ID: {sessionId}
            </Typography>
          )}
          <Typography variant="body2" color="text.secondary">
            Redirecting to dashboard...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          {isEditing ? 'Edit Analysis Topic' : 'Create New Analysis Topic'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isEditing 
            ? 'Update your strategic analysis topic configuration, search queries, and initial data sources.'
            : 'Set up a new strategic analysis topic by defining your research scope, search queries, and initial data sources.'
          }
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Stepper activeStep={activeStep} orientation={isMobile ? 'vertical' : 'horizontal'}>
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel>{step.label}</StepLabel>
                {isMobile && (
                  <StepContent>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {step.description}
                    </Typography>
                    {renderStepContent(index)}
                    <Box sx={{ mb: 2, mt: 2 }}>
                      <div>
                        <Button
                          variant="contained"
                          onClick={index === steps.length - 1 ? handleCreateTopic : handleNext}
                          sx={{ mt: 1, mr: 1 }}
                          disabled={loading}
                          startIcon={loading ? <CircularProgress size={20} /> : index === steps.length - 1 ? <SaveIcon /> : undefined}
                        >
                          {loading ? (isEditing ? 'Updating...' : 'Creating...') : index === steps.length - 1 ? (isEditing ? 'Update Topic' : 'Create Topic') : 'Continue'}
                        </Button>
                        <Button
                          disabled={index === 0 || loading}
                          onClick={handleBack}
                          sx={{ mt: 1, mr: 1 }}
                        >
                          Back
                        </Button>
                      </div>
                    </Box>
                  </StepContent>
                )}
              </Step>
            ))}
          </Stepper>

          {!isMobile && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {steps[activeStep].description}
              </Typography>
              {renderStepContent(activeStep)}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
                <Button
                  disabled={activeStep === 0 || loading}
                  onClick={handleBack}
                >
                  Back
                </Button>
                <Button
                  variant="contained"
                  onClick={activeStep === steps.length - 1 ? handleCreateTopic : handleNext}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : activeStep === steps.length - 1 ? <SaveIcon /> : <PlayArrowIcon />}
                >
                  {loading ? (isEditing ? 'Updating...' : 'Creating...') : activeStep === steps.length - 1 ? (isEditing ? 'Update Topic' : 'Create Topic') : 'Continue'}
                </Button>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Add Item Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Add {dialogType === 'query' ? 'Search Query' : 'Initial URL'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label={dialogType === 'query' ? 'Search Query' : 'URL'}
            placeholder={dialogType === 'query' ? 'Enter your search query...' : 'https://example.com'}
            value={dialogType === 'query' ? newQuery : newUrl}
            onChange={(e) => dialogType === 'query' ? setNewQuery(e.target.value) : setNewUrl(e.target.value)}
            sx={{ mt: 1 }}
            multiline={dialogType === 'query'}
            rows={dialogType === 'query' ? 2 : 1}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmAdd} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TopicCreationPage;
