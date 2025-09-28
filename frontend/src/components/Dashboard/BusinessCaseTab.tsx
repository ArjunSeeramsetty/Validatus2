/**
 * Enhanced Business Case Tab - No horizontal scroll, responsive layout
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
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
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
  materialsPerUnit: number;
  laborPerUnit: number;
  logisticsPerUnit: number;
  warrantyServicePerUnit: number;
  unitPrice: number;
  expectedVolume: number;
  fixedCosts: number;
  innovationCost: number;
  overheadPercentage: number;
  marketingPercentage: number;
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
    materialsPerUnit: 400,
    laborPerUnit: 250,
    logisticsPerUnit: 100,
    warrantyServicePerUnit: 50,
    unitPrice: 1200,
    expectedVolume: 1000,
    fixedCosts: 150000,
    innovationCost: 100000,
    overheadPercentage: 15,
    marketingPercentage: 8,
    discountRate: 0.12,
    timeDuration: 5
  });

  const [metrics, setMetrics] = useState<CalculatedMetrics | null>(null);
  const [scenarioResults, setScenarioResults] = useState<any[]>([]);

  const calculateFromDetailedInputs = (detailed: DetailedInputs): EssentialInputs => {
    const calculatedUnitCost = detailed.materialsPerUnit + 
                              detailed.laborPerUnit + 
                              detailed.logisticsPerUnit + 
                              detailed.warrantyServicePerUnit;

    const totalRevenue = detailed.unitPrice * detailed.expectedVolume;
    const overheadCosts = totalRevenue * (detailed.overheadPercentage / 100);
    const marketingCosts = totalRevenue * (detailed.marketingPercentage / 100);
    const calculatedFixedCosts = detailed.fixedCosts + overheadCosts + marketingCosts;

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
    
    let npv = -activeInputs.innovationCost;
    for (let year = 1; year <= activeInputs.timeDuration; year++) {
      const cashFlow = totalContribution - activeInputs.fixedCosts;
      npv += cashFlow / Math.pow(1 + activeInputs.discountRate, year);
    }

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

    if (costMode === 'detailed') {
      calculatedMetrics.calculatedUnitCost = activeInputs.unitCost;
      calculatedMetrics.calculatedFixedCosts = activeInputs.fixedCosts;
    }

    setMetrics(calculatedMetrics);
  };

  const runScenarioAnalysis = () => {
    const activeInputs = costMode === 'essential' ? essentialInputs : calculateFromDetailedInputs(detailedInputs);
    
    const scenarios = [
      { name: 'Conservative', multiplier: 0.8, color: '#ff4d4f', probability: 25 },
      { name: 'Base Case', multiplier: 1.0, color: '#52c41a', probability: 50 },
      { name: 'Optimistic', multiplier: 1.3, color: '#1890ff', probability: 25 }
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

  // Consistent styling for all text fields
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
    <Card sx={{ 
      backgroundColor: '#252547', 
      border: '1px solid #4CAF50',
      borderRadius: 2,
      mb: 3
    }}>
      <CardContent sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ color: '#4CAF50', mb: 2, display: 'flex', alignItems: 'center' }}>
          <Assessment sx={{ mr: 1 }} />
          Essential Cost Inputs
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
              Unit Price ($)
            </Typography>
            <TextField
              type="number"
              value={essentialInputs.unitPrice}
              onChange={(e) => handleEssentialInputChange('unitPrice', Number(e.target.value))}
              fullWidth
              size="small"
              sx={textFieldSx}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
              Unit Cost ($)
            </Typography>
            <TextField
              type="number"
              value={essentialInputs.unitCost}
              onChange={(e) => handleEssentialInputChange('unitCost', Number(e.target.value))}
              fullWidth
              size="small"
              sx={textFieldSx}
            />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
              Expected Volume: {essentialInputs.expectedVolume.toLocaleString()} units
            </Typography>
            <TextField
              type="number"
              value={essentialInputs.expectedVolume}
              onChange={(e) => handleEssentialInputChange('expectedVolume', Number(e.target.value))}
              fullWidth
              size="small"
              sx={textFieldSx}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
              Fixed Costs ($)
            </Typography>
            <TextField
              type="number"
              value={essentialInputs.fixedCosts}
              onChange={(e) => handleEssentialInputChange('fixedCosts', Number(e.target.value))}
              fullWidth
              size="small"
              sx={textFieldSx}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
              Innovation Cost ($)
            </Typography>
            <TextField
              type="number"
              value={essentialInputs.innovationCost}
              onChange={(e) => handleEssentialInputChange('innovationCost', Number(e.target.value))}
              fullWidth
              size="small"
              sx={textFieldSx}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
              Discount Rate: {formatPercent(essentialInputs.discountRate * 100)}
            </Typography>
            <TextField
              type="number"
              value={essentialInputs.discountRate * 100}
              onChange={(e) => handleEssentialInputChange('discountRate', Number(e.target.value) / 100)}
              fullWidth
              size="small"
              sx={textFieldSx}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
              Time Duration: {essentialInputs.timeDuration} years
            </Typography>
            <TextField
              type="number"
              value={essentialInputs.timeDuration}
              onChange={(e) => handleEssentialInputChange('timeDuration', Number(e.target.value))}
              fullWidth
              size="small"
              sx={textFieldSx}
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderDetailedInputs = () => {
    const calculatedInputs = calculateFromDetailedInputs(detailedInputs);
    
    return (
      <Card sx={{ 
        backgroundColor: '#252547', 
        border: '1px solid #9C27B0',
        borderRadius: 2,
        mb: 3
      }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ color: '#9C27B0', mb: 2, display: 'flex', alignItems: 'center' }}>
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
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Materials/unit ($)
                  </Typography>
                  <TextField
                    type="number"
                    value={detailedInputs.materialsPerUnit}
                    onChange={(e) => handleDetailedInputChange('materialsPerUnit', Number(e.target.value))}
                    fullWidth
                    size="small"
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
                    size="small"
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
                    size="small"
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
                    size="small"
                    sx={textFieldSx}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

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
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Fixed Costs ($)
                  </Typography>
                  <TextField
                    type="number"
                    value={detailedInputs.fixedCosts}
                    onChange={(e) => handleDetailedInputChange('fixedCosts', Number(e.target.value))}
                    fullWidth
                    size="small"
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
                    size="small"
                    sx={textFieldSx}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                    Marketing % of revenue
                  </Typography>
                  <TextField
                    type="number"
                    value={detailedInputs.marketingPercentage}
                    onChange={(e) => handleDetailedInputChange('marketingPercentage', Number(e.target.value))}
                    fullWidth
                    size="small"
                    sx={textFieldSx}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Innovation Cost */}
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Innovation/Capex Cost ($)
              </Typography>
              <TextField
                type="number"
                value={detailedInputs.innovationCost}
                onChange={(e) => handleDetailedInputChange('innovationCost', Number(e.target.value))}
                fullWidth
                size="small"
                sx={textFieldSx}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Unit Price ($)
              </Typography>
              <TextField
                type="number"
                value={detailedInputs.unitPrice}
                onChange={(e) => handleDetailedInputChange('unitPrice', Number(e.target.value))}
                fullWidth
                size="small"
                sx={textFieldSx}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Expected Volume: {detailedInputs.expectedVolume.toLocaleString()}
              </Typography>
              <TextField
                type="number"
                value={detailedInputs.expectedVolume}
                onChange={(e) => handleDetailedInputChange('expectedVolume', Number(e.target.value))}
                fullWidth
                size="small"
                sx={textFieldSx}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Discount Rate: {formatPercent(detailedInputs.discountRate * 100)}
              </Typography>
              <TextField
                type="number"
                value={detailedInputs.discountRate * 100}
                onChange={(e) => handleDetailedInputChange('discountRate', Number(e.target.value) / 100)}
                fullWidth
                size="small"
                sx={textFieldSx}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" sx={{ color: '#b8b8cc', mb: 1 }}>
                Time Duration: {detailedInputs.timeDuration} years
              </Typography>
              <TextField
                type="number"
                value={detailedInputs.timeDuration}
                onChange={(e) => handleDetailedInputChange('timeDuration', Number(e.target.value))}
                fullWidth
                size="small"
                sx={textFieldSx}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ 
      width: '100%', 
      maxWidth: '100%',
      overflow: 'hidden',
      boxSizing: 'border-box'
    }}>
      {/* Cost Mode Toggle */}
      <Box sx={{ mb: 3 }}>
        <FormControl>
          <FormLabel sx={{ color: '#e8e8f0', mb: 2 }}>
            Cost Input Mode
          </FormLabel>
          <RadioGroup
            row
            value={costMode}
            onChange={(e) => setCostMode(e.target.value as 'essential' | 'detailed')}
            sx={{
              '& .MuiFormControlLabel-root': {
                backgroundColor: '#1a1a35',
                borderRadius: 1,
                border: '1px solid #3d3d56',
                margin: '0 8px 0 0',
                padding: '4px 12px'
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

      {/* Input Forms */}
      <AnimatePresence mode="wait">
        <motion.div
          key={costMode}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {costMode === 'essential' ? renderEssentialInputs() : renderDetailedInputs()}
        </motion.div>
      </AnimatePresence>

      {/* Metrics Grid - Responsive */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
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
            <Typography variant="h5" sx={{ color: '#52c41a', fontWeight: 600 }}>
              {formatPercent(metrics?.grossMarginPercent || 0)}
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              {formatCurrency(metrics?.grossMargin || 0)} per unit
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            textAlign: 'center'
          }}>
            <AttachMoney sx={{ color: '#1890ff', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              Contribution/unit
            </Typography>
            <Typography variant="h5" sx={{ color: '#1890ff', fontWeight: 600 }}>
              {formatCurrency(metrics?.grossMargin || 0)}
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              per unit contribution
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            textAlign: 'center'
          }}>
            <Analytics sx={{ color: '#722ed1', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              Revenue (Y1)
            </Typography>
            <Typography variant="h5" sx={{ color: '#722ed1', fontWeight: 600 }}>
              {formatCurrency(metrics?.totalContribution || 0)}
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              first year revenue
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            textAlign: 'center'
          }}>
            <TrendingUp sx={{ color: '#fa8c16', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              Breakeven Volume
            </Typography>
            <Typography variant="h5" sx={{ color: '#fa8c16', fontWeight: 600 }}>
              {Math.round(metrics?.breakevenVolume || 0).toLocaleString()}
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              units to break even
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            textAlign: 'center'
          }}>
            <Analytics sx={{ color: '#13c2c2', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              Payback Period
            </Typography>
            <Typography variant="h5" sx={{ color: '#13c2c2', fontWeight: 600 }}>
              {metrics?.paybackPeriod ? (metrics.paybackPeriod * 12).toFixed(1) : '0.0'}m
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              months to payback
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            textAlign: 'center'
          }}>
            <TrendingUp sx={{ color: '#eb2f96', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              Simple ROI
            </Typography>
            <Typography 
              variant="h5" 
              sx={{ 
                color: (metrics?.simpleROI || 0) > 0 ? '#52c41a' : '#ff4d4f', 
                fontWeight: 600 
              }}
            >
              {formatPercent(metrics?.simpleROI || 0)}
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              return on investment
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            textAlign: 'center'
          }}>
            <AttachMoney sx={{ color: '#fa8c16', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              NPV ({costMode === 'essential' ? essentialInputs.timeDuration : detailedInputs.timeDuration}yr)
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
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              net present value
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#252547', 
            border: '1px solid #3d3d56',
            textAlign: 'center'
          }}>
            <Analytics sx={{ color: '#9c27b0', fontSize: 32, mb: 1 }} />
            <Typography variant="subtitle2" sx={{ color: '#b8b8cc' }}>
              IRR
            </Typography>
            <Typography 
              variant="h5" 
              sx={{ 
                color: (metrics?.irr || 0) > 0 ? '#52c41a' : '#ff4d4f', 
                fontWeight: 600 
              }}
            >
              {formatPercent(metrics?.irr || 0)}
            </Typography>
            <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
              internal rate of return
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Scenario Analysis - Responsive Table */}
      <Card sx={{ backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
            Scenario Analysis
          </Typography>
          
          <Box sx={{ 
            overflowX: 'auto',
            width: '100%',
            '& table': {
              minWidth: '600px' // Minimum table width
            }
          }}>
            <TableContainer>
              <Table size="small">
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
                          size="small"
                          sx={{
                            backgroundColor: `${scenario.color}20`,
                            color: scenario.color,
                            fontWeight: 600
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ borderBottom: '1px solid #3d3d56' }}>
                        <Typography sx={{ color: '#e8e8f0' }}>
                          {scenario.probability}%
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ color: '#e8e8f0', borderBottom: '1px solid #3d3d56' }}>
                        {Math.round(scenario.volume).toLocaleString()}
                      </TableCell>
                      <TableCell sx={{ color: '#e8e8f0', borderBottom: '1px solid #3d3d56' }}>
                        {formatCurrency(scenario.price)}
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
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default BusinessCaseTab;