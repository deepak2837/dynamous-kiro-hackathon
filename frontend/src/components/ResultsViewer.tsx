/**
 * Study Buddy Results Viewer Component
 * 
 * Comprehensive results display component for AI-generated medical study content.
 * Provides tabbed interface for viewing questions, mock tests, mnemonics, cheat sheets,
 * notes, flashcards, and study planner functionality.
 * 
 * Features:
 * - Tabbed content organization with visual indicators
 * - Interactive question viewer with difficulty filtering
 * - Mock test interface with timer and scoring
 * - Flashcard study mode with spaced repetition
 * - Study planner integration for personalized schedules
 * - Export functionality for offline study
 * - Real-time content loading and error handling
 * - Responsive design for mobile and desktop
 * 
 * @component
 * @param {ResultsViewerProps} props - Component props
 * @param {string} props.sessionId - Study session ID to load content for
 * @returns {JSX.Element} Tabbed results viewer interface
 * 
 * @example
 * ```tsx
 * <ResultsViewer sessionId="session-123" />
 * ```
 */

'use client';

import { useState, useEffect } from 'react';
import { Question, MockTest, Mnemonic, CheatSheet, Note, Flashcard, DifficultyLevel } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';
import InteractiveQuestion from './InteractiveQuestion';
import MockTestDialog from './MockTestDialog';
import MockTestInterface from './MockTestInterface';
import MockTestResults from './MockTestResults';
import ExportButton from './ExportButton';
import FlipFlashcard from './FlipFlashcard';
import StudyPlanForm from './StudyPlanForm';
import StudyPlannerViewer from './StudyPlannerViewer';
import { FiLoader, FiPlay, FiClock, FiFileText, FiStar, FiLayers } from 'react-icons/fi';

/**
 * Props for the ResultsViewer component
 */
interface ResultsViewerProps {
  /** Study session ID to load and display content for */
  sessionId: string;
}

/**
 * Available content types in the results viewer
 */
type ContentType = 'questions' | 'mock-tests' | 'mnemonics' | 'cheat-sheets' | 'notes' | 'flashcards' | 'study-planner';

