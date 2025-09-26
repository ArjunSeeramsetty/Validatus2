/**
 * Business Case Tab with Live Calculator
 * Matches Figma Business Case design exactly
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  TextField,
  Typography,
  Paper,
  Slider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress
} from '@mui/material';
import {
  Calculate,
  TrendingUp,
  AttachMoney,
  Timeline,
  Analytics
} from '@mui/icons-material';

interface BusinessCaseInputs {
  unitPrice: number;
  unitCost: number;
  expectedVolume: number;
  fixedCosts: number;
  innovationCost: number;
  discountRate: number;
}

interface CalculatedMetrics {
  grossMargin: number;
  grossMarginPercent: number;
  totalContribution: number;
  breakevenVolume: number;
  paybackPeriod: number;
  simpleROI: number;
  npv: number;
  irr: number;
}

const BusinessCaseTab: React.FC<{ data: any }> = ({ data }) => {
  const [inputs, setInputs] = useState<BusinessCaseInputs>({
    unitPrice: 1200,
    unitCost: 800,
    expectedVolume: 1000,
    fixedCosts: 200000,
    innovationCost: 100000,
    discountRate: 0.12
  });

  const [metrics, setMetrics] = useState<CalculatedMetrics | null>(null);
  const [scenarioResults, setScenarioResults] = useState<any[]>([]);

  useEffect(() => {
    calculateMetrics();
    runScenarioAnalysis();
  }, [inputs]);

  const calculateWithBackend = async (inputs: BusinessCaseInputs) => {
    try {
      const response = await fetch('http://localhost:8000/api/v3/dashboard/v2_analysis_20250905_185553_d5654178/business-case/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          unit_price: inputs.unitPrice,
          unit_cost: inputs.unitCost,
          expected_volume: inputs.expectedVolume,
          fixed_costs: inputs.fixedCosts,
          innovation_cost: inputs.innovationCost,
          discount_rate: inputs.discountRate
        })
      });
      
      const result = await response.json();
      if (result.success) {
        setMetrics({
          grossMargin: result.metrics.gross_margin,
          grossMarginPercent: result.metrics.gross_margin_percent,
          totalContribution: result.metrics.total_contribution,
          breakevenVolume: result.metrics.breakeven_volume,
          paybackPeriod: result.metrics.payback_period,
          simpleROI: result.metrics.simple_roi,
          npv: result.metrics.npv,
          irr: result.metrics.irr
        });
        setScenarioResults(result.scenarios);
      }
    } catch (error) {
      console.error('Backend calculation failed, using local calculation:', error);
      calculateMetrics();
      runScenarioAnalysis();
    }
  };

  const calculateMetrics = () => {
    const grossMargin = inputs.unitPrice - inputs.unitCost;
    const grossMarginPercent = (grossMargin / inputs.unitPrice) * 100;
    const totalContribution = grossMargin * inputs.expectedVolume;
    const breakevenVolume = inputs.fixedCosts / grossMargin;
    const paybackPeriod = inputs.innovationCost / (totalContribution - inputs.fixedCosts);
    const simpleROI = ((totalContribution - inputs.fixedCosts - inputs.innovationCost) / inputs.innovationCost) * 100;
    
    // NPV calculation (5-year projection)
    let npv = -inputs.innovationCost;
    for (let year = 1; year <= 5; year++) {
      const cashFlow = totalContribution - inputs.fixedCosts;
      npv += cashFlow / Math.pow(1 + inputs.discountRate, year);
    }

    // IRR approximation
    const irr = ((totalContribution - inputs.fixedCosts) / inputs.innovationCost) * 100;

    setMetrics({
      grossMargin,
      grossMarginPercent,
      totalContribution,
      breakevenVolume,
      paybackPeriod,
      simpleROI,
      npv,
      irr
    });
  };

  const runScenarioAnalysis = () => {
    const scenarios = [
      {
        name: 'Conservative',
        multiplier: 0.8,
        color: '#ff4d4f',
        probability: 25
      },
      {
        name: 'Base Case',
        multiplier: 1.0,
        color: '#52c41a',
        probability: 50
      },
      {
        name: 'Optimistic',
        multiplier: 1.3,
        color: '#1890ff',
        probability: 25
      }
    ];

    const results = scenarios.map(scenario => {
      const adjustedVolume = inputs.expectedVolume * scenario.multiplier;
      const adjustedPrice = inputs.unitPrice * (1 + (scenario.multiplier - 1) * 0.1);
      const grossMargin = adjustedPrice - inputs.unitCost;
      const contribution = grossMargin * adjustedVolume;
      const roi = ((contribution - inputs.fixedCosts - inputs.innovationCost) / inputs.innovationCost) * 100;
      
      return {
        ...scenario,
        volume: adjustedVolume,
        price: adjustedPrice,
        contribution,
        roi
      };
    });

    setScenarioResults(results);
  };

  const handleInputChange = (field: keyof BusinessCaseInputs, value: number) => {
    const newInputs = { ...inputs, [field]: value };
    setInputs(newInputs);
    // Use backend calculation for real-time updates
    calculateWithBackend(newInputs);
  };

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);

  const formatPercent = (value: number) => `${value.toFixed(1)}%`;

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={3}>
        {/* Left Panel - Inputs */}
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56', height: 'fit-content' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Calculate sx={{ color: '#1890ff', mr: 2 }} />
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  Business Inputs
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Unit Price ($)
                </Typography>
                <TextField
                  type="number"
                  value={inputs.unitPrice}
                  onChange={(e) => handleInputChange('unitPrice', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: '#1a1a35',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' },
                      '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputBase-input': { color: '#e8e8f0' }
                  }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Unit Cost ($)
                </Typography>
                <TextField
                  type="number"
                  value={inputs.unitCost}
                  onChange={(e) => handleInputChange('unitCost', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: '#1a1a35',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' },
                      '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputBase-input': { color: '#e8e8f0' }
                  }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 2 }}>
                  Expected Volume: {inputs.expectedVolume.toLocaleString()} units
                </Typography>
                <Slider
                  value={inputs.expectedVolume}
                  onChange={(_, value) => handleInputChange('expectedVolume', value as number)}
                  min={100}
                  max={5000}
                  step={100}
                  sx={{
                    color: '#1890ff',
                    '& .MuiSlider-thumb': {
                      backgroundColor: '#1890ff'
                    },
                    '& .MuiSlider-track': {
                      backgroundColor: '#1890ff'
                    },
                    '& .MuiSlider-rail': {
                      backgroundColor: '#3d3d56'
                    }
                  }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Fixed Costs ($)
                </Typography>
                <TextField
                  type="number"
                  value={inputs.fixedCosts}
                  onChange={(e) => handleInputChange('fixedCosts', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: '#1a1a35',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' },
                      '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputBase-input': { color: '#e8e8f0' }
                  }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Innovation Cost ($)
                </Typography>
                <TextField
                  type="number"
                  value={inputs.innovationCost}
                  onChange={(e) => handleInputChange('innovationCost', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: '#1a1a35',
                      '& fieldset': { borderColor: '#3d3d56' },
                      '&:hover fieldset': { borderColor: '#1890ff' },
                      '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                    },
                    '& .MuiInputBase-input': { color: '#e8e8f0' }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Center Panel - Key Metrics */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            {/* Gross Margin */}
            <Grid item xs={12}>
              <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AttachMoney sx={{ color: '#52c41a', mr: 1 }} />
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      Gross Margin
                    </Typography>
                  </Box>
                  <Typography variant="h3" sx={{ color: '#52c41a', fontWeight: 700 }}>
                    {formatPercent(metrics?.grossMarginPercent || 0)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    {formatCurrency(metrics?.grossMargin || 0)} per unit
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Breakeven Volume */}
            <Grid item xs={12}>
              <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TrendingUp sx={{ color: '#fa8c16', mr: 1 }} />
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      Breakeven Volume
                    </Typography>
                  </Box>
                  <Typography variant="h3" sx={{ color: '#fa8c16', fontWeight: 700 }}>
                    {Math.round(metrics?.breakevenVolume || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    units to break even
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* ROI */}
            <Grid item xs={12}>
              <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Analytics sx={{ color: '#1890ff', mr: 1 }} />
                    <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                      Simple ROI
                    </Typography>
                  </Box>
                  <Typography variant="h3" sx={{ color: '#1890ff', fontWeight: 700 }}>
                    {formatPercent(metrics?.simpleROI || 0)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                    return on investment
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Right Panel - Financial Projections */}
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Timeline sx={{ color: '#722ed1', mr: 2 }} />
                <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                  Financial Metrics
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Total Contribution
                </Typography>
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  {formatCurrency(metrics?.totalContribution || 0)}
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Payback Period
                </Typography>
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  {(metrics?.paybackPeriod || 0).toFixed(1)} years
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Net Present Value (5yr)
                </Typography>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: (metrics?.npv || 0) > 0 ? '#52c41a' : '#ff4d4f', 
                    fontWeight: 600 
                  }}
                >
                  {formatCurrency(metrics?.npv || 0)}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Internal Rate of Return
                </Typography>
                <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  {formatPercent(metrics?.irr || 0)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Bottom Panel - Scenario Analysis */}
        <Grid item xs={12}>
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3 }}>
                Scenario Analysis
              </Typography>

              <TableContainer component={Paper} sx={{ backgroundColor: '#1a1a35' }}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#252547' }}>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Scenario</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Probability</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Volume</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Price</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>Contribution</TableCell>
                      <TableCell sx={{ color: '#e8e8f0', fontWeight: 600 }}>ROI</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {scenarioResults.map((scenario, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip
                            label={scenario.name}
                            sx={{
                              backgroundColor: `${scenario.color}20`,
                              color: scenario.color,
                              fontWeight: 600
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#b8b8cc' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={scenario.probability}
                              sx={{
                                width: 60,
                                backgroundColor: '#3d3d56',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: scenario.color
                                }
                              }}
                            />
                            {scenario.probability}%
                          </Box>
                        </TableCell>
                        <TableCell sx={{ color: '#e8e8f0' }}>
                          {Math.round(scenario.volume).toLocaleString()}
                        </TableCell>
                        <TableCell sx={{ color: '#e8e8f0' }}>
                          {formatCurrency(scenario.price)}
                        </TableCell>
                        <TableCell sx={{ color: '#e8e8f0' }}>
                          {formatCurrency(scenario.contribution)}
                        </TableCell>
                        <TableCell sx={{ 
                          color: scenario.roi > 0 ? '#52c41a' : '#ff4d4f',
                          fontWeight: 600
                        }}>
                          {formatPercent(scenario.roi)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BusinessCaseTab;
