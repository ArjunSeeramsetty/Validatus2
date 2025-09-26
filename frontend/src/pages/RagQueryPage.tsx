import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Alert,
  Autocomplete,
  Paper,
  Link,
  Slider,
  FormControlLabel,
  Switch,
  Divider
} from '@mui/material';
import {
  Search,
  History,
  TuneRounded,
  OpenInNew,
  ContentCopy,
  QueryStats
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';
import { RagQueryService, RagQueryRequest, RagQueryResponse } from '../services/ragQueryService';

const RagQueryPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const [query, setQuery] = useState('');
  const [queryResults, setQueryResults] = useState<RagQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxResults, setMaxResults] = useState(10);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.7);
  const [includeMetadata, setIncludeMetadata] = useState(true);

  useEffect(() => {
    if (topicId) {
      loadQuerySuggestions();
    }
  }, [topicId]);

  const loadQuerySuggestions = async () => {
    try {
      const suggestions = await RagQueryService.getQuerySuggestions(topicId!);
      setSuggestions(suggestions);
    } catch (err) {
      console.warn('Failed to load query suggestions');
    }
  };

  const handleSearch = async () => {
    if (!query.trim() || !topicId) return;

    try {
      setLoading(true);
      setError(null);

      const queryRequest: RagQueryRequest = {
        topic_id: topicId,
        query: query.trim(),
        max_results: maxResults,
        similarity_threshold: similarityThreshold,
        include_metadata: includeMetadata
      };

      const results = await RagQueryService.queryVectorStore(queryRequest);
      setQueryResults(results);

      // Add to query history
      const updatedHistory = [query.trim(), ...queryHistory.filter(h => h !== query.trim())].slice(0, 10);
      setQueryHistory(updatedHistory);

    } catch (err: any) {
      setError(err.message || 'Failed to search knowledge base');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return '#52c41a';
    if (score >= 0.6) return '#fa8c16';
    return '#ff4d4f';
  };

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <QueryStats sx={{ fontSize: 32, color: '#1890ff', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              RAG Query Interface
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: '#b8b8cc', mb: 3 }}>
            Semantic search and knowledge retrieval from your topic's vector store
          </Typography>
          {topicId && (
            <Chip 
              label={`Topic: ${topicId}`}
              sx={{ backgroundColor: '#1890ff20', color: '#1890ff' }}
            />
          )}
        </Box>

        {/* Search Interface */}
        <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', mb: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                fullWidth
                multiline
                minRows={2}
                maxRows={4}
                placeholder="Ask a question about your topic's knowledge base..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#252547',
                    '& fieldset': { borderColor: '#3d3d56' },
                    '&:hover fieldset': { borderColor: '#1890ff' },
                    '&.Mui-focused fieldset': { borderColor: '#1890ff' },
                  },
                  '& .MuiInputBase-input': { color: '#e8e8f0' },
                }}
              />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  disabled={loading || !query.trim()}
                  startIcon={loading ? <CircularProgress size={20} /> : <Search />}
                  sx={{
                    minWidth: 120,
                    background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                    }
                  }}
                >
                  {loading ? 'Searching...' : 'Search'}
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  startIcon={<TuneRounded />}
                  sx={{ color: '#b8b8cc', borderColor: '#3d3d56' }}
                >
                  Advanced
                </Button>
              </Box>
            </Box>

            {/* Advanced Options */}
            {showAdvanced && (
              <Box sx={{ mt: 3, p: 3, backgroundColor: '#252547', borderRadius: 2 }}>
                <Typography variant="subtitle2" sx={{ color: '#e8e8f0', mb: 3 }}>
                  Advanced Search Options
                </Typography>
                <Box sx={{ display: 'flex', gap: 4 }}>
                  <Box sx={{ minWidth: 200 }}>
                    <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Max Results: {maxResults}
                    </Typography>
                    <Slider
                      value={maxResults}
                      onChange={(_, value) => setMaxResults(value as number)}
                      min={5}
                      max={50}
                      step={5}
                      marks={[
                        { value: 5, label: '5' },
                        { value: 25, label: '25' },
                        { value: 50, label: '50' }
                      ]}
                      sx={{ color: '#1890ff' }}
                    />
                  </Box>
                  <Box sx={{ minWidth: 200 }}>
                    <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Similarity Threshold: {similarityThreshold.toFixed(2)}
                    </Typography>
                    <Slider
                      value={similarityThreshold}
                      onChange={(_, value) => setSimilarityThreshold(value as number)}
                      min={0.3}
                      max={1.0}
                      step={0.05}
                      marks={[
                        { value: 0.3, label: '0.3' },
                        { value: 0.7, label: '0.7' },
                        { value: 1.0, label: '1.0' }
                      ]}
                      sx={{ color: '#1890ff' }}
                    />
                  </Box>
                  <Box>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={includeMetadata}
                          onChange={(e) => setIncludeMetadata(e.target.checked)}
                          sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: '#1890ff' } }}
                        />
                      }
                      label="Include Metadata"
                      sx={{ '& .MuiFormControlLabel-label': { color: '#e8e8f0' } }}
                    />
                  </Box>
                </Box>
              </Box>
            )}

            {/* Quick Suggestions */}
            {suggestions.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 2 }}>
                  Quick Questions:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {suggestions.map((suggestion, index) => (
                    <Chip
                      key={index}
                      label={suggestion}
                      onClick={() => handleSuggestionClick(suggestion)}
                      sx={{
                        backgroundColor: '#252547',
                        color: '#e8e8f0',
                        border: '1px solid #3d3d56',
                        '&:hover': {
                          backgroundColor: '#1890ff20',
                          borderColor: '#1890ff'
                        }
                      }}
                    />
                  ))}
                </Box>
              </Box>
            )}

            {/* Query History */}
            {queryHistory.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 2 }}>
                  Recent Queries:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {queryHistory.slice(0, 5).map((historyQuery, index) => (
                    <Chip
                      key={index}
                      icon={<History />}
                      label={historyQuery}
                      size="small"
                      onClick={() => setQuery(historyQuery)}
                      sx={{
                        backgroundColor: '#52c41a20',
                        color: '#52c41a',
                        border: '1px solid #52c41a40',
                        '&:hover': {
                          backgroundColor: '#52c41a30'
                        }
                      }}
                    />
                  ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}

        {/* Search Results */}
        {queryResults && (
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  Search Results
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Chip
                    size="small"
                    label={`${queryResults.total_results} results`}
                    sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
                  />
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    {queryResults.search_time_ms}ms
                  </Typography>
                </Box>
              </Box>

              <List>
                {queryResults.results.map((result, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      backgroundColor: '#252547',
                      mb: 2,
                      borderRadius: 2,
                      border: '1px solid #3d3d56',
                      flexDirection: 'column',
                      alignItems: 'stretch'
                    }}
                  >
                    <Box sx={{ width: '100%', mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ color: '#e8e8f0', fontWeight: 500 }}>
                          {result.metadata.title}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip
                            size="small"
                            label={`${(result.metadata.similarity_score * 100).toFixed(0)}%`}
                            sx={{
                              backgroundColor: `${getSimilarityColor(result.metadata.similarity_score)}20`,
                              color: getSimilarityColor(result.metadata.similarity_score)
                            }}
                          />
                          <Button
                            size="small"
                            onClick={() => copyToClipboard(result.content)}
                            startIcon={<ContentCopy />}
                            sx={{ color: '#b8b8cc', minWidth: 'auto', px: 1 }}
                          />
                        </Box>
                      </Box>
                      
                      <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2, lineHeight: 1.6 }}>
                        {result.content}
                      </Typography>

                      <Divider sx={{ backgroundColor: '#3d3d56', mb: 2 }} />

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Link
                          href={result.metadata.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          sx={{
                            color: '#1890ff',
                            textDecoration: 'none',
                            display: 'flex',
                            alignItems: 'center',
                            '&:hover': { textDecoration: 'underline' }
                          }}
                        >
                          {result.metadata.source_url}
                          <OpenInNew sx={{ fontSize: 16, ml: 0.5 }} />
                        </Link>
                        <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                          {new Date(result.metadata.scraped_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        )}

        {queryResults && queryResults.results.length === 0 && (
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', textAlign: 'center', p: 4 }}>
            <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 2 }}>
              No results found
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              Try adjusting your search terms or lowering the similarity threshold
            </Typography>
          </Card>
        )}
      </motion.div>
    </Box>
  );
};

export default RagQueryPage;
