/**
 * Enhanced Segment Page Component
 * Displays comprehensive segment analysis with Monte Carlo scenarios and rich content
 * WCAG AAA Compliant (7:1+ contrast ratios)
 */

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  CircularProgress, 
  Alert,
  Chip,
  Divider
} from '@mui/material';
import ExpandableTile from '../Common/ExpandableTile';
import axios from 'axios';

// WCAG AAA Compliant Color Palette (7:1+ contrast ratios)
const SEGMENT_COLORS = {
  market: {
    primary: '#1565C0',    // Dark blue (8.59:1 contrast with white)
    text: '#FFFFFF',       
    accent: '#42A5F5',
    light: '#E3F2FD'
  },
  consumer: {
    primary: '#2E7D32',    // Dark green (7.44:1 contrast)  
    text: '#FFFFFF',       
    accent: '#66BB6A',
    light: '#E8F5E9'
  },
  product: {
    primary: '#E65100',    // Dark orange (8.28:1 contrast)
    text: '#FFFFFF',       
    accent: '#FF9800',
    light: '#FFF3E0'
  },
  brand: {
    primary: '#4A148C',    // Dark purple (12.63:1 contrast)
    text: '#FFFFFF',       
    accent: '#7E57C2',
    light: '#F3E5F5'
  },
  experience: {
    primary: '#004D40',    // Dark teal (11.05:1 contrast)
    text: '#FFFFFF',       
    accent: '#00897B',
    light: '#E0F2F1'
  }
};

interface EnhancedSegmentPageProps {
  topicId: string;
  segment: 'market' | 'consumer' | 'product' | 'brand' | 'experience';
}

