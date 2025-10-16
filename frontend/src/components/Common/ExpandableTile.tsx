import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  Collapse,
  Box,
  Chip,
  CircularProgress,
  Tooltip,
  styled
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

const StyledCard = styled(Card)<{ expanded: boolean; bgcolor?: string }>(({ expanded, bgcolor }) => ({
  height: expanded ? 'auto' : '280px',
  minHeight: '280px',
  backgroundColor: bgcolor || '#5E35B1',
  color: 'white',
  overflow: 'hidden',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  cursor: 'pointer',
  '&:hover': {
    boxShadow: '0 8px 16px 0 rgba(0,0,0,0.4)',
    transform: 'translateY(-2px)',
  },
  '&::before': expanded ? {} : {
    content: '""',
    position: 'absolute',
    bottom: 60,
    left: 0,
    right: 0,
    height: '60px',
    background: `linear-gradient(transparent, ${bgcolor || '#5E35B1'})`,
    pointerEvents: 'none',
    zIndex: 1
  }
}));

const ContentWrapper = styled(Box)<{ expanded: boolean }>(({ expanded }) => ({
  height: expanded ? 'auto' : '220px',
  overflow: expanded ? 'visible' : 'hidden',
  position: 'relative',
  paddingBottom: expanded ? 0 : '20px'
}));

const ExpandButton = styled(IconButton)<{ expanded: boolean }>(({ expanded }) => ({
  position: 'absolute',
  bottom: 8,
  right: 8,
  backgroundColor: 'rgba(255, 255, 255, 0.2)',
  color: 'white',
  zIndex: 2,
  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
  transition: 'all 0.3s ease',
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    transform: expanded ? 'rotate(180deg) scale(1.1)' : 'rotate(0deg) scale(1.1)',
  }
}));

const MetricChip = styled(Chip)(() => ({
  backgroundColor: 'rgba(255, 255, 255, 0.2)',
  color: 'white',
  margin: '2px 4px',
  fontSize: '0.75rem',
  height: '24px',
  '& .MuiChip-icon': {
    color: 'white',
    fontSize: '16px'
  }
}));

const ConfidenceIndicator = styled(Box)<{ confidence: number }>(({ confidence }) => ({
  position: 'absolute',
  top: 12,
  right: 12,
  display: 'flex',
  alignItems: 'center',
  gap: '4px',
  backgroundColor: confidence > 0.8 ? 'rgba(76, 175, 80, 0.3)' : 
                   confidence > 0.6 ? 'rgba(255, 152, 0, 0.3)' : 
                   'rgba(244, 67, 54, 0.3)',
  padding: '4px 8px',
  borderRadius: '12px',
  fontSize: '0.75rem'
}));

interface ExpandableTileProps {
  title: string;
  content: React.ReactNode;
  bgcolor?: string;
  textColor?: string;  // NEW: Explicit text color for WCAG AAA accessibility
  chipColor?: string;  // NEW: Chip background color
  chipTextColor?: string;  // NEW: Chip text color
  additionalContent?: React.ReactNode;
  chips?: string[];
  metrics?: Record<string, string | number>;
  insights?: any[];
  loading?: boolean;
  confidence?: number | null;
  onExpand?: (expanded: boolean) => void;
  expandable?: boolean;
}

