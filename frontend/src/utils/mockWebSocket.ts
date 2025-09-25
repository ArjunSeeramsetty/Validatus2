// Mock WebSocket implementation for development
export const mockWebSocketImplementation = {
  socket: null,
  connected: false,
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
