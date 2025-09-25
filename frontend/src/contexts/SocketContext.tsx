import React, { createContext, useContext, ReactNode } from 'react';
import { mockWebSocketImplementation } from '../utils/mockWebSocket';

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
  return mockWebSocketImplementation;
};

// Provider props interface
interface SocketProviderProps {
  children: ReactNode;
}

// Socket provider component (WebSocket functionality disabled for now)
export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  // Disabled WebSocket implementation - provides mock interface
  const contextValue: SocketContextType = mockWebSocketImplementation;

  return (
    <SocketContext.Provider value={contextValue}>
      {children}
    </SocketContext.Provider>
  );
};

export default SocketProvider;