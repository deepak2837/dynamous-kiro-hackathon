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
              <div className="space-y-4">
                {questions.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    No questions generated yet.
                  </div>
                ) : (
                  questions.map((question, index) => {
                    // Handle both API formats: question_text or question
                    const questionText = (question as any).question_text || (question as any).question || '';
                    const questionId = (question as any).question_id || (question as any).id || index;
                    const difficulty = question.difficulty || 'medium';
                    const topic = question.topic || '';
                    const explanation = question.explanation || '';
                    
                    // Handle options - can be array or object
                    const options = question.options;
                    const correctAnswer = (question as any).correct_answer || '';
                    
                    // Convert options object to array if needed
                    const optionsArray = Array.isArray(options) 
                      ? options 
                      : Object.entries(options || {}).map(([key, value]) => ({
                          option_id: key,
                          text: value as string,
                          is_correct: key === correctAnswer
                        }));

                    return (
                      <div key={questionId} className="card">
                        <div className="flex justify-between items-start mb-3">
                          <h3 className="font-medium text-gray-900">
                            Q{index + 1}. {questionText}
                          </h3>
                          <div className="flex space-x-2">
                            <span className={getDifficultyClass(difficulty as DifficultyLevel)}>
                              {difficulty}
                            </span>
                            {topic && (
                              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                                {topic}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="space-y-2 mb-4">
                          {optionsArray.map((option: any, optIndex: number) => {
                            const optionText = option.text || option;
                            const optionKey = option.option_id || String.fromCharCode(65 + optIndex);
                            const isCorrect = option.is_correct || optionKey === correctAnswer;
                            
                            return (
                              <div
                                key={optIndex}
                                className={`p-2 rounded ${
                                  isCorrect
                                    ? 'bg-green-50 border border-green-200'
                                    : 'bg-gray-50'
                                }`}
                              >
                                <span className="font-medium">
                                  {optionKey}.
                                </span>{' '}
                                {optionText}
                                {isCorrect && (
                                  <span className="text-green-600 ml-2">✓</span>
                                )}
                              </div>
                            );
                          })}
                        </div>
                        {explanation && (
                          <div className="bg-blue-50 p-3 rounded">
                            <p className="text-sm text-blue-800">
                              <strong>Explanation:</strong> {explanation}
                            </p>
                          </div>
                        )}
                      </div>
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
