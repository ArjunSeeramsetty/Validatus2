import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress
} from '@mui/material';
import {
  Psychology, Timeline, Security, AttachMoney, 
  TrendingUp, Assessment
} from '@mui/icons-material';

interface ConsumerJourneyFlowProps {
  data: {
    decision_journey?: any;
    trust_factors?: any;
    price_sensitivity?: any;
    behavioral_insights?: string[];
  };
}

export default function ConsumerJourneyFlow({ data }: ConsumerJourneyFlowProps) {
  // Ensure data is not undefined
  const safeData = data || {};
  
  // Default journey data
  const defaultJourney = {
    awareness: {
      stage_duration: "2-4 weeks",
      key_influences: ["Social media", "Home improvement shows", "Neighbors"],
      pain_points: ["Limited knowledge", "Price uncertainty"]
    },
    consideration: {
      stage_duration: "4-8 weeks",
      key_influences: ["Online reviews", "Showroom visits", "Expert consultations"],
      pain_points: ["Complex options", "Installation concerns"]
    },
    purchase: {
      stage_duration: "2-3 weeks",
      key_influences: ["Price negotiations", "Warranty terms", "Installation timeline"],
      pain_points: ["Final cost", "Contractor reliability"]
    }
  };

  const defaultTrustFactors = {
    brand_reputation: 4.2,
    product_quality: 4.5,
    installation_service: 4.1,
    warranty_support: 3.9
  };

  const defaultPriceSensitivity = {
    segments: {
      premium: { threshold: 15000, price_elasticity: -0.3 },
      mid_range: { threshold: 8000, price_elasticity: -0.7 },
      value: { threshold: 4000, price_elasticity: -1.2 }
    }
  };

  const journey = safeData?.decision_journey || defaultJourney;
  const trustFactors = safeData?.trust_factors || defaultTrustFactors;
  const priceSensitivity = safeData?.price_sensitivity || defaultPriceSensitivity;
  const behavioralInsights = safeData?.behavioral_insights || [
    "Consumers prioritize quality over price in premium segments",
    "Social proof significantly influences purchase decisions",
    "Installation service quality is a key differentiator"
  ];

  const journeySteps = [
    {
      label: 'Awareness',
      duration: journey.awareness.stage_duration,
      influences: journey.awareness.key_influences,
      painPoints: journey.awareness.pain_points
    },
    {
      label: 'Consideration',
      duration: journey.consideration.stage_duration,
      influences: journey.consideration.key_influences,
      painPoints: journey.consideration.pain_points
    },
    {
      label: 'Purchase',
      duration: journey.purchase.stage_duration,
      influences: journey.purchase.key_influences,
      painPoints: journey.purchase.pain_points
    }
  ];

  const getTrustScoreColor = (score: number) => {
    if (score >= 4.5) return 'success';
    if (score >= 4.0) return 'warning';
    return 'error';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Consumer Decision Journey */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Timeline />
                Consumer Decision Journey
              </Typography>
              <Stepper orientation="vertical" sx={{ mt: 2 }}>
                {journeySteps.map((step, index) => (
                  <Step key={index} active>
                    <StepLabel>
                      <Typography variant="h6">{step.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Duration: {step.duration}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            Key Influences
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                            {(step.influences || []).map((influence, influenceIndex) => (
                              <Chip
                                key={influenceIndex}
                                label={influence}
                                size="small"
                                color="primary"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2" color="error" gutterBottom>
                            Pain Points
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {(step.painPoints || []).map((painPoint, painIndex) => (
                              <Chip
                                key={painIndex}
                                label={painPoint}
                                size="small"
                                color="error"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </Grid>
                      </Grid>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </CardContent>
          </Card>
        </Grid>

        {/* Trust Factors */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Security />
                Trust Factors
              </Typography>
              <Box sx={{ mt: 2 }}>
                {Object.entries(trustFactors || {}).map(([factor, score]) => (
                  <Box key={factor} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {factor.replace('_', ' ')}
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {score}/5.0
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(score / 5) * 100}
                      color={getTrustScoreColor(score)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Price Sensitivity Analysis */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AttachMoney />
                Price Sensitivity Analysis
              </Typography>
              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Segment</TableCell>
                      <TableCell>Price Threshold</TableCell>
                      <TableCell>Price Elasticity</TableCell>
                      <TableCell>Market Behavior</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries((priceSensitivity.segments || {})).map(([segment, data]: [string, any]) => (
                      <TableRow key={segment}>
                        <TableCell>
                          <Chip
                            label={segment.replace('_', ' ').toUpperCase()}
                            color={segment === 'premium' ? 'success' : segment === 'mid_range' ? 'warning' : 'error'}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {formatCurrency(data.threshold)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {data.price_elasticity.toFixed(1)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {Math.abs(data.price_elasticity) < 0.5 
                              ? "Low price sensitivity" 
                              : Math.abs(data.price_elasticity) < 1.0 
                              ? "Moderate price sensitivity" 
                              : "High price sensitivity"
                            }
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Behavioral Insights */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Psychology />
                Behavioral Insights
              </Typography>
              <Box sx={{ mt: 2 }}>
                {(behavioralInsights || []).map((insight, index) => (
                  <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2">
                      {insight}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
