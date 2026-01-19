'use client';

import { useState, useEffect } from 'react';
import { SessionStatus } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';

interface ProcessingStatusProps {
  sessionId: string;
  onComplete: () => void;
}

export default function ProcessingStatus({ sessionId, onComplete }: ProcessingStatusProps) {
  const [status, setStatus] = useState<SessionStatus>(SessionStatus.PENDING);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await StudyBuddyAPI.getProcessingStatus(sessionId);
        setStatus(response.status);
        setMessage(response.message || '');
        setError(response.error_message || '');

        if (response.status === SessionStatus.COMPLETED) {
          onComplete();
        } else if (response.status === SessionStatus.FAILED) {
          // Stop polling on failure
          return;
        }
      } catch (error) {
        console.error('Failed to check status:', error);
        setError('Failed to check processing status');
      }
    };

    // Initial check
    checkStatus();

    // Poll every 3 seconds if still processing
    const interval = setInterval(() => {
      if (status === SessionStatus.PROCESSING || status === SessionStatus.PENDING) {
        checkStatus();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [sessionId, status, onComplete]);

  const getStatusDisplay = () => {
    switch (status) {
      case SessionStatus.PENDING:
        return {
          className: 'status-pending',
          text: 'Pending',
          icon: '⏳'
        };
      case SessionStatus.PROCESSING:
        return {
          className: 'status-processing',
          text: 'Processing',
          icon: '⚡'
        };
      case SessionStatus.COMPLETED:
        return {
          className: 'status-completed',
          text: 'Completed',
          icon: '✅'
        };
      case SessionStatus.FAILED:
        return {
          className: 'status-failed',
          text: 'Failed',
          icon: '❌'
        };
      default:
        return {
          className: 'status-pending',
          text: 'Unknown',
          icon: '❓'
        };
    }
  };

  const statusDisplay = getStatusDisplay();

  return (
    <div className="card">
      <div className="text-center space-y-4">
        <div className="text-4xl">{statusDisplay.icon}</div>
        
        <div>
          <h3 className="text-lg font-semibold mb-2">Processing Your Files</h3>
          <span className={statusDisplay.className}>
            {statusDisplay.text}
          </span>
        </div>

        {message && (
          <p className="text-gray-600">{message}</p>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {(status === SessionStatus.PROCESSING || status === SessionStatus.PENDING) && (
          <div className="space-y-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
            <p className="text-sm text-gray-500">
              This may take a few minutes depending on file size and processing mode...
            </p>
          </div>
        )}

        {status === SessionStatus.COMPLETED && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-medium">
              🎉 Processing completed successfully!
            </p>
            <p className="text-green-700 text-sm mt-1">
              Your study materials are ready. Check the results below.
            </p>
          </div>
        )}

        <div className="text-xs text-gray-500">
          Session ID: {sessionId}
        </div>
      </div>
    </div>
  );
}
