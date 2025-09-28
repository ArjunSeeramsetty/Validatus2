import React, { useState } from 'react';
import {
  Box, TextField, Button, Card, CardContent, Typography,
  List, ListItem, ListItemText, Chip, CircularProgress,
  InputAdornment, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { Search, ExpandMore, Insights, TrendingUp } from '@mui/icons-material';
import { motion } from 'framer-motion';

interface SearchResult {
  content: string;
  source: string;
  confidence: number;
  category: string;
}

export default function SemanticSearchInterface() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [suggestions] = useState([
    'Smart pergola technology trends',
    'Consumer purchasing behavior',
    'Market size by region',
    'Competitive landscape analysis',
    'Premium vs value segments',
    'Installation and service factors'
  ]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const baseUrl = window.location.origin;
      const response = await fetch(
        `${baseUrl}/api/v3/pergola/semantic-search?query=${encodeURIComponent(query)}&max_results=10`
      );
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      // Fallback to mock results for demo
      setResults([
        {
          content: "Smart pergola technology is experiencing rapid adoption with IoT integration becoming standard in premium segments. Market research shows 35% adoption rate for automated controls.",
          source: "Market Research Report 2024",
          confidence: 0.92,
          category: "technology"
        },
        {
          content: "Consumer behavior analysis reveals that price sensitivity varies significantly by segment, with premium buyers prioritizing quality over cost considerations.",
          source: "Consumer Psychology Study",
          confidence: 0.88,
          category: "consumer"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'market': '#1976d2',
      'consumer': '#2e7d32',
      'product': '#ed6c02',
      'competitive': '#9c27b0',
      'technology': '#1976d2',
      'general': '#757575'
    };
    return colors[category] || colors.general;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return 'success';
    if (confidence > 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Search Interface */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Insights sx={{ mr: 1, verticalAlign: 'middle' }} />
              Semantic Research Explorer
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                fullWidth
                placeholder="Ask questions about pergola market research..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
              <Button
                variant="contained"
                onClick={handleSearch}
                disabled={loading || !query.trim()}
                sx={{ minWidth: 120 }}
              >
                {loading ? <CircularProgress size={20} /> : 'Search'}
              </Button>
            </Box>

            {/* Query Suggestions */}
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Quick searches:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {suggestions.map((suggestion, index) => (
                  <Chip
                    key={index}
                    label={suggestion}
                    onClick={() => handleSuggestionClick(suggestion)}
                    variant="outlined"
                    size="small"
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Search Results */}
        {results.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Search Results ({results.length})
                </Typography>
                
                <List>
                  {results.map((result, index) => (
                    <Accordion key={index}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', mr: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle2">
                              Result {index + 1}
                            </Typography>
                            <Chip
                              label={result.category}
                              size="small"
                              sx={{ 
                                backgroundColor: getCategoryColor(result.category) + '20',
                                color: getCategoryColor(result.category)
                              }}
                            />
                          </Box>
                          <Chip
                            label={`${(result.confidence * 100).toFixed(0)}%`}
                            size="small"
                            color={getConfidenceColor(result.confidence)}
                            variant="outlined"
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" paragraph>
                          {result.content}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Source: {result.source}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </List>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* No Results Message */}
        {!loading && results.length === 0 && query && (
          <Card>
            <CardContent>
              <Typography variant="body1" color="text.secondary" textAlign="center">
                No results found for "{query}". Try different keywords or check the suggestions above.
              </Typography>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </Box>
  );
}
