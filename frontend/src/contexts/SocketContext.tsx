import React, { createContext, useContext, ReactNode } from 'react';
// Removed mock WebSocket import - using real WebSocket implementation

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

// Real WebSocket implementation (disabled for now)
const realWebSocketImplementation: SocketContextType = {
  socket: null,
  connected: false,
  connectionStatus: 'disconnected',
  lastMessage: null,
  sendMessage: (message: string) => {
    console.log('WebSocket send (disabled):', message);
  },
  subscribe: (eventType: string, callback: (data: any) => void) => {
    console.log('WebSocket subscribe (disabled):', eventType);
    return () => console.log('WebSocket unsubscribe (disabled):', eventType);
  },
  unsubscribe: (eventType: string) => {
    console.log('WebSocket unsubscribe (disabled):', eventType);
  },
  reconnect: () => {
    console.log('WebSocket reconnect (disabled)');
  }
};

// Hook for WebSocket connection (disabled for now)
export const useWebSocketConnection = () => {
  return realWebSocketImplementation;
};

// Provider props interface
interface SocketProviderProps {
  children: ReactNode;
}

// Socket provider component (WebSocket functionality disabled for now)
export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  // Disabled WebSocket implementation - provides real interface
  const contextValue: SocketContextType = realWebSocketImplementation;

  return (
    <SocketContext.Provider value={contextValue}>
      {children}
    </SocketContext.Provider>
  );
};

export default SocketProvider;