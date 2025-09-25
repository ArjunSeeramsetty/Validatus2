import React, { createContext, useContext, ReactNode } from 'react';

// Define the context interface
interface SocketContextType {
  socket: null;
  connected: boolean;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  lastMessage: null;
  sendMessage: (message: string) => void;
  subscribe: (eventType: string, callback: (data: any) => void) => () => void;
  unsubscribe: (eventType: string) => void;
  reconnect: () => void;
}

// Create the context
const SocketContext = createContext<SocketContextType | undefined>(undefined);

// Hook to use the socket context
export const useSocket = () => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

// Hook for WebSocket connection (disabled for now)
export const useWebSocketConnection = () => {
  return {
    connectionStatus: 'disconnected' as const,
    lastMessage: null,
    sendMessage: (message: string) => {
      console.log('WebSocket disabled - message not sent:', message);
    },
    subscribe: (eventType: string, callback: (data: any) => void) => {
      console.log('WebSocket disabled - subscription not created:', eventType);
      return () => {}; // Return empty unsubscribe function
    },
    unsubscribe: (eventType: string) => {
      console.log('WebSocket disabled - unsubscribe not performed:', eventType);
    },
    reconnect: () => {
      console.log('WebSocket disabled - reconnection not attempted');
    }
  };
};

// Provider props interface
interface SocketProviderProps {
  children: ReactNode;
}

// Socket provider component (WebSocket functionality disabled for now)
export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  // Disabled WebSocket implementation - provides mock interface
  const contextValue: SocketContextType = {
    socket: null,
    connected: false,
    connectionStatus: 'disconnected',
    lastMessage: null,
    sendMessage: (message: string) => {
      console.log('WebSocket disabled - message not sent:', message);
    },
    subscribe: (eventType: string, callback: (data: any) => void) => {
      console.log('WebSocket disabled - subscription not created:', eventType);
      return () => {}; // Return empty unsubscribe function
    },
    unsubscribe: (eventType: string) => {
      console.log('WebSocket disabled - unsubscribe not performed:', eventType);
    },
    reconnect: () => {
      console.log('WebSocket disabled - reconnection not attempted');
    }
  };

  return (
    <SocketContext.Provider value={contextValue}>
      {children}
    </SocketContext.Provider>
  );
};

export default SocketProvider;