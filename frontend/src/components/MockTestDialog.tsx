import React from 'react';

interface MockTestDialogProps {
  testName: string;
  totalQuestions: number;
  duration: number;
  onStart: () => void;
  onCancel: () => void;
}

export default function MockTestDialog({ 
  testName, 
  totalQuestions, 
  duration, 
  onStart, 
  onCancel 
}: MockTestDialogProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">📝</span>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            Start Mock Test
          </h2>
          <h3 className="text-lg text-gray-700 mb-4">
            {testName}
          </h3>
        </div>

        <div className="space-y-4 mb-6">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-600">Total Questions:</span>
            <span className="font-semibold text-gray-900">{totalQuestions}</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-600">Duration:</span>
            <span className="font-semibold text-gray-900">{duration} minutes</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span className="text-gray-600">Time per question:</span>
            <span className="font-semibold text-gray-900">
              ~{Math.round(duration / totalQuestions * 60)} seconds
            </span>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <span className="text-yellow-600 mr-2">⚠️</span>
            <div className="text-sm text-yellow-800">
              <p className="font-semibold mb-2">Important Instructions:</p>
              <ul className="space-y-1 text-xs">
                <li>• The test will open in fullscreen mode</li>
                <li>• Timer will start immediately</li>
                <li>• Exiting fullscreen will auto-submit the test</li>
                <li>• You can navigate between questions freely</li>
                <li>• Test will auto-submit when time expires</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onStart}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Start Test
          </button>
        </div>
      </div>
    </div>
  );
}
