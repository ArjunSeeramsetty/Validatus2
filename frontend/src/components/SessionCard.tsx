import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Button
} from '@mui/material';
import {
  Schedule,
  CheckCircle,
  Error,
  Analytics,
  Pause,
  Refresh,
  MoreVert
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { AnalysisSession } from '../services/analysisService';

interface SessionCardProps {
  session: AnalysisSession;
  index: number;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return '#52c41a';
    case 'running': return '#1890ff';
    case 'failed': return '#ff4d4f';
    case 'created': return '#fa8c16';
    default: return '#8c8ca0';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed': return <CheckCircle sx={{ color: '#52c41a' }} />;
    case 'running': return <Schedule sx={{ color: '#1890ff' }} />;
    case 'failed': return <Error sx={{ color: '#ff4d4f' }} />;
    case 'created': return <Schedule sx={{ color: '#fa8c16' }} />;
    default: return <Analytics sx={{ color: '#8c8ca0' }} />;
  }
};

const SessionCard: React.FC<SessionCardProps> = ({ session, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
    >
      <Card sx={{
        background: '#1a1a35',
        border: '1px solid #3d3d56',
        borderRadius: 2,
        height: '100%',
        transition: 'transform 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 32px rgba(24, 144, 255, 0.1)'
        }
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getStatusIcon(session.status)}
              <Typography variant="h6" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                {session.topic}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={session.status}
                size="small"
                sx={{
                  backgroundColor: `${getStatusColor(session.status)}20`,
                  color: getStatusColor(session.status),
                  textTransform: 'capitalize',
                  fontWeight: 500
                }}
              />
              <IconButton size="small" sx={{ color: '#8c8ca0' }}>
                <MoreVert fontSize="small" />
              </IconButton>
            </Box>
          </Box>

          {session.enhanced_analytics && (
            <Chip
              label="Enhanced Analytics"
              size="small"
              sx={{
                backgroundColor: '#722ed120',
                color: '#722ed1',
                mb: 2,
                fontWeight: 500
              }}
            />
          )}

          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" sx={{ color: '#b8b8cc' }}>
                Progress
              </Typography>
              <Typography variant="body2" sx={{ color: '#e8e8f0', fontWeight: 600 }}>
                {session.progress}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={session.progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: '#3d3d56',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getStatusColor(session.status),
                  borderRadius: 3
                }
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
              Created: {new Date(session.created_at).toLocaleDateString()}
            </Typography>
            <Typography variant="caption" sx={{ color: '#8c8ca0' }}>
              ID: {session.id.slice(-8)}
            </Typography>
          </Box>

          {session.results && (
            <Box sx={{ p: 2, backgroundColor: '#252547', borderRadius: 1, mb: 2 }}>
              <Typography variant="caption" sx={{ color: '#b8b8cc', mb: 1, display: 'block' }}>
                Results Summary
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                  Insights: {session.results.insights}
                </Typography>
                <Typography variant="body2" sx={{ color: '#e8e8f0' }}>
                  Recommendations: {session.results.recommendations}
                </Typography>
              </Box>
            </Box>
          )}

          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
            {session.status === 'running' && (
              <Button size="small" startIcon={<Pause />} sx={{ color: '#fa8c16' }}>
                Pause
              </Button>
            )}
            {session.status === 'completed' && (
              <Button size="small" startIcon={<Analytics />} sx={{ color: '#1890ff' }}>
                View Results
              </Button>
            )}
            {session.status === 'failed' && (
              <Button size="small" startIcon={<Refresh />} sx={{ color: '#52c41a' }}>
                Retry
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default SessionCard;
