"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { FiEye, FiEyeOff, FiLoader, FiPhone, FiMail } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

const LoginPage = () => {
  const [step, setStep] = useState<'mobile' | 'password' | 'forgot-password' | 'verify-otp' | 'reset-password'>('mobile');
  const [mobileNumber, setMobileNumber] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otpMethod, setOtpMethod] = useState<'sms' | 'email'>('sms');
  const [email, setEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, checkUserExists, sendForgotPasswordOTP, resetPassword, user } = useAuth();
  const router = useRouter();

  // Redirect if already authenticated
  useEffect(() => {
    if (user) {
      router.push('/');
    }
  }, [user, router]);

  const validateMobileNumber = (mobile: string): boolean => {
    const cleanMobile = mobile.replace(/\D/g, '');
    return cleanMobile.length >= 10;
  };

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleMobileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateMobileNumber(mobileNumber)) {
      setError('Please enter a valid mobile number');
      return;
    }

    setIsLoading(true);
    try {
      const { exists, verified } = await checkUserExists(mobileNumber);
      
      if (exists && verified) {
        setStep('password');
      } else if (exists && !verified) {
        setError('Account not verified. Please complete registration.');
      } else {
        setError('Mobile number not registered. Please sign up first.');
        setTimeout(() => router.push('/register'), 2000);
      }
    } catch (err) {
      setError('Error checking mobile number. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);
    try {
      const success = await login(mobileNumber, password);
      
      if (success) {
        toast.success('Login successful!');
        router.push('/');
      } else {
        setError('Invalid password. Please try again.');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (otpMethod === 'email' && !validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);
    try {
      const success = await sendForgotPasswordOTP(mobileNumber, otpMethod, email);
      
      if (success) {
        toast.success(`OTP sent to your ${otpMethod === 'email' ? 'email' : 'mobile number'}`);
        setStep('verify-otp');
      } else {
        setError('Failed to send OTP. Please try again.');
      }
    } catch (err) {
      setError('Error sending OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    // For demo purposes, accept any 6-digit OTP
    toast.success('OTP verified successfully!');
    setStep('reset-password');
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);
    try {
      const success = await resetPassword(mobileNumber, otp, newPassword);
      
      if (success) {
        toast.success('Password reset successfully!');
        setStep('password');
        setPassword('');
        setOtp('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        setError('Failed to reset password. Please try again.');
      }
    } catch (err) {
      setError('Error resetting password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const resetToMobile = () => {
    setStep('mobile');
    setPassword('');
    setOtp('');
    setNewPassword('');
    setConfirmPassword('');
    setError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to StudyBuddy
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link href="/register" className="font-medium text-indigo-600 hover:text-indigo-500">
              create a new account
            </Link>
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          {/* Mobile Number Step */}
          {step === 'mobile' && (
            <form onSubmit={handleMobileSubmit} className="space-y-6">
              <div>
                <label htmlFor="mobile" className="block text-sm font-medium text-gray-700">
                  Mobile Number
                </label>
                <div className="mt-1 relative">
                  <input
                    id="mobile"
                    name="mobile"
                    type="tel"
                    required
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value)}
                    className="appearance-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="Enter your mobile number"
                  />
                  <FiPhone className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                </div>
              </div>

              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}

              <button
                type="submit"
                disabled={isLoading || !mobileNumber}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <FiLoader className="animate-spin h-5 w-5" />
                ) : (
                  'Continue'
                )}
              </button>
            </form>
          )}

          {/* Password Step */}
          {step === 'password' && (
            <form onSubmit={handlePasswordSubmit} className="space-y-6">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="mt-1 relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}

              <div className="flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setStep('forgot-password')}
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  Forgot password?
                </button>
                <button
                  type="button"
                  onClick={resetToMobile}
                  className="text-sm text-gray-600 hover:text-gray-500"
                >
                  Change mobile number
                </button>
              </div>

              <button
                type="submit"
                disabled={isLoading || !password}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <FiLoader className="animate-spin h-5 w-5" />
                ) : (
                  'Sign In'
                )}
              </button>
            </form>
          )}

          {/* Forgot Password Step */}
          {step === 'forgot-password' && (
            <form onSubmit={handleForgotPassword} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Reset Password</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      How would you like to receive the OTP?
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="sms"
                          checked={otpMethod === 'sms'}
                          onChange={(e) => setOtpMethod(e.target.value as 'sms')}
                          className="mr-2"
                        />
                        <FiPhone className="mr-1" />
                        SMS
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="email"
                          checked={otpMethod === 'email'}
                          onChange={(e) => setOtpMethod(e.target.value as 'email')}
                          className="mr-2"
                        />
                        <FiMail className="mr-1" />
                        Email
                      </label>
                    </div>
                  </div>

                  {otpMethod === 'email' && (
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Email Address
                      </label>
                      <input
                        id="email"
                        name="email"
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Enter your email address"
                      />
                    </div>
                  )}
                </div>
              </div>

              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setStep('password')}
                  className="flex-1 py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading || (otpMethod === 'email' && !email)}
                  className="flex-1 py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <FiLoader className="animate-spin h-5 w-5 mx-auto" />
                  ) : (
                    'Send OTP'
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Verify OTP Step */}
          {step === 'verify-otp' && (
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Verify OTP</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Enter the 6-digit OTP sent to your {otpMethod === 'email' ? 'email' : 'mobile number'}
                </p>
                
                <label htmlFor="otp" className="block text-sm font-medium text-gray-700">
                  OTP Code
                </label>
                <input
                  id="otp"
                  name="otp"
                  type="text"
                  maxLength={6}
                  required
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm text-center text-lg tracking-widest"
                  placeholder="000000"
                />
              </div>

              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setStep('forgot-password')}
                  className="flex-1 py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading || otp.length !== 6}
                  className="flex-1 py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <FiLoader className="animate-spin h-5 w-5 mx-auto" />
                  ) : (
                    'Verify OTP'
                  )}
                </button>
              </div>
            </form>
          )}

          {/* Reset Password Step */}
          {step === 'reset-password' && (
            <form onSubmit={handleResetPassword} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Set New Password</h3>
                
                <div className="space-y-4">
                  <div>
                    <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700">
                      New Password
                    </label>
                    <div className="mt-1 relative">
                      <input
                        id="newPassword"
                        name="newPassword"
                        type={showNewPassword ? 'text' : 'password'}
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Enter new password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 hover:text-gray-600"
                      >
                        {showNewPassword ? <FiEyeOff /> : <FiEye />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                      Confirm Password
                    </label>
                    <div className="mt-1 relative">
                      <input
                        id="confirmPassword"
                        name="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Confirm new password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 hover:text-gray-600"
                      >
                        {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}

              <button
                type="submit"
                disabled={isLoading || !newPassword || !confirmPassword}
                className="w-full py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <FiLoader className="animate-spin h-5 w-5 mx-auto" />
                ) : (
                  'Reset Password'
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
