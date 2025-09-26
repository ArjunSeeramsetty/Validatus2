/**
 * Interactive Scenario Cards Grid
 */
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Collapse,
  Grid,
  LinearProgress
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  TrendingUp,
  TrendingDown,
  Warning,
  Star
} from '@mui/icons-material';

interface Scenario {
  name: string;
  probability: number;
  kpis: Record<string, number>;
  narrative: string;
  key_drivers: string[];
  risk_level: string;
}

interface ScenarioGridProps {
  scenarios: Scenario[];
  onScenarioSelect: (scenario: Scenario) => void;
}

const ScenarioGrid: React.FC<ScenarioGridProps> = ({ scenarios, onScenarioSelect }) => {
  const [expandedScenario, setExpandedScenario] = useState<string | null>(null);

  const getScenarioColor = (name: string) => {
    const colors: Record<string, string> = {
      'Base Case': '#52c41a',
      'Aggressive Growth': '#1890ff',
      'Crisis': '#ff4d4f',
      'Differentiation': '#fa8c16',
      'Wildcard': '#722ed1'
    };
    return colors[name] || '#d9d9d9';
  };

  const getScenarioIcon = (name: string, riskLevel: string) => {
    if (name.includes('Crisis')) return <Warning />;
    if (name.includes('Aggressive')) return <TrendingUp />;
    if (name.includes('Differentiation')) return <Star />;
    return <TrendingUp />;
  };

  const formatKPI = (key: string, value: number) => {
    const formatters: Record<string, (v: number) => string> = {
      'roi': (v) => `${(v * 100).toFixed(1)}%`,
      'payback_period': (v) => `${v.toFixed(1)} years`,
      'npv': (v) => `$${(v / 1000).toFixed(0)}K`,
      'adoption_rate': (v) => `${(v * 100).toFixed(1)}%`
    };
    
    return formatters[key]?.(value) || value.toFixed(2);
  };

  return (
    <Card sx={{ backgroundColor: '#1a1a35', border: '1px solid #3d3d56' }}>
      <CardContent>
        <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
          Strategic Scenarios
        </Typography>
        
        <Grid container spacing={2}>
          {scenarios.map((scenario) => (
            <Grid item xs={12} md={6} lg={4} key={scenario.name}>
              <Card 
                sx={{ 
                  backgroundColor: '#252547',
                  border: `2px solid ${getScenarioColor(scenario.name)}20`,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: getScenarioColor(scenario.name),
                    transform: 'translateY(-2px)',
                    boxShadow: `0 8px 24px ${getScenarioColor(scenario.name)}30`
                  }
                }}
                onClick={() => onScenarioSelect(scenario)}
              >
                <CardContent>
                  {/* Header */}
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box 
                      sx={{ 
                        color: getScenarioColor(scenario.name),
                        mr: 1 
                      }}
                    >
                      {getScenarioIcon(scenario.name, scenario.risk_level)}
                    </Box>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        color: '#e8e8f0',
                        fontSize: '1rem',
                        fontWeight: 600 
                      }}
                    >
                      {scenario.name}
                    </Typography>
                  </Box>

                  {/* Probability */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Probability: {(scenario.probability * 100).toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={scenario.probability * 100}
                      sx={{
                        backgroundColor: '#3d3d56',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getScenarioColor(scenario.name)
                        }
                      }}
                    />
                  </Box>

                  {/* Key KPIs */}
                  <Box sx={{ mb: 2 }}>
                    <Grid container spacing={1}>
                      {Object.entries(scenario.kpis).slice(0, 4).map(([key, value]) => (
                        <Grid item xs={6} key={key}>
                          <Typography 
                            variant="caption" 
                            sx={{ color: '#b8b8cc', display: 'block' }}
                          >
                            {key.replace('_', ' ').toUpperCase()}
                          </Typography>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              color: '#e8e8f0',
                              fontWeight: 600 
                            }}
                          >
                            {formatKPI(key, value)}
                          </Typography>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>

                  {/* Risk Level */}
                  <Chip
                    size="small"
                    label={`${scenario.risk_level} Risk`}
                    sx={{
                      backgroundColor: `${getScenarioColor(scenario.name)}20`,
                      color: getScenarioColor(scenario.name),
                      fontSize: '0.75rem'
                    }}
                  />

                  {/* Expandable Details */}
                  <Box sx={{ mt: 2 }}>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedScenario(
                          expandedScenario === scenario.name ? null : scenario.name
                        );
                      }}
                      sx={{ color: '#b8b8cc' }}
                    >
                      {expandedScenario === scenario.name ? <ExpandLess /> : <ExpandMore />}
                    </IconButton>
                  </Box>

                  <Collapse in={expandedScenario === scenario.name}>
                    <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #3d3d56' }}>
                      <Typography 
                        variant="body2" 
                        sx={{ color: '#b8b8cc', mb: 2 }}
                      >
                        {scenario.narrative}
                      </Typography>
                      
                      <Typography 
                        variant="caption" 
                        sx={{ color: '#b8b8cc', display: 'block', mb: 1 }}
                      >
                        Key Drivers:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {scenario.key_drivers.map((driver) => (
                          <Chip
                            key={driver}
                            size="small"
                            label={driver}
                            sx={{
                              backgroundColor: '#3d3d56',
                              color: '#e8e8f0',
                              fontSize: '0.7rem'
                            }}
                          />
                        ))}
                      </Box>
                    </Box>
                  </Collapse>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ScenarioGrid;
