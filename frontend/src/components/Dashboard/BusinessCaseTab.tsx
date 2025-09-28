/**
 * Business Case Tab with Live Calculator - Fixed Version
 * Ensures Discount Rate and Time Duration inputs are properly rendered
 */
import { useState, useEffect } from 'react';
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
import PergolaChat from '../chat/PergolaChat';

interface BusinessCaseInputs {
  unitPrice: number;
  unitCost: number;
  expectedVolume: number;
  fixedCosts: number;
  innovationCost: number;
  discountRate: number;
  timeDuration: number;
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

const BusinessCaseTab = () => {
  const [inputs, setInputs] = useState<BusinessCaseInputs>({
    unitPrice: 1200,
    unitCost: 800,
    expectedVolume: 1000,
    fixedCosts: 200000,
    innovationCost: 100000,
    discountRate: 0.12,
    timeDuration: 5
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
          discount_rate: inputs.discountRate,
          time_duration: inputs.timeDuration
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
    
    // NPV calculation (using dynamic time duration)
    let npv = -inputs.innovationCost;
    for (let year = 1; year <= inputs.timeDuration; year++) {
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
          <Card sx={{ 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            height: 'fit-content'
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3, display: 'flex', alignItems: 'center' }}>
                <Calculate sx={{ mr: 1 }} />
                Business Inputs
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Unit Price */}
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Unit Price ($)
                  </Typography>
                  <TextField
                    type="number"
                    value={inputs.unitPrice}
                    onChange={(e) => handleInputChange('unitPrice', Number(e.target.value))}
                    fullWidth
                    variant="outlined"
                    label="Unit Price in USD"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#1a1a35',
                        '& fieldset': { borderColor: '#3d3d56' },
                        '&:hover fieldset': { borderColor: '#1890ff' },
                        '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                      },
                      '& .MuiInputBase-input': { color: '#e8e8f0' },
                      '& .MuiInputLabel-root': { color: '#b8b8cc' }
                    }}
                  />
                </Box>

                {/* Unit Cost */}
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Unit Cost ($)
                  </Typography>
                  <TextField
                    type="number"
                    value={inputs.unitCost}
                    onChange={(e) => handleInputChange('unitCost', Number(e.target.value))}
                    fullWidth
                    variant="outlined"
                    label="Unit Cost in USD"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#1a1a35',
                        '& fieldset': { borderColor: '#3d3d56' },
                        '&:hover fieldset': { borderColor: '#1890ff' },
                        '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                      },
                      '& .MuiInputBase-input': { color: '#e8e8f0' },
                      '& .MuiInputLabel-root': { color: '#b8b8cc' }
                    }}
                  />
                </Box>

                {/* Expected Volume */}
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Expected Volume: {inputs.expectedVolume.toLocaleString()} units
                  </Typography>
                  <Slider
                    value={inputs.expectedVolume}
                    onChange={(_, value) => handleInputChange('expectedVolume', value as number)}
                    min={100}
                    max={5000}
                    step={100}
                    aria-label="Expected Volume"
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `${value.toLocaleString()} units`}
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

                {/* Fixed Costs */}
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Fixed Costs ($)
                  </Typography>
                  <TextField
                    type="number"
                    value={inputs.fixedCosts}
                    onChange={(e) => handleInputChange('fixedCosts', Number(e.target.value))}
                    fullWidth
                    variant="outlined"
                    label="Fixed Costs in USD"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#1a1a35',
                        '& fieldset': { borderColor: '#3d3d56' },
                        '&:hover fieldset': { borderColor: '#1890ff' },
                        '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                      },
                      '& .MuiInputBase-input': { color: '#e8e8f0' },
                      '& .MuiInputLabel-root': { color: '#b8b8cc' }
                    }}
                  />
                </Box>

                {/* Innovation Cost */}
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Innovation Cost ($)
                  </Typography>
                  <TextField
                    type="number"
                    value={inputs.innovationCost}
                    onChange={(e) => handleInputChange('innovationCost', Number(e.target.value))}
                    fullWidth
                    variant="outlined"
                    label="Innovation Cost in USD"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#1a1a35',
                        '& fieldset': { borderColor: '#3d3d56' },
                        '&:hover fieldset': { borderColor: '#1890ff' },
                        '&.Mui-focused fieldset': { borderColor: '#1890ff' }
                      },
                      '& .MuiInputBase-input': { color: '#e8e8f0' },
                      '& .MuiInputLabel-root': { color: '#b8b8cc' }
                    }}
                  />
                </Box>

                {/* Discount Rate */}
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Discount Rate (%): {formatPercent(inputs.discountRate * 100)}
                  </Typography>
                  <Slider
                    value={inputs.discountRate * 100}
                    onChange={(_, value) => handleInputChange('discountRate', (value as number) / 100)}
                    min={5}
                    max={25}
                    step={0.5}
                    aria-label="Discount Rate Percentage"
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `${value}%`}
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

                {/* Time Duration */}
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Time Duration (Years): {inputs.timeDuration}
                  </Typography>
                  <Slider
                    value={inputs.timeDuration}
                    onChange={(_, value) => handleInputChange('timeDuration', value as number)}
                    min={1}
                    max={10}
                    step={1}
                    aria-label="Time Duration in Years"
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `${value} years`}
                    marks={[
                      { value: 1, label: '1y' },
                      { value: 3, label: '3y' },
                      { value: 5, label: '5y' },
                      { value: 10, label: '10y' }
                    ]}
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
                      },
                      '& .MuiSlider-mark': {
                        backgroundColor: '#1890ff'
                      },
                      '& .MuiSlider-markLabel': {
                        color: '#b8b8cc',
                        fontSize: '0.75rem'
                      }
                    }}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Center Panel - Key Metrics */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            {/* Gross Margin */}
            <Grid item xs={12}>
              <Paper sx={{ 
                p: 2, 
                backgroundColor: '#252547', 
                border: '1px solid #3d3d56',
                textAlign: 'center'
              }}>
                <TrendingUp sx={{ color: '#52c41a', fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                  Gross Margin
                </Typography>
                <Typography variant="h4" sx={{ color: '#52c41a', fontWeight: 600 }}>
                  {formatPercent(metrics?.grossMarginPercent || 0)}
                </Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  {formatCurrency(metrics?.grossMargin || 0)} per unit
                </Typography>
              </Paper>
            </Grid>

            {/* Breakeven Volume */}
            <Grid item xs={12}>
              <Paper sx={{ 
                p: 2, 
                backgroundColor: '#252547', 
                border: '1px solid #3d3d56',
                textAlign: 'center'
              }}>
                <Analytics sx={{ color: '#1890ff', fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                  Breakeven Volume
                </Typography>
                <Typography variant="h4" sx={{ color: '#1890ff', fontWeight: 600 }}>
                  {Math.round(metrics?.breakevenVolume || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  units to break even
                </Typography>
              </Paper>
            </Grid>

            {/* ROI */}
            <Grid item xs={12}>
              <Paper sx={{ 
                p: 2, 
                backgroundColor: '#252547', 
                border: '1px solid #3d3d56',
                textAlign: 'center'
              }}>
                <AttachMoney sx={{ color: '#fa8c16', fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                  Simple ROI
                </Typography>
                <Typography variant="h4" sx={{ color: '#fa8c16', fontWeight: 600 }}>
                  {formatPercent(metrics?.simpleROI || 0)}
                </Typography>
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  return on investment
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Grid>

        {/* Right Panel - Financial Projections */}
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            height: 'fit-content'
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3, display: 'flex', alignItems: 'center' }}>
                <Timeline sx={{ mr: 1 }} />
                Financial Metrics
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                    Total Contribution
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                    {formatCurrency(metrics?.totalContribution || 0)}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                    Payback Period
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                    {(metrics?.paybackPeriod || 0).toFixed(1)} years
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                    Net Present Value ({inputs.timeDuration}yr)
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
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                    Internal Rate of Return
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                    {formatPercent(metrics?.irr || 0)}
                  </Typography>
                </Box>
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
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#b8b8cc', borderBottom: '1px solid #3d3d56' }}>
                        Scenario
                      </TableCell>
                      <TableCell sx={{ color: '#b8b8cc', borderBottom: '1px solid #3d3d56' }}>
                        Probability
                      </TableCell>
                      <TableCell sx={{ color: '#b8b8cc', borderBottom: '1px solid #3d3d56' }}>
                        Volume
                      </TableCell>
                      <TableCell sx={{ color: '#b8b8cc', borderBottom: '1px solid #3d3d56' }}>
                        Price
                      </TableCell>
                      <TableCell sx={{ color: '#b8b8cc', borderBottom: '1px solid #3d3d56' }}>
                        Contribution
                      </TableCell>
                      <TableCell sx={{ color: '#b8b8cc', borderBottom: '1px solid #3d3d56' }}>
                        ROI
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {scenarioResults.map((scenario: any, index) => (
                      <TableRow key={index}>
                        <TableCell sx={{ borderBottom: '1px solid #3d3d56' }}>
                          <Chip 
                            label={scenario.name}
                            sx={{
                              backgroundColor: `${scenario.color}20`,
                              color: scenario.color,
                              fontWeight: 600
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ borderBottom: '1px solid #3d3d56' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={scenario.probability}
                              aria-label={`Probability: ${scenario.probability}%`}
                              title={`Probability: ${scenario.probability}%`}
                              sx={{
                                width: 60,
                                backgroundColor: '#3d3d56',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: scenario.color
                                }
                              }}
                            />
                            <Typography sx={{ color: '#e8e8f0' }}>
                              {scenario.probability}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell sx={{ color: '#e8e8f0', borderBottom: '1px solid #3d3d56' }}>
                          {Math.round(scenario.volume).toLocaleString()}
                        </TableCell>
                        <TableCell sx={{ color: '#e8e8f0', borderBottom: '1px solid #3d3d56' }}>
                          {formatCurrency(scenario.price)}
                        </TableCell>
                        <TableCell sx={{ color: '#e8e8f0', borderBottom: '1px solid #3d3d56' }}>
                          {formatCurrency(scenario.contribution)}
                        </TableCell>
                        <TableCell sx={{ 
                          color: scenario.roi > 0 ? '#52c41a' : '#ff4d4f',
                          fontWeight: 600,
                          borderBottom: '1px solid #3d3d56'
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

          {/* Chat Interface */}
          <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56', height: 600, mt: 3 }}>
            <CardContent sx={{ p: 0, height: '100%' }}>
              <PergolaChat 
                segment="business_case"
                onSegmentChange={(segment) => console.log('Segment changed:', segment)}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BusinessCaseTab;