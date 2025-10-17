/**
 * Experience Results Component
 * Displays experience analysis including user journey, touchpoints, and improvements
 */

import React from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  LinearProgress,
  Chip,
  CircularProgress
} from '@mui/material';
import { 
  Timeline, 
  TouchApp, 
  Warning, 
  TrendingUp,
  Assessment
} from '@mui/icons-material';

import type { ExperienceAnalysisData } from '../../hooks/useAnalysis';
import { useEnhancedAnalysis } from '../../hooks/useEnhancedAnalysis';
import { useSegmentPatterns } from '../../hooks/useSegmentPatterns';
import PatternMatchCard from './PatternMatchCard';

export interface ExperienceResultsProps {
  data: ExperienceAnalysisData;
  sessionId?: string;
}

const ExperienceResults: React.FC<ExperienceResultsProps> = ({ data, sessionId }) => {
  // Fetch enhanced analysis (Pattern Library, Monte Carlo)
  const { patternMatches, scenarios } = useEnhancedAnalysis(sessionId || null);

  // NEW: Fetch Experience-specific patterns (top 4)
  const { patternMatches: experiencePatterns, scenarios: experienceScenarios, hasPatterns } = useSegmentPatterns(
    sessionId || null,
    'experience'
  );

  // Use segment-specific patterns if available
  const displayPatterns = hasPatterns ? experiencePatterns : (
    patternMatches?.pattern_matches?.filter(p => 
      p.segments_involved.some(seg => seg.toLowerCase().includes('experience'))
    ) || []
  );
  const displayScenarios = hasPatterns ? experienceScenarios : scenarios;

  if (!data) {
    return (
      <Typography sx={{ color: '#888' }}>
        No experience analysis data available
      </Typography>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        
        {/* User Journey */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', bgcolor: '#00796B', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Timeline sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  User Journey
                </Typography>
              </Box>
              
              {data.user_journey && data.user_journey.length > 0 ? (
                <Box>
                  {data.user_journey.map((stage, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1, position: 'relative' }}>
                      {/* Stage indicator */}
                      <Box sx={{ 
                        position: 'absolute', 
                        left: -12, 
                        top: 20, 
                        width: 24, 
                        height: 24, 
                        borderRadius: '50%', 
                        bgcolor: '#4CAF50',
                        border: '3px solid #00796B',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Typography variant="caption" sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}>
                          {index + 1}
                        </Typography>
                      </Box>

                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: '#B2DFDB' }}>
                          {stage.stage}
                        </Typography>
                        <Chip 
                          label={stage.phase} 
                          size="small"
                          sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', fontSize: '0.7rem' }}
                        />
                      </Box>
                      <Typography variant="body2" sx={{ fontSize: '0.85rem', color: 'white', mb: 1.5 }}>
                        {stage.description}
                      </Typography>
                      
                      {stage.pain_points && stage.pain_points.length > 0 && (
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="caption" sx={{ color: '#FF5722', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Warning sx={{ fontSize: 14 }} />
                            Pain Points:
                          </Typography>
                          <List dense sx={{ pl: 2 }}>
                            {stage.pain_points.map((pain, i) => (
                              <ListItem key={i} sx={{ px: 0, py: 0.2 }}>
                                <ListItemText 
                                  primary={`• ${pain}`}
                                  primaryTypographyProps={{ fontSize: '0.75rem', color: '#FFCDD2' }}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                      
                      {stage.opportunities && stage.opportunities.length > 0 && (
                        <Box>
                          <Typography variant="caption" sx={{ color: '#4CAF50', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <TrendingUp sx={{ fontSize: 14 }} />
                            Opportunities:
                          </Typography>
                          <List dense sx={{ pl: 2 }}>
                            {stage.opportunities.map((opp, i) => (
                              <ListItem key={i} sx={{ px: 0, py: 0.2 }}>
                                <ListItemText 
                                  primary={`• ${opp}`}
                                  primaryTypographyProps={{ fontSize: '0.75rem', color: '#C8E6C9' }}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" sx={{ color: '#B2DFDB', fontStyle: 'italic' }}>
                  User journey mapping will be generated from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Experience Metrics */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#5D4037', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Assessment sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Experience Metrics
                </Typography>
              </Box>
              
              {data.experience_metrics && Object.keys(data.experience_metrics).length > 0 ? (
                <>
                  {Object.entries(data.experience_metrics).map(([metric, score]) => (
                    <Box key={metric} sx={{ mb: 2.5 }}>
                      <Typography variant="body2" sx={{ mb: 0.5, color: '#BCAAA4', fontSize: '0.85rem' }}>
                        {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={score * 100} 
                            sx={{ 
                              bgcolor: 'rgba(255,255,255,0.2)',
                              height: 8,
                              borderRadius: 1,
                              '& .MuiLinearProgress-bar': { 
                                bgcolor: score > 0.7 ? '#4CAF50' : score > 0.5 ? '#FF9800' : '#F44336',
                                borderRadius: 1
                              }
                            }} 
                          />
                        </Box>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', minWidth: 45 }}>
                          {(score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#BCAAA4', fontStyle: 'italic' }}>
                  Experience metrics will be calculated from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Touchpoints */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#455A64', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TouchApp sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Customer Touchpoints
                </Typography>
              </Box>
              
              {data.touchpoints && data.touchpoints.length > 0 ? (
                <>
                  {data.touchpoints.map((touchpoint, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.1)' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                        {touchpoint.name}
                      </Typography>
                      
                      <Grid container spacing={1.5}>
                        <Grid item xs={6}>
                          <Typography variant="caption" sx={{ color: '#B0BEC5' }}>
                            Importance
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#4CAF50' }}>
                            {(touchpoint.importance * 100).toFixed(0)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" sx={{ color: '#B0BEC5' }}>
                            Current Quality
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#FFC107' }}>
                            {(touchpoint.current_quality * 100).toFixed(0)}%
                          </Typography>
                        </Grid>
                      </Grid>
                      
                      {touchpoint.improvement_potential && (
                        <Box sx={{ mt: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#B0BEC5' }}>
                            Improvement Potential
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={touchpoint.improvement_potential * 100} 
                            sx={{ 
                              mt: 0.5,
                              bgcolor: 'rgba(255,255,255,0.1)',
                              height: 6,
                              borderRadius: 1,
                              '& .MuiLinearProgress-bar': { bgcolor: '#2196F3', borderRadius: 1 }
                            }} 
                          />
                        </Box>
                      )}
                    </Box>
                  ))}
                </>
              ) : (
                <Typography variant="body2" sx={{ color: '#B0BEC5', fontStyle: 'italic' }}>
                  Customer touchpoints will be identified from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Pain Points */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', bgcolor: '#424242', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Warning sx={{ fontSize: 28, color: '#FF5722' }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Experience Pain Points
                </Typography>
              </Box>
              
              {data.pain_points && data.pain_points.length > 0 ? (
                <List dense>
                  {data.pain_points.map((pain, index) => (
                    <ListItem key={index} sx={{ px: 0, py: 1, alignItems: 'flex-start', borderBottom: index < data.pain_points.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                      <Box sx={{ 
                        width: 28, 
                        height: 28, 
                        borderRadius: '4px', 
                        bgcolor: 'rgba(255, 87, 34, 0.2)', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        mr: 1.5,
                        mt: 0.2,
                        flexShrink: 0,
                        border: '1px solid rgba(255, 87, 34, 0.4)'
                      }}>
                        <Warning sx={{ fontSize: 16, color: '#FF5722' }} />
                      </Box>
                      <ListItemText
                        primary={pain}
                        primaryTypographyProps={{ 
                          fontSize: '0.9rem', 
                          color: '#E0E0E0',
                          fontWeight: 500
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" sx={{ color: '#BDBDBD', fontStyle: 'italic' }}>
                  Experience pain points will be identified from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Improvement Recommendations */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', bgcolor: '#2E7D32', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <TrendingUp sx={{ fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Improvement Recommendations
                </Typography>
              </Box>
              
              {data.improvement_recommendations && data.improvement_recommendations.length > 0 ? (
                <Grid container spacing={1.5}>
                  {data.improvement_recommendations.map((recommendation, index) => (
                    <Grid item xs={12} key={index}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1, display: 'flex', gap: 1.5 }}>
                        <Box sx={{ 
                          width: 32, 
                          height: 32, 
                          borderRadius: '50%', 
                          bgcolor: 'rgba(255,255,255,0.3)', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          flexShrink: 0
                        }}>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {index + 1}
                          </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ fontSize: '0.9rem', fontWeight: 500, pt: 0.5 }}>
                          {recommendation}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" sx={{ opacity: 0.9, fontStyle: 'italic' }}>
                  Experience improvement recommendations will be generated from analysis.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Experience Fit Score */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', bgcolor: '#00796B', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Experience Fit
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 180 }}>
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={(data.experience_fit?.overall_score || 0) * 100}
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
                      {`${Math.round((data.experience_fit?.overall_score || 0) * 100)}%`}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {data.experience_fit && Object.keys(data.experience_fit).length > 1 && (
                <Box sx={{ mt: 2 }}>
                  {Object.entries(data.experience_fit)
                    .filter(([key]) => key !== 'overall_score')
                    .map(([metric, value]) => (
                      <Box key={metric} sx={{ mb: 1.5 }}>
                        <Typography variant="caption" sx={{ color: '#B2DFDB', textTransform: 'capitalize' }}>
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

        {/* Pattern Library Insights - Enhanced Analysis (TOP 4 EXPERIENCE PATTERNS) */}
        {displayPatterns.length > 0 && (
          <Grid item xs={12}>
            <Box sx={{ mt: 4 }}>
              <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: '#00796B' }}>
                🎯 Strategic Pattern Insights (Pattern Library - Top 4)
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
                Patterns matched using actual Experience Intelligence scores • Monte Carlo simulations (1000 iterations)
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

export default ExperienceResults;

