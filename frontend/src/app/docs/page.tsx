"use client";
import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { FiDownload, FiExternalLink, FiBook, FiCode, FiDatabase, FiArrowLeft } from 'react-icons/fi';

const DocsPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState<'overview' | 'api' | 'database'>('overview');
  const [apiContent, setApiContent] = useState<string>('');

  useEffect(() => {
    if (activeSection === 'api') {
      fetch('/API_DOCUMENTATION.md')
        .then(response => response.text())
        .then(content => setApiContent(content))
        .catch(error => console.error('Error loading API docs:', error));
    }
  }, [activeSection]);

  const downloadApiDocs = () => {
    const link = document.createElement('a');
    link.href = '/API_DOCUMENTATION.md';
    link.download = 'StudyBuddy_API_Documentation.md';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (activeSection === 'api') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-fuchsia-50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <button
            onClick={() => setActiveSection('overview')}
            className="flex items-center text-pink-600 hover:text-pink-700 mb-6 transition-colors"
          >
            <FiArrowLeft className="mr-2" /> Back to Overview
          </button>
          
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-pink-100 shadow-lg">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold gradient-text">API Documentation</h1>
              <button onClick={downloadApiDocs} className="btn-primary text-sm">
                <FiDownload className="mr-2 w-4 h-4" /> Download
              </button>
            </div>
            
            <div className="prose prose-lg max-w-none markdown-container">
              <ReactMarkdown 
                components={{
                  code: ({node, className, children, ...props}: any) => {
                    const inline = !className?.includes('language-');
                    return inline ? (
                      <code className="bg-pink-100 text-pink-800 px-1 py-0.5 rounded text-sm" {...props}>
                        {children}
                      </code>
                    ) : (
                      <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-auto text-sm">
                        <code {...props}>{children}</code>
                      </pre>
                    );
                  },
                  h1: ({children}) => <h1 className="text-3xl font-bold text-gray-900 mb-6 border-b border-gray-200 pb-2">{children}</h1>,
                  h2: ({children}) => <h2 className="text-2xl font-semibold text-gray-800 mb-4 mt-8">{children}</h2>,
                  h3: ({children}) => <h3 className="text-xl font-semibold text-gray-700 mb-3 mt-6">{children}</h3>,
                  table: ({children}) => <div className="overflow-x-auto"><table className="min-w-full border border-gray-200 rounded-lg">{children}</table></div>,
                  th: ({children}) => <th className="bg-gray-50 px-4 py-2 text-left font-semibold text-gray-900 border-b">{children}</th>,
                  td: ({children}) => <td className="px-4 py-2 border-b border-gray-100">{children}</td>,
                  blockquote: ({children}) => <blockquote className="border-l-4 border-pink-300 pl-4 italic text-gray-600">{children}</blockquote>,
                }}
              >
                {apiContent || 'Loading API documentation...'}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (activeSection === 'database') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-fuchsia-50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <button
            onClick={() => setActiveSection('overview')}
            className="flex items-center text-pink-600 hover:text-pink-700 mb-6 transition-colors"
          >
            <FiArrowLeft className="mr-2" /> Back to Overview
          </button>
          
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-pink-100 shadow-lg">
            <h1 className="text-3xl font-bold gradient-text mb-8">Database Schema</h1>
            
            {/* Collections Overview */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-blue-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-4">MongoDB Collections</h3>
                <ul className="space-y-2 text-blue-700">
                  <li>• <code>study_sessions</code> - User study sessions</li>
                  <li>• <code>questions</code> - Generated questions</li>
                  <li>• <code>flashcards</code> - AI-generated flashcards</li>
                  <li>• <code>study_plans</code> - Personalized study plans</li>
                  <li>• <code>study_progress</code> - Progress tracking</li>
                  <li>• <code>mock_tests</code> - Practice tests</li>
                  <li>• <code>mnemonics</code> - Memory aids</li>
                  <li>• <code>cheat_sheets</code> - Quick references</li>
                  <li>• <code>notes</code> - Compiled study notes</li>
                </ul>
              </div>
              
              <div className="bg-green-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-green-900 mb-4">Key Features</h3>
                <ul className="space-y-2 text-green-700">
                  <li>• User-specific data isolation</li>
                  <li>• Optimized indexing for queries</li>
                  <li>• Spaced repetition tracking</li>
                  <li>• Progress analytics</li>
                  <li>• Session-based organization</li>
                </ul>
              </div>
            </div>

            {/* Detailed Schemas */}
            <div className="space-y-8">
              {/* Study Sessions */}
              <div className="border border-gray-200 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">study_sessions</h3>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
{`{
  _id: ObjectId,
  session_id: String (UUID),
  user_id: String,
  session_name: String,
  created_at: ISODate,
  files_uploaded: [{
    filename: String,
    file_type: String,
    file_size: Number,
    processing_mode: String
  }],
  processing_status: String, // "pending" | "processing" | "completed" | "failed"
  progress: Number, // 0-100
  outputs_generated: {
    questions: Boolean,
    mock_tests: Boolean,
    mnemonics: Boolean,
    cheat_sheets: Boolean,
    notes: Boolean,
    flashcards: Boolean
  }
}`}
                </pre>
              </div>

              {/* Flashcards */}
              <div className="border border-gray-200 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">flashcards</h3>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
{`{
  _id: ObjectId,
  id: String (UUID),
  session_id: String,
  user_id: String,
  question: String,
  answer: String,
  difficulty: String, // "easy" | "medium" | "hard"
  subject: String,
  tags: [String],
  next_review_date: ISODate,
  review_count: Number,
  success_rate: Number,
  created_at: ISODate,
  updated_at: ISODate
}`}
                </pre>
              </div>

              {/* Study Plans */}
              <div className="border border-gray-200 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">study_plans</h3>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
{`{
  _id: String, // Same as plan_id
  plan_id: String (UUID),
  session_id: String,
  user_id: String,
  plan_name: String,
  config: {
    exam_date: ISODate,
    daily_study_hours: Number,
    weak_areas: [String]
  },
  daily_schedules: [{
    date: ISODate,
    total_study_time: Number,
    tasks: [{
      task_id: String (UUID),
      title: String,
      description: String,
      task_type: String, // "study_notes" | "review_questions" | "practice_flashcards"
      subject: String, // "anatomy" | "physiology" | "pathology" | etc.
      estimated_duration: Number,
      priority: Number,
      content_ids: [String],
      status: String // "pending" | "in_progress" | "completed"
    }],
    total_tasks: Number
  }],
  total_study_days: Number,
  total_study_hours: Number,
  subjects_covered: [String],
  created_at: ISODate
}`}
                </pre>
              </div>

              {/* Questions */}
              <div className="border border-gray-200 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">questions</h3>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
{`{
  _id: ObjectId,
  question_id: String (UUID),
  session_id: String,
  user_id: String,
  question_text: String,
  options: [{
    option_id: String,
    text: String,
    is_correct: Boolean
  }],
  explanation: String,
  difficulty: String, // "Easy" | "Medium" | "Hard"
  medical_subject: String,
  tags: [String],
  created_at: ISODate
}`}
                </pre>
              </div>

              {/* Other Collections */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="border border-gray-200 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">mock_tests</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
{`{
  _id: ObjectId,
  test_id: String (UUID),
  session_id: String,
  user_id: String,
  test_name: String,
  questions: [String], // Question IDs
  duration_minutes: Number,
  total_questions: Number,
  created_at: ISODate
}`}
                  </pre>
                </div>

                <div className="border border-gray-200 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">mnemonics</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
{`{
  _id: ObjectId,
  mnemonic_id: String (UUID),
  session_id: String,
  user_id: String,
  topic: String,
  mnemonic_text: String,
  explanation: String,
  key_terms: [String],
  created_at: ISODate
}`}
                  </pre>
                </div>
              </div>

              {/* Indexes */}
              <div className="border border-gray-200 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Database Indexes</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-gray-800 mb-2">Primary Indexes</h4>
                    <pre className="bg-gray-50 p-3 rounded text-sm">
{`// study_sessions
{ user_id: 1, created_at: -1 }
{ session_id: 1 } (unique)

// flashcards  
{ session_id: 1, user_id: 1 }
{ next_review_date: 1 }

// study_plans
{ user_id: 1, created_at: -1 }
{ plan_id: 1 } (unique)`}
                    </pre>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800 mb-2">Secondary Indexes</h4>
                    <pre className="bg-gray-50 p-3 rounded text-sm">
{`// questions
{ session_id: 1 }
{ medical_subject: 1 }

// All collections
{ user_id: 1 }
{ created_at: -1 }`}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-fuchsia-50">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-2xl mb-6">
            <FiBook className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold gradient-text mb-4">StudyBuddy Documentation</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Complete API documentation and integration guide for the StudyBuddy AI-powered study companion
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <FiDownload className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Download API Docs</h3>
            <p className="text-gray-600 text-sm mb-4">Get the complete API documentation as a markdown file</p>
            <button
              onClick={downloadApiDocs}
              className="btn-primary text-sm w-full"
            >
              Download Docs
            </button>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
              <FiCode className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">API Reference</h3>
            <p className="text-gray-600 text-sm mb-4">Browse all endpoints, request/response formats</p>
            <button
              onClick={() => setActiveSection('api')}
              className="btn-secondary text-sm w-full inline-flex items-center justify-center"
            >
              View API Docs <FiExternalLink className="ml-2 w-4 h-4" />
            </button>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <FiDatabase className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Database Schema</h3>
            <p className="text-gray-600 text-sm mb-4">MongoDB collections and data models</p>
            <button 
              onClick={() => setActiveSection('database')}
              className="btn-secondary text-sm w-full"
            >
              View Schema
            </button>
          </div>
        </div>

        {/* API Overview */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-pink-100 shadow-lg shadow-pink-100/50 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">API Overview</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Base Configuration</h3>
              <div className="bg-gray-50 rounded-xl p-4 font-mono text-sm">
                <div className="text-gray-600">Base URL:</div>
                <div className="text-blue-600 font-semibold">http://localhost:8000</div>
                <div className="text-gray-600 mt-2">API Prefix:</div>
                <div className="text-blue-600 font-semibold">/api/v1</div>
                <div className="text-gray-600 mt-2">Authentication:</div>
                <div className="text-blue-600 font-semibold">Bearer JWT Token</div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-pink-400 rounded-full mr-3"></div>
                  Flashcard Generator with Spaced Repetition
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-pink-400 rounded-full mr-3"></div>
                  AI-Powered Study Planner
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-pink-400 rounded-full mr-3"></div>
                  Export Functions (PDF, JSON)
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-pink-400 rounded-full mr-3"></div>
                  Multi-format File Processing
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-pink-400 rounded-full mr-3"></div>
                  Session Management
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Endpoint Categories */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Authentication</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /auth/register</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /auth/login</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /auth/send-otp</code></li>
            </ul>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">File Processing</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /upload/</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">GET /upload/status/&#123;id&#125;</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /text-input/</code></li>
            </ul>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Flashcards</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><code className="bg-gray-100 px-2 py-1 rounded">GET /flashcards/&#123;id&#125;</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /flashcards/&#123;id&#125;/review</code></li>
            </ul>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Study Planner</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /study-planner/generate-plan</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">GET /study-planner/plans</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">PUT /study-planner/tasks/&#123;id&#125;/status</code></li>
            </ul>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Export & Download</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><code className="bg-gray-100 px-2 py-1 rounded">GET /download/&#123;type&#125;/&#123;id&#125;</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">POST /download/session/&#123;id&#125;/export</code></li>
            </ul>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-pink-100 shadow-lg shadow-pink-100/50">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Content Retrieval</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><code className="bg-gray-100 px-2 py-1 rounded">GET /questions/&#123;id&#125;</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">GET /mock-tests/&#123;id&#125;</code></li>
              <li><code className="bg-gray-100 px-2 py-1 rounded">GET /notes/&#123;id&#125;</code></li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t border-pink-100">
          <p className="text-gray-600">
            Built for the Dynamous Kiro Hackathon 2026 • 
            <a href="mailto:support@studybuddy.com" className="text-pink-600 hover:text-pink-700 ml-1">
              Contact Support
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default DocsPage;
