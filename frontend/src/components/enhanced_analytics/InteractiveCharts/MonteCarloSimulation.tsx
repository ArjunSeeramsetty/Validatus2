// frontend/src/components/enhanced_analytics/InteractiveCharts/MonteCarloSimulation.tsx
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Stack,
  Button,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Tooltip,
  IconButton,
  Grid,
  Paper,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  RefreshOutlined,
  FileDownloadOutlined,
  InfoOutlined,
  TrendingUpOutlined,
  WarningOutlined,
  StopOutlined
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  HistogramChart,
  Histogram,
  ScatterChart,
  Scatter,
  AreaChart,
  Area,
  ComposedChart,
  Bar
} from 'recharts';
import { useWebSocketConnection } from '../../../hooks/useWebSocketConnection';

interface SimulationParameters {
  iterations: number;
  timeHorizon: number;
  volatility: number;
  confidenceLevel: number;
  marketShock: number;
  correlationMatrix: number[][];
}

interface MonteCarloResult {
  iteration: number;
  finalValue: number;
  pathData: { time: number; value: number; }[];
  statistics: {
    mean: number;
    median: number;
    stdDev: number;
    var95: number;
    var99: number;
    maxDrawdown: number;
    sharpeRatio: number;
  };
}

interface MonteCarloSimulationProps {
  sessionId: string;
  factorResults?: Record<string, any>;
  initialValue?: number;
  autoStart?: boolean;
  onSimulationComplete?: (results: MonteCarloResult[]) => void;
}

