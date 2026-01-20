'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import FileUpload from '@/components/FileUpload';
import ProcessingStatus from '@/components/ProcessingStatus';
import ResultsViewer from '@/components/ResultsViewer';
import SessionHistory from '@/components/SessionHistory';

type AppState = 'upload' | 'processing' | 'results';

export default function StudyBuddyPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [appState, setAppState] = useState<AppState>('upload');
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [error, setError] = useState<string>('');

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  // Show loading while checking auth
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

  // Don't render if not authenticated
  if (!user) {
    return null;
  }

  const handleUploadSuccess = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setAppState('processing');
    setError('');
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const handleProcessingComplete = () => {
    setAppState('results');
  };

  const handleStartNew = () => {
    setAppState('upload');
    setCurrentSessionId('');
    setError('');
  };

  const handleSessionSelect = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setAppState('results');
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          StudyBuddy Dashboard
        </h1>
        <p className="text-gray-600">
          Upload your study materials and let AI create comprehensive learning resources
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="flex items-center justify-center space-x-4">
        <div className={`flex items-center space-x-2 ${
          appState === 'upload' ? 'text-blue-600' : 'text-gray-400'
        }`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            appState === 'upload' ? 'bg-blue-600 text-white' : 'bg-gray-200'
          }`}>
            1
          </div>
          <span className="font-medium">Upload</span>
        </div>
        
        <div className="w-8 h-px bg-gray-300"></div>
        
        <div className={`flex items-center space-x-2 ${
          appState === 'processing' ? 'text-blue-600' : 'text-gray-400'
        }`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            appState === 'processing' ? 'bg-blue-600 text-white' : 
            appState === 'results' ? 'bg-green-600 text-white' : 'bg-gray-200'
          }`}>
            {appState === 'results' ? '✓' : '2'}
          </div>
          <span className="font-medium">Process</span>
        </div>
        
        <div className="w-8 h-px bg-gray-300"></div>
        
        <div className={`flex items-center space-x-2 ${
          appState === 'results' ? 'text-blue-600' : 'text-gray-400'
        }`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            appState === 'results' ? 'bg-blue-600 text-white' : 'bg-gray-200'
          }`}>
            3
          </div>
          <span className="font-medium">Results</span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-red-600 mr-2">❌</span>
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div>
        {appState === 'upload' && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-6">Upload Study Materials</h2>
            <FileUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
          </div>
        )}

        {appState === 'processing' && (
          <ProcessingStatus
            sessionId={currentSessionId}
            onComplete={handleProcessingComplete}
          />
        )}

        {appState === 'results' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Study Materials Generated</h2>
              <button
                onClick={handleStartNew}
                className="btn-secondary"
              >
                Start New Session
              </button>
            </div>
            <ResultsViewer sessionId={currentSessionId} />
          </div>
        )}
      </div>

      {/* Help Section */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">Need Help?</h3>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Supported Files</h4>
            <p className="text-gray-600">PDF, JPG, PNG, PPTX up to 50MB each</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Processing Modes</h4>
            <p className="text-gray-600">Choose based on your file quality and needs</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Generated Content</h4>
            <p className="text-gray-600">Questions, tests, mnemonics, sheets, and notes</p>
          </div>
        </div>
      </div>

      {/* Session History */}
      <SessionHistory onSessionSelect={handleSessionSelect} />
    </div>
  );
}
