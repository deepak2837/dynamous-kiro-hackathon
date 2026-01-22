"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { FiPhone, FiLock, FiLoader, FiArrowRight, FiAlertCircle } from 'react-icons/fi';

const LoginPage = () => {
  const [mobileNumber, setMobileNumber] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const success = await login(mobileNumber, password);
      if (success) {
        router.push('/study-buddy');
      } else {
        setError('Invalid mobile number or password. Please try again.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Decorative Elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-pink-300/30 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-20 right-10 w-40 h-40 bg-fuchsia-300/30 rounded-full blur-3xl animate-float animation-delay-300" />

      <div className="max-w-md w-full space-y-8 relative">
        {/* Header */}
        <div className="text-center">
          <div className="relative inline-block mb-6">
            <div className="absolute inset-0 bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-3xl blur-xl opacity-50 animate-pulse" />
            <div className="relative w-20 h-20 bg-gradient-to-br from-pink-500 to-fuchsia-500 rounded-3xl flex items-center justify-center shadow-2xl shadow-pink-300/50 mx-auto">
              <span className="text-4xl">👋</span>
            </div>
          </div>
          <h2 className="text-4xl font-extrabold gradient-text mb-2">
            Welcome Back!
          </h2>
          <p className="text-gray-600">
            Sign in to continue your learning journey
          </p>
          <p className="mt-3 text-sm text-gray-500">
            Don't have an account?{' '}
            <Link href="/register" className="font-semibold text-pink-600 hover:text-pink-700 transition-colors">
              Create one now
            </Link>
          </p>
        </div>

        {/* Login Card */}
        <div className="card !p-8 animate-slide-up">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Mobile Number */}
            <div>
              <label htmlFor="mobile" className="block text-sm font-semibold text-gray-700 mb-2">
                Mobile Number
              </label>
              <div className="relative">
                <FiPhone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pink-400" />
                <input
                  id="mobile"
                  name="mobile"
                  type="tel"
                  required
                  value={mobileNumber}
                  onChange={(e) => setMobileNumber(e.target.value)}
                  className="input-field pl-12"
                  placeholder="Enter your mobile number"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pink-400" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-12"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center space-x-2 text-rose-600 bg-rose-50 rounded-xl p-4 border border-rose-200 animate-slide-up">
                <FiAlertCircle className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary py-4 text-lg font-bold disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <FiLoader className="w-5 h-5 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <FiArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-pink-100"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-400">For medical students</span>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-3 gap-4 text-center text-xs text-gray-500">
            <div className="flex flex-col items-center">
              <span className="text-2xl mb-1">📚</span>
              <span>Questions</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-2xl mb-1">🧠</span>
              <span>Mnemonics</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-2xl mb-1">📝</span>
              <span>Mock Tests</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
