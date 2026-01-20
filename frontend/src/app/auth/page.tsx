'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import AuthForm from '../../components/AuthForm';

export default function AuthPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  // If user is authenticated, show profile with Study Buddy link
  if (!isLoading && user) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold mb-6 text-center">Welcome!</h1>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <div className="mt-1 text-gray-900">{user.name}</div>
            </div>
            
            {user.email && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <div className="mt-1 text-gray-900">{user.email}</div>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Mobile</label>
              <div className="mt-1 text-gray-900">{user.mobile_number}</div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Role</label>
              <div className="mt-1 text-gray-900 capitalize">{user.role}</div>
            </div>
          </div>
          
          <div className="mt-6 space-y-3">
            <button
              onClick={() => router.push('/study-buddy')}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go to Study Buddy
            </button>
            
            <button
              onClick={logout}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  // Show auth form if not authenticated
  const handleAuthSuccess = (token: string, userData: any) => {
    // Auth context will handle the state update
    router.push('/study-buddy');
  };

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
