// frontend/src/components/SegmentContent.tsx

import React from 'react';
import { Box, Grid, Typography, Alert, AlertTitle } from '@mui/material';
import ExpandableTile from './Common/ExpandableTile';

interface SegmentContentProps {
  segment: string;
  data: any;
}

const SegmentContent: React.FC<SegmentContentProps> = ({ segment, data }) => {
  const { factors, matched_patterns, monte_carlo_scenarios, personas, rich_content } = data;

  // Validate data exists
  if (!data) {
    return (
      <Typography color="error">
        No data available for {segment} segment
      </Typography>
    );
  }

  return (
    <Box>
      {/* Monte Carlo Scenarios */}
      {monte_carlo_scenarios && monte_carlo_scenarios.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            🎲 Monte Carlo Scenarios ({monte_carlo_scenarios.length} scenarios)
          </Typography>
          <Grid container spacing={3}>
            {monte_carlo_scenarios.map((scenario: any, index: number) => (
              <Grid item xs={12} md={6} key={scenario.scenario_id || index}>
                <ExpandableTile
                  title={scenario.pattern_name || `Scenario ${index + 1}`}
                  bgcolor="#1976D2"
                  textColor="#FFFFFF"
                  content={scenario.strategic_response || 'No description available'}
                  confidence={scenario.probability_success}
                  additionalContent={
                    <Box>
                      <Typography variant="subtitle2" sx={{ color: 'white', mb: 1 }}>
                        KPI Results (1000 iterations)
                      </Typography>
                      {scenario.kpi_results && Object.entries(scenario.kpi_results).map(([kpi, results]: [string, any]) => (
                        <Box key={kpi} sx={{ mb: 1, p: 1, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                          <Typography variant="caption" sx={{ color: 'white', display: 'block' }}>
                            {kpi}: Mean {results.mean?.toFixed(2)}, 95% CI [{results.confidence_interval_95?.[0]?.toFixed(2)}, {results.confidence_interval_95?.[1]?.toFixed(2)}]
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  }
                  chips={[scenario.pattern_id, `${(scenario.probability_success * 100).toFixed(0)}% Success`]}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Personas (Consumer only) */}
      {segment === 'consumer' && personas && personas.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            👥 Consumer Personas
          </Typography>
          <Grid container spacing={3}>
            {personas.map((persona: any, index: number) => (
              <Grid item xs={12} md={6} key={index}>
                <ExpandableTile
                  title={`${persona.name} (${persona.age})`}
                  bgcolor="#7E57C2"
                  textColor="#FFFFFF"
                  content={`${persona.value_tier} • ${(persona.market_share * 100).toFixed(0)}% Market Share`}
                  confidence={persona.confidence}
                  additionalContent={
                    <Box>
                      <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
                        <strong>Pain Points:</strong>
                      </Typography>
                      {persona.pain_points?.map((point: string, i: number) => (
                        <Typography key={i} variant="caption" sx={{ color: 'rgba(255,255,255,0.9)', display: 'block' }}>
                          • {point}
                        </Typography>
                      ))}
                    </Box>
                  }
                  chips={[persona.value_tier]}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Rich Content (Product/Brand/Experience) */}
      {rich_content && Object.keys(rich_content).length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            📊 {segment.charAt(0).toUpperCase() + segment.slice(1)} Intelligence
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {JSON.stringify(rich_content, null, 2)}
          </Typography>
        </Box>
      )}

      {/* Factors Display */}
      {factors && Object.keys(factors).length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            📈 Factor Analysis
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(factors).map(([factorId, factorData]: [string, any]) => (
              <Grid item xs={12} sm={6} md={4} key={factorId}>
                <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    {factorId}
                  </Typography>
                  <Typography variant="h6" color="primary">
                    {(factorData.value * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Confidence: {(factorData.confidence * 100).toFixed(0)}%
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* No Data Message */}
      {(!monte_carlo_scenarios || monte_carlo_scenarios.length === 0) &&
       (!personas || personas.length === 0) &&
       (!rich_content || Object.keys(rich_content).length === 0) &&
       (!factors || Object.keys(factors).length === 0) && (
        <Alert severity="info">
          <AlertTitle>No Data Available</AlertTitle>
          Results have not been generated for this segment yet. Please ensure:
          <ul>
            <li>Scoring is complete</li>
            <li>Results generation has been triggered</li>
            <li>Database contains data for this topic</li>
          </ul>
        </Alert>
      )}
    </Box>
  );
};

export default SegmentContent;
