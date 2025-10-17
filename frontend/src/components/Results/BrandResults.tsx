/**
 * Brand Results Component
 * Displays brand analysis including positioning, perception, and opportunities
 */

import React from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress
} from '@mui/material';
import { 
  Loyalty, 
  Star, 
  TrendingUp,
  Message
} from '@mui/icons-material';

import type { BrandAnalysisData } from '../../hooks/useAnalysis';
import { useEnhancedAnalysis } from '../../hooks/useEnhancedAnalysis';
import { useSegmentPatterns } from '../../hooks/useSegmentPatterns';
import PatternMatchCard from './PatternMatchCard';

export interface BrandResultsProps {
  data: BrandAnalysisData;
  sessionId?: string;
}

const BrandResults: React.FC<BrandResultsProps> = ({ data, sessionId }) => {
  // Fetch enhanced analysis (Pattern Library, Monte Carlo)
  const { patternMatches, scenarios } = useEnhancedAnalysis(sessionId || null);

  // NEW: Fetch Brand-specific patterns (top 4)
  const { patternMatches: brandPatterns, scenarios: brandScenarios, hasPatterns } = useSegmentPatterns(
    sessionId || null,
    'brand'
  );

  // Use segment-specific patterns if available
  const displayPatterns = hasPatterns ? brandPatterns : (
    patternMatches?.pattern_matches?.filter(p => 
      p.segments_involved.some(seg => seg.toLowerCase().includes('brand'))
    ) || []
  );
  const displayScenarios = hasPatterns ? brandScenarios : scenarios;

  if (!data) {
    return (
      <Typography sx={{ color: '#888' }}>
        No brand analysis data available
      </Typography>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        
        {/* Brand Positioning */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#7B1FA2', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Loyalty sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Brand Positioning
                </Typography>
              </Box>
              
              {data.brand_positioning && Object.keys(data.brand_positioning).length > 0 ? (
                <>
                  {Object.entries(data.brand_positioning).map(([position, strength]) => (
                    <Box key={position} sx={{ mb: 2.5 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                        <Typography variant="body2" sx={{ fontWeight: 500, color: '#E1BEE7' }}>
                          {position}
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {(strength * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={strength * 100} 
                        sx={{ 
                          bgcolor: 'rgba(255,255,255,0.2)',
                          height: 8,
                          borderRadius: 1,
                          '& .MuiLinearProgress-bar': { 
                            bgcolor: 'white',
                            borderRadius: 1
                          }
                        }} 
                      />
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Brand positioning metrics will be analyzed from market data.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Brand Perception */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#303F9F', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Star sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Brand Perception
                </Typography>
              </Box>
              
              {data.brand_perception && Object.keys(data.brand_perception).length > 0 ? (
                <>
                  {Object.entries(data.brand_perception).map(([metric, score]) => (
                    <Box key={metric} sx={{ mb: 2.5 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                        <Typography variant="body2" sx={{ fontWeight: 500, color: '#C5CAE9' }}>
                          {metric}
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {(score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={score * 100} 
                        sx={{ 
                          bgcolor: 'rgba(255,255,255,0.2)',
                          height: 8,
                          borderRadius: 1,
                          '& .MuiLinearProgress-bar': { 
                            bgcolor: 'white',
                            borderRadius: 1
                          }
                        }} 
                      />
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#C5CAE9', fontStyle: 'italic' }}>
                  Brand perception metrics will be extracted from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Competitor Brands */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#424242', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Competitor Brands
              </Typography>
              
              {data.competitor_brands && data.competitor_brands.length > 0 ? (
                <>
                  {data.competitor_brands.map((brand, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.1)' }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white' }}>
                          {brand.name}
                        </Typography>
                        <Chip 
                          label={`Strength: ${(brand.strength * 100).toFixed(0)}%`}
                          size="small"
                          sx={{ 
                            bgcolor: brand.strength > 0.7 ? 'rgba(244, 67, 54, 0.2)' : 'rgba(76, 175, 80, 0.2)', 
                            color: brand.strength > 0.7 ? '#F44336' : '#4CAF50',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#BDBDBD' }}>
                        {brand.positioning}
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={brand.strength * 100} 
                        sx={{ 
                          mt: 1,
                          bgcolor: 'rgba(255,255,255,0.1)',
                          '& .MuiLinearProgress-bar': { 
                            bgcolor: brand.strength > 0.7 ? '#F44336' : '#4CAF50'
                          }
                        }} 
                      />
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#BDBDBD', fontStyle: 'italic' }}>
                  Competitor brand analysis will appear here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Brand Opportunities */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#00897B', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TrendingUp sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Brand Opportunities
                </Typography>
              </Box>
              
              {data.brand_opportunities && data.brand_opportunities.length > 0 ? (
                <List dense>
                  {data.brand_opportunities.map((opportunity, index) => (
                    <ListItem key={index} sx={{ px: 0, py: 1, alignItems: 'flex-start' }}>
                      <Box sx={{ 
                        width: 24, 
                        height: 24, 
                        borderRadius: '50%', 
                        bgcolor: 'rgba(255,255,255,0.2)', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        mr: 1.5,
                        mt: 0.2,
                        flexShrink: 0
                      }}>
                        <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                          {index + 1}
                        </Typography>
                      </Box>
                      <ListItemText
                        primary={opportunity}
                        primaryTypographyProps={{ 
                          fontSize: '0.9rem', 
                          color: 'white',
                          fontWeight: 500
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" sx={{ fontStyle: 'italic', opacity: 0.9 }}>
                  Brand growth opportunities will be identified from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Messaging Strategy */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', bgcolor: '#5E35B1', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Message sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Messaging Strategy
                </Typography>
              </Box>
              
              {data.messaging_strategy && Object.keys(data.messaging_strategy).length > 0 ? (
                <Grid container spacing={2}>
                  {data.messaging_strategy.key_messages && data.messaging_strategy.key_messages.length > 0 && (
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                        <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 1 }}>
                          Key Messages:
                        </Typography>
                        {data.messaging_strategy.key_messages.map((message: string, index: number) => (
                          <Typography key={index} variant="body2" sx={{ fontSize: '0.85rem', color: 'white', mb: 0.5 }}>
                            • {message}
                          </Typography>
                        ))}
                      </Box>
                    </Grid>
                  )}
                  
                  {data.messaging_strategy.tone && (
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                        <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 1 }}>
                          Brand Tone:
                        </Typography>
                        <Typography variant="body2" sx={{ fontSize: '0.85rem', color: 'white' }}>
                          {data.messaging_strategy.tone}
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                  
                  {data.messaging_strategy.differentiation && (
                    <Grid item xs={12}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                        <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 1 }}>
                          Differentiation Strategy:
                        </Typography>
                        <Typography variant="body2" sx={{ fontSize: '0.9rem', color: 'white' }}>
                          {data.messaging_strategy.differentiation}
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                </Grid>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Messaging strategy will be developed from brand analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Brand Fit Score */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#7E57C2', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Brand Fit
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 180 }}>
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={(data.brand_fit?.overall_score || 0) * 100}
                    size={140}
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
                    <Typography variant="h2" component="div" sx={{ color: 'white', fontWeight: 'bold' }}>
                      {`${Math.round((data.brand_fit?.overall_score || 0) * 100)}%`}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {data.brand_fit && Object.keys(data.brand_fit).length > 1 && (
                <Box sx={{ mt: 2 }}>
                  {Object.entries(data.brand_fit)
                    .filter(([key]) => key !== 'overall_score')
                    .map(([metric, value]) => (
                      <Box key={metric} sx={{ mb: 1.5 }}>
                        <Typography variant="caption" sx={{ color: '#B39DDB', textTransform: 'capitalize' }}>
                          {metric.replace(/_/g, ' ')}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Box sx={{ flexGrow: 1, bgcolor: 'rgba(255,255,255,0.2)', borderRadius: 1, height: 6 }}>
                            <Box 
                              sx={{ 
                                width: `${value * 100}%`, 
                                bgcolor: 'white', 
                                height: '100%', 
                                borderRadius: 1 
                              }} 
                            />
                          </Box>
                          <Typography variant="caption" sx={{ fontWeight: 'bold', minWidth: 35 }}>
                            {(value * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Pattern Library Insights - Enhanced Analysis (TOP 4 BRAND PATTERNS) */}
        {displayPatterns.length > 0 && (
          <Grid item xs={12}>
            <Box sx={{ mt: 4 }}>
              <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: '#7B1FA2' }}>
                🎯 Strategic Pattern Insights (Pattern Library - Top 4)
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
                Patterns matched using actual Brand Intelligence scores • Monte Carlo simulations (1000 iterations)
              </Typography>
              <Grid container spacing={2}>
                {displayPatterns.slice(0, 4).map((pattern) => (
                  <Grid item xs={12} lg={6} key={pattern.pattern_id}>
                    <PatternMatchCard 
                      pattern={pattern}
                      scenario={(displayScenarios as any)?.[pattern.pattern_id]}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Grid>
        )}

      </Grid>
    </Box>
  );
};

export default BrandResults;

