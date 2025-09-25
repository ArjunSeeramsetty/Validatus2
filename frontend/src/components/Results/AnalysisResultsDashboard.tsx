import React, { useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, 
  LinearProgress, Chip, Button, Paper, Alert,
  IconButton, Menu, MenuItem, ListItemIcon, ListItemText
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { motion } from 'framer-motion';
import { TrendingUp, Insights, Assessment, MoreVert, Download, Share, Refresh } from '@mui/icons-material';
import ExportDialog from '../Export/ExportDialog';

interface AnalysisResult {
  id: string;
  topic: string;
  status: 'completed' | 'running' | 'failed';
  layerScores: { [layer: string]: number };
  factorScores: { [factor: string]: number };
  segmentScores: { [segment: string]: number };
  insights: string[];
  recommendations: string[];
  createdAt: string;
  progress?: number;
}

interface AnalysisResultsDashboardProps {
  results?: AnalysisResult[];
}

const AnalysisResultsDashboard: React.FC<AnalysisResultsDashboardProps> = ({ results = [] }) => {
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedResult, setSelectedResult] = useState<AnalysisResult | null>(null);

  // Mock data for demonstration
  const mockResults: AnalysisResult[] = results.length > 0 ? results : [
    {
      id: 'analysis-1',
      topic: 'Electric Vehicle Market Analysis',
      status: 'completed',
      layerScores: {
        'Strategic Planning': 85,
        'Market Analysis': 92,
        'Competitive Intelligence': 78,
        'Risk Assessment': 88,
        'Value Creation': 91,
        'Implementation': 82
      },
      factorScores: {
        'Market Size': 95,
        'Growth Rate': 88,
        'Competition Level': 72,
        'Technology Readiness': 85,
        'Regulatory Environment': 90,
        'Customer Demand': 93
      },
      segmentScores: {
        'Luxury EVs': 89,
        'Mid-Market EVs': 85,
        'Budget EVs': 76,
        'Commercial EVs': 82
      },
      insights: [
        'Electric vehicle market is experiencing 35% year-over-year growth',
        'Luxury segment commands 40% higher profit margins than mid-market',
        'Regulatory incentives are driving adoption in key markets',
        'Battery technology improvements are reducing costs by 15% annually'
      ],
      recommendations: [
        'Focus on luxury segment for maximum profitability',
        'Invest in battery technology partnerships',
        'Expand into commercial vehicle market',
        'Develop charging infrastructure partnerships'
      ],
      createdAt: '2024-09-21T10:00:00Z'
    }
  ];

  const handleExportClick = (result: AnalysisResult) => {
    setSelectedSessionId(result.id);
    setSelectedResult(result);
    setExportDialogOpen(true);
    setAnchorEl(null);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, result: AnalysisResult) => {
    setAnchorEl(event.currentTarget);
    setSelectedResult(result);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedResult(null);
  };

  const renderLayerScores = (layerScores: { [layer: string]: number }) => {
    const data = Object.entries(layerScores).map(([layer, score]) => ({
      layer: layer.length > 12 ? layer.substring(0, 12) + '...' : layer,
      score,
      fullLayer: layer
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3d3d56" />
          <XAxis 
            dataKey="layer" 
            tick={{ fill: '#b8b8cc', fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            tick={{ fill: '#b8b8cc' }} 
            domain={[0, 100]}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1a35', 
              border: '1px solid #3d3d56',
              color: '#e8e8f0',
              borderRadius: '8px'
            }}
            formatter={(value: number, name: string, props: any) => [
              `${value}%`,
              props.payload.fullLayer
            ]}
          />
          <Bar 
            dataKey="score" 
            fill="#1890ff" 
            radius={[4, 4, 0, 0]}
            maxBarSize={60}
          />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderFactorTrends = (factorScores: { [factor: string]: number }) => {
    const data = Object.entries(factorScores).map(([factor, score], index) => ({
      factor: factor.length > 15 ? factor.substring(0, 15) + '...' : factor,
      score,
      trend: score + (Math.random() - 0.5) * 10, // Mock trend data
      fullFactor: factor
    }));

    return (
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3d3d56" />
          <XAxis 
            dataKey="factor" 
            tick={{ fill: '#b8b8cc', fontSize: 11 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis tick={{ fill: '#b8b8cc' }} domain={[0, 100]} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1a35', 
              border: '1px solid #3d3d56',
              color: '#e8e8f0',
              borderRadius: '8px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="score" 
            stroke="#52c41a" 
            strokeWidth={3}
            dot={{ fill: '#52c41a', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#52c41a', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <Box sx={{ p: 4, minHeight: '100vh', backgroundColor: '#0f0f23' }}>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Insights sx={{ color: '#1890ff', fontSize: 32 }} />
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
              Analysis Results Dashboard
            </Typography>
          </Box>
        </motion.div>

        {mockResults.length === 0 ? (
          <motion.div variants={itemVariants}>
            <Paper sx={{ p: 6, textAlign: 'center', background: '#1a1a35', border: '1px solid #3d3d56' }}>
              <Assessment sx={{ fontSize: 64, color: '#3d3d56', mb: 2 }} />
              <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 2 }}>
                No Analysis Results Yet
              </Typography>
              <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 3 }}>
                Complete your first strategic analysis to see results here
              </Typography>
              <Button 
                variant="contained" 
                href="/strategic-analysis"
                sx={{
                  background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                  }
                }}
              >
                Start Strategic Analysis
              </Button>
            </Paper>
          </motion.div>
        ) : (
          <Grid container spacing={3}>
            {mockResults.map((result, index) => (
              <Grid item xs={12} key={result.id}>
                <motion.div variants={itemVariants}>
                  <Card sx={{ 
                    background: '#1a1a35', 
                    border: '1px solid #3d3d56',
                    transition: 'transform 0.2s',
                    '&:hover': { transform: 'translateY(-2px)' }
                  }}>
                    <CardContent sx={{ p: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h5" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                          {result.topic}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Chip 
                            label={result.status.toUpperCase()} 
                            color={result.status === 'completed' ? 'success' : 'primary'}
                            size="small"
                            sx={{
                              backgroundColor: result.status === 'completed' ? '#52c41a20' : '#1890ff20',
                              color: result.status === 'completed' ? '#52c41a' : '#1890ff',
                              fontWeight: 600
                            }}
                          />
                          <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                            {new Date(result.createdAt).toLocaleDateString()}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={(e) => handleMenuOpen(e, result)}
                            sx={{ color: '#8c8ca0' }}
                          >
                            <MoreVert />
                          </IconButton>
                        </Box>
                      </Box>

                      {/* Layer Scores Visualization */}
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, fontWeight: 600 }}>
                        Strategic Layer Scores
                      </Typography>
                      {renderLayerScores(result.layerScores)}

                      {/* Factor Analysis */}
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, mt: 4, fontWeight: 600 }}>
                        Strategic Factor Trends
                      </Typography>
                      {renderFactorTrends(result.factorScores)}

                      {/* Factor Scores Grid */}
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, mt: 4, fontWeight: 600 }}>
                        Factor Analysis Breakdown
                      </Typography>
                      <Grid container spacing={2} sx={{ mb: 4 }}>
                        {Object.entries(result.factorScores).map(([factor, score]) => (
                          <Grid item xs={12} sm={6} md={4} key={factor}>
                            <Box sx={{ 
                              p: 2, 
                              background: '#252547', 
                              borderRadius: 2, 
                              border: '1px solid #3d3d56',
                              transition: 'transform 0.2s',
                              '&:hover': { transform: 'translateY(-2px)' }
                            }}>
                              <Typography variant="body2" sx={{ color: '#b8b8cc', mb: 1, fontWeight: 500 }}>
                                {factor}
                              </Typography>
                              <LinearProgress 
                                variant="determinate" 
                                value={score} 
                                sx={{ 
                                  height: 8, 
                                  borderRadius: 4,
                                  backgroundColor: '#3d3d56',
                                  '& .MuiLinearProgress-bar': {
                                    backgroundColor: score > 80 ? '#52c41a' : score > 60 ? '#fa8c16' : '#ff4d4f',
                                    borderRadius: 4
                                  }
                                }} 
                              />
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                                <Typography variant="caption" sx={{ 
                                  color: score > 80 ? '#52c41a' : score > 60 ? '#fa8c16' : '#ff4d4f',
                                  fontWeight: 600
                                }}>
                                  {score}%
                                </Typography>
                                <TrendingUp sx={{ 
                                  fontSize: 16, 
                                  color: score > 80 ? '#52c41a' : '#8c8ca0' 
                                }} />
                              </Box>
                            </Box>
                          </Grid>
                        ))}
                      </Grid>

                      {/* Key Insights */}
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, fontWeight: 600 }}>
                        Key Insights
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
                        {result.insights.map((insight, insightIndex) => (
                          <Alert 
                            key={insightIndex}
                            severity="info"
                            sx={{ 
                              backgroundColor: '#1890ff10',
                              border: '1px solid #1890ff30',
                              '& .MuiAlert-message': { color: '#e8e8f0' },
                              '& .MuiAlert-icon': { color: '#1890ff' }
                            }}
                          >
                            <Typography variant="body2">
                              {insight}
                            </Typography>
                          </Alert>
                        ))}
                      </Box>

                      {/* Recommendations */}
                      <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2, fontWeight: 600 }}>
                        Strategic Recommendations
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {result.recommendations.map((rec, recIndex) => (
                          <Alert 
                            key={recIndex}
                            severity="success"
                            sx={{ 
                              backgroundColor: '#52c41a10',
                              border: '1px solid #52c41a30',
                              '& .MuiAlert-message': { color: '#e8e8f0' },
                              '& .MuiAlert-icon': { color: '#52c41a' }
                            }}
                          >
                            <Typography variant="body2">
                              {rec}
                            </Typography>
                          </Alert>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Export Dialog */}
        <ExportDialog
          open={exportDialogOpen}
          onClose={() => setExportDialogOpen(false)}
          sessionId={selectedSessionId || ''}
          analysisData={selectedResult}
        />

        {/* Context Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          PaperProps={{
            sx: {
              backgroundColor: '#1a1a35',
              border: '1px solid #3d3d56',
              '& .MuiMenuItem-root': {
                color: '#e8e8f0',
                '&:hover': { backgroundColor: '#252547' }
              }
            }
          }}
        >
          <MenuItem onClick={() => selectedResult && handleExportClick(selectedResult)}>
            <ListItemIcon>
              <Download sx={{ color: '#1890ff' }} />
            </ListItemIcon>
            <ListItemText>Export Results</ListItemText>
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <ListItemIcon>
              <Share sx={{ color: '#52c41a' }} />
            </ListItemIcon>
            <ListItemText>Share Analysis</ListItemText>
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <ListItemIcon>
              <Refresh sx={{ color: '#fa8c16' }} />
            </ListItemIcon>
            <ListItemText>Refresh Data</ListItemText>
          </MenuItem>
        </Menu>
      </motion.div>
    </Box>
  );
};

export default AnalysisResultsDashboard;
