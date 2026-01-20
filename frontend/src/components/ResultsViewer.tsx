'use client';

import { useState, useEffect } from 'react';
import { Question, MockTest, Mnemonic, CheatSheet, Note, DifficultyLevel } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';

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

  useEffect(() => {
    loadContent(activeTab);
  }, [activeTab, sessionId]);

  const loadContent = async (contentType: ContentType) => {
    setLoading(true);
    try {
      switch (contentType) {
        case 'questions':
          const questionsResponse = await StudyBuddyAPI.getSessionQuestions(sessionId);
          setQuestions(questionsResponse.questions);
          break;
        case 'mock-tests':
          const testsResponse = await StudyBuddyAPI.getSessionMockTests(sessionId);
          setMockTests(testsResponse.mock_tests);
          break;
        case 'mnemonics':
          const mnemonicsResponse = await StudyBuddyAPI.getSessionMnemonics(sessionId);
          setMnemonics(mnemonicsResponse.mnemonics);
          break;
        case 'cheat-sheets':
          const sheetsResponse = await StudyBuddyAPI.getSessionCheatSheets(sessionId);
          setCheatSheets(sheetsResponse.cheat_sheets);
          break;
        case 'notes':
          const notesResponse = await StudyBuddyAPI.getSessionNotes(sessionId);
          setNotes(notesResponse.notes);
          break;
      }
    } catch (error) {
      console.error(`Failed to load ${contentType}:`, error);
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

  const tabs = [
    { id: 'questions', label: 'Questions', icon: '❓', count: questions.length },
    { id: 'mock-tests', label: 'Mock Tests', icon: '📊', count: mockTests.length },
    { id: 'mnemonics', label: 'Mnemonics', icon: '🧠', count: mnemonics.length },
    { id: 'cheat-sheets', label: 'Cheat Sheets', icon: '📋', count: cheatSheets.length },
    { id: 'notes', label: 'Notes', icon: '📖', count: notes.length },
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
              <div className="space-y-4">
                {questions.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    No questions generated yet.
                  </div>
                ) : (
                  questions.map((question, index) => (
                    <div key={question.question_id} className="card">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-medium text-gray-900">
                          Q{index + 1}. {question.question_text}
                        </h3>
                        <div className="flex space-x-2">
                          <span className={getDifficultyClass(question.difficulty)}>
                            {question.difficulty}
                          </span>
                          {question.topic && (
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                              {question.topic}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="space-y-2 mb-4">
                        {question.options.map((option, optIndex) => (
                          <div
                            key={optIndex}
                            className={`p-2 rounded ${
                              option.is_correct
                                ? 'bg-green-50 border border-green-200'
                                : 'bg-gray-50'
                            }`}
                          >
                            <span className="font-medium">
                              {String.fromCharCode(65 + optIndex)}.
                            </span>{' '}
                            {option.text}
                            {option.is_correct && (
                              <span className="text-green-600 ml-2">✓</span>
                            )}
                          </div>
                        ))}
                      </div>
                      <div className="bg-blue-50 p-3 rounded">
                        <p className="text-sm text-blue-800">
                          <strong>Explanation:</strong> {question.explanation}
                        </p>
                      </div>
                    </div>
                  ))
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
                        <button className="btn-primary">
                          Start Test
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
                      
                      <div className="prose max-w-none mb-4">
                        <div className="text-gray-700 whitespace-pre-wrap">
                          {note.content}
                        </div>
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
    </div>
  );
}
