/**
 * Consumer Results Component
 * Displays consumer analysis including personas, recommendations, challenges, and motivators
 */

import React from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Avatar,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Chip
} from '@mui/material';
import { 
  Person, 
  Warning, 
  Star,
  Group,
  TrendingUp
} from '@mui/icons-material';

import type { ConsumerAnalysisData } from '../../hooks/useAnalysis';
import { useEnhancedAnalysis } from '../../hooks/useEnhancedAnalysis';
import PatternMatchCard from './PatternMatchCard';

export interface ConsumerResultsProps {
  data: ConsumerAnalysisData;
  sessionId?: string;
}

const ConsumerResults: React.FC<ConsumerResultsProps> = ({ data, sessionId }) => {
  // Fetch enhanced analysis (Pattern Library, Monte Carlo)
  const { patternMatches, scenarios,  enginesAvailable } = useEnhancedAnalysis(sessionId || null);

  // Filter consumer-related patterns
  const consumerPatterns = patternMatches?.pattern_matches?.filter(p => 
    p.segments_involved.some(seg => seg.toLowerCase().includes('consumer'))
  ) || [];

  if (!data) {
    return (
      <Typography sx={{ color: '#888' }}>
        No consumer analysis data available
      </Typography>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        
        {/* Recommendations Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#5E35B1', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TrendingUp sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Recommendations
                </Typography>
              </Box>
              
              {data.recommendations && data.recommendations.length > 0 ? (
                <>
                  {data.recommendations.map((rec, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <Typography variant="subtitle2" sx={{ color: '#E1BEE7', fontWeight: 'bold', mb: 0.5 }}>
                        {rec.type || `Recommendation ${index + 1}`}
                        {rec.timeline && ` (${rec.timeline})`}
                      </Typography>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: 'white' }}>
                        {rec.description || rec}
                      </Typography>
                    </Box>
                  ))}

                  {data.additional_recommendations && data.additional_recommendations.length > 0 && (
                    <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255,255,255,0.2)' }}>
                      <Typography variant="caption" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 1, display: 'block' }}>
                        Additional Insights:
                      </Typography>
                      <List dense>
                        {data.additional_recommendations.map((item, index) => (
                          <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                            <ListItemText 
                              primary={`• ${item}`}
                              primaryTypographyProps={{ fontSize: '0.8rem', color: '#E1BEE7' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Consumer recommendations will appear here after analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* The Challenges Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#424242', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Warning sx={{ fontSize: 28, color: '#FF5722' }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  The Challenges
                </Typography>
              </Box>
              
              {data.challenges && data.challenges.length > 0 ? (
                <>
                  {data.challenges.length > 0 && (
                    <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(255, 87, 34, 0.1)', borderRadius: 1, border: '1px solid rgba(255, 87, 34, 0.3)' }}>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#FF5722', mb: 1 }}>
                        {data.challenges[0]}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#BDBDBD' }}>
                        Primary Challenge
                      </Typography>
                    </Box>
                  )}

                  {data.challenges.slice(1).map((challenge, index) => (
                    <Box key={index} sx={{ mb: 1.5 }}>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#E0E0E0' }}>
                        • {challenge}
                      </Typography>
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#BDBDBD', fontStyle: 'italic' }}>
                  Consumer challenges will be identified from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Top Motivators Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#424242', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Star sx={{ fontSize: 28, color: '#4CAF50' }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Top Motivators
                </Typography>
              </Box>
              
              {data.top_motivators && data.top_motivators.length > 0 ? (
                <>
                  {data.top_motivators.length > 0 && (
                    <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1, border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#4CAF50', mb: 1 }}>
                        {data.top_motivators[0]}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#BDBDBD' }}>
                        Primary Motivator
                      </Typography>
                    </Box>
                  )}

                  {data.top_motivators.slice(1).map((motivator, index) => (
                    <Box key={index} sx={{ mb: 1.5, p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ color: '#E0E0E0', fontWeight: 500 }}>
                        {motivator}
                      </Typography>
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#BDBDBD', fontStyle: 'italic' }}>
                  Consumer motivators will be extracted from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Relevant Personas Section */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', bgcolor: '#424242', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={3}>
                <Group sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Relevant Personas
                </Typography>
              </Box>
              
              {data.relevant_personas && data.relevant_personas.length > 0 ? (
                <Grid container spacing={2}>
                  {data.relevant_personas.map((persona, index) => (
                    <Grid item xs={12} md={4} key={index}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(94, 53, 177, 0.2)', borderRadius: 2, height: '100%', border: '1px solid rgba(94, 53, 177, 0.4)' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Avatar sx={{ bgcolor: '#5E35B1', mr: 2, width: 48, height: 48 }}>
                            <Person sx={{ fontSize: 28 }} />
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'white' }}>
                              {persona.name}
                            </Typography>
                            {persona.age && (
                              <Typography variant="caption" sx={{ color: '#BDBDBD' }}>
                                Age: {persona.age}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                        <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#E0E0E0', lineHeight: 1.5 }}>
                          {persona.description}
                        </Typography>
                        {persona.motivations && persona.motivations.length > 0 && (
                          <Box sx={{ mt: 1.5 }}>
                            {persona.motivations.slice(0, 2).map((motivation, i) => (
                              <Chip 
                                key={i}
                                label={motivation}
                                size="small"
                                sx={{ 
                                  mr: 0.5, 
                                  mt: 0.5,
                                  bgcolor: 'rgba(76, 175, 80, 0.2)', 
                                  color: '#4CAF50',
                                  fontSize: '0.7rem'
                                }}
                              />
                            ))}
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" sx={{ color: '#BDBDBD', fontStyle: 'italic' }}>
                  Consumer personas will be generated from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Target Audience Definition Section */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#5E35B1', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Target Audience Definition
              </Typography>
              
              {data.target_audience && Object.keys(data.target_audience).length > 0 ? (
                <>
                  {data.target_audience.primary_segment && (
                    <Box sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 0.5 }}>
                        Primary Segment
                      </Typography>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#E1BEE7' }}>
                        {data.target_audience.primary_segment}
                      </Typography>
                    </Box>
                  )}

                  {data.target_audience.secondary_segment && (
                    <Box sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 0.5 }}>
                        Secondary Segment
                      </Typography>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: '#E1BEE7' }}>
                        {data.target_audience.secondary_segment}
                      </Typography>
                    </Box>
                  )}

                  {data.target_audience.segments && Object.keys(data.target_audience.segments).length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" sx={{ color: '#B39DDB', fontWeight: 'bold', mb: 1, display: 'block' }}>
                        Additional Segments:
                      </Typography>
                      {Object.entries(data.target_audience.segments).map(([segment, details]) => (
                        <Box key={segment} sx={{ mb: 1.5 }}>
                          <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'white', fontWeight: 500 }}>
                            {segment}:
                          </Typography>
                          <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#E1BEE7', ml: 1 }}>
                            {details}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  )}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#E1BEE7', fontStyle: 'italic' }}>
                  Target audience segments will be defined from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Consumer Fit Section */}
        <Grid item xs={12}>
          <Card sx={{ bgcolor: '#FF5722', color: 'white' }}>
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={3}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Consumer Fit
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2 }}>
                    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                      <CircularProgress
                        variant="determinate"
                        value={(data.consumer_fit?.overall_score || 0) * 100}
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
                          {`${Math.round((data.consumer_fit?.overall_score || 0) * 100)}%`}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={9}>
                  <Box>
                    {data.consumer_fit && Object.keys(data.consumer_fit).length > 1 ? (
                      <>
                        <Typography variant="body1" sx={{ mb: 2, fontSize: '0.95rem', fontWeight: 500 }}>
                          <strong>Consumer Fit Analysis:</strong> Based on target audience alignment, demographic matching, and behavioral patterns.
                        </Typography>
                        <Grid container spacing={1}>
                          {Object.entries(data.consumer_fit)
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
                      </>
                    ) : (
                      <Typography variant="body2" sx={{ fontSize: '0.95rem' }}>
                        <strong>Consumer Fit Analysis:</strong> The consumer fit score indicates strong alignment between the target audience and product offering, with high adoption likelihood among identified personas.
                      </Typography>
                    )}
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Pattern Library Insights - Enhanced Analysis */}
        {enginesAvailable && consumerPatterns.length > 0 && (
          <Grid item xs={12}>
            <Box sx={{ mt: 4 }}>
              <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: '#5E35B1' }}>
                🎯 Strategic Pattern Insights (Pattern Library)
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
                Patterns matched using actual Consumer Intelligence scores • Monte Carlo simulations (1000 iterations)
              </Typography>
              <Grid container spacing={2}>
                {consumerPatterns.map((pattern) => (
                  <Grid item xs={12} lg={6} key={pattern.pattern_id}>
                    <PatternMatchCard 
                      pattern={pattern}
                      scenario={scenarios?.scenarios?.[pattern.pattern_id]}
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

export default ConsumerResults;

