// frontend/src/hooks/useWebSocketConnection.ts
import { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { useSnackbar } from 'notistack';

interface WebSocketMessage {
  type: string;
  sessionId?: string;
  timestamp: string;
  data: any;
}

interface WebSocketContextType {
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: string) => void;
  subscribe: (eventType: string, callback: (data: any) => void) => () => void;
  unsubscribe: (eventType: string) => void;
  reconnect: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocketConnection = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketConnection must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
  url?: string;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  url = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000/ws',
  autoReconnect = false, // Disabled for now since backend doesn't have WebSocket endpoint
  maxReconnectAttempts = 0,
  reconnectInterval = 3000
}) => {
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const { enqueueSnackbar } = useSnackbar();
  
  const ws = useRef<WebSocket | null>(null);
  const subscribers = useRef<Map<string, Set<(data: any) => void>>>(new Map());
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimer = useRef<NodeJS.Timeout | null>(null);
  const messageQueue = useRef<string[]>([]);

  // Initialize WebSocket connection
  const connect = useCallback(() => {
    try {
      setConnectionStatus('connecting');
      
      // Add authentication token to WebSocket URL
      const token = localStorage.getItem('auth_token');
      const wsUrl = token ? `${url}?token=${token}` : url;
      
      ws.current = new WebSocket(wsUrl);
      
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        setReconnectAttempts(0);
        
        // Send queued messages
        while (messageQueue.current.length > 0) {
          const queuedMessage = messageQueue.current.shift();
          if (queuedMessage && ws.current) {
            ws.current.send(queuedMessage);
          }
        }
        
        // Start heartbeat
        startHeartbeat();
        
        enqueueSnackbar('Real-time connection established', { 
          variant: 'success',
          autoHideDuration: 3000,
        });
      };
      
      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          
          // Handle system messages
          if (message.type === 'system') {
            handleSystemMessage(message);
          } else {
            // Dispatch to subscribers
            const typeSubscribers = subscribers.current.get(message.type);
            if (typeSubscribers) {
              typeSubscribers.forEach(callback => {
                try {
                  callback(message.data);
                } catch (error) {
                  console.error('Error in WebSocket subscriber callback:', error);
                }
              });
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason);
        setConnectionStatus('disconnected');
        stopHeartbeat();
        
        if (autoReconnect && reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.min(reconnectInterval * Math.pow(2, reconnectAttempts), 30000);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`);
          
          reconnectTimer.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, delay);
          
          enqueueSnackbar(`Connection lost. Reconnecting in ${Math.round(delay / 1000)} seconds...`, { 
            variant: 'warning',
            autoHideDuration: 5000,
          });
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          setConnectionStatus('error');
          enqueueSnackbar('Unable to establish real-time connection. Some features may not work.', { 
            variant: 'error',
            persist: true,
          });
        }
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('error');
    }
  }, [url, autoReconnect, maxReconnectAttempts, reconnectInterval, reconnectAttempts, enqueueSnackbar]);

  // Send heartbeat to keep connection alive
  const startHeartbeat = useCallback(() => {
    heartbeatTimer.current = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        sendMessage(JSON.stringify({ type: 'heartbeat', timestamp: new Date().toISOString() }));
      }
    }, 30000); // Send heartbeat every 30 seconds
  }, []);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimer.current) {
      clearInterval(heartbeatTimer.current);
      heartbeatTimer.current = null;
    }
  }, []);

  // Handle system messages
  const handleSystemMessage = useCallback((message: WebSocketMessage) => {
    switch (message.data.subtype) {
      case 'analysis_started':
        enqueueSnackbar(`Strategic analysis for "${message.data.topic}" has begun`, { 
          variant: 'info',
          autoHideDuration: 4000,
        });
        break;
        
      case 'analysis_completed':
        enqueueSnackbar(`Strategic analysis for "${message.data.topic}" finished successfully`, { 
          variant: 'success',
          autoHideDuration: 5000,
        });
        break;
        
      case 'analysis_error':
        enqueueSnackbar(message.data.error || 'An error occurred during analysis', { 
          variant: 'error',
          autoHideDuration: 8000,
        });
        break;
        
      case 'server_maintenance':
        enqueueSnackbar('Server maintenance scheduled. Save your work.', { 
          variant: 'warning',
          autoHideDuration: 10000,
        });
        break;
        
      default:
        console.log('Unhandled system message:', message.data);
    }
  }, [enqueueSnackbar]);

  // Send message through WebSocket
  const sendMessage = useCallback((messageStr: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(messageStr);
    } else {
      // Queue message if not connected
      messageQueue.current.push(messageStr);
      
      if (connectionStatus === 'disconnected') {
        connect();
      }
    }
  }, [connectionStatus, connect]);

  // Subscribe to specific event types
  const subscribe = useCallback((eventType: string, callback: (data: any) => void) => {
    if (!subscribers.current.has(eventType)) {
      subscribers.current.set(eventType, new Set());
    }
    
    subscribers.current.get(eventType)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      const typeSubscribers = subscribers.current.get(eventType);
      if (typeSubscribers) {
        typeSubscribers.delete(callback);
        if (typeSubscribers.size === 0) {
          subscribers.current.delete(eventType);
        }
      }
    };
  }, []);

  // Unsubscribe from event type
  const unsubscribe = useCallback((eventType: string) => {
    subscribers.current.delete(eventType);
  }, []);

  // Manual reconnect
  const reconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
    }
    
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
    }
    
    setReconnectAttempts(0);
    connect();
  }, [connect]);

  // Initialize connection on mount (disabled for now)
  useEffect(() => {
    // connect(); // Disabled until backend WebSocket endpoint is implemented
    
    return () => {
      stopHeartbeat();
      
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
      
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect, stopHeartbeat]);

  // Handle browser visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && connectionStatus === 'disconnected') {
        // Reconnect when tab becomes visible
        reconnect();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [connectionStatus, reconnect]);

  // Handle network status changes
  useEffect(() => {
    const handleOnline = () => {
      if (connectionStatus === 'disconnected' || connectionStatus === 'error') {
        reconnect();
      }
    };

    const handleOffline = () => {
      enqueueSnackbar('Network offline. Check your internet connection', { 
        variant: 'warning',
        autoHideDuration: 5000,
      });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [connectionStatus, reconnect, enqueueSnackbar]);

  const contextValue: WebSocketContextType = {
    connectionStatus,
    lastMessage,
    sendMessage,
    subscribe,
    unsubscribe,
    reconnect
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Hook for specific event subscriptions
export const useWebSocketSubscription = (eventType: string, callback: (data: any) => void) => {
  const { subscribe } = useWebSocketConnection();
  
  useEffect(() => {
    const unsubscribeFunc = subscribe(eventType, callback);
    return unsubscribeFunc;
  }, [eventType, callback, subscribe]);
};

// Hook for sending messages with typing
export const useWebSocketSender = () => {
  const { sendMessage } = useWebSocketConnection();
  
  return useCallback((type: string, data: any, sessionId?: string) => {
    const message = {
      type,
      sessionId,
      timestamp: new Date().toISOString(),
      data
    };
    
    sendMessage(JSON.stringify(message));
  }, [sendMessage]);
};

export default WebSocketProvider;