export default function ResultsViewer({ sessionId }: ResultsViewerProps) {
  // Tab and content state
  const [activeTab, setActiveTab] = useState<ContentType>('questions');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [mockTests, setMockTests] = useState<MockTest[]>([]);
  const [mnemonics, setMnemonics] = useState<Mnemonic[]>([]);
  const [cheatSheets, setCheatSheets] = useState<CheatSheet[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(false);

  // Flashcard study state
  const [studyMode, setStudyMode] = useState(false);
  const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);

  // Study planner state
  const [showPlanForm, setShowPlanForm] = useState(false);
  const [planGenerating, setPlanGenerating] = useState(false);
  const [studyPlanExists, setStudyPlanExists] = useState(false);
  const [planSuccessMessage, setPlanSuccessMessage] = useState<string | null>(null);

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

  // Key to force StudyPlannerViewer to refresh
  const [planRefreshKey, setPlanRefreshKey] = useState(0);

  useEffect(() => {
    loadContent(activeTab);
  }, [activeTab, sessionId]);

  // Check if study plan exists
  useEffect(() => {
    const checkPlanExists = async () => {
      try {
        await StudyBuddyAPI.getStudyPlan(sessionId);
        setStudyPlanExists(true);
      } catch (error: any) {
        if (error?.response?.status === 404) {
          setStudyPlanExists(false);
        }
      }
    };
    checkPlanExists();
  }, [sessionId, planRefreshKey]);

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
        case 'flashcards':
          const flashcardsResponse = await StudyBuddyAPI.getSessionFlashcards(sessionId);
          const flashcardsData = Array.isArray(flashcardsResponse)
            ? flashcardsResponse
            : flashcardsResponse?.flashcards || flashcardsResponse || [];
          setFlashcards(flashcardsData);
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
        case 'flashcards': setFlashcards([]); break;
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

  // Flashcard study handlers
  const handleStartFlashcardStudy = () => {
    setStudyMode(true);
    setCurrentFlashcardIndex(0);
  };

  const handleNextFlashcard = () => {
    if (currentFlashcardIndex < flashcards.length - 1) {
      setCurrentFlashcardIndex(currentFlashcardIndex + 1);
    } else {
      // End of study session
      setStudyMode(false);
      setCurrentFlashcardIndex(0);
    }
  };

  const handlePreviousFlashcard = () => {
    if (currentFlashcardIndex > 0) {
      setCurrentFlashcardIndex(currentFlashcardIndex - 1);
    }
  };

  const handleExitFlashcardStudy = () => {
    setStudyMode(false);
    setCurrentFlashcardIndex(0);
  };

  // Study planner handlers
  const handleCreateStudyPlan = () => {
    setShowPlanForm(true);
  };

  const handlePlanFormSubmit = async (config: any) => {
    setPlanGenerating(true);
    setPlanSuccessMessage(null);
    try {
      await StudyBuddyAPI.generateStudyPlan(sessionId, config);
      setShowPlanForm(false);
      setStudyPlanExists(true);

      // Show success message
      setPlanSuccessMessage('Study plan created successfully! 🎉');

      // Force refresh the StudyPlannerViewer
      setPlanRefreshKey(prev => prev + 1);

      // Switch to study-planner tab
      setActiveTab('study-planner');

      // Auto-hide success message after 5 seconds
      setTimeout(() => setPlanSuccessMessage(null), 5000);
    } catch (error) {
      console.error('Failed to generate study plan:', error);
      alert('Failed to generate study plan. Please try again.');
    } finally {
      setPlanGenerating(false);
    }
  };

  const handlePlanFormCancel = () => {
    setShowPlanForm(false);
  };

  const tabs = [
    { id: 'questions', label: 'Questions', icon: '❓', count: questions?.length || 0 },
    { id: 'mock-tests', label: 'Mock Tests', icon: '📊', count: mockTests?.length || 0 },
    { id: 'mnemonics', label: 'Mnemonics', icon: '🧠', count: mnemonics?.length || 0 },
    { id: 'cheat-sheets', label: 'Cheat Sheets', icon: '📋', count: cheatSheets?.length || 0 },
    { id: 'notes', label: 'Notes', icon: '📖', count: notes?.length || 0 },
    { id: 'flashcards', label: 'Flashcards', icon: '🎴', count: flashcards?.length || 0 },
    { id: 'study-planner', label: 'Study Planner', icon: '📅', count: 0 },
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
                  <>
                    {/* Export Button */}
                    <div className="flex justify-end mb-4">
                      <ExportButton
                        sessionId={sessionId}
                        contentType="questions"
                        label="Export Questions PDF"
                      />
                    </div>

                    {questions.map((question, index) => (
                      <div key={(question as any).question_id || (question as any).id || index} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
                        <InteractiveQuestion question={question} index={index} />
                      </div>
                    ))}
                  </>
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
                  <>
                    {/* Export Button */}
                    <div className="flex justify-end mb-4">
                      <ExportButton
                        sessionId={sessionId}
                        contentType="mnemonics"
                        label="Export Mnemonics PDF"
                      />
                    </div>

                    {mnemonics.map((mnemonic, index) => (
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
                    ))}
                  </>
                )}
              </div>
            )}

            {/* Cheat Sheets Tab */}
            {activeTab === 'cheat-sheets' && (
              <div className="space-y-4">
                {cheatSheets.length === 0 ? (
                  <EmptyState icon="📋" message="No cheat sheets generated yet." />
                ) : (
                  <>
                    {/* Export Button */}
                    <div className="flex justify-end mb-4">
                      <ExportButton
                        sessionId={sessionId}
                        contentType="cheatsheet"
                        label="Export Cheat Sheets PDF"
                      />
                    </div>

                    {cheatSheets.map((sheet, index) => (
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
                    ))}
                  </>
                )}
              </div>
            )}

            {/* Notes Tab */}
            {activeTab === 'notes' && (
              <div className="space-y-4">
                {notes.length === 0 ? (
                  <EmptyState icon="📖" message="No notes generated yet." />
                ) : (
                  <>
                    {/* Export Button */}
                    <div className="flex justify-end mb-4">
                      <ExportButton
                        sessionId={sessionId}
                        contentType="notes"
                        label="Export Notes PDF"
                      />
                    </div>

                    {notes.map((note, index) => (
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
                    ))}
                  </>
                )}
              </div>
            )}

            {/* Flashcards Tab */}
            {activeTab === 'flashcards' && (
              <div className="space-y-4">
                {flashcards.length === 0 ? (
                  <EmptyState icon="🎴" message="No flashcards generated yet." />
                ) : (
                  <div className="text-center mb-6">
                    <p className="text-gray-600">
                      {flashcards.length} flashcards ready for spaced repetition study
                    </p>
                    <div className="mt-4">
                      <button
                        onClick={handleStartFlashcardStudy}
                        className="bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg transition-all duration-300"
                      >
                        Start Study Session
                      </button>
                    </div>
                  </div>
                )}

                {flashcards.length > 0 && (
                  <div className="grid gap-4">
                    {flashcards.slice(0, 5).map((flashcard, index) => (
                      <div
                        key={flashcard.flashcard_id}
                        className="card animate-slide-up"
                        style={{ animationDelay: `${index * 100}ms` }}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">🎴</span>
                            <div>
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${flashcard.category === 'anatomy' ? 'bg-blue-100 text-blue-700' :
                                flashcard.category === 'pharmacology' ? 'bg-green-100 text-green-700' :
                                  flashcard.category === 'pathology' ? 'bg-red-100 text-red-700' :
                                    flashcard.category === 'physiology' ? 'bg-purple-100 text-purple-700' :
                                      'bg-gray-100 text-gray-700'
                                }`}>
                                {flashcard.category}
                              </span>
                              {flashcard.medical_topic && (
                                <span className="ml-2 text-sm text-gray-500">
                                  {flashcard.medical_topic}
                                </span>
                              )}
                            </div>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyClass(flashcard.difficulty)}`}>
                            {flashcard.difficulty}
                          </span>
                        </div>

                        <div className="space-y-4">
                          <div>
                            <h4 className="font-medium text-gray-700 mb-2">Front:</h4>
                            <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                              {flashcard.front_text}
                            </p>
                          </div>

                          <div>
                            <h4 className="font-medium text-gray-700 mb-2">Back:</h4>
                            <p className="text-gray-900 bg-pink-50 p-3 rounded-lg">
                              {flashcard.back_text}
                            </p>
                          </div>

                          {flashcard.pronunciation && (
                            <div className="text-sm text-gray-600 bg-blue-50 p-2 rounded">
                              <strong>Pronunciation:</strong> {flashcard.pronunciation}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}

                    {flashcards.length > 5 && (
                      <div className="text-center py-4">
                        <p className="text-gray-500">
                          Showing 5 of {flashcards.length} flashcards. Start a study session to review all cards.
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Study Planner Tab */}
            {activeTab === 'study-planner' && (
              <div className="space-y-4">
                {/* Success Message */}
                {planSuccessMessage && (
                  <div className="bg-green-100 border border-green-300 text-green-800 px-6 py-4 rounded-xl flex items-center justify-between animate-slide-up">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">✅</span>
                      <span className="font-medium">{planSuccessMessage}</span>
                    </div>
                    <button
                      onClick={() => setPlanSuccessMessage(null)}
                      className="text-green-600 hover:text-green-800"
                    >
                      ✕
                    </button>
                  </div>
                )}

                <StudyPlannerViewer key={planRefreshKey} sessionId={sessionId} />

                {/* Create/Update Study Plan Button */}
                <div className="text-center py-8">
                  <button
                    onClick={handleCreateStudyPlan}
                    className="bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white px-8 py-4 rounded-xl font-medium hover:shadow-lg transition-all duration-300 flex items-center space-x-3 mx-auto"
                  >
                    <span className="text-2xl">{studyPlanExists ? '🔄' : '📅'}</span>
                    <span>{studyPlanExists ? 'Update Study Plan' : 'Create New Study Plan'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Study Plan Form Modal */}
      {showPlanForm && (
        <StudyPlanForm
          onSubmit={handlePlanFormSubmit}
          onCancel={handlePlanFormCancel}
          isLoading={planGenerating}
        />
      )}

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

      {/* Flashcard Study Interface */}
      {studyMode && flashcards.length > 0 && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Flashcard Study Session</h2>
                <p className="text-gray-600">
                  Card {currentFlashcardIndex + 1} of {flashcards.length}
                </p>
              </div>
              <button
                onClick={handleExitFlashcardStudy}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Flashcard Content */}
            <div className="p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center space-x-2 mb-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${flashcards[currentFlashcardIndex].category === 'anatomy' ? 'bg-blue-100 text-blue-700' :
                    flashcards[currentFlashcardIndex].category === 'pharmacology' ? 'bg-green-100 text-green-700' :
                      flashcards[currentFlashcardIndex].category === 'pathology' ? 'bg-red-100 text-red-700' :
                        flashcards[currentFlashcardIndex].category === 'physiology' ? 'bg-purple-100 text-purple-700' :
                          'bg-gray-100 text-gray-700'
                    }`}>
                    {flashcards[currentFlashcardIndex].category}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyClass(flashcards[currentFlashcardIndex].difficulty)}`}>
                    {flashcards[currentFlashcardIndex].difficulty}
                  </span>
                </div>
              </div>

              {/* Flip Flashcard */}
              <FlipFlashcard flashcard={flashcards[currentFlashcardIndex]} />

              {/* Navigation Buttons */}
              <div className="flex space-x-4 mb-6">
                <button
                  onClick={handlePreviousFlashcard}
                  disabled={currentFlashcardIndex === 0}
                  className="flex-1 bg-gray-500 text-white py-3 rounded-xl font-medium hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                >
                  Previous
                </button>
                <button
                  onClick={handleNextFlashcard}
                  className="flex-1 bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white py-3 rounded-xl font-medium hover:shadow-lg transition-all duration-300"
                >
                  {currentFlashcardIndex === flashcards.length - 1 ? 'Finish Study' : 'Next Card'}
                </button>
              </div>

              {/* Progress Bar */}
              <div className="mt-6">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{Math.round(((currentFlashcardIndex + 1) / flashcards.length) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-pink-500 to-fuchsia-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentFlashcardIndex + 1) / flashcards.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
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
