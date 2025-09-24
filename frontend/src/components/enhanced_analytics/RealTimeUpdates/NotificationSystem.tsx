// frontend/src/components/enhanced_analytics/RealTimeUpdates/NotificationSystem.tsx
import React from 'react';
import {
  Snackbar,
  Alert,
  Slide,
  SlideProps,
  Stack,
  Typography,
  IconButton,
  Box,
  Paper,
  Chip
} from '@mui/material';
import {
  CloseOutlined,
  CheckCircleOutlined,
  ErrorOutlined,
  WarningOutlined,
  InfoOutlined
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  sessionId?: string;
  autoHide?: boolean;
  duration?: number;
}

interface NotificationSystemProps {
  notifications: Notification[];
  onDismiss: (index: number) => void;
  maxNotifications?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  backgroundColor: '#1a1a35',
  border: '1px solid #3d3d56',
  borderRadius: '12px',
  backdropFilter: 'blur(10px)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
}));

const NotificationContainer = styled(Box)(({ theme }) => ({
  position: 'fixed',
  zIndex: 9999,
  maxWidth: '400px',
  width: '100%',
}));

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="left" />;
}

const NotificationSystem: React.FC<NotificationSystemProps> = ({
  notifications,
  onDismiss,
  maxNotifications = 5,
  position = 'top-right'
}) => {
  const getPositionStyles = () => {
    const baseStyles = {
      top: position.includes('top') ? 24 : 'auto',
      bottom: position.includes('bottom') ? 24 : 'auto',
      right: position.includes('right') ? 24 : 'auto',
      left: position.includes('left') ? 24 : 'auto',
    };
    return baseStyles;
  };

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircleOutlined sx={{ color: '#52c41a' }} />;
      case 'error':
        return <ErrorOutlined sx={{ color: '#ff4d4f' }} />;
      case 'warning':
        return <WarningOutlined sx={{ color: '#fa8c16' }} />;
      case 'info':
        return <InfoOutlined sx={{ color: '#1890ff' }} />;
      default:
        return <InfoOutlined sx={{ color: '#1890ff' }} />;
    }
  };

  const getAlertSeverity = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'info';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) {
      return `${diffInSeconds}s ago`;
    } else if (diffInSeconds < 3600) {
      return `${Math.floor(diffInSeconds / 60)}m ago`;
    } else {
      return date.toLocaleTimeString();
    }
  };

  return (
    <NotificationContainer sx={getPositionStyles()}>
      <Stack spacing={2}>
        {notifications.slice(0, maxNotifications).map((notification, index) => (
          <StyledPaper key={notification.id} elevation={8}>
            <Alert
              severity={getAlertSeverity(notification.type)}
              icon={getIcon(notification.type)}
              action={
                <IconButton
                  size="small"
                  onClick={() => onDismiss(index)}
                  sx={{ color: '#b8b8cc' }}
                >
                  <CloseOutlined fontSize="small" />
                </IconButton>
              }
              sx={{
                backgroundColor: 'transparent',
                color: '#e8e8f0',
                '& .MuiAlert-icon': {
                  color: 'inherit',
                },
                '& .MuiAlert-message': {
                  width: '100%',
                },
              }}
            >
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ color: '#e8e8f0', fontWeight: 'bold' }}>
                    {notification.title}
                  </Typography>
                  <Stack direction="row" spacing={1} alignItems="center">
                    {notification.sessionId && (
                      <Chip
                        label={notification.sessionId.substring(0, 8)}
                        size="small"
                        sx={{
                          backgroundColor: '#1890ff20',
                          color: '#1890ff',
                          fontSize: '10px',
                          height: '20px',
                        }}
                      />
                    )}
                    <Typography variant="caption" sx={{ color: '#8c8ca0', fontSize: '11px' }}>
                      {formatTimestamp(notification.timestamp)}
                    </Typography>
                  </Stack>
                </Box>
                <Typography variant="body2" sx={{ color: '#b8b8cc', lineHeight: 1.4 }}>
                  {notification.message}
                </Typography>
              </Box>
            </Alert>
          </StyledPaper>
        ))}
      </Stack>
    </NotificationContainer>
  );
};

export default NotificationSystem;