const MonteCarloSimulation: React.FC<MonteCarloSimulationProps> = ({
  sessionId,
  factorResults = {},
  initialValue = 100,
  autoStart = false,
  onSimulationComplete
}) => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const [simulationResults, setSimulationResults] = useState<MonteCarloResult[]>([]);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [parameters, setParameters] = useState<SimulationParameters>({
    iterations: 10000,
    timeHorizon: 252, // Trading days in a year
    volatility: 0.2,
    confidenceLevel: 0.95,
    marketShock: 0.0,
    correlationMatrix: [[1.0]]
  });
  const [visualizationMode, setVisualizationMode] = useState<'paths' | 'distribution' | 'statistics' | 'risk'>('paths');
  const [selectedPaths, setSelectedPaths] = useState<number>(100);
  const [showConfidenceIntervals, setShowConfidenceIntervals] = useState(true);

  const { sendMessage, lastMessage } = useWebSocketConnection();

  // Handle WebSocket messages for real-time simulation updates
  useEffect(() => {
    if (lastMessage && lastMessage.data) {
      try {
        const message = JSON.parse(lastMessage.data);
        
        if (message.type === 'monte_carlo_update' && message.sessionId === sessionId) {
          setCurrentIteration(message.iteration);
          setProgress((message.iteration / parameters.iterations) * 100);
          
          if (message.result) {
            setSimulationResults(prev => [...prev, message.result]);
          }
          
          if (message.iteration >= parameters.iterations) {
            setIsRunning(false);
            setProgress(100);
            onSimulationComplete?.(simulationResults);
          }
        }
      } catch (error) {
        console.error('Error parsing Monte Carlo WebSocket message:', error);
      }
    }
  }, [lastMessage, sessionId, parameters.iterations, simulationResults, onSimulationComplete]);

  // Start simulation
  const startSimulation = useCallback(async () => {
    try {
      setIsRunning(true);
      setIsPaused(false);
      setProgress(0);
      setCurrentIteration(0);
      setSimulationResults([]);

      // Send simulation parameters to backend
      const message = {
        type: 'start_monte_carlo',
        sessionId,
        parameters: {
          ...parameters,
          initialValue,
          factorInputs: factorResults
        }
      };

      sendMessage(JSON.stringify(message));
    } catch (error) {
      console.error('Error starting Monte Carlo simulation:', error);
      setIsRunning(false);
    }
  }, [sessionId, parameters, initialValue, factorResults, sendMessage]);

  // Pause/Resume simulation
  const togglePause = useCallback(() => {
    const message = {
      type: isPaused ? 'resume_monte_carlo' : 'pause_monte_carlo',
      sessionId
    };
    
    sendMessage(JSON.stringify(message));
    setIsPaused(!isPaused);
  }, [isPaused, sessionId, sendMessage]);

  // Stop simulation
  const stopSimulation = useCallback(() => {
    const message = {
      type: 'stop_monte_carlo',
      sessionId
    };
    
    sendMessage(JSON.stringify(message));
    setIsRunning(false);
    setIsPaused(false);
  }, [sessionId, sendMessage]);

  // Reset simulation
  const resetSimulation = useCallback(() => {
    setSimulationResults([]);
    setCurrentIteration(0);
    setProgress(0);
    setIsRunning(false);
    setIsPaused(false);
  }, []);

  // Calculate simulation statistics
  const simulationStatistics = useMemo(() => {
    if (simulationResults.length === 0) {
      return null;
    }

    const finalValues = simulationResults.map(r => r.finalValue);
    const sortedValues = [...finalValues].sort((a, b) => a - b);
    
    const mean = finalValues.reduce((sum, val) => sum + val, 0) / finalValues.length;
    const median = sortedValues[Math.floor(sortedValues.length / 2)];
    const variance = finalValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / finalValues.length;
    const stdDev = Math.sqrt(variance);
    
    const var95Index = Math.floor(sortedValues.length * 0.05);
    const var99Index = Math.floor(sortedValues.length * 0.01);
    const var95 = sortedValues[var95Index];
    const var99 = sortedValues[var99Index];
    
    // Calculate maximum drawdown
    const maxDrawdowns = simulationResults.map(result => {
      let maxDD = 0;
      let peak = result.pathData[0].value;
      
      for (const point of result.pathData) {
        if (point.value > peak) {
          peak = point.value;
        } else {
          const drawdown = (peak - point.value) / peak;
          maxDD = Math.max(maxDD, drawdown);
        }
      }
      return maxDD;
    });
    
    const avgMaxDrawdown = maxDrawdowns.reduce((sum, dd) => sum + dd, 0) / maxDrawdowns.length;
    
    // Probability of positive returns
    const positiveReturns = finalValues.filter(val => val > initialValue).length;
    const probabilityProfit = (positiveReturns / finalValues.length) * 100;
    
    return {
      mean,
      median,
      stdDev,
      var95,
      var99,
      maxDrawdown: avgMaxDrawdown,
      probabilityProfit,
      totalSimulations: simulationResults.length,
      confidenceInterval95: [
        mean - 1.96 * (stdDev / Math.sqrt(finalValues.length)),
        mean + 1.96 * (stdDev / Math.sqrt(finalValues.length))
      ]
    };
  }, [simulationResults, initialValue]);

  // Prepare path data for visualization
  const pathVisualizationData = useMemo(() => {
    if (simulationResults.length === 0) return [];
    
    // Take a sample of paths for visualization performance
    const sampleSize = Math.min(selectedPaths, simulationResults.length);
    const step = Math.max(1, Math.floor(simulationResults.length / sampleSize));
    const sampledResults = simulationResults.filter((_, index) => index % step === 0);
    
    // Transform data for time series chart
    const maxLength = Math.max(...sampledResults.map(r => r.pathData.length));
    const pathData = [];
    
    for (let timeIndex = 0; timeIndex < maxLength; timeIndex++) {
      const dataPoint: any = { time: timeIndex };
      
      sampledResults.forEach((result, pathIndex) => {
        if (result.pathData[timeIndex]) {
          dataPoint[`path_${pathIndex}`] = result.pathData[timeIndex].value;
        }
      });
      
      // Calculate percentiles for confidence bands
      const values = sampledResults
        .map(r => r.pathData[timeIndex]?.value)
        .filter(v => v !== undefined)
        .sort((a, b) => a - b);
      
      if (values.length > 0) {
        dataPoint.p5 = values[Math.floor(values.length * 0.05)];
        dataPoint.p25 = values[Math.floor(values.length * 0.25)];
        dataPoint.p50 = values[Math.floor(values.length * 0.50)];
        dataPoint.p75 = values[Math.floor(values.length * 0.75)];
        dataPoint.p95 = values[Math.floor(values.length * 0.95)];
        dataPoint.mean = values.reduce((sum, v) => sum + v, 0) / values.length;
      }
      
      pathData.push(dataPoint);
    }
    
    return pathData;
  }, [simulationResults, selectedPaths]);

  // Prepare distribution data
  const distributionData = useMemo(() => {
    if (simulationResults.length === 0) return [];
    
    const finalValues = simulationResults.map(r => r.finalValue);
    const min = Math.min(...finalValues);
    const max = Math.max(...finalValues);
    const binCount = 50;
    const binWidth = (max - min) / binCount;
    
    const histogram = [];
    for (let i = 0; i < binCount; i++) {
      const binStart = min + i * binWidth;
      const binEnd = binStart + binWidth;
      const count = finalValues.filter(v => v >= binStart && v < binEnd).length;
      
      histogram.push({
        binStart,
        binEnd,
        binMidpoint: binStart + binWidth / 2,
        count,
        probability: count / finalValues.length,
        cumulativeProbability: finalValues.filter(v => v <= binEnd).length / finalValues.length
      });
    }
    
    return histogram;
  }, [simulationResults]);

  const renderPathsVisualization = () => (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={pathVisualizationData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#3d3d56" />
        <XAxis 
          dataKey="time" 
          stroke="#b8b8cc"
          label={{ value: 'Time (Days)', position: 'insideBottom', offset: -10, fill: '#b8b8cc' }}
        />
        <YAxis 
          stroke="#b8b8cc"
          label={{ value: 'Portfolio Value', angle: -90, position: 'insideLeft', fill: '#b8b8cc' }}
        />
        <RechartsTooltip 
          contentStyle={{ 
            background: '#1a1a35', 
            border: '1px solid #3d3d56',
            borderRadius: '8px',
            color: '#e8e8f0'
          }}
        />
        
        {/* Confidence intervals */}
        {showConfidenceIntervals && (
          <>
            <Area
              type="monotone"
              dataKey="p95"
              stackId="1"
              stroke="none"
              fill="#1890ff20"
            />
            <Area
              type="monotone"
              dataKey="p75"
              stackId="2"
              stroke="none"
              fill="#1890ff30"
            />
            <Area
              type="monotone"
              dataKey="p25"
              stackId="3"
              stroke="none"
              fill="#1890ff40"
            />
            <Area
              type="monotone"
              dataKey="p5"
              stackId="4"
              stroke="none"
              fill="none"
            />
          </>
        )}
        
        {/* Mean line */}
        <Line
          type="monotone"
          dataKey="mean"
          stroke="#1890ff"
          strokeWidth={3}
          dot={false}
          name="Mean Path"
        />
        
        {/* Median line */}
        <Line
          type="monotone"
          dataKey="p50"
          stroke="#52c41a"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
          name="Median Path"
        />
      </AreaChart>
    </ResponsiveContainer>
  );

  const renderDistributionVisualization = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={8}>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={distributionData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3d3d56" />
            <XAxis 
              dataKey="binMidpoint"
              stroke="#b8b8cc"
              label={{ value: 'Portfolio Value', position: 'insideBottom', offset: -10, fill: '#b8b8cc' }}
            />
            <YAxis 
              yAxisId="left"
              stroke="#b8b8cc"
              label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fill: '#b8b8cc' }}
            />
            <YAxis 
              yAxisId="right" 
              orientation="right"
              stroke="#52c41a"
              label={{ value: 'Cumulative Probability', angle: 90, position: 'insideRight', fill: '#52c41a' }}
            />
            <RechartsTooltip 
              contentStyle={{ 
                background: '#1a1a35', 
                border: '1px solid #3d3d56',
                color: '#e8e8f0'
              }}
            />
            <Legend />
            <Bar 
              yAxisId="left"
              dataKey="count" 
              fill="#1890ff" 
              name="Frequency"
              opacity={0.8}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="cumulativeProbability" 
              stroke="#52c41a" 
              strokeWidth={2}
              name="Cumulative Probability"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </Grid>
      <Grid item xs={12} md={4}>
        <Stack spacing={2}>
          <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <Typography variant="h6" sx={{ color: '#ff4d4f', mb: 1 }}>
              Value at Risk (95%)
            </Typography>
            <Typography variant="h4" sx={{ color: '#e8e8f0' }}>
              ${simulationStatistics?.var95?.toFixed(2) || 0}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <Typography variant="h6" sx={{ color: '#1890ff', mb: 1 }}>
              Expected Value
            </Typography>
            <Typography variant="h4" sx={{ color: '#e8e8f0' }}>
              ${simulationStatistics?.mean?.toFixed(2) || 0}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
            <Typography variant="h6" sx={{ color: '#52c41a', mb: 1 }}>
              Probability of Profit
            </Typography>
            <Typography variant="h4" sx={{ color: '#e8e8f0' }}>
              {simulationStatistics?.probabilityProfit?.toFixed(1) || 0}%
            </Typography>
          </Paper>
        </Stack>
      </Grid>
    </Grid>
  );

  const renderStatisticsView = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
          <Typography variant="h6" sx={{ color: '#1890ff', mb: 1 }}>
            Mean Return
          </Typography>
          <Typography variant="h4" sx={{ color: '#e8e8f0' }}>
            ${simulationStatistics?.mean?.toFixed(2) || 0}
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
          <Typography variant="h6" sx={{ color: '#fa8c16', mb: 1 }}>
            Standard Deviation
          </Typography>
          <Typography variant="h4" sx={{ color: '#e8e8f0' }}>
            ${simulationStatistics?.stdDev?.toFixed(2) || 0}
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
          <Typography variant="h6" sx={{ color: '#ff4d4f', mb: 1 }}>
            VaR (95%)
          </Typography>
          <Typography variant="h4" sx={{ color: '#e8e8f0' }}>
            ${simulationStatistics?.var95?.toFixed(2) || 0}
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Paper sx={{ p: 2, backgroundColor: '#252547', border: '1px solid #3d3d56' }}>
          <Typography variant="h6" sx={{ color: '#722ed1', mb: 1 }}>
            Max Drawdown
          </Typography>
          <Typography variant="h4" sx={{ color: '#e8e8f0' }}>
            {((simulationStatistics?.maxDrawdown || 0) * 100).toFixed(1)}%
          </Typography>
        </Paper>
      </Grid>
    </Grid>
  );

  // Auto-start simulation if requested
  useEffect(() => {
    if (autoStart && !isRunning && simulationResults.length === 0) {
      startSimulation();
    }
  }, [autoStart, isRunning, simulationResults.length, startSimulation]);

  return (
    <Box sx={{ backgroundColor: '#0f0f23', minHeight: '100vh' }}>
      {/* Control Panel */}
      <Card 
        sx={{ 
          background: '#1a1a35', 
          border: '1px solid #3d3d56', 
          mb: 2 
        }}
      >
        <CardContent sx={{ p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Button
                  variant="contained"
                  startIcon={<PlayCircleOutlined />}
                  onClick={startSimulation}
                  disabled={isRunning}
                  sx={{ backgroundColor: '#1890ff' }}
                >
                  Start Simulation
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={isPaused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
                  onClick={togglePause}
                  disabled={!isRunning}
                  sx={{ borderColor: '#1890ff', color: '#1890ff' }}
                >
                  {isPaused ? 'Resume' : 'Pause'}
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<StopOutlined />}
                  onClick={stopSimulation}
                  disabled={!isRunning}
                  sx={{ borderColor: '#ff4d4f', color: '#ff4d4f' }}
                >
                  Stop
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<RefreshOutlined />}
                  onClick={resetSimulation}
                  disabled={isRunning}
                  sx={{ borderColor: '#52c41a', color: '#52c41a' }}
                >
                  Reset
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<FileDownloadOutlined />}
                  disabled={simulationResults.length === 0}
                  sx={{ borderColor: '#fa8c16', color: '#fa8c16' }}
                >
                  Export Results
                </Button>
              </Stack>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Stack direction="row" spacing={2} alignItems="center">
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  Progress: {currentIteration.toLocaleString()} / {parameters.iterations.toLocaleString()}
                </Typography>
                <LinearProgress 
                  variant="determinate"
                  value={progress}
                  sx={{ 
                    flexGrow: 1,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: '#3d3d56',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#1890ff',
                    },
                  }}
                />
              </Stack>
            </Grid>
          </Grid>

          {/* Parameters */}
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel sx={{ color: '#b8b8cc' }}>Iterations</InputLabel>
                <Select
                  value={parameters.iterations}
                  onChange={(e) => setParameters(prev => ({ ...prev, iterations: e.target.value as number }))}
                  disabled={isRunning}
                  sx={{ color: '#e8e8f0' }}
                >
                  <MenuItem value={1000}>1,000</MenuItem>
                  <MenuItem value={5000}>5,000</MenuItem>
                  <MenuItem value={10000}>10,000</MenuItem>
                  <MenuItem value={50000}>50,000</MenuItem>
                  <MenuItem value={100000}>100,000</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Volatility: {(parameters.volatility * 100).toFixed(1)}%
                </Typography>
                <Slider
                  min={0.05}
                  max={0.5}
                  step={0.01}
                  value={parameters.volatility}
                  onChange={(_, value) => setParameters(prev => ({ ...prev, volatility: value as number }))}
                  disabled={isRunning}
                  sx={{ color: '#1890ff' }}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Time Horizon: {parameters.timeHorizon} days
                </Typography>
                <Slider
                  min={30}
                  max={1260}
                  step={30}
                  value={parameters.timeHorizon}
                  onChange={(_, value) => setParameters(prev => ({ ...prev, timeHorizon: value as number }))}
                  disabled={isRunning}
                  sx={{ color: '#1890ff' }}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1 }}>
                  Market Shock: {(parameters.marketShock * 100).toFixed(1)}%
                </Typography>
                <Slider
                  min={-0.5}
                  max={0.5}
                  step={0.01}
                  value={parameters.marketShock}
                  onChange={(_, value) => setParameters(prev => ({ ...prev, marketShock: value as number }))}
                  disabled={isRunning}
                  sx={{ color: '#1890ff' }}
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Visualization Controls */}
      <Card 
        sx={{ 
          background: '#1a1a35', 
          border: '1px solid #3d3d56', 
          mb: 2 
        }}
      >
        <CardContent sx={{ p: 2 }}>
          <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
            <Button
              variant={visualizationMode === 'paths' ? 'contained' : 'outlined'}
              onClick={() => setVisualizationMode('paths')}
              size="small"
              sx={{ 
                backgroundColor: visualizationMode === 'paths' ? '#1890ff' : 'transparent',
                borderColor: '#1890ff',
                color: '#1890ff'
              }}
            >
              Simulation Paths
            </Button>
            <Button
              variant={visualizationMode === 'distribution' ? 'contained' : 'outlined'}
              onClick={() => setVisualizationMode('distribution')}
              size="small"
              sx={{ 
                backgroundColor: visualizationMode === 'distribution' ? '#1890ff' : 'transparent',
                borderColor: '#1890ff',
                color: '#1890ff'
              }}
            >
              Distribution
            </Button>
            <Button
              variant={visualizationMode === 'statistics' ? 'contained' : 'outlined'}
              onClick={() => setVisualizationMode('statistics')}
              size="small"
              sx={{ 
                backgroundColor: visualizationMode === 'statistics' ? '#1890ff' : 'transparent',
                borderColor: '#1890ff',
                color: '#1890ff'
              }}
            >
              Statistics
            </Button>
            <Button
              variant={visualizationMode === 'risk' ? 'contained' : 'outlined'}
              onClick={() => setVisualizationMode('risk')}
              size="small"
              sx={{ 
                backgroundColor: visualizationMode === 'risk' ? '#1890ff' : 'transparent',
                borderColor: '#1890ff',
                color: '#1890ff'
              }}
            >
              Risk Metrics
            </Button>
            
            {visualizationMode === 'paths' && (
              <FormControl size="small" sx={{ minWidth: 100 }}>
                <InputLabel sx={{ color: '#b8b8cc' }}>Show Paths</InputLabel>
                <Select
                  value={selectedPaths}
                  onChange={(e) => setSelectedPaths(e.target.value as number)}
                  sx={{ color: '#e8e8f0' }}
                >
                  <MenuItem value={10}>10</MenuItem>
                  <MenuItem value={50}>50</MenuItem>
                  <MenuItem value={100}>100</MenuItem>
                  <MenuItem value={500}>500</MenuItem>
                </Select>
              </FormControl>
            )}
          </Stack>
        </CardContent>
      </Card>

      {/* Main Visualization */}
      <Card
        sx={{
          background: '#1a1a35',
          border: '1px solid #3d3d56'
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <TrendingUpOutlined sx={{ color: '#1890ff' }} />
              <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
                Monte Carlo Simulation Results
              </Typography>
              {isRunning && <CircularProgress size={20} sx={{ color: '#1890ff' }} />}
              <Tooltip title="10,000 iteration Monte Carlo simulation with real-time updates">
                <IconButton size="small">
                  <InfoOutlined sx={{ color: '#b8b8cc' }} />
                </IconButton>
              </Tooltip>
            </Stack>
            {simulationStatistics && (
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                  Simulations: {simulationStatistics.totalSimulations.toLocaleString()}
                </Typography>
                {simulationStatistics.probabilityProfit < 50 && (
                  <Tooltip title="Low probability of positive returns">
                    <WarningOutlined sx={{ color: '#ff4d4f' }} />
                  </Tooltip>
                )}
              </Stack>
            )}
          </Box>

          {simulationResults.length === 0 && !isRunning && (
            <Alert
              severity="info"
              sx={{ 
                background: '#252547', 
                border: '1px solid #3d3d56',
                color: '#e8e8f0'
              }}
            >
              No simulation data available. Start a Monte Carlo simulation to see results and analysis.
            </Alert>
          )}

          {visualizationMode === 'paths' && simulationResults.length > 0 && renderPathsVisualization()}
          {visualizationMode === 'distribution' && simulationResults.length > 0 && renderDistributionVisualization()}
          {visualizationMode === 'statistics' && simulationResults.length > 0 && renderStatisticsView()}
          
          {isRunning && (
            <Box sx={{ textAlign: 'center', py: 5 }}>
              <CircularProgress size={60} sx={{ color: '#1890ff', mb: 2 }} />
              <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 1 }}>
                Running simulation... {currentIteration.toLocaleString()} iterations completed
              </Typography>
              <LinearProgress 
                variant="determinate"
                value={progress}
                sx={{ 
                  maxWidth: '300px',
                  mx: 'auto',
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: '#3d3d56',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: '#1890ff',
                  },
                }}
              />
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default MonteCarloSimulation;
