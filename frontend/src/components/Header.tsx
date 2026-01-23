"use client";
import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { FiUser, FiLogOut, FiChevronDown, FiBookOpen, FiCalendar, FiSettings, FiFileText } from 'react-icons/fi';
import Link from 'next/link';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);

  return (
    <header className="glass-header sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo and Title */}
          <Link href="/" className="flex items-center group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative bg-gradient-to-r from-pink-500 to-fuchsia-500 p-2 rounded-xl">
                <FiBookOpen className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="ml-3">
              <h1 className="text-xl font-bold gradient-text">StudyBuddy</h1>
              <span className="text-xs text-pink-400 font-medium">AI-Powered Study Companion</span>
            </div>
          </Link>

          {/* Center - Welcome Message for logged in users */}
          {user && (
            <div className="hidden md:flex items-center space-x-3 bg-white/30 backdrop-blur-md px-4 py-2 rounded-2xl border border-pink-100">
              <span className="text-sm text-pink-500 font-medium">✨ For Medical Students</span>
              <div className="w-px h-4 bg-pink-200"></div>
              <span className="text-sm text-gray-700">Welcome back, <span className="font-semibold text-pink-600">{user.name}</span>! 👋</span>
            </div>
          )}

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            {!user && (
              <div className="hidden sm:block text-sm text-pink-500 font-medium bg-pink-100/50 px-3 py-1 rounded-full">
                ✨ For Medical Students
              </div>
            )}

            {/* User Profile Section */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="flex items-center space-x-3 text-gray-700 hover:text-pink-600 focus:outline-none 
                           bg-white/50 hover:bg-white/80 backdrop-blur-md px-4 py-3 rounded-2xl 
                           border border-pink-100 transition-all duration-300 group shadow-lg shadow-pink-100/50"
                >
                  <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-full flex items-center justify-center shadow-lg shadow-pink-200/50">
                    <FiUser className="w-5 h-5 text-white" />
                  </div>
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-semibold text-gray-900">{user.name}</p>
                    <p className="text-xs text-pink-500">
                      {user.role === 'student' ? `${user.course}` : user.speciality}
                    </p>
                  </div>
                  <FiChevronDown className={`w-4 h-4 transition-transform duration-300 ${showDropdown ? 'rotate-180' : ''}`} />
                </button>

                {/* Enhanced Dropdown Menu */}
                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-80 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl shadow-pink-200/30 border border-pink-100 z-50 animate-slide-down overflow-hidden">
                    {/* User Info Header */}
                    <div className="px-6 py-5 border-b border-pink-100 bg-gradient-to-r from-pink-50 to-fuchsia-50">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-full flex items-center justify-center shadow-lg shadow-pink-200/50">
                          <FiUser className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <p className="text-base font-bold text-gray-900">{user.name}</p>
                          <p className="text-sm text-pink-600 font-medium">
                            {user.role === 'student' ? `${user.course} - ${user.college_name}` : `${user.speciality} - ${user.hospital_name}`}
                          </p>
                          {user.mobile_number && (
                            <p className="text-xs text-gray-500 mt-1">{user.mobile_number}</p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Menu Items */}
                    <div className="p-2">
                      <Link
                        href="/study-planner"
                        onClick={() => setShowDropdown(false)}
                        className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-pink-50 hover:text-pink-600 rounded-xl transition-all duration-200 group"
                      >
                        <div className="w-8 h-8 bg-pink-100 group-hover:bg-pink-200 rounded-lg flex items-center justify-center mr-3 transition-colors">
                          <FiCalendar className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="font-medium">Study Planner</p>
                          <p className="text-xs text-gray-500">Organize your study schedule</p>
                        </div>
                      </Link>
                      
                      <Link
                        href="/docs"
                        onClick={() => setShowDropdown(false)}
                        className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-xl transition-all duration-200 group"
                      >
                        <div className="w-8 h-8 bg-blue-100 group-hover:bg-blue-200 rounded-lg flex items-center justify-center mr-3 transition-colors">
                          <FiFileText className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="font-medium">API Docs</p>
                          <p className="text-xs text-gray-500">View API documentation</p>
                        </div>
                      </Link>
                   

                      <div className="border-t border-pink-100 mt-2 pt-2">
                        <button
                          onClick={() => {
                            logout();
                            setShowDropdown(false);
                          }}
                          className="flex items-center w-full px-4 py-3 text-sm text-rose-600 hover:bg-rose-50 rounded-xl transition-all duration-200 group"
                        >
                          <div className="w-8 h-8 bg-rose-100 group-hover:bg-rose-200 rounded-lg flex items-center justify-center mr-3 transition-colors">
                            <FiLogOut className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="font-medium">Sign out</p>
                            <p className="text-xs text-rose-400">End your session</p>
                          </div>
                        </button>
                      </div>
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
