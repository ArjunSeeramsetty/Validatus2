/**
 * Market Segment Analysis Tab
 * Shows market trends, competition, and growth scenarios
 */
import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Public
} from '@mui/icons-material';

const MarketTab: React.FC<{ data: any }> = () => {
  const marketMetrics = {
    trendsScore: 82,
    competitionScore: 68,
    demandScore: 85,
    growthScore: 78,
    stabilityScore: 65
  };

  const marketFactors = [
    {
      factor: 'Market Trends & Dynamics',
      score: 82,
      impact: 'Volume, Adoption',
      description: '3-9% CAGR with strong outdoor living momentum',
      distribution: 'Triangular',
      range: '3-9% growth rate',
      confidence: 0.85
    },
    {
      factor: 'Competition & Barriers',
      score: 68,
      impact: 'Conversion, Margin',
      description: 'Mixed permit environment with rivalry cost pressures',
      distribution: 'Bernoulli + Normal',
      range: '55-85% permit probability',
      confidence: 0.72
    },
    {
      factor: 'Market Demand & Adoption',
      score: 85,
      impact: 'Volume, Adoption',
      description: 'Strong demand spread with 3-7% adoption CAGR',
      distribution: 'Triangular',
      range: '3-7% adoption rate',
      confidence: 0.88
    },
    {
      factor: 'Growth & Expansion',
      score: 78,
      impact: 'Volume, NPV',
      description: 'Regional expansion opportunities in adjacent markets',
      distribution: 'Triangular',
      range: '3-8% market expansion',
      confidence: 0.80
    },
    {
      factor: 'Market Stability & Risk',
      score: 65,
      impact: 'COGS, Margin',
      description: 'Cost volatility from supply chain and regulatory shifts',
      distribution: 'Normal',
      range: '0-35% cost variance',
      confidence: 0.75
    }
  ];

  const competitiveScenarios = [
    {
      name: 'Market Leadership',
      probability: 30,
      color: '#52c41a',
      description: 'Strong differentiation drives premium positioning',
      marketShare: 25,
      marginImpact: 15,
      volumeGrowth: 35
    },
    {
      name: 'Competitive Parity',
      probability: 50,
      color: '#1890ff',
      description: 'Balanced competitive environment with steady growth',
      marketShare: 15,
      marginImpact: 0,
      volumeGrowth: 12
    },
    {
      name: 'Price Competition',
      probability: 20,
      color: '#ff4d4f',
      description: 'Intense price pressure reduces margins',
      marketShare: 10,
      marginImpact: -18,
      volumeGrowth: -5
    }
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  const getDistributionColor = (dist: string) => {
    const colors: Record<string, string> = {
      'Triangular': '#1890ff',
      'Normal': '#52c41a',
      'Bernoulli + Normal': '#fa8c16',
      'Beta': '#722ed1'
    };
    return colors[dist] || '#d9d9d9';
  };

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={3}>
        {/* Market Metrics Overview */}
        <Grid item xs={12}>
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Public sx={{ color: '#fa8c16', mr: 2, fontSize: 28 }} />
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  Market Intelligence Overview
                </Typography>
              </Box>

              <Grid container spacing={3} columns={{ md: 15 }}>
                {Object.entries(marketMetrics).map(([key, score]) => (
                  <Grid item xs={12} sm={6} md={3} key={key}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography 
                        variant="h4" 
                        sx={{ 
                          color: getScoreColor(score), 
                          fontWeight: 700,
                          mb: 1
                        }}
                      >
                        {score}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#b8b8cc',
                          textTransform: 'capitalize'
                        }}
                      >
                        {key.replace('Score', '')}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={score}
                        sx={{
                          mt: 1,
                          backgroundColor: '#3d3d56',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getScoreColor(score)
                          }
                        }}
                      />
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Market Factor Analysis */}
        <Grid item xs={12} md={8}>
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
                Market Factor Analysis
              </Typography>

              <TableContainer component={Paper} sx={{ backgroundColor: '#1a1a35' }}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#252547' }}>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Factor</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Score</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Distribution</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Range</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Confidence</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {marketFactors.map((factor, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                              {factor.factor}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              Impact: {factor.impact}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography 
                              variant="h6" 
                              sx={{ 
                                color: getScoreColor(factor.score),
                                fontWeight: 700,
                                minWidth: 30
                              }}
                            >
                              {factor.score}
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={factor.score}
                              sx={{
                                width: 60,
                                backgroundColor: '#3d3d56',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: getScoreColor(factor.score)
                                }
                              }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={factor.distribution}
                            sx={{
                              backgroundColor: `${getDistributionColor(factor.distribution)}20`,
                              color: getDistributionColor(factor.distribution),
                              fontSize: '0.75rem'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#b8b8cc', fontSize: '0.875rem' }}>
                          {factor.range}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={factor.confidence * 100}
                              sx={{
                                width: 50,
                                backgroundColor: '#3d3d56',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: '#52c41a'
                                }
                              }}
                            />
                            <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                              {(factor.confidence * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Competitive Scenarios */}
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
                Competitive Scenarios
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {competitiveScenarios.map((scenario, index) => (
                  <Paper
                    key={index}
                    sx={{
                      backgroundColor: '#1a1a35',
                      border: `1px solid ${scenario.color}30`,
                      p: 2
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                      <Typography 
                        variant="subtitle1" 
                        sx={{ color: scenario.color, fontWeight: 600 }}
                      >
                        {scenario.name}
                      </Typography>
                      <Chip
                        size="small"
                        label={`${scenario.probability}%`}
                        sx={{
                          backgroundColor: `${scenario.color}20`,
                          color: scenario.color
                        }}
                      />
                    </Box>

                    <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 2 }}>
                      {scenario.description}
                    </Typography>

                    <Grid container spacing={1}>
                      <Grid item xs={4}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="caption" sx={{ color: '#b8b8cc', display: 'block' }}>
                            SHARE
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                            {scenario.marketShare}%
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={4}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="caption" sx={{ color: '#b8b8cc', display: 'block' }}>
                            MARGIN
                          </Typography>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              color: scenario.marginImpact > 0 ? '#52c41a' : scenario.marginImpact < 0 ? '#ff4d4f' : '#e8e8f0',
                              fontWeight: 600
                            }}
                          >
                            {scenario.marginImpact > 0 ? '+' : ''}{scenario.marginImpact}%
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={4}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="caption" sx={{ color: '#b8b8cc', display: 'block' }}>
                            VOLUME
                          </Typography>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              color: scenario.volumeGrowth > 0 ? '#52c41a' : scenario.volumeGrowth < 0 ? '#ff4d4f' : '#e8e8f0',
                              fontWeight: 600
                            }}
                          >
                            {scenario.volumeGrowth > 0 ? '+' : ''}{scenario.volumeGrowth}%
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </Paper>
                ))}
              </Box>
            </CardContent>
          </Card>

        </Grid>
      </Grid>
    </Box>
  );
};

export default MarketTab;