'use client';

import { useState, useEffect } from 'react';
import AuthForm from '../../components/AuthForm';
import apiClient from '../../lib/api';

export default function AuthPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Set token in API client
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Verify token by fetching user info
      apiClient.get('/auth/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          // Token is invalid, remove it
          localStorage.removeItem('auth_token');
          delete apiClient.defaults.headers.common['Authorization'];
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const handleAuthSuccess = (token: string, userData: any) => {
    // Set token in API client
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    delete apiClient.defaults.headers.common['Authorization'];
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (user) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold mb-6 text-center">Welcome!</h1>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <div className="mt-1 text-gray-900">{user.name}</div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <div className="mt-1 text-gray-900">{user.email}</div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">User ID</label>
              <div className="mt-1 text-gray-900">{user.user_id}</div>
            </div>
          </div>
          
          <button
            onClick={handleLogout}
            className="mt-6 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Logout
          </button>
          
          <div className="mt-4 text-center">
            <a 
              href="/study-buddy" 
              className="text-blue-600 hover:text-blue-800 underline"
            >
              Go to Study Buddy
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <AuthForm mode={mode} onSuccess={handleAuthSuccess} />
      
      <div className="text-center mt-4">
        <button
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          className="text-blue-600 hover:text-blue-800 underline"
        >
          {mode === 'login' 
            ? "Don't have an account? Register" 
            : "Already have an account? Login"
          }
        </button>
      </div>
    </div>
  );
}
