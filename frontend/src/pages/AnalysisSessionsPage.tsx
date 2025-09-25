import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  IconButton,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Alert
} from '@mui/material';
import {
  Add,
  PlayArrow,
  Pause,
  Stop,
  Analytics,
  Schedule,
  CheckCircle,
  Error,
  Refresh,
  MoreVert
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAnalysisSessions, useTopics } from '../hooks/useAnalysisData';
import { useAuth } from '../contexts/AuthContext';
import SessionCard from '../components/SessionCard';
import AnalysisProgressTracker from '../components/Analysis/AnalysisProgressTracker';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const AnalysisSessionsPage: React.FC = () => {
  const { sessions, loading, createSession } = useAnalysisSessions();
  const { topics } = useTopics();
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [open, setOpen] = useState(false);
  const [newSession, setNewSession] = useState({
    topic: '',
    enhanced_analytics: false,
    parameters: {
      depth: 'comprehensive',
      include_competitors: true,
      include_financial: true,
      include_market_trends: true
    }
  });
  const [creating, setCreating] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  const [showProgressTracker, setShowProgressTracker] = useState(false);
  const [trackingSessionId, setTrackingSessionId] = useState<string | null>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleViewProgress = (sessionId: string) => {
    setTrackingSessionId(sessionId);
    setShowProgressTracker(true);
  };

  const handleProgressComplete = (results: any) => {
    setShowProgressTracker(false);
    setTrackingSessionId(null);
    setAlert({ type: 'success', message: 'Analysis completed successfully!' });
  };


  const filterSessionsByStatus = (status: string) => {
    if (status === 'all') return sessions;
    return sessions.filter(session => session.status === status);
  };

  const handleCreateSession = async () => {
    if (!newSession.topic) {
      setAlert({ type: 'error', message: 'Please select a topic' });
      return;
    }

    try {
      setCreating(true);
      await createSession(
        newSession.topic,
        user?.id || '1',
        newSession.parameters,
        newSession.enhanced_analytics
      );

      setAlert({ type: 'success', message: 'Analysis session created successfully!' });
      setOpen(false);
      
      // Show progress tracker for the new running session
      if (result.session_id) {
        setTrackingSessionId(result.session_id);
        setShowProgressTracker(true);
      }
      
      setNewSession({
        topic: '',
        enhanced_analytics: false,
        parameters: {
          depth: 'comprehensive',
          include_competitors: true,
          include_financial: true,
          include_market_trends: true
        }
      });
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message });
    } finally {
      setCreating(false);
    }
  };


  return (
    <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0f0f23' }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" sx={{ color: '#e8e8f0', fontWeight: 600, mb: 1 }}>
              Analysis Sessions
            </Typography>
            <Typography variant="body1" sx={{ color: '#b8b8cc' }}>
              Monitor and manage your strategic analysis sessions
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpen(true)}
            sx={{
              background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
              }
            }}
          >
            New Analysis
          </Button>
        </Box>

        {/* Alert */}
        {alert && (
          <Alert 
            severity={alert.type} 
            onClose={() => setAlert(null)}
            sx={{ mb: 3 }}
          >
            {alert.message}
          </Alert>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: '#3d3d56', mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{
            '& .MuiTab-root': { color: '#b8b8cc' },
            '& .Mui-selected': { color: '#1890ff' },
            '& .MuiTabs-indicator': { backgroundColor: '#1890ff' }
          }}>
            <Tab label={`All (${sessions.length})`} />
            <Tab label={`Running (${filterSessionsByStatus('running').length})`} />
            <Tab label={`Completed (${filterSessionsByStatus('completed').length})`} />
            <Tab label={`Failed (${filterSessionsByStatus('failed').length})`} />
          </Tabs>
        </Box>

        {/* Tab Panels */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {sessions.map((session, index) => (
              <Grid item xs={12} md={6} lg={4} key={session.id}>
                <SessionCard session={session} index={index} />
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            {filterSessionsByStatus('running').map((session, index) => (
              <Grid item xs={12} md={6} lg={4} key={session.id}>
                <SessionCard session={session} index={index} />
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            {filterSessionsByStatus('completed').map((session, index) => (
              <Grid item xs={12} md={6} lg={4} key={session.id}>
                <SessionCard session={session} index={index} />
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            {filterSessionsByStatus('failed').map((session, index) => (
              <Grid item xs={12} md={6} lg={4} key={session.id}>
                <SessionCard session={session} index={index} />
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Empty State */}
        {sessions.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 8 }}>
            <Analytics sx={{ fontSize: 64, color: '#3d3d56', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#b8b8cc', mb: 2 }}>
              No analysis sessions yet
            </Typography>
            <Typography variant="body2" sx={{ color: '#8c8ca0', mb: 4 }}>
              Create your first analysis session to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpen(true)}
              sx={{
                background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
                }
              }}
            >
              Create Analysis Session
            </Button>
          </Box>
        )}
      </motion.div>

      {/* Create Session Dialog */}
      <Dialog 
        open={open} 
        onClose={() => setOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: '#1a1a35',
            border: '1px solid #3d3d56'
          }
        }}
      >
        <DialogTitle sx={{ color: '#e8e8f0' }}>
          Create Analysis Session
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel sx={{ color: '#b8b8cc' }}>Topic</InputLabel>
              <Select
                value={newSession.topic}
                onChange={(e) => setNewSession(prev => ({ ...prev, topic: e.target.value }))}
                sx={{
                  backgroundColor: '#252547',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#3d3d56' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#1890ff' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#1890ff' },
                  '& .MuiSelect-select': { color: '#e8e8f0' }
                }}
              >
                {topics.map((topic) => (
                  <MenuItem key={topic.id} value={topic.name}>
                    {topic.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={newSession.enhanced_analytics}
                  onChange={(e) => setNewSession(prev => ({ ...prev, enhanced_analytics: e.target.checked }))}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': { color: '#1890ff' },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#1890ff' }
                  }}
                />
              }
              label={
                <Box>
                  <Typography sx={{ color: '#e8e8f0' }}>Enhanced Analytics</Typography>
                  <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
                    Use advanced AI models for deeper insights
                  </Typography>
                </Box>
              }
            />

            <FormControl fullWidth>
              <InputLabel sx={{ color: '#b8b8cc' }}>Analysis Depth</InputLabel>
              <Select
                value={newSession.parameters.depth}
                onChange={(e) => setNewSession(prev => ({ 
                  ...prev, 
                  parameters: { ...prev.parameters, depth: e.target.value } 
                }))}
                sx={{
                  backgroundColor: '#252547',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#3d3d56' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#1890ff' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#1890ff' },
                  '& .MuiSelect-select': { color: '#e8e8f0' }
                }}
              >
                <MenuItem value="quick">Quick Analysis</MenuItem>
                <MenuItem value="standard">Standard Analysis</MenuItem>
                <MenuItem value="comprehensive">Comprehensive Analysis</MenuItem>
              </Select>
            </FormControl>

            <Box>
              <Typography variant="h6" sx={{ color: '#e8e8f0', mb: 2 }}>
                Include Components
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={newSession.parameters.include_competitors}
                      onChange={(e) => setNewSession(prev => ({ 
                        ...prev, 
                        parameters: { ...prev.parameters, include_competitors: e.target.checked } 
                      }))}
                      sx={{
                        '& .MuiSwitch-switchBase.Mui-checked': { color: '#1890ff' },
                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#1890ff' }
                      }}
                    />
                  }
                  label={<Typography sx={{ color: '#e8e8f0' }}>Competitor Analysis</Typography>}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={newSession.parameters.include_financial}
                      onChange={(e) => setNewSession(prev => ({ 
                        ...prev, 
                        parameters: { ...prev.parameters, include_financial: e.target.checked } 
                      }))}
                      sx={{
                        '& .MuiSwitch-switchBase.Mui-checked': { color: '#1890ff' },
                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#1890ff' }
                      }}
                    />
                  }
                  label={<Typography sx={{ color: '#e8e8f0' }}>Financial Analysis</Typography>}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={newSession.parameters.include_market_trends}
                      onChange={(e) => setNewSession(prev => ({ 
                        ...prev, 
                        parameters: { ...prev.parameters, include_market_trends: e.target.checked } 
                      }))}
                      sx={{
                        '& .MuiSwitch-switchBase.Mui-checked': { color: '#1890ff' },
                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#1890ff' }
                      }}
                    />
                  }
                  label={<Typography sx={{ color: '#e8e8f0' }}>Market Trends</Typography>}
                />
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} sx={{ color: '#b8b8cc' }}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateSession}
            variant="contained"
            disabled={creating}
            sx={{
              background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #096dd9 0%, #1890ff 100%)',
              }
            }}
          >
            {creating ? 'Creating...' : 'Create Session'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Progress Tracker Dialog */}
      {showProgressTracker && trackingSessionId && (
        <Dialog
          open={showProgressTracker}
          onClose={() => setShowProgressTracker(false)}
          maxWidth="lg"
          fullWidth
          PaperProps={{
            sx: {
              background: '#0f0f23',
              border: '1px solid #3d3d56',
              borderRadius: 2,
              maxHeight: '90vh'
            }
          }}
        >
          <AnalysisProgressTracker
            sessionId={trackingSessionId}
            onAnalysisComplete={handleProgressComplete}
          />
        </Dialog>
      )}
    </Box>
  );
};

export default AnalysisSessionsPage;