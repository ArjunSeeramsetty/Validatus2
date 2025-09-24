// frontend/src/contexts/AuthContext.tsx
// DEMO ONLY - This file contains demo authentication logic for development/testing purposes
// In production, replace with secure server-side authentication using HttpOnly cookies and Authorization Code + PKCE

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // DEMO ONLY - Check for stored auth token
    // In production, this should use secure HttpOnly cookies and server-side session validation
    const token = sessionStorage.getItem('demo_auth_token'); // Use sessionStorage with short lifetime for demo
    if (token) {
      // Mock user for demo
      setUser({
        id: '1',
        email: 'demo@validatus.com',
        name: 'Demo User',
        role: 'analyst'
      });
      setIsAuthenticated(true);
    }
  }, []);

  const login = async (email: string, password: string) => {
    // DEMO ONLY - Mock login for demo
    // In production, this should call backend auth endpoint with Authorization Code + PKCE
    const mockUser = {
      id: '1',
      email,
      name: 'Demo User',
      role: 'analyst'
    };
    
    sessionStorage.setItem('demo_auth_token', 'mock_token'); // Use sessionStorage for demo
    setUser(mockUser);
    setIsAuthenticated(true);
  };

  const logout = () => {
    sessionStorage.removeItem('demo_auth_token'); // Use sessionStorage for demo
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