const ExpandableTile: React.FC<ExpandableTileProps> = ({
  title,
  content,
  bgcolor = '#5E35B1',
  textColor = '#FFFFFF',  // Default white for dark backgrounds
  chipColor = 'rgba(255,255,255,0.25)',
  chipTextColor = '#FFFFFF',
  additionalContent,
  chips = [],
  metrics = {},
  insights = [],
  loading = false,
  confidence = null,
  onExpand,
  expandable = true
}) => {
  const [expanded, setExpanded] = useState(false);

  const handleExpandClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (!expandable || loading) return;
    
    setExpanded(!expanded);
    
    if (onExpand) {
      onExpand(!expanded);
    }
  };

  const handleCardClick = () => {
    if (expandable && !expanded && !loading) {
      handleExpandClick({ stopPropagation: () => {} } as any);
    }
  };

  return (
    <StyledCard 
      expanded={expanded} 
      bgcolor={bgcolor}
      onClick={handleCardClick}
    >
      <CardContent sx={{ height: '100%', pb: 6, position: 'relative' }}>
        
        {/* Confidence Indicator - Uses ACTUAL segment score */}
        {confidence !== null && confidence > 0 && (
          <ConfidenceIndicator confidence={confidence}>
            <TrendingUpIcon fontSize="small" />
            {(confidence * 100).toFixed(0)}%
          </ConfidenceIndicator>
        )}
        
        {/* Title */}
        <Typography 
          variant="h6" 
          gutterBottom 
          sx={{ 
            fontWeight: 'bold', 
            color: textColor,  // Use explicit text color
            pr: confidence !== null ? 6 : 0,
            mb: 2
          }}
        >
          {title}
          {loading && (
            <CircularProgress 
              size={16} 
              sx={{ ml: 1, color: 'rgba(255,255,255,0.7)' }} 
            />
          )}
        </Typography>
        
        {/* Chips - Data-driven tags */}
        {chips.length > 0 && (
          <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {chips.map((chip, index) => (
              <Chip 
                key={index}
                label={chip}
                size="small"
                sx={{
                  backgroundColor: chipColor,
                  color: chipTextColor,
                  margin: '2px 4px',
                  fontSize: '0.75rem',
                  height: '24px',
                  fontWeight: 'bold'
                }}
              />
            ))}
          </Box>
        )}

        <ContentWrapper expanded={expanded}>
          
          {/* Main Content */}
          <Box sx={{ mb: 2 }}>
            {typeof content === 'string' ? (
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255,255,255,0.9)',
                  lineHeight: 1.5
                }}
              >
                {content}
              </Typography>
            ) : (
              content
            )}
          </Box>
          
          {/* Metrics Display - ACTUAL values from database */}
          {Object.keys(metrics).length > 0 && (
            <Box sx={{ mb: 2 }}>
              {Object.entries(metrics).map(([key, value]) => (
                <Box key={key} sx={{ mb: 1 }}>
                  <Typography 
                    variant="caption" 
                    sx={{ color: 'rgba(255,255,255,0.7)', display: 'block' }}
                  >
                    {key}
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ color: 'white', fontWeight: 'bold' }}
                  >
                    {value}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
          
          {/* Insights Preview (when collapsed) - From ACTUAL LLM generation */}
          {!expanded && insights.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255,255,255,0.8)',
                  fontSize: '0.85rem',
                  fontStyle: 'italic'
                }}
              >
                {insights.length} insight{insights.length > 1 ? 's' : ''} available
              </Typography>
            </Box>
          )}
          
          {/* Expanded Content */}
          <Collapse in={expanded} timeout={300}>
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255,255,255,0.3)' }}>
              
              {/* Additional Content */}
              {additionalContent && (
                <Box sx={{ mb: 3 }}>
                  {additionalContent}
                </Box>
              )}
              
              {/* Insights Detail - Generated from ACTUAL data via LLM */}
              {insights.length > 0 && (
                <Box>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      color: 'white', 
                      fontWeight: 'bold', 
                      mb: 2,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }}
                  >
                    <InfoIcon fontSize="small" />
                    Data-Driven Insights
                  </Typography>
                  
                  {insights.map((insight: any, index: number) => (
                    <Box 
                      key={index} 
                      sx={{ 
                        mb: 2, 
                        p: 2, 
                        bgcolor: 'rgba(255,255,255,0.1)', 
                        borderRadius: 1,
                        border: '1px solid rgba(255,255,255,0.2)'
                      }}
                    >
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.85rem', 
                          color: 'rgba(255,255,255,0.9)',
                          mb: 1
                        }}
                      >
                        {typeof insight === 'string' ? insight : insight.content}
                      </Typography>
                      
                      {typeof insight === 'object' && insight.confidence && (
                        <Chip
                          label={`Confidence: ${(insight.confidence * 100).toFixed(0)}%`}
                          size="small"
                          sx={{ 
                            bgcolor: 'rgba(255,255,255,0.2)', 
                            color: 'white',
                            fontSize: '0.7rem',
                            height: '20px',
                            mt: 1
                          }}
                        />
                      )}
                      
                      {typeof insight === 'object' && insight.source && (
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: 'rgba(255,255,255,0.6)',
                            fontStyle: 'italic',
                            fontSize: '0.7rem',
                            display: 'block',
                            mt: 1
                          }}
                        >
                          Source: {insight.source}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          </Collapse>
        </ContentWrapper>
        
        {/* Expand Button */}
        {expandable && (
          <Tooltip title={expanded ? "Collapse" : "Expand for details"}>
            <ExpandButton 
              onClick={handleExpandClick} 
              size="small"
              expanded={expanded}
              disabled={loading}
            >
              <ExpandMoreIcon />
            </ExpandButton>
          </Tooltip>
        )}
        
        {/* Loading Overlay */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 3
            }}
          >
            <CircularProgress size={40} sx={{ color: 'white' }} />
          </Box>
        )}
      </CardContent>
    </StyledCard>
  );
};

export default ExpandableTile;