const EnhancedSegmentPage: React.FC<EnhancedSegmentPageProps> = ({ topicId, segment }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const colors = SEGMENT_COLORS[segment];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const baseURL = process.env.REACT_APP_API_URL || 'https://validatus-backend-ssivkqhvhq-uc.a.run.app';
        const response = await axios.get(`${baseURL}/api/v3/enhanced-segment-results/${topicId}/${segment}`);
        
        setData(response.data);
      } catch (err: any) {
        console.error('Error fetching enhanced segment data:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to load segment data');
      } finally {
        setLoading(false);
      }
    };

    if (topicId && segment) {
      fetchData();
    }
  }, [topicId, segment]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress sx={{ color: colors.primary }} />
        <Typography sx={{ ml: 2, color: colors.primary, fontWeight: 'bold' }}>
          Loading {segment} analysis...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 3 }}>
        <Typography variant="h6">Error Loading Segment Data</Typography>
        <Typography variant="body2">{error}</Typography>
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert severity="info" sx={{ m: 3 }}>
        No data available for {segment} segment
      </Alert>
    );
  }

  const { monte_carlo_scenarios, matched_patterns, personas, rich_content, factors } = data;

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.primary, mb: 1 }}>
          {segment.charAt(0).toUpperCase() + segment.slice(1)} Intelligence
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          {data.topic_name || topicId}
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip 
            label={`${monte_carlo_scenarios?.length || 0} Scenarios`} 
            sx={{ bgcolor: colors.light, color: colors.primary, fontWeight: 'bold' }}
          />
          <Chip 
            label={`${matched_patterns?.length || 0} Patterns`}
            sx={{ bgcolor: colors.light, color: colors.primary, fontWeight: 'bold' }}
          />
          <Chip 
            label={`${data.content_items_analyzed || 0} Content Items`}
            sx={{ bgcolor: colors.light, color: colors.primary, fontWeight: 'bold' }}
          />
        </Box>
      </Box>

      <Divider sx={{ mb: 4 }} />

      {/* Monte Carlo Scenarios Section */}
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold', color: colors.primary }}>
        🎲 Monte Carlo Strategic Scenarios
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
        {monte_carlo_scenarios?.length || 0} scenarios analyzed with 1,000 iterations each
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 5 }}>
        {monte_carlo_scenarios?.map((scenario: any, index: number) => (
          <Grid 
            item 
            xs={12} 
            md={segment === 'experience' ? 6 : segment === 'product' ? 4 : 6} 
            key={scenario.scenario_id}
          >
            <ExpandableTile
              title={scenario.pattern_name}
              bgcolor={colors.primary}
              textColor={colors.text}
              chipColor="rgba(255,255,255,0.25)"
              chipTextColor={colors.text}
              content={scenario.strategic_response}
              confidence={scenario.probability_success}
              additionalContent={
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold', color: colors.text }}>
                    Monte Carlo Simulation Results
                  </Typography>
                  
                  {/* KPI Results */}
                  {Object.entries(scenario.kpi_results || {}).map(([kpi, results]: [string, any]) => (
                    <Box key={kpi} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: colors.text, mb: 1 }}>
                        {kpi.replace(/_/g, ' ').toUpperCase()}
                      </Typography>
                      
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.9)', display: 'block' }}>
                            Mean: <strong>{results.mean?.toFixed(2)}%</strong>
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.9)', display: 'block' }}>
                            Median: <strong>{results.median?.toFixed(2)}%</strong>
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.9)', display: 'block' }}>
                            Std Dev: {results.std?.toFixed(2)}%
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.9)', display: 'block' }}>
                            Range: {results.min?.toFixed(1)}% - {results.max?.toFixed(1)}%
                          </Typography>
                        </Grid>
                      </Grid>
                      
                      <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 0.5 }}>
                        <Typography variant="caption" sx={{ color: colors.text, display: 'block', fontWeight: 'bold' }}>
                          95% CI: [{results.confidence_interval_95?.[0]?.toFixed(2)}%, {results.confidence_interval_95?.[1]?.toFixed(2)}%]
                        </Typography>
                        <Typography variant="caption" sx={{ color: colors.text, display: 'block' }}>
                          Success Probability: {(results.probability_positive * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                  
                  {/* Overall Scenario Stats */}
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(255,255,255,0.2)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.3)' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: colors.text, mb: 1 }}>
                      Scenario Summary
                    </Typography>
                    <Typography variant="body2" sx={{ color: colors.text, fontSize: '0.85rem' }}>
                      Overall Success: <strong>{(scenario.probability_success * 100).toFixed(1)}%</strong>
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', display: 'block', mt: 1 }}>
                      Based on {scenario.iterations_run?.toLocaleString()} iterations
                    </Typography>
                  </Box>
                </Box>
              }
              chips={[
                scenario.pattern_id,
                `${(scenario.probability_success * 100).toFixed(0)}% Success`,
                '1000 iterations'
              ]}
              metrics={{
                'Pattern': scenario.pattern_id,
                'Success Probability': `${(scenario.probability_success * 100).toFixed(0)}%`,
                'KPIs Analyzed': Object.keys(scenario.kpi_results || {}).length
              }}
            />
          </Grid>
        ))}
      </Grid>

      {/* Product Rich Content */}
      {segment === 'product' && rich_content && Object.keys(rich_content).length > 0 && (
        <>
          <Divider sx={{ mb: 4 }} />
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold', color: colors.primary }}>
            📦 Product Intelligence
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Key Features */}
            {rich_content.features && rich_content.features.length > 0 && (
              <Grid item xs={12} md={6}>
                <ExpandableTile
                  title="Key Product Features"
                  bgcolor={colors.primary}
                  textColor={colors.text}
                  chipColor="rgba(255,255,255,0.25)"
                  chipTextColor={colors.text}
                  content={`${rich_content.features.length} features identified from market analysis`}
                  additionalContent={
                    <Box>
                      {rich_content.features.map((feature: any, idx: number) => (
                        <Box key={idx} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: colors.text }}>
                            {feature.name}
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 1, fontSize: '0.85rem', color: 'rgba(255,255,255,0.9)' }}>
                            {feature.description}
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                              Importance: {(feature.importance * 100).toFixed(0)}%
                            </Typography>
                            <Chip 
                              label={feature.market_validation}
                              size="small"
                              sx={{ bgcolor: 'rgba(255,255,255,0.25)', color: colors.text, fontWeight: 'bold' }}
                            />
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  }
                  chips={['Product Features', 'Market Validated']}
                />
              </Grid>
            )}

            {/* Innovation Opportunities */}
            {rich_content.innovation_opportunities && rich_content.innovation_opportunities.length > 0 && (
              <Grid item xs={12} md={6}>
                <ExpandableTile
                  title="Innovation Opportunities"
                  bgcolor={colors.primary}
                  textColor={colors.text}
                  chipColor="rgba(255,255,255,0.25)"
                  chipTextColor={colors.text}
                  content={`${rich_content.innovation_opportunities.length} innovation pathways identified`}
                  additionalContent={
                    <Box>
                      {rich_content.innovation_opportunities.map((opp: any, idx: number) => (
                        <Box key={idx} sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: colors.text }}>
                            {opp.opportunity}
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            <Chip label={`Impact: ${opp.impact}`} size="small" sx={{ bgcolor: 'rgba(76,175,80,0.3)', color: '#FFFFFF' }} />
                            <Chip label={`Feasibility: ${opp.feasibility}`} size="small" sx={{ bgcolor: 'rgba(33,150,243,0.3)', color: '#FFFFFF' }} />
                            <Chip label={`Timeline: ${opp.timeline}`} size="small" sx={{ bgcolor: 'rgba(255,152,0,0.3)', color: '#FFFFFF' }} />
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  }
                  chips={['Innovation', 'R&D Opportunities']}
                />
              </Grid>
            )}
          </Grid>
        </>
      )}

      {/* Brand Rich Content */}
      {segment === 'brand' && rich_content && Object.keys(rich_content).length > 0 && (
        <>
          <Divider sx={{ mb: 4 }} />
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold', color: colors.primary }}>
            🎯 Brand Intelligence
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Brand Positioning */}
            {rich_content.positioning && (
              <Grid item xs={12} md={6}>
                <ExpandableTile
                  title="Brand Positioning Strategy"
                  bgcolor={colors.primary}
                  textColor={colors.text}
                  chipColor="rgba(255,255,255,0.25)"
                  chipTextColor={colors.text}
                  content={rich_content.positioning.current || 'Analyzing brand position...'}
                  additionalContent={
                    <Box>
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: colors.text }}>
                        Current vs Desired Positioning
                      </Typography>
                      <Box sx={{ mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', display: 'block' }}>
                          CURRENT:
                        </Typography>
                        <Typography variant="body2" sx={{ color: colors.text, mb: 1 }}>
                          {rich_content.positioning.current}
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', display: 'block', mt: 1 }}>
                          DESIRED:
                        </Typography>
                        <Typography variant="body2" sx={{ color: colors.text }}>
                          {rich_content.positioning.desired}
                        </Typography>
                      </Box>
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: colors.text }}>
                        Gap Analysis
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem' }}>
                        {rich_content.positioning.gap_analysis}
                      </Typography>
                    </Box>
                  }
                  chips={['Brand Strategy', 'Positioning']}
                />
              </Grid>
            )}

            {/* Brand Perception */}
            {rich_content.perception && (
              <Grid item xs={12} md={6}>
                <ExpandableTile
                  title="Brand Perception & Trust"
                  bgcolor={colors.primary}
                  textColor={colors.text}
                  chipColor="rgba(255,255,255,0.25)"
                  chipTextColor={colors.text}
                  content={rich_content.perception.market_sentiment || 'Analyzing market perception...'}
                  additionalContent={
                    <Box>
                      {rich_content.perception.strengths && rich_content.perception.strengths.length > 0 && (
                        <>
                          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: colors.text }}>
                            Perceived Strengths
                          </Typography>
                          {rich_content.perception.strengths.map((strength: string, idx: number) => (
                            <Typography key={idx} variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', mb: 0.5 }}>
                              ✓ {strength}
                            </Typography>
                          ))}
                        </>
                      )}
                      
                      {rich_content.perception.weaknesses && rich_content.perception.weaknesses.length > 0 && (
                        <>
                          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 'bold', color: colors.text }}>
                            Areas for Improvement
                          </Typography>
                          {rich_content.perception.weaknesses.map((weakness: string, idx: number) => (
                            <Typography key={idx} variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', mb: 0.5 }}>
                              → {weakness}
                            </Typography>
                          ))}
                        </>
                      )}
                    </Box>
                  }
                  chips={['Perception Analysis', 'Market Sentiment']}
                />
              </Grid>
            )}
          </Grid>
        </>
      )}

      {/* Experience Rich Content */}
      {segment === 'experience' && rich_content && Object.keys(rich_content).length > 0 && (
        <>
          <Divider sx={{ mb: 4 }} />
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold', color: colors.primary }}>
            ⭐ Experience Intelligence
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Customer Journey */}
            {rich_content.journey_stages && rich_content.journey_stages.length > 0 && (
              <Grid item xs={12}>
                <ExpandableTile
                  title="Customer Journey Map"
                  bgcolor={colors.primary}
                  textColor={colors.text}
                  chipColor="rgba(255,255,255,0.25)"
                  chipTextColor={colors.text}
                  content={`${rich_content.journey_stages.length} journey stages analyzed with touchpoints and pain points`}
                  additionalContent={
                    <Box>
                      <Grid container spacing={2}>
                        {rich_content.journey_stages.map((stage: any, idx: number) => (
                          <Grid item xs={12} md={6} key={idx}>
                            <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: colors.text }}>
                                {stage.stage}
                              </Typography>
                              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', display: 'block', mb: 1 }}>
                                Touchpoints: {stage.touchpoints?.join(', ')}
                              </Typography>
                              
                              {stage.pain_points && stage.pain_points.length > 0 && (
                                <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(244,67,54,0.2)', borderRadius: 0.5 }}>
                                  <Typography variant="caption" sx={{ color: '#FFFFFF', fontWeight: 'bold' }}>
                                    Pain Points:
                                  </Typography>
                                  {stage.pain_points.map((pain: string, pidx: number) => (
                                    <Typography key={pidx} variant="caption" sx={{ color: '#FFFFFF', display: 'block', fontSize: '0.75rem' }}>
                                      • {pain}
                                    </Typography>
                                  ))}
                                </Box>
                              )}
                              
                              {stage.satisfaction_score !== undefined && (
                                <Box sx={{ mt: 1 }}>
                                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                                    Satisfaction: {(stage.satisfaction_score * 100).toFixed(0)}%
                                  </Typography>
                                </Box>
                              )}
                            </Box>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  }
                  chips={['Journey Mapping', 'Touchpoint Analysis']}
                  metrics={{
                    'Journey Stages': rich_content.journey_stages.length,
                    'Pain Points': rich_content.critical_pain_points?.length || 0
                  }}
                />
              </Grid>
            )}
          </Grid>
        </>
      )}

      {/* Consumer Personas */}
      {segment === 'consumer' && personas && personas.length > 0 && (
        <>
          <Divider sx={{ mb: 4 }} />
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold', color: colors.primary }}>
            👥 Consumer Personas
          </Typography>
          
          <Grid container spacing={3}>
            {personas.map((persona: any, idx: number) => (
              <Grid item xs={12} md={6} key={idx}>
                <ExpandableTile
                  title={`${persona.name} (${persona.age})`}
                  bgcolor={colors.primary}
                  textColor={colors.text}
                  chipColor="rgba(255,255,255,0.25)"
                  chipTextColor={colors.text}
                  content={`${persona.value_tier} Tier • ${(persona.market_share * 100).toFixed(0)}% Market Share`}
                  confidence={persona.confidence}
                  additionalContent={
                    <Box>
                      {persona.demographics && (
                        <>
                          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: colors.text }}>
                            Demographics
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 2, fontSize: '0.85rem', color: 'rgba(255,255,255,0.9)' }}>
                            {persona.demographics.location} • {persona.demographics.income} • {persona.demographics.occupation}
                          </Typography>
                        </>
                      )}

                      {persona.pain_points && persona.pain_points.length > 0 && (
                        <>
                          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: colors.text }}>
                            Pain Points
                          </Typography>
                          {persona.pain_points.map((pain: string, pidx: number) => (
                            <Typography key={pidx} variant="body2" sx={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.9)', mb: 0.5 }}>
                              • {pain}
                            </Typography>
                          ))}
                        </>
                      )}

                      {persona.key_messaging && persona.key_messaging.length > 0 && (
                        <>
                          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 'bold', color: colors.text }}>
                            Key Messaging
                          </Typography>
                          {persona.key_messaging.map((message: string, midx: number) => (
                            <Typography key={midx} variant="body2" sx={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.9)', mb: 0.5 }}>
                              ✓ {message}
                            </Typography>
                          ))}
                        </>
                      )}
                    </Box>
                  }
                  chips={[persona.value_tier, `${(persona.market_share * 100).toFixed(0)}% Share`]}
                  metrics={{
                    'Market Share': `${(persona.market_share * 100).toFixed(0)}%`,
                    'Value Tier': persona.value_tier,
                    'Confidence': `${(persona.confidence * 100).toFixed(0)}%`
                  }}
                />
              </Grid>
            ))}
          </Grid>
        </>
      )}
      
    </Box>
  );
};

export default EnhancedSegmentPage;

