/**
 * Content Tab Component - Displays scraped content and manages scraping
 * 🆕 NEW COMPONENT: Integrates with existing backend content services
 */
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
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Badge
} from '@mui/material';
import {
  CloudDownload,
  Refresh,
  PlayArrow,
  CheckCircle,
  Error,
  Warning,
  Link as LinkIcon,
  Visibility,
  Assessment,
  Timeline
} from '@mui/icons-material';
import { apiClient } from '../services/apiClient';
import { topicService } from '../services/topicService';

interface ContentItem {
  url: string;
  title: string;
  description: string;
  content_preview: string;
  domain: string;
  status: string;
  relevance_score: number;
  quality_score: number;
  priority_level: number;
  source: string;
  collection_method: string;
  created_at: string;
  word_count: number;
  content_length: number;
  metadata: any;
}

const ContentTab: React.FC = () => {
  const [topics, setTopics] = useState<any[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<any>(null);
  const [contentData, setContentData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [contentLoading, setContentLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null);
  const [showContentDialog, setShowContentDialog] = useState(false);

  useEffect(() => {
    loadTopics();
  }, []);

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

  const loadTopicContent = async (topic: any) => {
    try {
      setContentLoading(true);
      setError(null);
      
      // ✅ USING NEW API: /api/v3/content/{session_id}
      const response = await apiClient.get(`/api/v3/content/${topic.session_id}`);
      setContentData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load content');
    } finally {
      setContentLoading(false);
    }
  };

  const handleTopicSelect = (topic: any) => {
    setSelectedTopic(topic);
    loadTopicContent(topic);
  };

  const startScraping = async (forceRefresh: boolean = false) => {
    if (!selectedTopic) return;
    
    try {
      setScraping(true);
      setError(null);
      
      // ✅ USING NEW API: /api/v3/content/{session_id}/scrape
      const response = await apiClient.post(
        `/api/v3/content/${selectedTopic.session_id}/scrape?force_refresh=${forceRefresh}`
      );
      
      if (response.data.success) {
        // Reload content after scraping starts
        setTimeout(() => loadTopicContent(selectedTopic), 2000);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start scraping');
    } finally {
      setScraping(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scraped':
      case 'completed':
        return 'success';
      case 'processing':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.7) return 'success';
    if (score >= 0.4) return 'warning';
    return 'error';
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ color: '#e8e8f0', mb: 1, display: 'flex', alignItems: 'center' }}>
          <CloudDownload sx={{ mr: 1 }} />
          Content Management
        </Typography>
        <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
          View and manage scraped content from collected URLs. Monitor quality metrics and scraping status.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Topic Selection */}
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d44' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  Topics ({topics.length})
                </Typography>
                <IconButton size="small" onClick={loadTopics} disabled={loading}>
                  <Refresh sx={{ color: '#1890ff' }} />
                </IconButton>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <List sx={{ maxHeight: 500, overflow: 'auto' }}>
                  {topics.map((topic) => (
                    <ListItem
                      key={topic.session_id}
                      button
                      selected={selectedTopic?.session_id === topic.session_id}
                      onClick={() => handleTopicSelect(topic)}
                      sx={{
                        borderRadius: 1,
                        mb: 1,
                        backgroundColor: selectedTopic?.session_id === topic.session_id ? '#2d2d44' : 'transparent',
                        '&:hover': { backgroundColor: '#2d2d44' }
                      }}
                    >
                      <ListItemText
                        primary={
                          <Typography variant="body1" sx={{ color: '#e8e8f0' }}>
                            {topic.topic}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              {topic.description?.substring(0, 80)}...
                            </Typography>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Chip
                          label={topic.status}
                          size="small"
                          color={topic.status === 'completed' ? 'success' : 'default'}
                          variant="outlined"
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Content Display */}
        <Grid item xs={12} md={8}>
          {selectedTopic ? (
            <Box>
              <Card sx={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d44', mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
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
                        variant="outlined"
                        startIcon={<Refresh />}
                        onClick={() => loadTopicContent(selectedTopic)}
                        disabled={contentLoading}
                        sx={{ borderColor: '#1890ff', color: '#1890ff' }}
                      >
                        Refresh
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={scraping ? <CircularProgress size={16} /> : <PlayArrow />}
                        onClick={() => startScraping(false)}
                        disabled={scraping || contentLoading}
                        sx={{ backgroundColor: '#1890ff' }}
                      >
                        {scraping ? 'Scraping...' : 'Start Scraping'}
                      </Button>
                    </Box>
                  </Box>

                  {contentLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                      <CircularProgress />
                    </Box>
                  ) : contentData ? (
                    <Box>
                      {/* Statistics Cards */}
                      <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={6} sm={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#0f0f1a' }}>
                            <Typography variant="h4" sx={{ color: '#1890ff' }}>
                              {contentData.statistics?.total_items || 0}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              Total URLs
                            </Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#0f0f1a' }}>
                            <Typography variant="h4" sx={{ color: '#52c41a' }}>
                              {formatNumber(contentData.statistics?.total_words || 0)}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              Total Words
                            </Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#0f0f1a' }}>
                            <Typography variant="h4" sx={{ color: '#fa8c16' }}>
                              {((contentData.statistics?.average_quality_score || 0) * 100).toFixed(0)}%
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              Avg Quality
                            </Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#0f0f1a' }}>
                            <Typography variant="h4" sx={{ color: '#eb2f96' }}>
                              {Object.keys(contentData.statistics?.status_breakdown || {}).length}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              Status Types
                            </Typography>
                          </Paper>
                        </Grid>
                      </Grid>

                      {/* Content Table */}
                      <TableContainer component={Paper} sx={{ backgroundColor: '#0f0f1a', maxHeight: 500 }}>
                        <Table stickyHeader size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell sx={{ backgroundColor: '#1a1a2e', color: '#e8e8f0' }}>Status</TableCell>
                              <TableCell sx={{ backgroundColor: '#1a1a2e', color: '#e8e8f0' }}>Title</TableCell>
                              <TableCell sx={{ backgroundColor: '#1a1a2e', color: '#e8e8f0' }}>Domain</TableCell>
                              <TableCell sx={{ backgroundColor: '#1a1a2e', color: '#e8e8f0' }}>Quality</TableCell>
                              <TableCell sx={{ backgroundColor: '#1a1a2e', color: '#e8e8f0' }}>Words</TableCell>
                              <TableCell sx={{ backgroundColor: '#1a1a2e', color: '#e8e8f0' }}>Actions</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {contentData.content_items?.map((item: ContentItem, index: number) => (
                              <TableRow key={index} sx={{ '&:hover': { backgroundColor: '#2d2d44' } }}>
                                <TableCell>
                                  <Chip
                                    size="small"
                                    label={item.status}
                                    color={getStatusColor(item.status) as any}
                                    variant="outlined"
                                  />
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2" noWrap sx={{ maxWidth: 250, color: '#e8e8f0' }}>
                                    {item.title}
                                  </Typography>
                                  <Typography variant="caption" sx={{ color: '#888' }}>
                                    {item.source} • {item.collection_method}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                                    {item.domain}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Tooltip title={`Relevance: ${(item.relevance_score * 100).toFixed(0)}%`}>
                                    <Chip
                                      label={`${(item.quality_score * 100).toFixed(0)}%`}
                                      size="small"
                                      color={getQualityColor(item.quality_score) as any}
                                      variant="filled"
                                    />
                                  </Tooltip>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                                    {formatNumber(item.word_count)}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <IconButton
                                    size="small"
                                    onClick={() => {
                                      setSelectedContent(item);
                                      setShowContentDialog(true);
                                    }}
                                    sx={{ color: '#1890ff' }}
                                  >
                                    <Visibility fontSize="small" />
                                  </IconButton>
                                  <IconButton
                                    size="small"
                                    onClick={() => window.open(item.url, '_blank')}
                                    sx={{ color: '#52c41a' }}
                                  >
                                    <LinkIcon fontSize="small" />
                                  </IconButton>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>

                      {contentData.content_items?.length === 0 && (
                        <Box sx={{ textAlign: 'center', py: 4 }}>
                          <Typography variant="body1" sx={{ color: '#888' }}>
                            No content items found. Collect some URLs first.
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  ) : (
                    <Typography variant="body1" sx={{ color: '#888', textAlign: 'center', py: 3 }}>
                      Select a topic to view its content
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Box>
          ) : (
            <Card sx={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d44' }}>
              <CardContent>
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <CloudDownload sx={{ fontSize: 64, color: '#888', mb: 2 }} />
                  <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 1 }}>
                    No Topic Selected
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888' }}>
                    Select a topic from the left panel to view and manage its content
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Content Preview Dialog */}
      <Dialog
        open={showContentDialog}
        onClose={() => setShowContentDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { backgroundColor: '#1a1a2e', color: '#e8e8f0' } }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid #2d2d44' }}>
          Content Preview
        </DialogTitle>
        <DialogContent>
          {selectedContent && (
            <Box sx={{ pt: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#e8e8f0' }}>
                {selectedContent.title}
              </Typography>
              <Typography variant="caption" sx={{ color: '#888', display: 'block', mb: 2 }}>
                {selectedContent.url}
              </Typography>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Words</Typography>
                  <Typography variant="body1" sx={{ color: '#e8e8f0' }}>
                    {formatNumber(selectedContent.word_count)}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Quality</Typography>
                  <Typography variant="body1" sx={{ color: '#e8e8f0' }}>
                    {(selectedContent.quality_score * 100).toFixed(1)}%
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Status</Typography>
                  <Chip
                    label={selectedContent.status}
                    size="small"
                    color={getStatusColor(selectedContent.status) as any}
                  />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>Priority</Typography>
                  <Typography variant="body1" sx={{ color: '#e8e8f0' }}>
                    {selectedContent.priority_level}/10
                  </Typography>
                </Grid>
              </Grid>

              <Typography variant="subtitle2" gutterBottom sx={{ color: '#e8e8f0' }}>
                Content Preview:
              </Typography>
              <Paper sx={{ p: 2, backgroundColor: '#0f0f1a', maxHeight: 300, overflow: 'auto' }}>
                <Typography variant="body2" sx={{ color: '#b8b8cc', whiteSpace: 'pre-wrap' }}>
                  {selectedContent.content_preview || selectedContent.description}
                </Typography>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid #2d2d44' }}>
          <Button onClick={() => setShowContentDialog(false)} sx={{ color: '#b8b8cc' }}>
            Close
          </Button>
          {selectedContent && (
            <Button
              onClick={() => window.open(selectedContent.url, '_blank')}
              variant="contained"
              sx={{ backgroundColor: '#1890ff' }}
            >
              Open Source
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ContentTab;
