"use client";
import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { FiUser, FiLogOut, FiChevronDown, FiBookOpen } from 'react-icons/fi';
import Link from 'next/link';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);

  return (
    <header className="glass-header sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <Link href="/" className="flex items-center group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative bg-gradient-to-r from-pink-500 to-fuchsia-500 p-2 rounded-xl">
                <FiBookOpen className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="ml-3">
              <h1 className="text-xl font-bold gradient-text">
                StudyBuddy
              </h1>
              <span className="text-xs text-pink-400 font-medium">
                AI-Powered Study Companion
              </span>
            </div>
          </Link>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            <div className="hidden sm:block text-sm text-pink-500 font-medium bg-pink-100/50 px-3 py-1 rounded-full">
              ✨ For Medical Students
            </div>

            {/* User Profile Section */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="flex items-center space-x-2 text-gray-700 hover:text-pink-600 focus:outline-none 
                           bg-white/50 hover:bg-white/80 backdrop-blur-md px-3 py-2 rounded-xl 
                           border border-pink-100 transition-all duration-300 group"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-full flex items-center justify-center shadow-lg shadow-pink-200/50">
                    <FiUser className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm font-medium">{user.name}</span>
                  <FiChevronDown className={`w-4 h-4 transition-transform duration-300 ${showDropdown ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown Menu */}
                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-72 bg-white/90 backdrop-blur-xl rounded-2xl shadow-2xl shadow-pink-200/30 border border-pink-100 z-50 animate-slide-down overflow-hidden">
                    <div className="px-4 py-4 border-b border-pink-100 bg-gradient-to-r from-pink-50 to-fuchsia-50">
                      <p className="text-sm font-semibold text-gray-900">{user.name}</p>
                      <p className="text-xs text-pink-500">{user.mobile_number}</p>
                      {user.email && (
                        <p className="text-xs text-gray-500">{user.email}</p>
                      )}
                      <div className="mt-2 flex flex-wrap gap-1">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white">
                          {user.role}
                        </span>
                        {user.college_name && (
                          <span className="text-xs text-gray-500 bg-white/50 px-2 py-0.5 rounded-full">
                            {user.college_name}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="p-2">
                      <button
                        onClick={() => {
                          logout();
                          setShowDropdown(false);
                        }}
                        className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-pink-50 hover:text-pink-600 rounded-xl transition-all duration-200"
                      >
                        <FiLogOut className="w-4 h-4 mr-3" />
                        Sign out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  href="/login"
                  className="text-sm text-pink-600 hover:text-pink-700 font-medium transition-colors"
                >
                  Sign in
                </Link>
                <Link
                  href="/register"
                  className="btn-primary text-sm"
                >
                  Sign up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Click outside to close dropdown */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </header>
  );
};

export default Header;
