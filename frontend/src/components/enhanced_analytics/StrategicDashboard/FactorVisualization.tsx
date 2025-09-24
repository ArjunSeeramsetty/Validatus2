// frontend/src/components/enhanced_analytics/StrategicDashboard/FactorVisualization.tsx
import React, { useState, useMemo, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Stack,
  Tabs,
  Tab,
  LinearProgress,
  Chip,
  Tooltip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Switch,
  FormControlLabel,
  Radio,
  RadioGroup,
  FormLabel,
  Grid,
  Paper,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  InfoOutlined,
  TrendingUpOutlined,
  WarningOutlined,
  FilterListOutlined,
  ViewListOutlined,
  RadarOutlined,
  BubbleChartOutlined
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  Treemap,
  Cell,
  ComposedChart,
  Area,
  AreaChart
} from 'recharts';

// Factor definitions mapping to F1-F28
const FACTOR_DEFINITIONS = {
  // Market Factors (F1-F7)
  'F1_market_size': {
    name: 'Market Size',
    category: 'Market',
    description: 'Total Addressable Market with growth projections',
    weight: 0.15,
    color: '#1890ff',
    icon: '🏢'
  },
  'F2_market_growth': {
    name: 'Market Growth',
    category: 'Market',
    description: 'Market growth rate and sustainability analysis',
    weight: 0.12,
    color: '#52c41a',
    icon: '📈'
  },
  'F3_market_maturity': {
    name: 'Market Maturity',
    category: 'Market',
    description: 'Market lifecycle stage and opportunity assessment',
    weight: 0.10,
    color: '#fa8c16',
    icon: '🔄'
  },
  'F4_competitive_intensity': {
    name: 'Competitive Intensity',
    category: 'Market',
    description: "Porter's Five Forces competitive analysis",
    weight: 0.13,
    color: '#ff4d4f',
    icon: '⚔️'
  },
  'F5_barrier_to_entry': {
    name: 'Barriers to Entry',
    category: 'Market',
    description: 'Market entry barriers and defensibility',
    weight: 0.11,
    color: '#722ed1',
    icon: '🚧'
  },
  'F6_regulatory_environment': {
    name: 'Regulatory Environment',
    category: 'Market',
    description: 'Regulatory complexity and compliance requirements',
    weight: 0.09,
    color: '#13c2c2',
    icon: '⚖️'
  },
  'F7_economic_sensitivity': {
    name: 'Economic Sensitivity',
    category: 'Market',
    description: 'Economic cycle sensitivity and resilience',
    weight: 0.08,
    color: '#eb2f96',
    icon: '💰'
  },

  // Product Factors (F8-F14)
  'F8_product_differentiation': {
    name: 'Product Differentiation',
    category: 'Product',
    description: 'Product uniqueness and competitive advantage',
    weight: 0.14,
    color: '#1890ff',
    icon: '🎯'
  },
  'F9_innovation_capability': {
    name: 'Innovation Capability',
    category: 'Product',
    description: 'R&D capabilities and innovation pipeline',
    weight: 0.13,
    color: '#52c41a',
    icon: '💡'
  },
  'F10_quality_reliability': {
    name: 'Quality & Reliability',
    category: 'Product',
    description: 'Product quality and reliability metrics',
    weight: 0.12,
    color: '#fa8c16',
    icon: '✅'
  },
  'F11_scalability_potential': {
    name: 'Scalability Potential',
    category: 'Product',
    description: 'Business model scalability and growth potential',
    weight: 0.11,
    color: '#ff4d4f',
    icon: '📊'
  },
  'F12_customer_stickiness': {
    name: 'Customer Stickiness',
    category: 'Product',
    description: 'Customer retention and switching costs',
    weight: 0.10,
    color: '#722ed1',
    icon: '🔗'
  },
  'F13_pricing_power': {
    name: 'Pricing Power',
    category: 'Product',
    description: 'Pricing flexibility and margin sustainability',
    weight: 0.09,
    color: '#13c2c2',
    icon: '💲'
  },
  'F14_lifecycle_position': {
    name: 'Lifecycle Position',
    category: 'Product',
    description: 'Product lifecycle stage and longevity',
    weight: 0.08,
    color: '#eb2f96',
    icon: '🔄'
  },

  // Financial Factors (F15-F21)
  'F15_revenue_growth': {
    name: 'Revenue Growth',
    category: 'Financial',
    description: 'Revenue growth rate and sustainability',
    weight: 0.16,
    color: '#1890ff',
    icon: '💹'
  },
  'F16_profitability_margins': {
    name: 'Profitability Margins',
    category: 'Financial',
    description: 'Gross, operating, and net margin analysis',
    weight: 0.15,
    color: '#52c41a',
    icon: '📈'
  },
  'F17_cash_flow_generation': {
    name: 'Cash Flow Generation',
    category: 'Financial',
    description: 'Free cash flow generation and conversion',
    weight: 0.14,
    color: '#fa8c16',
    icon: '💰'
  },
  'F18_capital_efficiency': {
    name: 'Capital Efficiency',
    category: 'Financial',
    description: 'Return on invested capital and asset utilization',
    weight: 0.13,
    color: '#ff4d4f',
    icon: '⚡'
  },
  'F19_financial_stability': {
    name: 'Financial Stability',
    category: 'Financial',
    description: 'Debt levels, liquidity, and financial risk',
    weight: 0.12,
    color: '#722ed1',
    icon: '🏦'
  },
  'F20_cost_structure': {
    name: 'Cost Structure',
    category: 'Financial',
    description: 'Fixed vs variable cost optimization',
    weight: 0.10,
    color: '#13c2c2',
    icon: '📊'
  },
  'F21_working_capital': {
    name: 'Working Capital',
    category: 'Financial',
    description: 'Working capital management efficiency',
    weight: 0.08,
    color: '#eb2f96',
    icon: '⚙️'
  },

  // Strategic Factors (F22-F28)
  'F22_brand_strength': {
    name: 'Brand Strength',
    category: 'Strategic',
    description: 'Brand recognition, loyalty, and equity',
    weight: 0.16,
    color: '#1890ff',
    icon: '🏆'
  },
  'F23_management_quality': {
    name: 'Management Quality',
    category: 'Strategic',
    description: 'Leadership capability and execution track record',
    weight: 0.15,
    color: '#52c41a',
    icon: '👥'
  },
  'F24_strategic_positioning': {
    name: 'Strategic Positioning',
    category: 'Strategic',
    description: 'Competitive positioning and strategic clarity',
    weight: 0.14,
    color: '#fa8c16',
    icon: '🎯'
  },
  'F25_operational_excellence': {
    name: 'Operational Excellence',
    category: 'Strategic',
    description: 'Operational efficiency and process optimization',
    weight: 0.13,
    color: '#ff4d4f',
    icon: '⚙️'
  },
  'F26_digital_transformation': {
    name: 'Digital Transformation',
    category: 'Strategic',
    description: 'Digital capabilities and technology adoption',
    weight: 0.12,
    color: '#722ed1',
    icon: '💻'
  },
  'F27_sustainability_esg': {
    name: 'Sustainability & ESG',
    category: 'Strategic',
    description: 'Environmental, Social, Governance factors',
    weight: 0.10,
    color: '#13c2c2',
    icon: '🌿'
  },
  'F28_strategic_flexibility': {
    name: 'Strategic Flexibility',
    category: 'Strategic',
    description: 'Adaptability and strategic option value',
    weight: 0.08,
    color: '#eb2f96',
    icon: '🔄'
  }
};

