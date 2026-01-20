"use client";
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ErrorLogger from '@/utils/errorLogger';

interface User {
  id: string;
  name: string;
  mobile_number: string;
  email?: string;
  role: 'student' | 'doctor' | 'admin';
  otp_method: 'email' | 'sms';
  verified: boolean;
  college_name?: string;
  course?: string;
  year?: number;
  exam_name?: string;
  hospital_name?: string;
  speciality?: string;
  experience?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (mobile_number: string, password: string) => Promise<boolean>;
  register: (userData: RegisterData) => Promise<boolean>;
  logout: () => void;
  sendOTP: (mobile_number: string, otp_method: 'email' | 'sms', email?: string) => Promise<boolean>;
  verifyOTP: (mobile_number: string, otp: string) => Promise<boolean>;
  sendForgotPasswordOTP: (mobile_number: string, otp_method: 'email' | 'sms', email?: string) => Promise<boolean>;
  resetPassword: (mobile_number: string, otp: string, new_password: string) => Promise<boolean>;
  checkUserExists: (mobile_number: string) => Promise<{ exists: boolean; verified?: boolean }>;
}

interface RegisterData {
  name: string;
  mobile_number: string;
  email?: string;
  password: string;
  role: 'student' | 'doctor' | 'admin';
  otp_method: 'email' | 'sms';
  college_name?: string;
  course?: string;
  year?: number;
  exam_name?: string;
  hospital_name?: string;
  speciality?: string;
  experience?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        const storedUser = localStorage.getItem('auth_user');

        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        ErrorLogger.logError(error as Error, 'auth_initialization', undefined, { storedToken: !!storedToken });
        console.error('Error initializing auth:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        setToken(null);
        setUser(null);
      }
      setIsLoading(false);
    };

    // Set timeout to prevent infinite loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    initAuth();
    
    return () => clearTimeout(timer);
  }, []);

  const normalizePhoneNumber = (phone: string): string => {
    phone = phone.trim();
    if (!phone.startsWith('+')) {
      if (phone.startsWith('91') && phone.length === 12) {
        phone = '+' + phone;
      } else if (phone.length === 10) {
        phone = '+91' + phone;
      } else {
        phone = '+' + phone;
      }
    }
    return phone;
  };

  const checkUserExists = async (mobile_number: string): Promise<{ exists: boolean; verified?: boolean }> => {
    try {
      const normalizedNumber = normalizePhoneNumber(mobile_number);
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/check-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mobile_number: normalizedNumber }),
      });

      if (response.ok) {
        return await response.json();
      }
      return { exists: false };
    } catch (error) {
      ErrorLogger.logError(error as Error, 'check_user_exists', undefined, { mobile_number });
      console.error('Error checking user exists:', error);
      return { exists: false };
    }
  };

  const sendOTP = async (mobile_number: string, otp_method: 'email' | 'sms', email?: string): Promise<boolean> => {
    try {
      const normalizedNumber = normalizePhoneNumber(mobile_number);
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/send-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_number: normalizedNumber,
          otp_method,
          email: otp_method === 'email' ? email : undefined,
        }),
      });

      return response.ok;
    } catch (error) {
      ErrorLogger.logError(error as Error, 'send_otp', undefined, { mobile_number, otp_method });
      console.error('Error sending OTP:', error);
      return false;
    }
  };

  const verifyOTP = async (mobile_number: string, otp: string): Promise<boolean> => {
    try {
      const normalizedNumber = normalizePhoneNumber(mobile_number);
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/verify-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_number: normalizedNumber,
          otp,
        }),
      });

      return response.ok;
    } catch (error) {
      console.error('Error verifying OTP:', error);
      return false;
    }
  };

  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      const normalizedData = {
        ...userData,
        mobile_number: normalizePhoneNumber(userData.mobile_number),
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(normalizedData),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('auth_user', JSON.stringify(data.user));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error registering user:', error);
      return false;
    }
  };

  const login = async (mobile_number: string, password: string): Promise<boolean> => {
    try {
      const normalizedNumber = normalizePhoneNumber(mobile_number);
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_number: normalizedNumber,
          password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setUser(data.user);
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('auth_user', JSON.stringify(data.user));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error logging in:', error);
      return false;
    }
  };

  const sendForgotPasswordOTP = async (mobile_number: string, otp_method: 'email' | 'sms', email?: string): Promise<boolean> => {
    try {
      const normalizedNumber = normalizePhoneNumber(mobile_number);
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_number: normalizedNumber,
          otp_method,
          email: otp_method === 'email' ? email : undefined,
        }),
      });

      return response.ok;
    } catch (error) {
      console.error('Error sending forgot password OTP:', error);
      return false;
    }
  };

  const resetPassword = async (mobile_number: string, otp: string, new_password: string): Promise<boolean> => {
    try {
      const normalizedNumber = normalizePhoneNumber(mobile_number);
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_number: normalizedNumber,
          otp,
          new_password,
        }),
      });

      return response.ok;
    } catch (error) {
      console.error('Error resetting password:', error);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    router.push('/login');
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
    sendOTP,
    verifyOTP,
    sendForgotPasswordOTP,
    resetPassword,
    checkUserExists,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
