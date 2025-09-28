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
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  TrendingUp,
  AttachMoney,
  Timeline,
  Analytics,
  ExpandMore,
  Assessment,
  Build
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface EssentialInputs {
  unitPrice: number;
  unitCost: number;
  expectedVolume: number;
  fixedCosts: number;
  innovationCost: number;
  discountRate: number;
  timeDuration: number;
}

interface DetailedInputs {
  // Unit Cost Components
  materialsPerUnit: number;
  laborPerUnit: number;
  logisticsPerUnit: number;
  warrantyServicePerUnit: number;
  
  // Pricing
  unitPrice: number;
  expectedVolume: number;
  
  // Fixed Cost Components (separate from Innovation Cost)
  rdCosts: number;           // R&D costs
  marketingCosts: number;    // Marketing costs
  adminCosts: number;        // Admin costs
  equipmentCosts: number;    // Equipment costs
  overheadPercentage: number; // Overhead as % of revenue
  
  // Innovation Cost (separate for calculations)
  innovationCost: number;
  
  // Financial
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
  calculatedUnitCost?: number;
  calculatedFixedCosts?: number;
}

const BusinessCaseTab: React.FC<{ data: any }> = () => {
  const [costMode, setCostMode] = useState<'essential' | 'detailed'>('essential');

  const [essentialInputs, setEssentialInputs] = useState<EssentialInputs>({
    unitPrice: 1200,
    unitCost: 800,
    expectedVolume: 1000,
    fixedCosts: 200000,
    innovationCost: 100000,
    discountRate: 0.12,
    timeDuration: 5
  });

  const [detailedInputs, setDetailedInputs] = useState<DetailedInputs>({
    // Unit Cost Components (will calculate unitCost)
    materialsPerUnit: 400,
    laborPerUnit: 250,
    logisticsPerUnit: 100,
    warrantyServicePerUnit: 50,
    
    // Pricing
    unitPrice: 1200,
    expectedVolume: 1000,
    
    // Fixed Cost Components (separate from Innovation Cost)
    rdCosts: 80000,           // R&D costs
    marketingCosts: 60000,    // Marketing costs
    adminCosts: 40000,        // Admin costs
    equipmentCosts: 30000,    // Equipment costs
    overheadPercentage: 15,   // Overhead as % of revenue
    
    // Innovation Cost (separate for calculations)
    innovationCost: 100000,
    
    // Financial
    discountRate: 0.12,
    timeDuration: 5
  });

  const [metrics, setMetrics] = useState<CalculatedMetrics | null>(null);
  const [scenarioResults, setScenarioResults] = useState<any[]>([]);

  // Calculate derived values from detailed inputs
  const calculateFromDetailedInputs = (detailed: DetailedInputs): EssentialInputs => {
    // Unit Cost = Materials + Labor + Logistics + Warranty/Service
    const calculatedUnitCost = detailed.materialsPerUnit + 
                              detailed.laborPerUnit + 
                              detailed.logisticsPerUnit + 
                              detailed.warrantyServicePerUnit;

    // Total Revenue
    const totalRevenue = detailed.unitPrice * detailed.expectedVolume;
    
    // Additional Fixed Costs from overhead percentage
    const overheadCosts = totalRevenue * (detailed.overheadPercentage / 100);
    
    // Total Fixed Costs = R&D + Marketing + Admin + Equipment + Overhead
    const calculatedFixedCosts = detailed.rdCosts + 
                                detailed.marketingCosts + 
                                detailed.adminCosts + 
                                detailed.equipmentCosts + 
                                overheadCosts;

    return {
      unitPrice: detailed.unitPrice,
      unitCost: calculatedUnitCost,
      expectedVolume: detailed.expectedVolume,
      fixedCosts: calculatedFixedCosts,
      innovationCost: detailed.innovationCost,
      discountRate: detailed.discountRate,
      timeDuration: detailed.timeDuration
    };
  };

  useEffect(() => {
    calculateMetrics();
    runScenarioAnalysis();
  }, [essentialInputs, detailedInputs, costMode]);


  const calculateMetrics = () => {
    const activeInputs = costMode === 'essential' ? essentialInputs : calculateFromDetailedInputs(detailedInputs);
    
    const grossMargin = activeInputs.unitPrice - activeInputs.unitCost;
    const grossMarginPercent = (grossMargin / activeInputs.unitPrice) * 100;
    const totalContribution = grossMargin * activeInputs.expectedVolume;
    const breakevenVolume = activeInputs.fixedCosts / grossMargin;
    const paybackPeriod = activeInputs.innovationCost / (totalContribution - activeInputs.fixedCosts);
    const simpleROI = ((totalContribution - activeInputs.fixedCosts - activeInputs.innovationCost) / activeInputs.innovationCost) * 100;
    
    // NPV calculation using dynamic time duration
    let npv = -activeInputs.innovationCost;
    for (let year = 1; year <= activeInputs.timeDuration; year++) {
      const cashFlow = totalContribution - activeInputs.fixedCosts;
      npv += cashFlow / Math.pow(1 + activeInputs.discountRate, year);
    }

    // IRR approximation
    const irr = ((totalContribution - activeInputs.fixedCosts) / activeInputs.innovationCost) * 100;

    const calculatedMetrics: CalculatedMetrics = {
      grossMargin,
      grossMarginPercent,
      totalContribution,
      breakevenVolume,
      paybackPeriod,
      simpleROI,
      npv,
      irr
    };

    // Add calculated values for detailed mode
    if (costMode === 'detailed') {
      calculatedMetrics.calculatedUnitCost = activeInputs.unitCost;
      calculatedMetrics.calculatedFixedCosts = activeInputs.fixedCosts;
    }

    setMetrics(calculatedMetrics);
  };

  const runScenarioAnalysis = () => {
    const activeInputs = costMode === 'essential' ? essentialInputs : calculateFromDetailedInputs(detailedInputs);
    
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
      const adjustedVolume = activeInputs.expectedVolume * scenario.multiplier;
      const adjustedPrice = activeInputs.unitPrice * (1 + (scenario.multiplier - 1) * 0.1);
      const grossMargin = adjustedPrice - activeInputs.unitCost;
      const contribution = grossMargin * adjustedVolume;
      const roi = ((contribution - activeInputs.fixedCosts - activeInputs.innovationCost) / activeInputs.innovationCost) * 100;
      
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

  const handleEssentialInputChange = (field: keyof EssentialInputs, value: number) => {
    setEssentialInputs(prev => ({ ...prev, [field]: value }));
  };

  const handleDetailedInputChange = (field: keyof DetailedInputs, value: number) => {
    setDetailedInputs(prev => ({ ...prev, [field]: value }));
  };

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
  
  const formatPercent = (value: number) => `${value.toFixed(1)}%`;

  // Consistent TextField styling
  const textFieldSx = {
    '& .MuiOutlinedInput-root': {
      backgroundColor: '#1a1a35',
      '& fieldset': { borderColor: '#3d3d56' },
      '&:hover fieldset': { borderColor: '#4CAF50' },
      '&.Mui-focused fieldset': { borderColor: '#4CAF50' }
    },
    '& .MuiInputBase-input': { color: '#e8e8f0' }
  };

  const renderEssentialInputs = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ 
        backgroundColor: '#252547', 
        border: '1px solid #4CAF50',
        borderRadius: 2
      }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ color: '#4CAF50', mb: 3, display: 'flex', alignItems: 'center' }}>
            <Assessment sx={{ mr: 1 }} />
            Essential Cost Inputs
          </Typography>

          <Grid container spacing={3}>
            {/* Unit Price */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Unit Price ($)
              </Typography>
              <TextField
                type="number"
                value={essentialInputs.unitPrice}
                onChange={(e) => handleEssentialInputChange('unitPrice', Number(e.target.value))}
                fullWidth
                variant="outlined"
                sx={textFieldSx}
              />
            </Grid>

            {/* Unit Cost */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Unit Cost ($)
              </Typography>
              <TextField
                type="number"
                value={essentialInputs.unitCost}
                onChange={(e) => handleEssentialInputChange('unitCost', Number(e.target.value))}
                fullWidth
                variant="outlined"
                sx={textFieldSx}
              />
            </Grid>

            {/* Expected Volume */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Expected Sales Volume (units)
              </Typography>
              <TextField
                type="number"
                value={essentialInputs.expectedVolume}
                onChange={(e) => handleEssentialInputChange('expectedVolume', Number(e.target.value))}
                fullWidth
                variant="outlined"
                sx={textFieldSx}
              />
            </Grid>

            {/* Fixed Costs */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Fixed Costs ($)
              </Typography>
              <TextField
                type="number"
                value={essentialInputs.fixedCosts}
                onChange={(e) => handleEssentialInputChange('fixedCosts', Number(e.target.value))}
                fullWidth
                variant="outlined"
                sx={textFieldSx}
              />
            </Grid>

            {/* Innovation Cost */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Innovation/Capex Costs ($)
              </Typography>
              <TextField
                type="number"
                value={essentialInputs.innovationCost}
                onChange={(e) => handleEssentialInputChange('innovationCost', Number(e.target.value))}
                fullWidth
                variant="outlined"
                sx={textFieldSx}
              />
            </Grid>

            {/* Discount Rate */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Discount Rate (%)
              </Typography>
              <TextField
                type="number"
                value={essentialInputs.discountRate * 100}
                onChange={(e) => handleEssentialInputChange('discountRate', Number(e.target.value) / 100)}
                fullWidth
                variant="outlined"
                sx={textFieldSx}
              />
            </Grid>

            {/* Time Duration */}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Time Duration (years)
              </Typography>
              <TextField
                type="number"
                value={essentialInputs.timeDuration}
                onChange={(e) => handleEssentialInputChange('timeDuration', Number(e.target.value))}
                fullWidth
                variant="outlined"
                sx={textFieldSx}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderDetailedInputs = () => {
    const calculatedInputs = calculateFromDetailedInputs(detailedInputs);
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        <Card sx={{ 
          backgroundColor: '#252547', 
          border: '1px solid #9C27B0',
          borderRadius: 2
        }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ color: '#9C27B0', mb: 3, display: 'flex', alignItems: 'center' }}>
              <Build sx={{ mr: 1 }} />
              Detailed Cost Inputs
            </Typography>

            {/* Unit Cost Components */}
            <Accordion sx={{ backgroundColor: '#1a1a35', mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                <Typography sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  Unit Cost Components 
                  <Chip 
                    size="small" 
                    label={formatCurrency(calculatedInputs.unitCost)}
                    sx={{ ml: 2, backgroundColor: '#9C27B0', color: 'white' }}
                  />
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Materials/unit ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.materialsPerUnit}
                      onChange={(e) => handleDetailedInputChange('materialsPerUnit', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Labor/unit ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.laborPerUnit}
                      onChange={(e) => handleDetailedInputChange('laborPerUnit', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Logistics/unit ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.logisticsPerUnit}
                      onChange={(e) => handleDetailedInputChange('logisticsPerUnit', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Warranty/Service/unit ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.warrantyServicePerUnit}
                      onChange={(e) => handleDetailedInputChange('warrantyServicePerUnit', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Pricing & Volume */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Unit Price ($)
                </Typography>
                <TextField
                  type="number"
                  value={detailedInputs.unitPrice}
                  onChange={(e) => handleDetailedInputChange('unitPrice', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={textFieldSx}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Expected Volume (units)
                </Typography>
                <TextField
                  type="number"
                  value={detailedInputs.expectedVolume}
                  onChange={(e) => handleDetailedInputChange('expectedVolume', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={textFieldSx}
                />
              </Grid>
            </Grid>

            {/* Fixed Cost Components */}
            <Accordion sx={{ backgroundColor: '#1a1a35', mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#e8e8f0' }} />}>
                <Typography sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                  Fixed Cost Components
                  <Chip 
                    size="small" 
                    label={formatCurrency(calculatedInputs.fixedCosts)}
                    sx={{ ml: 2, backgroundColor: '#9C27B0', color: 'white' }}
                  />
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      R&D Costs ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.rdCosts}
                      onChange={(e) => handleDetailedInputChange('rdCosts', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Marketing Costs ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.marketingCosts}
                      onChange={(e) => handleDetailedInputChange('marketingCosts', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Admin Costs ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.adminCosts}
                      onChange={(e) => handleDetailedInputChange('adminCosts', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Equipment Costs ($)
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.equipmentCosts}
                      onChange={(e) => handleDetailedInputChange('equipmentCosts', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                      Overhead % of revenue
                    </Typography>
                    <TextField
                      type="number"
                      value={detailedInputs.overheadPercentage}
                      onChange={(e) => handleDetailedInputChange('overheadPercentage', Number(e.target.value))}
                      fullWidth
                      variant="outlined"
                      sx={textFieldSx}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Innovation Cost - Direct Input */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Innovation/Capex Cost ($)
                </Typography>
                <TextField
                  type="number"
                  value={detailedInputs.innovationCost}
                  onChange={(e) => handleDetailedInputChange('innovationCost', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={textFieldSx}
                />
              </Grid>
            </Grid>

            {/* Financial Parameters */}
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Discount Rate (%)
                </Typography>
                <TextField
                  type="number"
                  value={detailedInputs.discountRate * 100}
                  onChange={(e) => handleDetailedInputChange('discountRate', Number(e.target.value) / 100)}
                  fullWidth
                  variant="outlined"
                  sx={textFieldSx}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Time Duration (years)
                </Typography>
                <TextField
                  type="number"
                  value={detailedInputs.timeDuration}
                  onChange={(e) => handleDetailedInputChange('timeDuration', Number(e.target.value))}
                  fullWidth
                  variant="outlined"
                  sx={textFieldSx}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  return (
    <Box sx={{ p: 4 }}>
      {/* Cost Mode Toggle */}
      <Box sx={{ mb: 4 }}>
        <FormControl>
          <FormLabel sx={{ color: '#e8e8f0', mb: 2, fontSize: '1.1rem', fontWeight: 600 }}>
            Cost Input Mode
          </FormLabel>
          <RadioGroup
            row
            value={costMode}
            onChange={(e) => setCostMode(e.target.value as 'essential' | 'detailed')}
            sx={{
              '& .MuiFormControlLabel-root': {
                backgroundColor: '#1a1a35',
                borderRadius: 2,
                border: '1px solid #3d3d56',
                margin: '0 8px 0 0',
                padding: '8px 16px',
                '&:hover': {
                  backgroundColor: '#252547'
                }
              },
              '& .Mui-checked + .MuiFormControlLabel-label': {
                color: '#e8e8f0',
                fontWeight: 600
              }
            }}
          >
            <FormControlLabel 
              value="essential" 
              control={<Radio sx={{ color: '#4CAF50' }} />} 
              label="Essential Cost"
              sx={{
                border: costMode === 'essential' ? '2px solid #4CAF50' : 'none',
                '& .MuiFormControlLabel-label': {
                  color: costMode === 'essential' ? '#4CAF50' : '#b8b8cc'
                }
              }}
            />
            <FormControlLabel 
              value="detailed" 
              control={<Radio sx={{ color: '#9C27B0' }} />} 
              label="Detailed Cost"
              sx={{
                border: costMode === 'detailed' ? '2px solid #9C27B0' : 'none',
                '& .MuiFormControlLabel-label': {
                  color: costMode === 'detailed' ? '#9C27B0' : '#b8b8cc'
                }
              }}
            />
          </RadioGroup>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {/* Left Panel - Inputs */}
        <Grid item xs={12} lg={5}>
          <AnimatePresence mode="wait">
            {costMode === 'essential' ? renderEssentialInputs() : renderDetailedInputs()}
          </AnimatePresence>
        </Grid>

        {/* Right Panel - Metrics and Results */}
        <Grid item xs={12} lg={7}>
          <Grid container spacing={2}>
            {/* Key Metrics */}
            <Grid item xs={12} sm={4}>
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

            <Grid item xs={12} sm={4}>
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

            <Grid item xs={12} sm={4}>
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

            {/* Financial Projections */}
            <Grid item xs={12}>
              <Card sx={{ 
                backgroundColor: '#252547', 
                border: '1px solid #3d3d56'
              }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 3, display: 'flex', alignItems: 'center' }}>
                    <Timeline sx={{ mr: 1 }} />
                    Financial Metrics
                  </Typography>

                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                          Total Contribution
                        </Typography>
                        <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                          {formatCurrency(metrics?.totalContribution || 0)}
                        </Typography>
                      </Box>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                          Payback Period
                        </Typography>
                        <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                          {(metrics?.paybackPeriod || 0).toFixed(1)} years
                        </Typography>
                      </Box>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                          Net Present Value ({costMode === 'essential' ? essentialInputs.timeDuration : detailedInputs.timeDuration}yr)
                        </Typography>
                        <Typography 
                          variant="h4" 
                          sx={{ 
                            color: (metrics?.npv || 0) > 0 ? '#52c41a' : '#ff4d4f', 
                            fontWeight: 700 
                          }}
                        >
                          {formatCurrency(metrics?.npv || 0)}
                        </Typography>
                      </Box>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
                          Internal Rate of Return
                        </Typography>
                        <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 700 }}>
                          {formatPercent(metrics?.irr || 0)}
                        </Typography>
                      </Box>
                    </Grid>

                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Scenario Analysis */}
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
            </Grid>

          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BusinessCaseTab;
