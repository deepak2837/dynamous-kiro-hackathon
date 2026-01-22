'use client';

import { useState, useEffect } from 'react';
import { Question, MockTest, Mnemonic, CheatSheet, Note, DifficultyLevel } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';
import InteractiveQuestion from './InteractiveQuestion';
import MockTestDialog from './MockTestDialog';
import MockTestInterface from './MockTestInterface';
import MockTestResults from './MockTestResults';
import { FiLoader, FiPlay, FiClock, FiFileText, FiStar } from 'react-icons/fi';

interface ResultsViewerProps {
  sessionId: string;
}

type ContentType = 'questions' | 'mock-tests' | 'mnemonics' | 'cheat-sheets' | 'notes';

export default function ResultsViewer({ sessionId }: ResultsViewerProps) {
  const [activeTab, setActiveTab] = useState<ContentType>('questions');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [mockTests, setMockTests] = useState<MockTest[]>([]);
  const [mnemonics, setMnemonics] = useState<Mnemonic[]>([]);
  const [cheatSheets, setCheatSheets] = useState<CheatSheet[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(false);

  // Mock Test State
  const [selectedTest, setSelectedTest] = useState<MockTest | null>(null);
  const [showTestDialog, setShowTestDialog] = useState(false);
  const [testMode, setTestMode] = useState(false);
  const [testQuestions, setTestQuestions] = useState<Question[]>([]);
  const [testResults, setTestResults] = useState<{
    results: Array<{ questionId: string; userAnswer: string; correctAnswer: string; isCorrect: boolean; question: Question }>;
    timeSpent: number;
    totalTime: number;
  } | null>(null);

  useEffect(() => {
    loadContent(activeTab);
  }, [activeTab, sessionId]);

  const loadContent = async (contentType: ContentType) => {
    setLoading(true);
    try {
      switch (contentType) {
        case 'questions':
          const questionsResponse = await StudyBuddyAPI.getSessionQuestions(sessionId);
          const questionsData = Array.isArray(questionsResponse)
            ? questionsResponse
            : questionsResponse?.questions || questionsResponse || [];
          setQuestions(questionsData);
          break;
        case 'mock-tests':
          const testsResponse = await StudyBuddyAPI.getSessionMockTests(sessionId);
          const testsData = Array.isArray(testsResponse)
            ? testsResponse
            : testsResponse?.mock_tests || testsResponse || [];
          setMockTests(testsData);
          break;
        case 'mnemonics':
          const mnemonicsResponse = await StudyBuddyAPI.getSessionMnemonics(sessionId);
          const mnemonicsData = Array.isArray(mnemonicsResponse)
            ? mnemonicsResponse
            : mnemonicsResponse?.mnemonics || mnemonicsResponse || [];
          setMnemonics(mnemonicsData);
          break;
        case 'cheat-sheets':
          const sheetsResponse = await StudyBuddyAPI.getSessionCheatSheets(sessionId);
          const sheetsData = Array.isArray(sheetsResponse)
            ? sheetsResponse
            : sheetsResponse?.cheat_sheets || sheetsResponse || [];
          setCheatSheets(sheetsData);
          break;
        case 'notes':
          const notesResponse = await StudyBuddyAPI.getSessionNotes(sessionId);
          const notesData = Array.isArray(notesResponse)
            ? notesResponse
            : notesResponse?.notes || notesResponse || [];
          setNotes(notesData);
          break;
      }
    } catch (error) {
      console.error(`Failed to load ${contentType}:`, error);
      switch (contentType) {
        case 'questions': setQuestions([]); break;
        case 'mock-tests': setMockTests([]); break;
        case 'mnemonics': setMnemonics([]); break;
        case 'cheat-sheets': setCheatSheets([]); break;
        case 'notes': setNotes([]); break;
      }
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyClass = (difficulty: DifficultyLevel) => {
    switch (difficulty) {
      case DifficultyLevel.EASY: return 'difficulty-easy';
      case DifficultyLevel.MEDIUM: return 'difficulty-medium';
      case DifficultyLevel.HARD: return 'difficulty-hard';
      default: return 'difficulty-medium';
    }
  };

  // Mock Test Handlers
  const handleStartTest = async (test: MockTest) => {
    setSelectedTest(test);
    setShowTestDialog(true);
  };

  const handleConfirmStartTest = async () => {
    if (!selectedTest) return;

    setShowTestDialog(false);
    setLoading(true);

    try {
      const questionsData = await StudyBuddyAPI.getSessionQuestions(sessionId, 0, 100);
      const questionsArray = Array.isArray(questionsData) ? questionsData : (questionsData as any)?.questions || [];

      let testQs = questionsArray;
      if (selectedTest.questions && selectedTest.questions.length > 0) {
        const testQuestionIds = new Set(selectedTest.questions);
        testQs = questionsArray.filter((q: Question) =>
          testQuestionIds.has((q as any).question_id || (q as any).id)
        );
        if (testQs.length === 0) testQs = questionsArray;
      }

      setTestQuestions(testQs);
      setTestMode(true);
    } catch (error) {
      console.error('Failed to load test questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestSubmit = (answers: Record<string, string>, timeSpent: number) => {
    if (!selectedTest) return;

    const results = testQuestions.map((q) => {
      const questionId = (q as any).question_id || (q as any).id;
      const userAnswer = answers[questionId] || '';
      const correctAnswer = String((q as any).correct_answer || 'A');
      const isCorrect = userAnswer === correctAnswer;

      return { questionId, userAnswer, correctAnswer, isCorrect, question: q };
    });

    setTestResults({
      results,
      timeSpent,
      totalTime: selectedTest.duration_minutes * 60
    });
    setTestMode(false);
  };

  const handleTestExit = () => {
    setTestMode(false);
    setSelectedTest(null);
    setTestQuestions([]);
    setTestResults(null);
  };

  const handleRetakeTest = () => {
    if (selectedTest) {
      setTestResults(null);
      handleConfirmStartTest();
    }
  };

  const handleCloseResults = () => {
    setTestResults(null);
    setSelectedTest(null);
  };

  const tabs = [
    { id: 'questions', label: 'Questions', icon: '❓', count: questions?.length || 0 },
    { id: 'mock-tests', label: 'Mock Tests', icon: '📊', count: mockTests?.length || 0 },
    { id: 'mnemonics', label: 'Mnemonics', icon: '🧠', count: mnemonics?.length || 0 },
    { id: 'cheat-sheets', label: 'Cheat Sheets', icon: '📋', count: cheatSheets?.length || 0 },
    { id: 'notes', label: 'Notes', icon: '📖', count: notes?.length || 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="relative">
        <div className="bg-white/70 backdrop-blur-xl rounded-2xl p-2 border border-pink-100 shadow-lg shadow-pink-100/20">
          <nav className="flex space-x-1 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as ContentType)}
                className={`relative py-3 px-4 font-medium text-sm whitespace-nowrap rounded-xl transition-all duration-300 flex items-center space-x-2 ${activeTab === tab.id
                    ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg shadow-pink-300/50'
                    : 'text-gray-600 hover:text-pink-600 hover:bg-pink-50'
                  }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.count > 0 && (
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${activeTab === tab.id
                      ? 'bg-white/30 text-white'
                      : 'bg-pink-100 text-pink-600'
                    }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="min-h-96">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <div className="relative w-16 h-16 mx-auto mb-4">
                <div className="absolute inset-0 bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-full animate-ping opacity-30" />
                <div className="relative w-16 h-16 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-full flex items-center justify-center">
                  <FiLoader className="w-8 h-8 text-white animate-spin" />
                </div>
              </div>
              <p className="text-pink-600 font-medium">Loading content...</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Questions Tab */}
            {activeTab === 'questions' && (
              <div className="space-y-4">
                {questions.length === 0 ? (
                  <EmptyState icon="❓" message="No questions generated yet." />
                ) : (
                  questions.map((question, index) => (
                    <div key={(question as any).question_id || (question as any).id || index} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
                      <InteractiveQuestion question={question} index={index} />
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Mock Tests Tab */}
            {activeTab === 'mock-tests' && (
              <div className="space-y-4">
                {mockTests.length === 0 ? (
                  <EmptyState icon="📊" message="No mock tests generated yet." />
                ) : (
                  mockTests.map((test, index) => (
                    <div
                      key={test.test_id}
                      className="card group animate-slide-up"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                        <div className="flex items-start space-x-4">
                          <div className="w-14 h-14 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-2xl flex items-center justify-center shadow-lg shadow-pink-200/50 group-hover:scale-110 transition-transform duration-300">
                            <span className="text-2xl">📝</span>
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-pink-600 transition-colors">
                              {test.test_name}
                            </h3>
                            <div className="flex flex-wrap gap-3 mt-2">
                              <span className="flex items-center text-sm text-gray-600 bg-pink-50 px-3 py-1 rounded-full">
                                <FiFileText className="w-4 h-4 mr-1 text-pink-500" />
                                {test.total_questions} questions
                              </span>
                              <span className="flex items-center text-sm text-gray-600 bg-fuchsia-50 px-3 py-1 rounded-full">
                                <FiClock className="w-4 h-4 mr-1 text-fuchsia-500" />
                                {test.duration_minutes} minutes
                              </span>
                            </div>
                          </div>
                        </div>
                        <button
                          className="btn-primary flex items-center space-x-2"
                          onClick={() => handleStartTest(test)}
                        >
                          <FiPlay className="w-4 h-4" />
                          <span>Start Test</span>
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Mnemonics Tab */}
            {activeTab === 'mnemonics' && (
              <div className="space-y-4">
                {mnemonics.length === 0 ? (
                  <EmptyState icon="🧠" message="No mnemonics generated yet." />
                ) : (
                  mnemonics.map((mnemonic, index) => (
                    <div
                      key={mnemonic.mnemonic_id}
                      className="card animate-slide-up"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <h3 className="text-lg font-bold text-gray-900 mb-3">
                        {mnemonic.topic}
                      </h3>
                      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border-2 border-amber-200 rounded-2xl p-5 mb-4">
                        <p className="text-amber-800 font-bold text-xl text-center">
                          "{mnemonic.mnemonic_text}"
                        </p>
                      </div>
                      <p className="text-gray-700 mb-4 leading-relaxed">{mnemonic.explanation}</p>
                      {mnemonic.key_terms.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {mnemonic.key_terms.map((term, idx) => (
                            <span
                              key={idx}
                              className="bg-pink-100 text-pink-700 px-3 py-1.5 rounded-full text-sm font-medium"
                            >
                              {term}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Cheat Sheets Tab */}
            {activeTab === 'cheat-sheets' && (
              <div className="space-y-4">
                {cheatSheets.length === 0 ? (
                  <EmptyState icon="📋" message="No cheat sheets generated yet." />
                ) : (
                  cheatSheets.map((sheet, index) => (
                    <div
                      key={sheet.sheet_id}
                      className="card animate-slide-up"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                        <span className="text-2xl mr-3">📋</span>
                        {sheet.title}
                      </h3>

                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="bg-pink-50/50 rounded-2xl p-5">
                          <h4 className="font-bold text-pink-700 mb-4 flex items-center">
                            <span className="w-8 h-8 bg-pink-100 rounded-lg flex items-center justify-center mr-2">📌</span>
                            Key Points
                          </h4>
                          <ul className="space-y-2">
                            {sheet.key_points.map((point, idx) => (
                              <li key={idx} className="text-sm text-gray-700 flex items-start">
                                <span className="text-pink-500 mr-2 mt-1">•</span>
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-rose-50/50 rounded-2xl p-5">
                          <h4 className="font-bold text-rose-700 mb-4 flex items-center">
                            <span className="w-8 h-8 bg-rose-100 rounded-lg flex items-center justify-center mr-2">⭐</span>
                            High-Yield Facts
                          </h4>
                          <ul className="space-y-2">
                            {sheet.high_yield_facts.map((fact, idx) => (
                              <li key={idx} className="text-sm text-gray-700 flex items-start">
                                <FiStar className="text-rose-500 mr-2 mt-1 flex-shrink-0 w-4 h-4" />
                                <span>{fact}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {sheet.quick_references && Object.keys(sheet.quick_references).length > 0 && (
                        <div className="mt-6 pt-6 border-t border-pink-100">
                          <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                            <span className="text-xl mr-2">📚</span>
                            Quick References
                          </h4>
                          <div className="grid gap-2">
                            {Object.entries(sheet.quick_references).map(([term, definition]) => (
                              <div key={term} className="bg-white/70 p-3 rounded-xl border border-pink-100">
                                <span className="font-semibold text-pink-700">{term}:</span>{' '}
                                <span className="text-gray-700">{definition}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Notes Tab */}
            {activeTab === 'notes' && (
              <div className="space-y-4">
                {notes.length === 0 ? (
                  <EmptyState icon="📖" message="No notes generated yet." />
                ) : (
                  notes.map((note, index) => (
                    <div
                      key={note.note_id}
                      className="card animate-slide-up"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                        <span className="text-2xl mr-3">📖</span>
                        {note.title}
                      </h3>

                      <div className="prose max-w-none mb-6">
                        <div
                          className="text-gray-700 whitespace-pre-wrap leading-relaxed"
                          dangerouslySetInnerHTML={{
                            __html: note.content
                              .replace(/\*\*(.*?)\*\*/g, '<strong class="text-pink-700">$1</strong>')
                              .replace(/\*(.*?)\*/g, '<em>$1</em>')
                              .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold mt-6 mb-3 text-gray-900">$1</h3>')
                              .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-gray-900">$1</h2>')
                              .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-6 mb-3 text-gray-900">$1</h1>')
                          }}
                        />
                      </div>

                      {note.summary_points.length > 0 && (
                        <div className="bg-gradient-to-r from-pink-50 to-fuchsia-50 border-2 border-pink-200 rounded-2xl p-5">
                          <h4 className="font-bold text-pink-700 mb-4 flex items-center">
                            <span className="text-xl mr-2">✨</span>
                            Summary Points
                          </h4>
                          <ul className="space-y-2">
                            {note.summary_points.map((point, idx) => (
                              <li key={idx} className="text-sm text-pink-800 flex items-start">
                                <span className="text-pink-500 mr-2 mt-1">•</span>
                                <span>{point}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Mock Test Dialog */}
      {showTestDialog && selectedTest && (
        <MockTestDialog
          testName={selectedTest.test_name}
          totalQuestions={selectedTest.total_questions}
          duration={selectedTest.duration_minutes}
          onStart={handleConfirmStartTest}
          onCancel={() => setShowTestDialog(false)}
        />
      )}

      {/* Mock Test Interface (Fullscreen) */}
      {testMode && selectedTest && testQuestions.length > 0 && (
        <MockTestInterface
          questions={testQuestions}
          testName={selectedTest.test_name}
          duration={selectedTest.duration_minutes}
          onSubmit={handleTestSubmit}
          onExit={handleTestExit}
        />
      )}

      {/* Mock Test Results */}
      {testResults && selectedTest && (
        <MockTestResults
          testName={selectedTest.test_name}
          results={testResults.results}
          timeSpent={testResults.timeSpent}
          totalTime={testResults.totalTime}
          onClose={handleCloseResults}
          onRetakeTest={handleRetakeTest}
        />
      )}
    </div>
  );
}

function EmptyState({ icon, message }: { icon: string; message: string }) {
  return (
    <div className="card text-center py-16">
      <div className="text-6xl mb-4 animate-float">{icon}</div>
      <p className="text-gray-500 text-lg">{message}</p>
    </div>
  );
}
