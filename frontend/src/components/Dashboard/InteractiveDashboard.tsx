// frontend/src/components/Dashboard/InteractiveDashboard.tsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Chart components
import LayerScoresChart from './Charts/LayerScoresChart';
import FactorAnalysisChart from './Charts/FactorAnalysisChart';
import SegmentAnalysisChart from './Charts/SegmentAnalysisChart';

// Custom components
import ExportDialog from '../Export/ExportDialog';
import FilterPanel from '../Filters/FilterPanel';
import RealTimeProgress from '../Progress/RealTimeProgress';

// Types and hooks
import { RootState, AppDispatch } from '../../store/store';
import { fetchAnalysisResults, exportResults } from '../../store/slices/resultsSlice';

interface InteractiveDashboardProps {
  sessionId: string;
}

const InteractiveDashboard: React.FC<InteractiveDashboardProps> = ({ sessionId }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentResults, loading, exportStatus } = useSelector((state: RootState) => state.results);
  const { user } = useSelector((state: RootState) => state.auth);
  
  // Local state
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [filterPanelOpen, setFilterPanelOpen] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<any>({});
  
  // Real-time updates
  const [isConnected, setIsConnected] = useState(true);
  const [progress, setProgress] = useState<any>(null);

  // Effects
  useEffect(() => {
    if (sessionId) {
      dispatch(fetchAnalysisResults(sessionId));
    }
  }, [sessionId, dispatch]);

  // Event handlers
  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const handleExport = (format: string) => {
    if (user && sessionId) {
      dispatch(exportResults({ sessionId, format, userId: user.id }));
    }
    handleMenuClose();
  };

  const handleRefresh = () => {
    dispatch(fetchAnalysisResults(sessionId));
    handleMenuClose();
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  if (loading) {
    return <RealTimeProgress sessionId={sessionId} />;
  }

  if (!currentResults) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography variant="h6" color="text.secondary">
          No analysis results available
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Analysis Results
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip 
              label={currentResults.topic} 
              color="primary" 
              variant="outlined" 
            />
            <Chip 
              label={currentResults.status} 
              color="success" 
              size="small" 
            />
            {isConnected && (
              <Chip 
                label="Live Updates" 
                color="info" 
                size="small" 
                variant="outlined"
              />
            )}
          </Box>
        </Box>
        
        <Box>
          <IconButton onClick={() => setFilterPanelOpen(true)}>
            <FilterIcon />
          </IconButton>
          <IconButton onClick={handleRefresh}>
            <RefreshIcon />
          </IconButton>
          <IconButton onClick={handleMenuClick}>
            <MoreVertIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Main Dashboard Grid */}
      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ duration: 0.5 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Overview
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" color="primary">
                        {(currentResults.overall_metrics?.overall_score * 100 || 0).toFixed(1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Overall Score
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" color="secondary">
                        {currentResults.layer_scores?.length || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Layers Analyzed
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" color="info">
                        {currentResults.factor_calculations?.length || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Strategic Factors
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h3" color="success">
                        {currentResults.segment_scores?.length || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Market Segments
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Layer Scores Chart */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Strategic Layer Scores
                </Typography>
                <LayerScoresChart data={currentResults.layer_scores} />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Factor Analysis Chart */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Factor Analysis
                </Typography>
                <FactorAnalysisChart data={currentResults.factor_calculations} />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Segment Analysis */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Segment Analysis
                </Typography>
                <SegmentAnalysisChart data={currentResults.segment_scores} />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Insights Panel */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Key Insights
                </Typography>
                <Box>
                  {currentResults.insights?.slice(0, 5).map((insight, index) => (
                    <Box key={index} mb={2}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        • {insight}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Strategic Recommendations
                </Typography>
                <Grid container spacing={2}>
                  {currentResults.recommendations?.map((recommendation, index) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Box 
                        p={2} 
                        border={1} 
                        borderColor="grey.300" 
                        borderRadius={1}
                        bgcolor="grey.50"
                      >
                        <Typography variant="body1">
                          {recommendation}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => setExportDialogOpen(true)}>
          <DownloadIcon sx={{ mr: 1 }} />
          Export Results
        </MenuItem>
        <MenuItem onClick={handleRefresh}>
          <RefreshIcon sx={{ mr: 1 }} />
          Refresh Data
        </MenuItem>
      </Menu>

      {/* Export Dialog */}
      <ExportDialog
        open={exportDialogOpen}
        onClose={() => setExportDialogOpen(false)}
        sessionId={sessionId}
        onExport={handleExport}
        exportStatus={exportStatus[sessionId]}
      />

      {/* Filter Panel */}
      <FilterPanel
        open={filterPanelOpen}
        onClose={() => setFilterPanelOpen(false)}
        filters={selectedFilters}
        onFiltersChange={setSelectedFilters}
      />
    </Box>
  );
};

export default InteractiveDashboard;
