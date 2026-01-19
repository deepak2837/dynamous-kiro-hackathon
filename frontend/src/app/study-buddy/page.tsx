'use client';

import { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import ProcessingStatus from '@/components/ProcessingStatus';
import ResultsViewer from '@/components/ResultsViewer';

type AppState = 'upload' | 'processing' | 'results';

export default function StudyBuddyPage() {
  const [appState, setAppState] = useState<AppState>('upload');
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [error, setError] = useState<string>('');

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
    </div>
  );
}
