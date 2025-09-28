/**
 * Evidence Explorer Component
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Button,
  TextField,
  InputAdornment
} from '@mui/material';
import { ExpandMore, Search, Link, Assessment } from '@mui/icons-material';
import { apiClient } from '../../services/apiClient';

interface EvidenceExplorerProps {
  sessionId: string;
}

const EvidenceExplorer: React.FC<EvidenceExplorerProps> = ({ sessionId }) => {
  const [evidence, setEvidence] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | false>('sources');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadEvidence();
  }, [sessionId]);

  const loadEvidence = async () => {
    try {
      setLoading(true);
      // Try to load from session data
      const response = await apiClient.get(`/api/v3/analysis/${sessionId}/scenarios`);
      setEvidence(response.data.evidence || {});
    } catch (error) {
      console.error('Failed to load evidence:', error);
      // Set mock evidence for demo
      setEvidence({
        sources: [
          {
            title: 'Market Analysis Report 2024',
            url: 'https://example.com/market-analysis',
            relevance: 0.85,
            type: 'market_research'
          },
          {
            title: 'Competitive Landscape Study',
            url: 'https://example.com/competitive-study',
            relevance: 0.72,
            type: 'competitive_analysis'
          },
          {
            title: 'Technology Adoption Trends',
            url: 'https://example.com/tech-trends',
            relevance: 0.68,
            type: 'technology_research'
          }
        ],
        patterns: [
          {
            name: 'Seasonal Installation Compression',
            confidence: 0.72,
            description: 'Installation capacity constraints during peak seasons'
          },
          {
            name: 'Technology Adoption S-Curve',
            confidence: 0.75,
            description: 'Gradual adoption followed by rapid acceleration'
          }
        ],
        insights: [
          'Market growth rate of 15% annually',
          'Competitive intensity increasing by 20%',
          'Technology adoption accelerating in Q3-Q4'
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 0.8) return '#52c41a';
    if (relevance >= 0.6) return '#fa8c16';
    return '#ff4d4f';
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'market_research': '#1890ff',
      'competitive_analysis': '#fa8c16',
      'technology_research': '#52c41a',
      'financial_analysis': '#722ed1'
    };
    return colors[type] || '#d9d9d9';
  };

  const filteredSources = evidence?.sources?.filter((source: any) =>
    source.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    source.type.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  if (loading) {
    return (
      <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 2 }}>
            <CircularProgress size={24} />
            <Typography variant="body2" sx={{ color: '#b8b8cc', ml: 2 }}>
              Loading evidence...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Assessment sx={{ color: '#1890ff', mr: 1 }} />
          <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
            Evidence Explorer
          </Typography>
        </Box>

        {/* Search */}
        <TextField
          fullWidth
          size="small"
          placeholder="Search evidence sources..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search sx={{ color: '#b8b8cc' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            mb: 2,
            '& .MuiOutlinedInput-root': {
              color: '#e8e8f0',
              '& fieldset': { borderColor: '#3d3d56' },
              '&:hover fieldset': { borderColor: '#1890ff' }
            },
            '& .MuiInputLabel-root': { color: '#b8b8cc' }
          }}
        />

        {/* Evidence Sources */}
        <Accordion 
          expanded={expanded === 'sources'} 
          onChange={(_, isExpanded) => setExpanded(isExpanded ? 'sources' : false)}
          sx={{ backgroundColor: '#252547', mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Typography variant="subtitle1" sx={{ color: '#e8e8f0' }}>
              Evidence Sources ({filteredSources.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List dense>
              {filteredSources.map((source: any, index: number) => (
                <ListItem key={index} sx={{ py: 1, borderBottom: '1px solid #3d3d56' }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="body2" sx={{ color: '#e8e8f0', flex: 1 }}>
                          {source.title}
                        </Typography>
                        <Chip
                          size="small"
                          label={`${(source.relevance * 100).toFixed(0)}%`}
                          sx={{
                            backgroundColor: `${getRelevanceColor(source.relevance)}20`,
                            color: getRelevanceColor(source.relevance),
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="caption" sx={{ color: '#b8b8cc', display: 'block', mb: 1 }}>
                          {source.url}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip
                            size="small"
                            label={source.type.replace('_', ' ').toUpperCase()}
                            sx={{
                              backgroundColor: `${getTypeColor(source.type)}20`,
                              color: getTypeColor(source.type),
                              fontSize: '0.7rem'
                            }}
                          />
                          <Button
                            size="small"
                            startIcon={<Link />}
                            sx={{ 
                              color: '#1890ff', 
                              fontSize: '0.7rem',
                              minWidth: 'auto',
                              px: 1
                            }}
                            onClick={() => {
                              const w = window.open(source.url, '_blank', 'noopener,noreferrer');
                              if (w) w.opener = null;
                            }}
                          >
                            View
                          </Button>
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        {/* Strategic Patterns */}
        <Accordion 
          expanded={expanded === 'patterns'} 
          onChange={(_, isExpanded) => setExpanded(isExpanded ? 'patterns' : false)}
          sx={{ backgroundColor: '#252547', mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Typography variant="subtitle1" sx={{ color: '#e8e8f0' }}>
              Strategic Patterns ({evidence?.patterns?.length || 0})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List dense>
              {evidence?.patterns?.map((pattern: any, index: number) => (
                <ListItem key={index} sx={{ py: 1 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                          {pattern.name}
                        </Typography>
                        <Chip
                          size="small"
                          label={`${(pattern.confidence * 100).toFixed(0)}%`}
                          sx={{
                            backgroundColor: '#1890ff20',
                            color: '#1890ff',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                        {pattern.description}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        {/* Key Insights */}
        <Accordion 
          expanded={expanded === 'insights'} 
          onChange={(_, isExpanded) => setExpanded(isExpanded ? 'insights' : false)}
          sx={{ backgroundColor: '#252547' }}
        >
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
            <Typography variant="subtitle1" sx={{ color: '#e8e8f0' }}>
              Key Insights ({evidence?.insights?.length || 0})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List dense>
              {evidence?.insights?.map((insight: string, index: number) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                        • {insight}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
};

export default EvidenceExplorer;
