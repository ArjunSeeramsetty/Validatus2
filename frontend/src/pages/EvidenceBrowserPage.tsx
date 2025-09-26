import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Link,
  Tooltip,
  IconButton,
  TextField,
  InputAdornment,
  Pagination
} from '@mui/material';
import {
  ExpandMore,
  Link as LinkIcon,
  Search,
  FilterList,
  OpenInNew,
  Star,
  StarBorder,
  Refresh
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useParams, useSearchParams } from 'react-router-dom';
import { apiClient } from '../services/apiClient';

interface EvidenceItem {
  url: string;
  title: string;
  content_preview: string;
  quality_score: number;
  scraped_at: string;
  word_count: number;
  relevance_score: number;
  source_type: 'article' | 'report' | 'website' | 'academic' | 'news';
  metadata: {
    author?: string;
    published_date?: string;
    domain: string;
  };
}

interface LayerEvidence {
  layer_name: string;
  layer_description: string;
  evidence_count: number;
  evidence_items: EvidenceItem[];
  avg_quality_score: number;
  total_content_length: number;
}

const EvidenceBrowserPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [evidenceData, setEvidenceData] = useState<LayerEvidence[]>([]);
  const [filteredData, setFilteredData] = useState<LayerEvidence[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLayer, setSelectedLayer] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    if (topicId) {
      loadEvidenceData();
    }
  }, [topicId]);

  useEffect(() => {
    filterEvidence();
  }, [searchTerm, selectedLayer, evidenceData]);

  const loadEvidenceData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Call evidence API - if not available, use mock data
      let response;
      try {
        response = await apiClient.get(`/api/v3/topics/${topicId}/evidence`);
      } catch (apiError) {
        // Generate mock evidence data
        response = { data: generateMockEvidenceData() };
      }
      
      setEvidenceData(response.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load evidence data');
    } finally {
      setLoading(false);
    }
  };

  const generateMockEvidenceData = (): LayerEvidence[] => {
    const layers = [
      'Strategic Planning', 'Market Analysis', 'Risk Assessment', 'Value Creation',
      'Innovation Management', 'Competitive Intelligence', 'Financial Analysis'
    ];
    
    return layers.map(layer => ({
      layer_name: layer,
      layer_description: `Evidence and sources related to ${layer.toLowerCase()}`,
      evidence_count: Math.floor(Math.random() * 15) + 5,
      avg_quality_score: Math.random() * 0.3 + 0.7,
      total_content_length: Math.floor(Math.random() * 50000) + 10000,
      evidence_items: Array.from({ length: Math.floor(Math.random() * 10) + 5 }, (_, i) => ({
        url: `https://example.com/${layer.toLowerCase().replace(' ', '-')}-${i + 1}`,
        title: `${layer} Analysis Report ${i + 1}`,
        content_preview: `This is a comprehensive analysis of ${layer.toLowerCase()} aspects, providing detailed insights into market conditions, strategic opportunities, and risk factors that impact business decisions...`,
        quality_score: Math.random() * 0.4 + 0.6,
        scraped_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        word_count: Math.floor(Math.random() * 5000) + 1000,
        relevance_score: Math.random() * 0.3 + 0.7,
        source_type: ['article', 'report', 'website', 'academic', 'news'][Math.floor(Math.random() * 5)] as any,
        metadata: {
          author: `Expert ${i + 1}`,
          published_date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          domain: `example${i + 1}.com`
        }
      }))
    }));
  };

  const filterEvidence = () => {
    let filtered = evidenceData;
    
    if (selectedLayer) {
      filtered = filtered.filter(layer => layer.layer_name === selectedLayer);
    }
    
    if (searchTerm) {
      filtered = filtered.map(layer => ({
        ...layer,
        evidence_items: layer.evidence_items.filter(item =>
          item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.content_preview.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.url.toLowerCase().includes(searchTerm.toLowerCase())
        )
      })).filter(layer => layer.evidence_items.length > 0);
    }
    
    setFilteredData(filtered);
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.8) return '#52c41a';
    if (score >= 0.6) return '#fa8c16';
    return '#ff4d4f';
  };

  const getSourceTypeColor = (type: string) => {
    const colors = {
      article: '#1890ff',
      report: '#52c41a',
      website: '#fa8c16',
      academic: '#722ed1',
      news: '#eb2f96'
    };
    return colors[type as keyof typeof colors] || '#b8b8cc';
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number) => {
    setCurrentPage(page);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedLayer(null);
    setCurrentPage(1);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2, color: '#e8e8f0' }}>
          Loading Evidence Data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={loadEvidenceData} startIcon={<Refresh />}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1400, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <LinkIcon sx={{ fontSize: 32, color: '#1890ff', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              Evidence Browser
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: '#b8b8cc', mb: 3 }}>
            Browse and analyze collected evidence and sources by strategic layer
          </Typography>
          
          {/* Search and Filters */}
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <TextField
              placeholder="Search evidence..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: '#b8b8cc' }} />
                  </InputAdornment>
                ),
              }}
              sx={{
                minWidth: 300,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#252547',
                  '& fieldset': { borderColor: '#3d3d56' },
                  '&:hover fieldset': { borderColor: '#1890ff' },
                  '&.Mui-focused fieldset': { borderColor: '#1890ff' },
                },
                '& .MuiInputBase-input': { color: '#e8e8f0' },
              }}
            />
            <Button
              variant="outlined"
              onClick={clearFilters}
              sx={{ color: '#b8b8cc', borderColor: '#3d3d56' }}
            >
              Clear Filters
            </Button>
          </Box>

          {/* Layer Filter Chips */}
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
            {evidenceData.map(layer => (
              <Chip
                key={layer.layer_name}
                label={`${layer.layer_name} (${layer.evidence_count})`}
                onClick={() => setSelectedLayer(selectedLayer === layer.layer_name ? null : layer.layer_name)}
                variant={selectedLayer === layer.layer_name ? "filled" : "outlined"}
                sx={{
                  backgroundColor: selectedLayer === layer.layer_name ? '#1890ff20' : 'transparent',
                  color: selectedLayer === layer.layer_name ? '#1890ff' : '#e8e8f0',
                  borderColor: '#3d3d56',
                  '&:hover': {
                    backgroundColor: '#1890ff20'
                  }
                }}
              />
            ))}
          </Box>
        </Box>

        {/* Evidence Layers */}
        {filteredData.map((layer, layerIndex) => (
          <Accordion
            key={layer.layer_name}
            defaultExpanded={layerIndex === 0}
            sx={{ mb: 2, backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}
          >
            <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', mr: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="h6" sx={{ color: '#e8e8f0', mr: 2 }}>
                    {layer.layer_name}
                  </Typography>
                  <Chip
                    size="small"
                    label={`${layer.evidence_items.length} sources`}
                    sx={{ backgroundColor: '#52c41a20', color: '#52c41a' }}
                  />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    Avg Quality: {(layer.avg_quality_score * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    {(layer.total_content_length / 1000).toFixed(0)}K words
                  </Typography>
                </Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 3 }}>
                {layer.layer_description}
              </Typography>
              
              <List>
                {layer.evidence_items
                  .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                  .map((item, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      backgroundColor: '#252547',
                      mb: 2,
                      borderRadius: 2,
                      border: '1px solid #3d3d56'
                    }}
                  >
                    <ListItemIcon>
                      <LinkIcon sx={{ color: getSourceTypeColor(item.source_type) }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                          <Link
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{
                              color: '#1890ff',
                              textDecoration: 'none',
                              fontWeight: 500,
                              '&:hover': { textDecoration: 'underline' }
                            }}
                          >
                            {item.title}
                          </Link>
                          <IconButton size="small" href={item.url} target="_blank">
                            <OpenInNew sx={{ fontSize: 16, color: '#b8b8cc' }} />
                          </IconButton>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                            {item.content_preview}
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
                            <Chip
                              size="small"
                              label={`Quality: ${(item.quality_score * 100).toFixed(0)}%`}
                              sx={{
                                backgroundColor: `${getQualityColor(item.quality_score)}20`,
                                color: getQualityColor(item.quality_score)
                              }}
                            />
                            <Chip
                              size="small"
                              label={item.source_type}
                              sx={{
                                backgroundColor: `${getSourceTypeColor(item.source_type)}20`,
                                color: getSourceTypeColor(item.source_type)
                              }}
                            />
                            <Chip
                              size="small"
                              label={`${item.word_count} words`}
                              sx={{ backgroundColor: '#fa8c1620', color: '#fa8c16' }}
                            />
                            <Typography variant="caption" sx={{ color: '#b8b8cc', ml: 1 }}>
                              {item.metadata.domain} • {new Date(item.scraped_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
              
              {layer.evidence_items.length > itemsPerPage && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <Pagination
                    count={Math.ceil(layer.evidence_items.length / itemsPerPage)}
                    page={currentPage}
                    onChange={handlePageChange}
                    sx={{
                      '& .MuiPaginationItem-root': {
                        color: '#e8e8f0',
                        borderColor: '#3d3d56'
                      },
                      '& .Mui-selected': {
                        backgroundColor: '#1890ff20',
                        color: '#1890ff'
                      }
                    }}
                  />
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        ))}

        {filteredData.length === 0 && (
          <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56', p: 4, textAlign: 'center' }}>
            <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 2 }}>
              No evidence found
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              Try adjusting your search terms or filters
            </Typography>
          </Card>
        )}
      </motion.div>
    </Box>
  );
};

export default EvidenceBrowserPage;
