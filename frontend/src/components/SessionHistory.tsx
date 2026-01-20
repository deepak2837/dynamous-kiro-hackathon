"use client";
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { FiClock, FiFileText, FiBook, FiTarget, FiBookmark, FiEdit3, FiChevronRight } from 'react-icons/fi';

interface Session {
  session_id: string;
  session_name: string;
  created_at: string;
  status: string;
  files_uploaded: any[];
  content_counts?: {
    questions: number;
    mock_tests: number;
    mnemonics: number;
    cheat_sheets: number;
    notes: number;
  };
}

interface SessionHistoryProps {
  onSessionSelect?: (sessionId: string) => void;
}

const SessionHistory: React.FC<SessionHistoryProps> = ({ onSessionSelect }) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (token) {
      fetchSessions();
    }
  }, [token]);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch(`${API_BASE_URL}/api/v1/history/sessions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      } else {
        console.error('Failed to fetch sessions:', response.status);
        setError('Failed to load session history');
        setSessions([]);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
      setError('Failed to load session history');
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getContentSummary = (session: Session) => {
    if (!session.content_counts) return 'Processing...';
    
    const counts = session.content_counts;
    const total = counts.questions + counts.mock_tests + counts.mnemonics + counts.cheat_sheets + counts.notes;
    
    if (total === 0) return 'No content generated';
    
    const items = [];
    if (counts.questions > 0) items.push(`${counts.questions} questions`);
    if (counts.mock_tests > 0) items.push(`${counts.mock_tests} tests`);
    if (counts.mnemonics > 0) items.push(`${counts.mnemonics} mnemonics`);
    if (counts.cheat_sheets > 0) items.push(`${counts.cheat_sheets} sheets`);
    if (counts.notes > 0) items.push(`${counts.notes} notes`);
    
    return items.slice(0, 2).join(', ') + (items.length > 2 ? '...' : '');
  };

  if (!token) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
        <p className="text-gray-500">Please login to view your session history</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center space-x-2 mb-4">
          <FiClock className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Session History</h3>
        </div>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center space-x-2 mb-4">
          <FiClock className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Session History</h3>
        </div>
        <p className="text-red-600">{error}</p>
        <button 
          onClick={fetchSessions}
          className="mt-2 text-blue-600 hover:text-blue-800"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <FiClock className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Session History</h3>
        </div>
        <span className="text-sm text-gray-500">{sessions.length} sessions</span>
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-8">
          <FiFileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No sessions yet</p>
          <p className="text-sm text-gray-400">Upload some files to get started!</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              className="border rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
              onClick={() => onSessionSelect?.(session.session_id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {session.session_name}
                    </h4>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(session.status)}`}>
                      {session.status}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500 mb-2">
                    <span className="flex items-center space-x-1">
                      <FiClock className="h-3 w-3" />
                      <span>{formatDate(session.created_at)}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <FiFileText className="h-3 w-3" />
                      <span>{session.files_uploaded?.length || 0} files</span>
                    </span>
                  </div>
                  
                  <p className="text-xs text-gray-600">
                    {getContentSummary(session)}
                  </p>
                </div>
                
                <FiChevronRight className="h-4 w-4 text-gray-400 ml-2 flex-shrink-0" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SessionHistory;
