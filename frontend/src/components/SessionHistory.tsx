"use client";
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { FiClock, FiFileText, FiChevronRight, FiRefreshCw, FiFolder, FiLoader } from 'react-icons/fi';

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

  const getStatusStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-emerald-700 bg-emerald-100/80 border-emerald-200';
      case 'processing':
        return 'text-pink-700 bg-pink-100/80 border-pink-200 animate-pulse';
      case 'failed':
        return 'text-rose-700 bg-rose-100/80 border-rose-200';
      default:
        return 'text-gray-600 bg-gray-100/80 border-gray-200';
    }
  };

  const getContentSummary = (session: Session) => {
    if (!session.content_counts) return 'Processing...';

    const counts = session.content_counts;
    const total = counts.questions + counts.mock_tests + counts.mnemonics + counts.cheat_sheets + counts.notes;

    if (total === 0) return 'No content generated';

    const items = [];
    if (counts.questions > 0) items.push(`${counts.questions} Q`);
    if (counts.mock_tests > 0) items.push(`${counts.mock_tests} Tests`);
    if (counts.mnemonics > 0) items.push(`${counts.mnemonics} Mnemonics`);

    return items.slice(0, 3).join(' • ');
  };

  if (!token) {
    return (
      <div className="card text-center py-12">
        <div className="text-5xl mb-4 animate-float">🔐</div>
        <p className="text-gray-500">Please login to view your session history</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-xl flex items-center justify-center">
            <FiClock className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-bold text-gray-900">Session History</h3>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-20 bg-gradient-to-r from-pink-100/50 to-fuchsia-100/50 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-xl flex items-center justify-center">
            <FiClock className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-bold text-gray-900">Session History</h3>
        </div>
        <div className="text-center py-8">
          <div className="text-4xl mb-3">😔</div>
          <p className="text-rose-600 font-medium mb-4">{error}</p>
          <button
            onClick={fetchSessions}
            className="btn-secondary inline-flex items-center space-x-2"
          >
            <FiRefreshCw className="w-4 h-4" />
            <span>Try again</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-xl flex items-center justify-center shadow-lg shadow-pink-200/50">
            <FiClock className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-bold text-gray-900">Session History</h3>
        </div>
        <span className="text-sm text-pink-600 font-medium bg-pink-100/50 px-3 py-1 rounded-full">
          {sessions.length} sessions
        </span>
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-5xl mb-4 animate-float">📂</div>
          <p className="text-gray-600 font-medium">No sessions yet</p>
          <p className="text-sm text-pink-400 mt-1">Upload some files to get started!</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
          {sessions.map((session, index) => (
            <div
              key={session.session_id}
              className="bg-white/70 backdrop-blur-sm border border-pink-100 rounded-xl p-4 hover:bg-white hover:shadow-lg hover:shadow-pink-100/30 transition-all duration-300 cursor-pointer group animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
              onClick={() => onSessionSelect?.(session.session_id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="text-sm font-semibold text-gray-900 truncate group-hover:text-pink-600 transition-colors">
                      {session.session_name}
                    </h4>
                    <span className={`px-2 py-0.5 text-xs rounded-full font-medium border ${getStatusStyle(session.status)}`}>
                      {session.status}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                    <span className="flex items-center gap-1">
                      <FiClock className="h-3 w-3 text-pink-400" />
                      <span>{formatDate(session.created_at)}</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <FiFileText className="h-3 w-3 text-fuchsia-400" />
                      <span>{session.files_uploaded?.length || 0} files</span>
                    </span>
                  </div>

                  <p className="text-xs text-pink-600 font-medium">
                    {getContentSummary(session)}
                  </p>
                </div>

                <div className="w-8 h-8 bg-pink-100 rounded-lg flex items-center justify-center group-hover:bg-gradient-to-r group-hover:from-pink-500 group-hover:to-fuchsia-500 transition-all duration-300 ml-3 flex-shrink-0">
                  <FiChevronRight className="h-4 w-4 text-pink-500 group-hover:text-white transition-colors" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SessionHistory;
