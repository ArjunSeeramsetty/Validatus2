// DEMO ONLY - This file contains demo authentication logic for development/testing purposes
// In production, replace with secure server-side authentication using HttpOnly cookies and Authorization Code + PKCE

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { loginSuccess, logout as reduxLogout } from '../store/slices/authSlice';

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
  const dispatch = useDispatch();
  
  // Get auth state from Redux store
  const { user: reduxUser, isAuthenticated: reduxIsAuthenticated } = useSelector(
    (state: RootState) => state.auth
  );
  
  const [user, setUser] = useState<User | null>(reduxUser);
  const [isAuthenticated, setIsAuthenticated] = useState(reduxIsAuthenticated);

  // Sync local state with Redux store
  useEffect(() => {
    setUser(reduxUser);
    setIsAuthenticated(reduxIsAuthenticated);
  }, [reduxUser, reduxIsAuthenticated]);

  useEffect(() => {
    // DEMO ONLY - Check for stored auth token
    // In production, this should use secure HttpOnly cookies and server-side session validation
    const token = sessionStorage.getItem('demo_auth_token'); // Use sessionStorage with short lifetime for demo
    if (token && !isAuthenticated) {
      // Mock user for demo
      const mockUser = {
        id: '1',
        email: 'demo@validatus.com',
        name: 'Demo User',
        role: 'analyst'
      };
      
      setUser(mockUser);
      setIsAuthenticated(true);
      
      // Update Redux store
      dispatch(loginSuccess(mockUser));
    }
  }, [dispatch, isAuthenticated]);

  const login = async (email: string, password: string) => {
    // DEMO ONLY - Mock login for demo
    // In production, this should call backend auth endpoint with Authorization Code + PKCE
    
    // Simple demo validation
    if (password !== 'demo123') {
      throw new Error('Invalid credentials. Use password: demo123');
    }
    
    const mockUser = {
      id: '1',
      email,
      name: 'Demo User',
      role: 'analyst'
    };
    
    sessionStorage.setItem('demo_auth_token', 'mock_token'); // Use sessionStorage for demo
    setUser(mockUser);
    setIsAuthenticated(true);
    
    // Update Redux store
    dispatch(loginSuccess(mockUser));
  };

  const logout = () => {
    sessionStorage.removeItem('demo_auth_token'); // Use sessionStorage for demo
    setUser(null);
    setIsAuthenticated(false);
    
    // Update Redux store
    dispatch(reduxLogout());
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

// Hook to use the auth context
export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};