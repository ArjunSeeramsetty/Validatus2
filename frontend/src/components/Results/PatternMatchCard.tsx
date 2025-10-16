/**
 * Pattern Match Card Component
 * Displays pattern matches from Pattern Library with Monte Carlo scenarios
 */

import React from 'react';
import { Box, Typography, LinearProgress, Grid } from '@mui/material';
import ExpandableTile from '../Common/ExpandableTile';
import type { PatternMatch, MonteCarloScenario } from '../../services/enhancedAnalysisService';

interface PatternMatchCardProps {
  pattern: PatternMatch;
  scenario?: MonteCarloScenario;
}

const PatternMatchCard: React.FC<PatternMatchCardProps> = ({ pattern, scenario }) => {
  // Determine background color based on pattern type
  const getBgColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'success':
        return '#4CAF50'; // Green
      case 'opportunity':
        return '#FF9800'; // Orange
      case 'fragility':
        return '#F44336'; // Red
      case 'adaptation':
        return '#2196F3'; // Blue
      default:
        return '#9C27B0'; // Purple
    }
  };

  // Format chips
  const chips = [
    pattern.pattern_type,
    ...pattern.segments_involved.map(s => `${s} Segment`),
    'Data-Driven',
    `${(pattern.confidence * 100).toFixed(0)}% Confidence`
  ];

  // Prepare metrics
  const metrics: Record<string, string> = {
    'Confidence': `${(pattern.confidence * 100).toFixed(0)}%`,
    'Evidence Strength': `${(pattern.evidence_strength * 100).toFixed(0)}%`,
    'Segments': pattern.segments_involved.join(', '),
    'Factors': pattern.factors_triggered.join(', ')
  };

  return (
    <ExpandableTile
      title={`${pattern.pattern_id}: ${pattern.pattern_name}`}
      bgcolor={getBgColor(pattern.pattern_type)}
      content={pattern.strategic_response}
      confidence={pattern.confidence}
      chips={chips}
      metrics={metrics}
      additionalContent={
        <Box>
          {/* Strategic Response Section */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
              📋 Strategic Response
            </Typography>
            <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: 'white', lineHeight: 1.6 }}>
                {pattern.strategic_response}
              </Typography>
            </Box>
          </Box>

          {/* Expected Impact Section */}
          {pattern.effect_size_hints && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                📊 Expected Impact
              </Typography>
              <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.6 }}>
                  {pattern.effect_size_hints}
                </Typography>
              </Box>
            </Box>
          )}

          {/* Outcome Measures Section */}
          {pattern.outcome_measures && pattern.outcome_measures.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                🎯 Outcome Measures
              </Typography>
              <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 1 }}>
                {pattern.outcome_measures.map((measure, idx) => (
                  <Typography 
                    key={idx} 
                    variant="body2" 
                    sx={{ color: 'rgba(255,255,255,0.9)', mb: 0.5 }}
                  >
                    • {measure}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}

          {/* Monte Carlo Simulation Results */}
          {scenario && scenario.expected_outcomes && (
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'white', mb: 2 }}>
                🎲 Monte Carlo Simulation Results ({scenario.simulation_count} iterations)
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(scenario.expected_outcomes).map(([kpi, results]) => (
                  <Grid item xs={12} md={6} key={kpi}>
                    <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                      <Typography 
                        variant="body2" 
                        sx={{ color: 'white', fontWeight: 'bold', mb: 1.5 }}
                      >
                        {kpi.replace(/_/g, ' ').toUpperCase()}
                      </Typography>
                      
                      {/* Mean Value */}
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          Mean (Expected Value)
                        </Typography>
                        <Typography variant="h6" sx={{ color: 'white' }}>
                          {results.mean?.toFixed(2)}
                        </Typography>
                      </Box>

                      {/* 95% Confidence Interval */}
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          95% Confidence Interval
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                          [{results.confidence_interval_95?.[0]?.toFixed(2)}, {results.confidence_interval_95?.[1]?.toFixed(2)}]
                        </Typography>
                      </Box>

                      {/* Probability of Positive Outcome */}
                      {results.probability_positive !== undefined && (
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                            Probability of Positive Outcome
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={results.probability_positive * 100}
                              sx={{ 
                                flexGrow: 1,
                                height: 8,
                                borderRadius: 1,
                                bgcolor: 'rgba(255,255,255,0.2)',
                                '& .MuiLinearProgress-bar': {
                                  bgcolor: results.probability_positive > 0.7 ? '#4CAF50' : results.probability_positive > 0.5 ? '#FF9800' : '#F44336',
                                  borderRadius: 1
                                }
                              }}
                            />
                            <Typography variant="body2" sx={{ color: 'white', fontWeight: 'bold', minWidth: 45 }}>
                              {(results.probability_positive * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </Box>
                      )}

                      {/* Standard Deviation */}
                      <Box>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          Std Dev (Variability): ±{results.std_dev?.toFixed(2)}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Data Source Footer */}
          <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid rgba(255,255,255,0.2)' }}>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)', fontStyle: 'italic' }}>
              💡 Pattern matched using actual v2.0 scoring results • 100% data-driven • No hardcoded values
            </Typography>
          </Box>
        </Box>
      }
    />
  );
};

export default PatternMatchCard;

