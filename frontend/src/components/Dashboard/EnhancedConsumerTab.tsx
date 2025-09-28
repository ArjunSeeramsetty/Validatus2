/**
 * Enhanced Consumer Tab with Tile-Based Factor Analysis
 * Three tiles per row design for better visual organization
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  People,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Info,
  Psychology,
  Favorite,
  Visibility,
  TouchApp
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const EnhancedConsumerTab: React.FC<{ data: any }> = ({ data }) => {
  const [consumerMetrics, setConsumerMetrics] = useState({
    demandScore: 78,
    behaviorScore: 85,
    loyaltyScore: 72,
    perceptionScore: 88,
    adoptionScore: 76
  });

  const [consumerFactors, setConsumerFactors] = useState([
    {
      id: 'demand_need',
      title: 'Consumer Demand & Need',
      icon: Psychology,
      score: 78,
      trend: 'up',
      change: '+12%',
      description: 'Strong demand for outdoor living solutions with 30-80% own-price elasticity',
      impact: 'Volume, Adoption',
      confidence: 0.85,
      color: '#52c41a',
      details: {
        keyMetrics: ['Price Elasticity: 30-80%', 'Market Penetration: 25%', 'Need Intensity: High'],
        insights: ['Post-COVID outdoor living trend', 'Premium lifestyle investments', 'Weather-independent usage']
      }
    },
    {
      id: 'behavior_habits',
      title: 'Consumer Behavior & Habits',
      icon: TouchApp,
      score: 85,
      trend: 'stable',
      change: '+2%',
      description: 'Weekly vs monthly usage patterns show strong engagement potential',
      impact: 'Conversion, Retention',
      confidence: 0.78,
      color: '#1890ff',
      details: {
        keyMetrics: ['Usage Frequency: Weekly', 'Engagement Rate: 78%', 'Session Duration: 45min'],
        insights: ['Seasonal usage patterns', 'Entertainment focus', 'Family gathering preference']
      }
    },
    {
      id: 'loyalty_retention',
      title: 'Consumer Loyalty & Retention',
      icon: Favorite,
      score: 72,
      trend: 'up',
      change: '+8%',
      description: 'Retention baseline 60-85% with 5-15% loyalty uplift potential',
      impact: 'Retention, NRR',
      confidence: 0.82,
      color: '#eb2f96',
      details: {
        keyMetrics: ['Base Retention: 60-85%', 'Loyalty Uplift: 5-15%', 'NPS Score: 72'],
        insights: ['Brand switching costs', 'Service quality impact', 'Community effect']
      }
    },
    {
      id: 'perception_sentiment',
      title: 'Consumer Perception & Sentiment',
      icon: Visibility,
      score: 88,
      trend: 'up',
      change: '+15%',
      description: 'Strong prestige multiplier (0.10-0.30) driven by outdoor lifestyle trends',
      impact: 'Adoption, ASP',
      confidence: 0.90,
      color: '#fa8c16',
      details: {
        keyMetrics: ['Prestige Factor: 0.10-0.30', 'Brand Awareness: 88%', 'Sentiment Score: 4.2/5'],
        insights: ['Luxury positioning', 'Status symbol effect', 'Social media influence']
      }
    },
    {
      id: 'adoption_engagement',
      title: 'Consumer Adoption & Engagement',
      icon: TrendingUp,
      score: 76,
      trend: 'up',
      change: '+10%',
      description: 'Referral boost potential +5-12pp with strong network effects',
      impact: 'Adoption, Conversion',
      confidence: 0.75,
      color: '#722ed1',
      details: {
        keyMetrics: ['Referral Rate: +5-12pp', 'Adoption Rate: 76%', 'Time to Value: 2 weeks'],
        insights: ['Word-of-mouth marketing', 'Demonstration effect', 'Early adopter influence']
      }
    },
    {
      id: 'market_readiness',
      title: 'Market Readiness & Timing',
      icon: People,
      score: 82,
      trend: 'stable',
      change: '+3%',
      description: 'Optimal market conditions with high consumer readiness scores',
      impact: 'Market Entry, Timing',
      confidence: 0.87,
      color: '#13c2c2',
      details: {
        keyMetrics: ['Readiness Score: 82%', 'Market Timing: Optimal', 'Competition Gap: Medium'],
        insights: ['Economic conditions favorable', 'Consumer spending power', 'Market education level']
      }
    }
  ]);

  useEffect(() => {
    if (data) {
      // Extract consumer-specific data from the analysis results
      const consumerFactorData = data.strategic_factors || {};
      
      // Calculate consumer metrics from actual data
      const consumerFactorKeys = Object.keys(consumerFactorData).filter(key => 
        key.toLowerCase().includes('consumer') || 
        key.toLowerCase().includes('customer') ||
        key.toLowerCase().includes('demand') ||
        key.toLowerCase().includes('behavior') ||
        key.toLowerCase().includes('loyalty') ||
        key.toLowerCase().includes('perception') ||
        key.toLowerCase().includes('adoption')
      );
      
      if (consumerFactorKeys.length > 0) {
        const factorValues = consumerFactorKeys.map(key => {
          const value = consumerFactorData[key];
          return typeof value === 'number' ? value : 0.5;
        });
        
        const avgScore = factorValues.reduce((sum, val) => sum + val, 0) / factorValues.length;
        const normalizedScore = Math.round(avgScore * 100);
        
        setConsumerMetrics({
          demandScore: Math.min(100, Math.max(0, normalizedScore)),
          behaviorScore: Math.min(100, Math.max(0, Math.round(normalizedScore * 1.1))),
          loyaltyScore: Math.min(100, Math.max(0, Math.round(normalizedScore * 0.9))),
          perceptionScore: Math.min(100, Math.max(0, Math.round(normalizedScore * 1.15))),
          adoptionScore: Math.min(100, Math.max(0, Math.round(normalizedScore * 0.95)))
        });
      }
    }
  }, [data]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp />;
      case 'down': return <TrendingDown />;
      default: return <TrendingFlat />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#fa8c16';
    return '#ff4d4f';
  };

  return (
    <Box>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          sx={{ 
            color: '#e8e8f0', 
            fontWeight: 700, 
            mb: 1,
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <People sx={{ mr: 2, color: '#52c41a', fontSize: 36 }} />
          Consumer Intelligence Analysis
        </Typography>
        <Typography variant="subtitle1" sx={{ color: '#b8b8cc' }}>
          Comprehensive consumer behavior insights and factor analysis
        </Typography>
      </Box>

      {/* Consumer Metrics Overview */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
          Consumer Metrics Overview
        </Typography>
        
        <Grid container spacing={2}>
          {Object.entries(consumerMetrics).map(([key, score]) => (
            <Grid item xs={12} sm={6} md={2.4} key={key}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Paper sx={{ 
                  p: 2, 
                  backgroundColor: '#252547', 
                  border: '1px solid #3d3d56',
                  textAlign: 'center',
                  height: '140px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}>
                  <Typography 
                    variant="h3" 
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
                      textTransform: 'capitalize',
                      mb: 1
                    }}
                  >
                    {key.replace('Score', '').replace(/([A-Z])/g, ' $1')}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={score}
                    sx={{
                      backgroundColor: '#3d3d56',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getScoreColor(score)
                      }
                    }}
                  />
                </Paper>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Consumer Factor Analysis - Tile Layout (3 per row) */}
      <Box>
        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
          Consumer Factor Analysis
        </Typography>
        
        <Grid container spacing={3}>
          {consumerFactors.map((factor, index) => (
            <Grid item xs={12} md={4} key={factor.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card sx={{
                  backgroundColor: '#252547',
                  border: `1px solid ${factor.color}30`,
                  height: '100%',
                  position: 'relative',
                  overflow: 'visible',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    transition: 'transform 0.3s ease',
                    boxShadow: `0 8px 25px ${factor.color}20`
                  }
                }}>
                  <CardContent sx={{ p: 3 }}>
                    {/* Header */}
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      justifyContent: 'space-between',
                      mb: 2
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                        <Box sx={{
                          p: 1,
                          backgroundColor: `${factor.color}20`,
                          borderRadius: 2,
                          mr: 2
                        }}>
                          <factor.icon sx={{ color: factor.color, fontSize: 24 }} />
                        </Box>
                        
                        <Box sx={{ flex: 1 }}>
                          <Typography 
                            variant="subtitle1" 
                            sx={{ 
                              color: '#e8e8f0', 
                              fontWeight: 600,
                              lineHeight: 1.2
                            }}
                          >
                            {factor.title}
                          </Typography>
                        </Box>
                      </Box>

                      <Tooltip title="Factor Information">
                        <IconButton size="small" sx={{ color: '#b8b8cc' }}>
                          <Info fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    {/* Score and Trend */}
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      mb: 2 
                    }}>
                      <Typography 
                        variant="h3" 
                        sx={{ 
                          color: factor.color,
                          fontWeight: 700
                        }}
                      >
                        {factor.score}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getTrendIcon(factor.trend)}
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: factor.trend === 'up' ? '#52c41a' : 
                                   factor.trend === 'down' ? '#ff4d4f' : '#b8b8cc',
                            fontWeight: 600,
                            ml: 0.5
                          }}
                        >
                          {factor.change}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Progress Bar */}
                    <LinearProgress
                      variant="determinate"
                      value={factor.score}
                      sx={{
                        mb: 2,
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: '#3d3d56',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: factor.color,
                          borderRadius: 3
                        }
                      }}
                    />

                    {/* Description */}
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#b8b8cc',
                        mb: 2,
                        lineHeight: 1.4
                      }}
                    >
                      {factor.description}
                    </Typography>

                    {/* Tags */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      <Chip
                        size="small"
                        label={`Impact: ${factor.impact}`}
                        sx={{
                          backgroundColor: `${factor.color}20`,
                          color: factor.color,
                          fontSize: '0.7rem',
                          height: 24
                        }}
                      />
                      <Chip
                        size="small"
                        label={`Confidence: ${(factor.confidence * 100).toFixed(0)}%`}
                        sx={{
                          backgroundColor: '#52c41a20',
                          color: '#52c41a',
                          fontSize: '0.7rem',
                          height: 24
                        }}
                      />
                    </Box>

                    {/* Key Metrics */}
                    <Box>
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          color: '#b8b8cc',
                          display: 'block',
                          mb: 1,
                          textTransform: 'uppercase',
                          letterSpacing: 0.5
                        }}
                      >
                        Key Metrics
                      </Typography>
                      
                      {factor.details.keyMetrics.slice(0, 2).map((metric, idx) => (
                        <Typography 
                          key={idx}
                          variant="caption" 
                          sx={{ 
                            color: '#e8e8f0',
                            display: 'block',
                            fontSize: '0.75rem',
                            mb: 0.5
                          }}
                        >
                          • {metric}
                        </Typography>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
};

export default EnhancedConsumerTab;
