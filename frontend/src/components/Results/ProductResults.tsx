/**
 * Product Results Component
 * Displays product analysis including features, positioning, and innovation opportunities
 */

import React from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Chip, 
  List, 
  ListItem, 
  ListItemText, 
  LinearProgress,
  CircularProgress
} from '@mui/material';
import { 
  Build, 
  Lightbulb, 
  TrendingUp, 
  Assessment,
  Star
} from '@mui/icons-material';

import type { ProductAnalysisData } from '../../hooks/useAnalysis';

export interface ProductResultsProps {
  data: ProductAnalysisData;
}

const ProductResults: React.FC<ProductResultsProps> = ({ data }) => {
  if (!data) {
    return (
      <Typography sx={{ color: '#888' }}>
        No product analysis data available
      </Typography>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        
        {/* Product Features Section */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#1976D2', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Build sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Key Product Features
                </Typography>
              </Box>
              
              {data.product_features && data.product_features.length > 0 ? (
                <>
                  {data.product_features.map((feature, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white' }}>
                          {feature.name}
                        </Typography>
                        {feature.category && (
                          <Chip 
                            label={feature.category} 
                            size="small"
                            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }}
                          />
                        )}
                      </Box>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#E3F2FD', mb: 1 }}>
                        {feature.description}
                      </Typography>
                      {feature.importance !== undefined && (
                        <>
                          <Typography variant="caption" sx={{ color: '#BBDEFB' }}>
                            Importance: {(feature.importance * 100).toFixed(0)}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={feature.importance * 100} 
                            sx={{ 
                              mt: 0.5, 
                              bgcolor: 'rgba(255,255,255,0.2)',
                              '& .MuiLinearProgress-bar': { bgcolor: '#81D4FA' }
                            }} 
                          />
                        </>
                      )}
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#E3F2FD', fontStyle: 'italic' }}>
                  Product features will be analyzed from market research.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Competitive Positioning */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#388E3C', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Assessment sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Competitive Positioning
                </Typography>
              </Box>
              
              {data.competitive_positioning && Object.keys(data.competitive_positioning).length > 0 ? (
                <>
                  {Object.entries(data.competitive_positioning).map(([aspect, details]) => (
                    <Box key={aspect} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <Typography variant="subtitle2" sx={{ color: '#C8E6C9', fontWeight: 'bold', mb: 0.5 }}>
                        {aspect.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: 'white' }}>
                        {typeof details === 'string' ? details : JSON.stringify(details)}
                      </Typography>
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#C8E6C9', fontStyle: 'italic' }}>
                  Competitive positioning analysis will appear here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Innovation Opportunities */}
        <Grid item xs={12}>
          <Card sx={{ bgcolor: '#FF6F00', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Lightbulb sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Innovation Opportunities
                </Typography>
              </Box>
              
              {data.innovation_opportunities && data.innovation_opportunities.length > 0 ? (
                <Grid container spacing={1.5}>
                  {data.innovation_opportunities.map((opportunity, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1, height: '100%' }}>
                        <Box display="flex" alignItems="flex-start" gap={1}>
                          <Star sx={{ fontSize: 20, color: '#FFD54F', mt: 0.2 }} />
                          <Typography variant="body2" sx={{ fontSize: '0.9rem', fontWeight: 500 }}>
                            {opportunity}
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" sx={{ fontStyle: 'italic', opacity: 0.9 }}>
                  Innovation opportunities will be identified from market analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Technical Specifications */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#455A64', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Technical Specifications
              </Typography>
              
              {data.technical_specifications && Object.keys(data.technical_specifications).length > 0 ? (
                <List dense>
                  {Object.entries(data.technical_specifications).map(([spec, value]) => (
                    <ListItem key={spec} sx={{ px: 0, py: 1, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <ListItemText
                        primary={spec.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        secondary={typeof value === 'string' ? value : JSON.stringify(value)}
                        primaryTypographyProps={{ 
                          fontSize: '0.9rem', 
                          fontWeight: 'bold', 
                          color: '#B0BEC5' 
                        }}
                        secondaryTypographyProps={{ 
                          fontSize: '0.85rem', 
                          color: 'white',
                          mt: 0.5
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" sx={{ color: '#B0BEC5', fontStyle: 'italic' }}>
                  Technical specifications will be extracted from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Product Roadmap */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#7B1FA2', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TrendingUp sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Product Roadmap
                </Typography>
              </Box>
              
              {data.product_roadmap && data.product_roadmap.length > 0 ? (
                <>
                  {data.product_roadmap.map((item, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: '#E1BEE7' }}>
                          {item.phase}
                        </Typography>
                        <Chip 
                          label={item.timeline} 
                          size="small"
                          sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }}
                        />
                      </Box>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: 'white' }}>
                        {item.features}
                      </Typography>
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Product roadmap will be generated based on market opportunities.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Product Fit Score */}
        <Grid item xs={12}>
          <Card sx={{ bgcolor: '#1976D2', color: 'white' }}>
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={3}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Product Fit
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2 }}>
                    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                      <CircularProgress
                        variant="determinate"
                        value={(data.product_fit?.overall_score || 0) * 100}
                        size={120}
                        thickness={5}
                        sx={{ color: 'white' }}
                      />
                      <Box
                        sx={{
                          top: 0,
                          left: 0,
                          bottom: 0,
                          right: 0,
                          position: 'absolute',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <Typography variant="h3" component="div" sx={{ color: 'white', fontWeight: 'bold' }}>
                          {`${Math.round((data.product_fit?.overall_score || 0) * 100)}%`}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={9}>
                  {data.product_fit && Object.keys(data.product_fit).length > 1 ? (
                    <Grid container spacing={1.5}>
                      {Object.entries(data.product_fit)
                        .filter(([key]) => key !== 'overall_score')
                        .map(([metric, value]) => (
                          <Grid item xs={12} sm={6} key={metric}>
                            <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                              <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                                {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Box sx={{ flexGrow: 1, bgcolor: 'rgba(255,255,255,0.2)', borderRadius: 1, height: 8 }}>
                                  <Box 
                                    sx={{ 
                                      width: `${value * 100}%`, 
                                      bgcolor: 'white', 
                                      height: '100%', 
                                      borderRadius: 1 
                                    }} 
                                  />
                                </Box>
                                <Typography variant="caption" sx={{ fontWeight: 'bold', minWidth: 40 }}>
                                  {(value * 100).toFixed(0)}%
                                </Typography>
                              </Box>
                            </Box>
                          </Grid>
                        ))}
                    </Grid>
                  ) : (
                    <Typography variant="body1" sx={{ fontSize: '0.95rem' }}>
                      Product fit score indicates strong alignment between product features, market needs, and competitive positioning. Technical feasibility and scalability metrics support successful market entry.
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

      </Grid>
    </Box>
  );
};

export default ProductResults;

