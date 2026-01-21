'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Question, MockTest, Mnemonic, CheatSheet, Note, DifficultyLevel } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';
import InteractiveQuestion from './InteractiveQuestion';
import MockTestDialog from './MockTestDialog';
import MockTestInterface from './MockTestInterface';
import MockTestResults from './MockTestResults';

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

  // Mock test states
  const [showTestDialog, setShowTestDialog] = useState(false);
  const [selectedTest, setSelectedTest] = useState<MockTest | null>(null);
  const [testQuestions, setTestQuestions] = useState<Question[]>([]);
  const [showTestInterface, setShowTestInterface] = useState(false);
  const [showTestResults, setShowTestResults] = useState(false);
  const [testResults, setTestResults] = useState<any[]>([]);
  const [testTimeSpent, setTestTimeSpent] = useState(0);

  useEffect(() => {
    loadContent(activeTab);
  }, [activeTab, sessionId]);

  const loadContent = async (contentType: ContentType) => {
    setLoading(true);
    try {
      switch (contentType) {
        case 'questions':
          const questionsResponse = await StudyBuddyAPI.getSessionQuestions(sessionId);
          // API returns array directly or object with questions property
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
      // Reset to empty array on error
      switch (contentType) {
        case 'questions':
          setQuestions([]);
          break;
        case 'mock-tests':
          setMockTests([]);
          break;
        case 'mnemonics':
          setMnemonics([]);
          break;
        case 'cheat-sheets':
          setCheatSheets([]);
          break;
        case 'notes':
          setNotes([]);
          break;
      }
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyClass = (difficulty: DifficultyLevel) => {
    switch (difficulty) {
      case DifficultyLevel.EASY:
        return 'difficulty-easy';
      case DifficultyLevel.MEDIUM:
        return 'difficulty-medium';
      case DifficultyLevel.HARD:
        return 'difficulty-hard';
      default:
        return 'difficulty-medium';
    }
  };

  // Mock test handlers
  const handleStartTest = async (test: MockTest) => {
    try {
      setSelectedTest(test);
      setShowTestDialog(true);
    } catch (error) {
      console.error('Failed to prepare test:', error);
    }
  };

  const handleTestDialogStart = async () => {
    if (!selectedTest) return;
    
    try {
      setLoading(true);
      const response = await StudyBuddyAPI.getMockTest(selectedTest.test_id);
      setTestQuestions(response.questions);
      setShowTestDialog(false);
      setShowTestInterface(true);
    } catch (error) {
      console.error('Failed to load test questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestSubmit = (answers: Record<string, string>, timeSpent: number) => {
    if (!selectedTest || !testQuestions.length) return;

    const results = testQuestions.map(question => {
      const userAnswer = answers[question.question_id];
      const options = question.options || [];
      const isStringArray = options.length > 0 && typeof options[0] === 'string';
      
      let correctAnswer, isCorrect;
      if (isStringArray) {
        const correctIndex = question.correct_answer || 0;
        correctAnswer = correctIndex.toString();
        isCorrect = userAnswer === correctIndex.toString();
      } else {
        const correctOption = options.find(opt => opt.is_correct);
        correctAnswer = correctOption?.option_id || '';
        isCorrect = userAnswer === correctOption?.option_id;
      }

      return {
        questionId: question.question_id,
        userAnswer: userAnswer || '',
        correctAnswer,
        isCorrect,
        question
      };
    });

    setTestResults(results);
    setTestTimeSpent(timeSpent);
    setShowTestInterface(false);
    setShowTestResults(true);
  };

  const handleTestExit = () => {
    setShowTestInterface(false);
    setSelectedTest(null);
    setTestQuestions([]);
  };

  const handleResultsClose = () => {
    setShowTestResults(false);
    setSelectedTest(null);
    setTestQuestions([]);
    setTestResults([]);
  };

  const handleRetakeTest = () => {
    setShowTestResults(false);
    setShowTestDialog(true);
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
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as ContentType)}
              className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="flex items-center space-x-2">
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.count > 0 && (
                  <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="min-h-96">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">Loading...</span>
          </div>
        ) : (
          <div>
            {/* Questions Tab */}
            {activeTab === 'questions' && (
              <div className="space-y-6">
                {questions.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    No questions generated yet.
                  </div>
                ) : (
                  questions.map((question, index) => {
                    const questionId = (question as any).question_id || (question as any).id || index;
                    
                    return (
                      <InteractiveQuestion
                        key={questionId}
                        question={question}
                        index={index}
                      />
                    );
                  })
                )}
              </div>
            )}

            {/* Mock Tests Tab */}
            {activeTab === 'mock-tests' && (
              <div className="space-y-4">
                {mockTests.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    No mock tests generated yet.
                  </div>
                ) : (
                  mockTests.map((test) => (
                    <div key={test.test_id} className="card">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            {test.test_name}
                          </h3>
                          <div className="flex space-x-4 text-sm text-gray-600">
                            <span>📝 {test.total_questions} questions</span>
                            <span>⏱️ {test.duration_minutes} minutes</span>
                          </div>
                        </div>
                        <button 
                          className="btn-primary"
                          onClick={() => handleStartTest(test)}
                          disabled={loading}
                        >
                          {loading ? 'Loading...' : 'Start Test'}
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
                  <div className="text-center py-12 text-gray-500">
                    No mnemonics generated yet.
                  </div>
                ) : (
                  mnemonics.map((mnemonic) => (
                    <div key={mnemonic.mnemonic_id} className="card">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {mnemonic.topic}
                      </h3>
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-3">
                        <p className="text-yellow-800 font-medium text-lg">
                          "{mnemonic.mnemonic_text}"
                        </p>
                      </div>
                      <p className="text-gray-700 mb-3">{mnemonic.explanation}</p>
                      {mnemonic.key_terms.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {mnemonic.key_terms.map((term, index) => (
                            <span
                              key={index}
                              className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm"
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
                  <div className="text-center py-12 text-gray-500">
                    No cheat sheets generated yet.
                  </div>
                ) : (
                  cheatSheets.map((sheet) => (
                    <div key={sheet.sheet_id} className="card">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        {sheet.title}
                      </h3>
                      
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Key Points</h4>
                          <ul className="space-y-1">
                            {sheet.key_points.map((point, index) => (
                              <li key={index} className="text-sm text-gray-700 flex items-start">
                                <span className="text-blue-600 mr-2">•</span>
                                {point}
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">High-Yield Facts</h4>
                          <ul className="space-y-1">
                            {sheet.high_yield_facts.map((fact, index) => (
                              <li key={index} className="text-sm text-gray-700 flex items-start">
                                <span className="text-red-600 mr-2">★</span>
                                {fact}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {sheet.quick_references && Object.keys(sheet.quick_references).length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <h4 className="font-medium text-gray-900 mb-2">Quick References</h4>
                          <div className="grid gap-2">
                            {Object.entries(sheet.quick_references).map(([term, definition]) => (
                              <div key={term} className="bg-gray-50 p-2 rounded">
                                <span className="font-medium text-gray-900">{term}:</span>{' '}
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
                  <div className="text-center py-12 text-gray-500">
                    No notes generated yet.
                  </div>
                ) : (
                  notes.map((note) => (
                    <div key={note.note_id} className="card">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        {note.title}
                      </h3>
                      
                      <div className="prose prose-blue max-w-none mb-4">
                        <ReactMarkdown
                          components={{
                            h1: ({children}) => <h1 className="text-2xl font-bold text-gray-900 mb-4">{children}</h1>,
                            h2: ({children}) => <h2 className="text-xl font-semibold text-gray-900 mb-3 mt-6">{children}</h2>,
                            h3: ({children}) => <h3 className="text-lg font-medium text-gray-900 mb-2 mt-4">{children}</h3>,
                            p: ({children}) => <p className="text-gray-700 mb-3 leading-relaxed">{children}</p>,
                            ul: ({children}) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                            ol: ({children}) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                            li: ({children}) => <li className="text-gray-700 ml-4">{children}</li>,
                            strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                            em: ({children}) => <em className="italic text-gray-800">{children}</em>,
                            code: ({children}) => <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-gray-800">{children}</code>,
                            blockquote: ({children}) => <blockquote className="border-l-4 border-blue-200 pl-4 italic text-gray-600 my-4">{children}</blockquote>,
                          }}
                        >
                          {note.content}
                        </ReactMarkdown>
                      </div>

                      {note.summary_points.length > 0 && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <h4 className="font-medium text-blue-900 mb-2">Summary Points</h4>
                          <ul className="space-y-1">
                            {note.summary_points.map((point, index) => (
                              <li key={index} className="text-sm text-blue-800 flex items-start">
                                <span className="text-blue-600 mr-2">•</span>
                                {point}
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

      {/* Mock Test Modals */}
      {showTestDialog && selectedTest && (
        <MockTestDialog
          testName={selectedTest.test_name}
          totalQuestions={selectedTest.total_questions}
          duration={selectedTest.duration_minutes}
          onStart={handleTestDialogStart}
          onCancel={() => setShowTestDialog(false)}
        />
      )}

      {showTestInterface && selectedTest && testQuestions.length > 0 && (
        <MockTestInterface
          questions={testQuestions}
          testName={selectedTest.test_name}
          duration={selectedTest.duration_minutes}
          onSubmit={handleTestSubmit}
          onExit={handleTestExit}
        />
      )}

      {showTestResults && selectedTest && testResults.length > 0 && (
        <MockTestResults
          testName={selectedTest.test_name}
          results={testResults}
          timeSpent={testTimeSpent}
          totalTime={selectedTest.duration_minutes * 60}
          onClose={handleResultsClose}
          onRetakeTest={handleRetakeTest}
        />
      )}
    </div>
  );
}
