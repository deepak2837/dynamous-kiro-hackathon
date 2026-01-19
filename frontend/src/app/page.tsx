import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="space-y-8">
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
        <Link 
          href="/study-buddy" 
          className="btn-primary text-lg px-8 py-3 inline-block"
        >
          Start Studying 🚀
        </Link>
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
        <Link 
          href="/study-buddy" 
          className="btn-primary text-lg px-8 py-3 inline-block"
        >
          Get Started Now
        </Link>
      </div>
    </div>
  );
}
