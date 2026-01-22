"use client";
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FiUser, FiLogOut, FiUpload, FiZap, FiFileText, FiCpu, FiAward, FiBookOpen, FiArrowRight } from 'react-icons/fi';
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
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="text-center">
          <div className="relative">
            <div className="w-20 h-20 border-4 border-pink-200 rounded-full animate-spin border-t-pink-500 mx-auto mb-6" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-full animate-pulse" />
            </div>
          </div>
          <p className="text-pink-600 font-medium animate-pulse">Loading StudyBuddy...</p>
        </div>
      </div>
    );
  }

  const features = [
    { icon: FiUpload, title: 'Multi-Format Upload', desc: 'Upload PDFs, images, slides, and video links. We support all your study materials.', color: 'from-pink-400 to-rose-500' },
    { icon: FiCpu, title: 'AI-Powered Processing', desc: 'Choose from Default, OCR, or AI-based processing modes for optimal results.', color: 'from-rose-400 to-fuchsia-500' },
    { icon: FiFileText, title: 'Question Banks', desc: 'Auto-generated MCQs with difficulty classification and detailed explanations.', color: 'from-fuchsia-400 to-purple-500' },
    { icon: FiZap, title: 'Mock Tests', desc: 'Timed tests with auto-generated names and comprehensive scoring.', color: 'from-purple-400 to-violet-500' },
    { icon: FiBookOpen, title: 'Mnemonics', desc: 'India-specific memory aids for better retention of medical concepts.', color: 'from-violet-400 to-pink-500' },
    { icon: FiAward, title: 'Cheat Sheets & Notes', desc: 'Key topics, high-yield points, and compiled study materials.', color: 'from-pink-500 to-rose-400' },
  ];

  const steps = [
    { num: '01', title: 'Upload', desc: 'Upload your study materials' },
    { num: '02', title: 'Process', desc: 'Choose processing mode' },
    { num: '03', title: 'Generate', desc: 'AI creates study materials' },
    { num: '04', title: 'Study', desc: 'Access & download materials' },
  ];

  return (
    <div className="space-y-16">
      {/* User Welcome Bar */}
      {user && (
        <div className="card animate-slide-up">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-2xl flex items-center justify-center shadow-lg shadow-pink-200/50 animate-pulse-glow">
                <FiUser className="h-7 w-7 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 text-lg">Welcome back, {user.name}! 👋</h3>
                <p className="text-sm text-pink-500">
                  {user.role === 'student' ? `${user.course} - ${user.college_name}` : `${user.speciality} - ${user.hospital_name}`}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button className="btn-ghost flex items-center space-x-2">
                <FiUser className="h-4 w-4" />
                <span>Profile</span>
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 text-rose-600 hover:bg-rose-50 rounded-xl transition-all duration-300"
              >
                <FiLogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="text-center relative py-8">
        {/* Decorative elements */}
        <div className="absolute top-0 left-1/4 w-20 h-20 bg-pink-300/30 rounded-full blur-2xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-32 h-32 bg-fuchsia-300/30 rounded-full blur-2xl animate-float animation-delay-300" />

        <div className="relative">
          <div className="inline-flex items-center px-4 py-2 bg-pink-100/80 backdrop-blur-sm rounded-full text-pink-600 text-sm font-medium mb-6 animate-bounce-in">
            <span className="animate-wiggle inline-block mr-2">🎓</span> AI-Powered Learning Platform
          </div>

          <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 animate-slide-up">
            <span className="gradient-text">Welcome to</span>
            <br />
            <span className="text-gray-900">StudyBuddy</span>
          </h1>

          <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto animate-slide-up animation-delay-200 leading-relaxed">
            Transform your study materials into comprehensive learning resources.
            Upload PDFs, images, slides, and videos to generate{' '}
            <span className="text-pink-600 font-semibold">question banks</span>,{' '}
            <span className="text-rose-500 font-semibold">mock tests</span>,{' '}
            <span className="text-fuchsia-500 font-semibold">mnemonics</span>, and more.
          </p>

          {user ? (
            <div className="space-y-8 animate-slide-up animation-delay-300">
              <Link
                href="/study-buddy"
                className="btn-primary text-lg px-10 py-4 inline-flex items-center space-x-3 group"
              >
                <span>Start Studying</span>
                <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                <span className="text-2xl">🚀</span>
              </Link>

              <div className="text-center">
                <p className="text-gray-500 mb-4">Or upload files directly:</p>
                <Link
                  href="/study-buddy"
                  className="dropzone max-w-xl mx-auto block hover:scale-[1.02] transition-transform duration-300"
                >
                  <div className="text-5xl mb-4 animate-float">📁</div>
                  <p className="text-gray-600 mb-2">
                    Drag & drop files here, or <span className="text-pink-600 font-semibold">click to select</span>
                  </p>
                  <p className="text-sm text-pink-400">
                    Supports PDF, JPG, PNG, PPTX (max 50MB each)
                  </p>
                </Link>
              </div>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up animation-delay-300">
              <Link
                href="/login"
                className="btn-primary text-lg px-10 py-4 inline-flex items-center space-x-2"
              >
                <span>Login</span>
                <FiArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/register"
                className="btn-secondary text-lg px-10 py-4"
              >
                Create Account
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <div
            key={feature.title}
            className="card group animate-slide-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
              <feature.icon className="h-7 w-7 text-white" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-pink-600 transition-colors">{feature.title}</h3>
            <p className="text-gray-600 leading-relaxed">
              {feature.desc}
            </p>
          </div>
        ))}
      </div>

      {/* How It Works */}
      <div className="card-glass animate-slide-up">
        <h2 className="text-3xl font-bold mb-10 text-center">
          <span className="gradient-text">How It Works</span>
        </h2>
        <div className="grid md:grid-cols-4 gap-8 relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-10 left-[12%] right-[12%] h-0.5 bg-gradient-to-r from-pink-300 via-rose-300 to-fuchsia-300" />

          {steps.map((step, index) => (
            <div key={step.num} className="text-center relative group">
              <div className="relative inline-block mb-4">
                <div className="w-20 h-20 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-pink-200/50 group-hover:scale-110 group-hover:-rotate-3 transition-all duration-300">
                  <span className="text-white font-bold text-xl">{step.num}</span>
                </div>
                {index < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-8 transform -translate-y-1/2 text-pink-300">
                    <FiArrowRight className="w-6 h-6" />
                  </div>
                )}
              </div>
              <h3 className="font-bold text-gray-900 mb-1">{step.title}</h3>
              <p className="text-sm text-gray-600">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative overflow-hidden rounded-3xl animate-slide-up">
        <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-rose-500 to-fuchsia-500" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIxMCIvPjwvZz48L2c+PC9zdmc+')] opacity-20" />

        <div className="relative text-center py-16 px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Study Experience?
          </h2>
          <p className="text-pink-100 mb-8 text-lg max-w-2xl mx-auto">
            Join thousands of medical students who are studying smarter with AI.
          </p>
          {user ? (
            <Link
              href="/study-buddy"
              className="inline-flex items-center space-x-2 bg-white text-pink-600 font-bold py-4 px-10 rounded-2xl shadow-2xl hover:shadow-pink-900/30 hover:scale-105 transition-all duration-300"
            >
              <span>Get Started Now</span>
              <FiArrowRight className="w-5 h-5" />
            </Link>
          ) : (
            <Link
              href="/register"
              className="inline-flex items-center space-x-2 bg-white text-pink-600 font-bold py-4 px-10 rounded-2xl shadow-2xl hover:shadow-pink-900/30 hover:scale-105 transition-all duration-300"
            >
              <span>Create Account</span>
              <FiArrowRight className="w-5 h-5" />
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
