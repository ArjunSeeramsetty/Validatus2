/**
 * Business Case Score Visualization
 */
import React from 'react';
import { Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { TrendingUp, Assessment } from '@mui/icons-material';

interface BusinessCaseScore {
  score: number;
  confidence_band: [number, number];
  components: Record<string, number>;
}

interface BusinessCaseScoreCardProps {
  score: BusinessCaseScore;
  height?: number;
}

const BusinessCaseScoreCard: React.FC<BusinessCaseScoreCardProps> = ({ score, height = 280 }) => {
  
  const getScoreColor = (value: number) => {
    if (value >= 0.8) return '#52c41a';  // Green
    if (value >= 0.6) return '#fa8c16';  // Orange  
    return '#ff4d4f';  // Red
  };

  const getScoreLabel = (value: number) => {
    if (value >= 0.8) return 'Strong';
    if (value >= 0.6) return 'Moderate';
    return 'Weak';
  };

  return (
    <Card 
      sx={{ 
        backgroundColor: '#1a1a35', 
        border: '1px solid #3d3d56',
        height 
      }}
    >
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Assessment sx={{ color: '#1890ff', mr: 1 }} />
          <Typography variant="h6" sx={{ color: '#e8e8f0' }}>
            Business Case Score
          </Typography>
        </Box>

        {/* Main Score Display */}
        <Box 
          sx={{ 
            flex: 1,
            display: 'flex', 
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
            <CircularProgress
              variant="determinate"
              value={score.score * 100}
              size={120}
              thickness={6}
              sx={{
                color: getScoreColor(score.score),
                '& .MuiCircularProgress-circle': {
                  strokeLinecap: 'round',
                }
              }}
            />
            <CircularProgress
              variant="determinate"
              value={100}
              size={120}
              thickness={6}
              sx={{
                color: '#3d3d56',
                position: 'absolute',
                left: 0,
                zIndex: 0
              }}
            />
            <Box
              sx={{
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column'
              }}
            >
              <Typography 
                variant="h3" 
                sx={{ 
                  color: getScoreColor(score.score),
                  fontWeight: 700,
                  lineHeight: 1
                }}
              >
                {(score.score * 100).toFixed(0)}
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ color: '#b8b8cc' }}
              >
                /100
              </Typography>
            </Box>
          </Box>

          <Typography 
            variant="h6" 
            sx={{ 
              color: getScoreColor(score.score),
              fontWeight: 600,
              mb: 1
            }}
          >
            {getScoreLabel(score.score)} Case
          </Typography>

          {/* Confidence Band */}
          <Typography 
            variant="body2" 
            sx={{ color: '#b8b8cc', textAlign: 'center' }}
          >
            Confidence: {(score.confidence_band[0] * 100).toFixed(0)}% - {(score.confidence_band[1] * 100).toFixed(0)}%
          </Typography>
        </Box>

        {/* Component Breakdown */}
        <Box sx={{ mt: 2 }}>
          <Typography 
            variant="caption" 
            sx={{ color: '#b8b8cc', mb: 1, display: 'block' }}
          >
            Contributing Factors:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {Object.entries(score.components).slice(0, 3).map(([key, value]) => (
              <Box
                key={key}
                sx={{
                  backgroundColor: '#252547',
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  flex: 1,
                  minWidth: 60
                }}
              >
                <Typography 
                  variant="caption" 
                  sx={{ color: '#b8b8cc', display: 'block' }}
                >
                  {key.toUpperCase()}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ color: '#e8e8f0', fontWeight: 600 }}
                >
                  {(value * 100).toFixed(0)}%
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BusinessCaseScoreCard;
