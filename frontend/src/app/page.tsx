"use client";
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FiUser, FiLogOut } from 'react-icons/fi';
import { useAuth } from '@/contexts/AuthContext';

export default function HomePage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading StudyBuddy...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* User Info Bar */}
      {user && (
        <div className="bg-white rounded-lg shadow-sm border p-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
              <FiUser className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Welcome back, {user.name}!</h3>
              <p className="text-sm text-gray-600">
                {user.role === 'student' ? `${user.course} - ${user.college_name}` : `${user.speciality} - ${user.hospital_name}`}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button className="flex items-center space-x-2 text-gray-600 hover:text-indigo-600 transition-colors">
              <FiUser className="h-5 w-5" />
              <span>Profile</span>
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <FiLogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to StudyBuddy
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Transform your study materials into comprehensive learning resources. 
          Upload PDFs, images, slides, and videos to generate question banks, 
          mock tests, mnemonics, cheat sheets, and notes.
        </p>
        
        {user ? (
          <div className="space-y-6">
            <Link 
              href="/study-buddy" 
              className="btn-primary text-lg px-8 py-3 inline-block"
            >
              Start Studying 🚀
            </Link>
            <div className="text-center">
              <p className="text-gray-600 mb-4">Or upload files directly:</p>
              <div className="max-w-2xl mx-auto">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer">
                  <div className="text-4xl mb-4">📁</div>
                  <p className="text-gray-600 mb-2">
                    Drag & drop files here, or <span className="text-blue-600">click to select</span>
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports PDF, JPG, PNG, PPTX (max 50MB each)
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-x-4">
            <Link 
              href="/login" 
              className="btn-primary text-lg px-8 py-3 inline-block"
            >
              Login
            </Link>
            <Link 
              href="/register" 
              className="btn-secondary text-lg px-8 py-3 inline-block"
            >
              Register
            </Link>
          </div>
        )}
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
        <div className="card">
          <div className="text-2xl mb-3">📤</div>
          <h3 className="text-lg font-semibold mb-2">Multi-Format Upload</h3>
          <p className="text-gray-600">
            Upload PDFs, images, slides, and video links. We support all your study materials.
          </p>
        </div>

        <div className="card">
          <div className="text-2xl mb-3">🤖</div>
          <h3 className="text-lg font-semibold mb-2">AI-Powered Processing</h3>
          <p className="text-gray-600">
            Choose from Default, OCR, or AI-based processing modes for optimal results.
          </p>
        </div>

        <div className="card">
          <div className="text-2xl mb-3">📝</div>
          <h3 className="text-lg font-semibold mb-2">Question Banks</h3>
          <p className="text-gray-600">
            Auto-generated MCQs with difficulty classification and detailed explanations.
          </p>
        </div>

        <div className="card">
          <div className="text-2xl mb-3">📊</div>
          <h3 className="text-lg font-semibold mb-2">Mock Tests</h3>
          <p className="text-gray-600">
            Timed tests with auto-generated names and comprehensive scoring.
          </p>
        </div>

        <div className="card">
          <div className="text-2xl mb-3">🧠</div>
          <h3 className="text-lg font-semibold mb-2">Mnemonics</h3>
          <p className="text-gray-600">
            India-specific memory aids for better retention of medical concepts.
          </p>
        </div>

        <div className="card">
          <div className="text-2xl mb-3">📋</div>
          <h3 className="text-lg font-semibold mb-2">Cheat Sheets & Notes</h3>
          <p className="text-gray-600">
            Key topics, high-yield points, and compiled study materials.
          </p>
        </div>
      </div>

      {/* How It Works */}
      <div className="card mt-12">
        <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">1</span>
            </div>
            <h3 className="font-semibold mb-2">Upload</h3>
            <p className="text-sm text-gray-600">Upload your study materials</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">2</span>
            </div>
            <h3 className="font-semibold mb-2">Process</h3>
            <p className="text-sm text-gray-600">Choose processing mode</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">3</span>
            </div>
            <h3 className="font-semibold mb-2">Generate</h3>
            <p className="text-sm text-gray-600">AI creates study materials</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">4</span>
            </div>
            <h3 className="font-semibold mb-2">Study</h3>
            <p className="text-sm text-gray-600">Access & download materials</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center bg-blue-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Ready to Transform Your Study Experience?
        </h2>
        <p className="text-gray-600 mb-6">
          Join thousands of medical students who are studying smarter with AI.
        </p>
        {user ? (
          <Link 
            href="/study-buddy" 
            className="btn-primary text-lg px-8 py-3 inline-block"
          >
            Get Started Now
          </Link>
        ) : (
          <Link 
            href="/register" 
            className="btn-primary text-lg px-8 py-3 inline-block"
          >
            Create Account
          </Link>
        )}
      </div>
    </div>
  );
}
