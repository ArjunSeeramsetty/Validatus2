// frontend/src/contexts/SocketContext.tsx

import React, { createContext, useContext } from 'react';
import { WebSocketProvider } from '../hooks/useWebSocketConnection';

interface SocketContextType {
  isConnected: boolean;
  socket: any;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

interface SocketProviderProps {
  children: React.ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const isConnected = true; // Mock connection for demo
  const socket = null; // Mock socket for demo

  const value = {
    isConnected,
    socket
  };

  return (
    <SocketContext.Provider value={value}>
      <WebSocketProvider
        url={import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000/ws'}
        autoReconnect={false}
        maxReconnectAttempts={0}
        reconnectInterval={3000}
      >
        {children}
      </WebSocketProvider>
    </SocketContext.Provider>
  );
};