interface FactorResult {
  formula_name: string;
  raw_score: number;
  normalized_score: number;
  confidence: number;
  calculation_steps: Array<{ step: string; value: any }>;
  metadata: {
    weight: number;
    description: string;
    calculation_timestamp: string;
  };
}

interface FactorVisualizationProps {
  factorResults: Record<string, FactorResult>;
  sessionId: string;
  isLoading?: boolean;
  showDetailedView?: boolean;
  onFactorSelect?: (factorId: string) => void;
}

const FactorVisualization: React.FC<FactorVisualizationProps> = ({
  factorResults,
  sessionId,
  isLoading = false,
  showDetailedView = false,
  onFactorSelect
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [visualizationType, setVisualizationType] = useState<'overview' | 'radar' | 'treemap' | 'detailed'>('overview');
  const [showConfidence, setShowConfidence] = useState(true);
  const [sortBy, setSortBy] = useState<'score' | 'confidence' | 'weight' | 'name'>('score');
  const [scoreThreshold, setScoreThreshold] = useState<[number, number]>([0, 1]);

  // Process factor data for visualizations
  const processedFactorData = useMemo(() => {
    const factors = Object.entries(factorResults).map(([factorId, result]) => {
      const definition = FACTOR_DEFINITIONS[factorId as keyof typeof FACTOR_DEFINITIONS];
      return {
        id: factorId,
        name: definition?.name || factorId,
        category: definition?.category || 'Unknown',
        score: result.normalized_score,
        rawScore: result.raw_score,
        confidence: result.confidence,
        weight: definition?.weight || 0,
        color: definition?.color || '#1890ff',
        icon: definition?.icon || '📊',
        description: definition?.description || result.metadata.description,
        calculationSteps: result.calculation_steps,
        timestamp: result.metadata.calculation_timestamp
      };
    });

    // Filter by category
    const filtered = selectedCategory === 'All' 
      ? factors 
      : factors.filter(f => f.category === selectedCategory);

    // Filter by score threshold
    const thresholdFiltered = filtered.filter(
      f => f.score >= scoreThreshold[0] && f.score <= scoreThreshold[1]
    );

    // Sort factors
    const sorted = [...thresholdFiltered].sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.score - a.score;
        case 'confidence':
          return b.confidence - a.confidence;
        case 'weight':
          return b.weight - a.weight;
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return b.score - a.score;
      }
    });

    return sorted;
  }, [factorResults, selectedCategory, sortBy, scoreThreshold]);

  // Category summary data
  const categoryData = useMemo(() => {
    const categories = ['Market', 'Product', 'Financial', 'Strategic'];
    return categories.map(category => {
      const categoryFactors = processedFactorData.filter(f => f.category === category);
      const avgScore = categoryFactors.reduce((sum, f) => sum + f.score, 0) / categoryFactors.length || 0;
      const avgConfidence = categoryFactors.reduce((sum, f) => sum + f.confidence, 0) / categoryFactors.length || 0;
      const totalWeight = categoryFactors.reduce((sum, f) => sum + f.weight, 0);

      return {
        category,
        averageScore: avgScore,
        averageConfidence: avgConfidence,
        totalWeight,
        factorCount: categoryFactors.length,
        color: categoryFactors[0]?.color || '#1890ff'
      };
    });
  }, [processedFactorData]);

  // Radar chart data
  const radarData = useMemo(() => {
    return processedFactorData.map(factor => ({
      factor: factor.name.substring(0, 15) + '...',
      score: Math.round(factor.score * 100),
      confidence: Math.round(factor.confidence * 100),
      fullName: factor.name
    }));
  }, [processedFactorData]);

  const handleFactorClick = useCallback((factorId: string) => {
    onFactorSelect?.(factorId);
  }, [onFactorSelect]);

  const renderOverviewChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={processedFactorData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#3d3d56" />
        <XAxis 
          dataKey="name" 
          angle={-45}
          textAnchor="end"
          height={100}
          stroke="#b8b8cc"
          fontSize={12}
        />
        <YAxis stroke="#b8b8cc" />
        <RechartsTooltip 
          contentStyle={{ 
            background: '#1a1a35', 
            border: '1px solid #3d3d56',
            borderRadius: '8px',
            color: '#e8e8f0'
          }}
          formatter={(value: any, name: string) => [
            `${(value * 100).toFixed(1)}%`,
            name === 'score' ? 'Score' : 'Confidence'
          ]}
        />
        <Legend />
        <Bar 
          dataKey="score" 
          fill="#1890ff" 
          name="Factor Score"
          radius={[4, 4, 0, 0]}
        />
        {showConfidence && (
          <Bar 
            dataKey="confidence" 
            fill="#52c41a" 
            name="Confidence"
            radius={[4, 4, 0, 0]}
            opacity={0.7}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );

  const renderRadarChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart data={radarData}>
        <PolarGrid stroke="#3d3d56" />
        <PolarAngleAxis 
          dataKey="factor" 
          tick={{ fill: '#b8b8cc', fontSize: 11 }}
        />
        <PolarRadiusAxis 
          angle={90}
          domain={[0, 100]}
          tick={{ fill: '#b8b8cc', fontSize: 10 }}
        />
        <Radar 
          name="Factor Scores" 
          dataKey="score" 
          stroke="#1890ff" 
          fill="#1890ff" 
          fillOpacity={0.3}
          strokeWidth={2}
        />
        {showConfidence && (
          <Radar 
            name="Confidence" 
            dataKey="confidence" 
            stroke="#52c41a" 
            fill="#52c41a" 
            fillOpacity={0.2}
            strokeWidth={2}
          />
        )}
        <RechartsTooltip 
          contentStyle={{ 
            background: '#1a1a35', 
            border: '1px solid #3d3d56',
            color: '#e8e8f0'
          }}
        />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );

  const renderFactorCards = () => (
    <Grid container spacing={2}>
      {processedFactorData.map((factor, index) => (
        <Grid item xs={12} sm={6} lg={4} xl={3} key={factor.id}>
          <Card
            sx={{
              background: '#1a1a35',
              border: `1px solid ${factor.score > 0.7 ? '#52c41a' : factor.score < 0.4 ? '#ff4d4f' : '#3d3d56'}`,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 20px rgba(24, 144, 255, 0.3)',
              }
            }}
            onClick={() => handleFactorClick(factor.id)}
          >
            <CardContent sx={{ p: 2 }}>
              <Stack spacing={1}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography sx={{ fontSize: '16px' }}>{factor.icon}</Typography>
                    <Typography variant="subtitle2" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                      {factor.name}
                    </Typography>
                  </Stack>
                  <Chip 
                    label={factor.category} 
                    size="small"
                    sx={{ 
                      backgroundColor: factor.color + '20',
                      color: factor.color,
                      fontSize: '10px'
                    }}
                  />
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={factor.score * 100}
                  sx={{
                    height: 6,
                    backgroundColor: '#3d3d56',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: factor.color,
                    },
                  }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Score: <Typography component="span" sx={{ color: '#e8e8f0' }}>
                      {(factor.score * 100).toFixed(1)}%
                    </Typography>
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                    Confidence: <Typography component="span" sx={{ color: '#e8e8f0' }}>
                      {(factor.confidence * 100).toFixed(0)}%
                    </Typography>
                  </Typography>
                </Box>

                {factor.score < 0.4 && (
                  <Alert severity="warning" size="small" sx={{ backgroundColor: '#2d1b0e', color: '#e8e8f0' }}>
                    <Typography variant="caption">Below Threshold</Typography>
                  </Alert>
                )}

                <Tooltip title={factor.description}>
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: '#8c8ca0',
                      cursor: 'help',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                  >
                    {factor.description}
                  </Typography>
                </Tooltip>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ backgroundColor: '#0f0f23', minHeight: '100vh', p: 0 }}>
      {/* Controls */}
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
              <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel sx={{ color: '#b8b8cc' }}>Category</InputLabel>
                  <Select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    label="Category"
                    sx={{ color: '#e8e8f0' }}
                  >
                    <MenuItem value="All">All Categories</MenuItem>
                    <MenuItem value="Market">Market</MenuItem>
                    <MenuItem value="Product">Product</MenuItem>
                    <MenuItem value="Financial">Financial</MenuItem>
                    <MenuItem value="Strategic">Strategic</MenuItem>
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 100 }}>
                  <InputLabel sx={{ color: '#b8b8cc' }}>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    label="Sort By"
                    sx={{ color: '#e8e8f0' }}
                  >
                    <MenuItem value="score">Score</MenuItem>
                    <MenuItem value="confidence">Confidence</MenuItem>
                    <MenuItem value="weight">Weight</MenuItem>
                    <MenuItem value="name">Name</MenuItem>
                  </Select>
                </FormControl>

                <FormControlLabel
                  control={
                    <Switch
                      checked={showConfidence}
                      onChange={(e) => setShowConfidence(e.target.checked)}
                      size="small"
                    />
                  }
                  label={<Typography variant="caption" sx={{ color: '#b8b8cc' }}>Show Confidence</Typography>}
                />
              </Stack>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Stack direction="row" spacing={1} alignItems="center">
                <FilterListOutlined sx={{ color: '#b8b8cc', fontSize: 16 }} />
                <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                  Score Range: {(scoreThreshold[0] * 100).toFixed(0)}% - {(scoreThreshold[1] * 100).toFixed(0)}%
                </Typography>
              </Stack>
              <Slider
                value={scoreThreshold}
                onChange={(_, value) => setScoreThreshold(value as [number, number])}
                min={0}
                max={1}
                step={0.1}
                marks={{
                  0: { label: '0%' },
                  0.5: { label: '50%' },
                  1: { label: '100%' }
                }}
                sx={{ mt: 1 }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Category Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        {categoryData.map(category => (
          <Grid item xs={12} sm={6} lg={3} key={category.category}>
            <Card
              sx={{
                background: '#1a1a35',
                border: '1px solid #3d3d56'
              }}
            >
              <CardContent sx={{ p: 2 }}>
                <Stack spacing={1}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle2" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                      {category.category}
                    </Typography>
                    <Chip label={`${category.factorCount} factors`} size="small" />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={category.averageScore * 100}
                    sx={{
                      height: 6,
                      backgroundColor: '#3d3d56',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: category.color,
                      },
                    }}
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                      Avg Score: <Typography component="span" sx={{ color: '#e8e8f0' }}>
                        {(category.averageScore * 100).toFixed(1)}%
                      </Typography>
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                      Confidence: <Typography component="span" sx={{ color: '#e8e8f0' }}>
                        {(category.averageConfidence * 100).toFixed(0)}%
                      </Typography>
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

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
                F1-F28 Strategic Factor Analysis
              </Typography>
              <Typography variant="caption" sx={{ color: '#b8b8cc' }}>
                ({processedFactorData.length} factors • Session: {sessionId.substring(0, 8)})
              </Typography>
            </Stack>
            <Tooltip title="Factor analysis based on comprehensive strategic assessment">
              <IconButton size="small">
                <InfoOutlined sx={{ color: '#b8b8cc' }} />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Visualization Type Selector */}
          <Box sx={{ mb: 3 }}>
            <RadioGroup
              row
              value={visualizationType}
              onChange={(e) => setVisualizationType(e.target.value as any)}
            >
              <FormControlLabel 
                value="overview" 
                control={<Radio size="small" sx={{ color: '#1890ff' }} />}
                label={<Typography variant="caption" sx={{ color: '#e8e8f0' }}>Overview</Typography>}
              />
              <FormControlLabel 
                value="radar" 
                control={<Radio size="small" sx={{ color: '#1890ff' }} />}
                label={<Typography variant="caption" sx={{ color: '#e8e8f0' }}>Radar</Typography>}
              />
              <FormControlLabel 
                value="detailed" 
                control={<Radio size="small" sx={{ color: '#1890ff' }} />}
                label={<Typography variant="caption" sx={{ color: '#e8e8f0' }}>Cards</Typography>}
              />
            </RadioGroup>
          </Box>

          {/* Visualization Content */}
          {visualizationType === 'overview' && renderOverviewChart()}
          {visualizationType === 'radar' && renderRadarChart()}
          {visualizationType === 'detailed' && renderFactorCards()}
        </CardContent>
      </Card>
    </Box>
  );
};

export default FactorVisualization;
