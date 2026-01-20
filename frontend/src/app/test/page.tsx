export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          StudyBuddy Test Page
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          This is a simple test page to verify the frontend is working.
        </p>
        <div className="space-x-4">
          <a href="/login" className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            Login
          </a>
          <a href="/register" className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700">
            Register
          </a>
        </div>
      </div>
    </div>
  );
}
