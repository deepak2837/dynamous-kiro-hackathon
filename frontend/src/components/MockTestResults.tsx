import React from 'react';
import { Question } from '@/types/api';

interface TestResult {
  questionId: string;
  userAnswer: string;
  correctAnswer: string;
  isCorrect: boolean;
  question: Question;
}

interface MockTestResultsProps {
  testName: string;
  results: TestResult[];
  timeSpent: number;
  totalTime: number;
  onClose: () => void;
  onRetakeTest: () => void;
}

export default function MockTestResults({ 
  testName, 
  results, 
  timeSpent, 
  totalTime, 
  onClose, 
  onRetakeTest 
}: MockTestResultsProps) {
  const correctAnswers = results.filter(r => r.isCorrect).length;
  const totalQuestions = results.length;
  const percentage = Math.round((correctAnswers / totalQuestions) * 100);
  const wrongAnswers = results.filter(r => !r.isCorrect);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-50 border-green-200';
    if (percentage >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold mb-2">Test Results</h2>
              <h3 className="text-xl text-blue-100">{testName}</h3>
            </div>
            <button
              onClick={onClose}
              className="text-blue-100 hover:text-white text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Score Summary */}
          <div className={`rounded-lg border-2 p-6 mb-6 ${getScoreBg(percentage)}`}>
            <div className="text-center">
              <div className={`text-4xl font-bold mb-2 ${getScoreColor(percentage)}`}>
                {percentage}%
              </div>
              <div className="text-lg text-gray-700 mb-4">
                {correctAnswers} out of {totalQuestions} correct
              </div>
              <div className="flex justify-center space-x-8 text-sm text-gray-600">
                <div>
                  <span className="font-semibold">Time Spent:</span> {formatTime(timeSpent)}
                </div>
                <div>
                  <span className="font-semibold">Total Time:</span> {formatTime(totalTime)}
                </div>
                <div>
                  <span className="font-semibold">Efficiency:</span> {Math.round((timeSpent / totalTime) * 100)}%
                </div>
              </div>
            </div>
          </div>

          {/* Performance Breakdown */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{correctAnswers}</div>
              <div className="text-sm text-green-700">Correct</div>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-red-600">{wrongAnswers.length}</div>
              <div className="text-sm text-red-700">Incorrect</div>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-gray-600">
                {totalQuestions - results.filter(r => r.userAnswer).length}
              </div>
              <div className="text-sm text-gray-700">Unanswered</div>
            </div>
          </div>

          {/* Wrong Answers Details */}
          {wrongAnswers.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Review Incorrect Answers ({wrongAnswers.length})
              </h3>
              <div className="space-y-4">
                {wrongAnswers.map((result, index) => {
                  // Handle both string array and object array formats
                  const options = result.question.options || [];
                  const isStringArray = options.length > 0 && typeof options[0] === 'string';
                  
                  let correctOption, userOption;
                  if (isStringArray) {
                    const correctIndex = result.question.correct_answer || 0;
                    correctOption = { text: options[correctIndex] };
                    const userIndex = parseInt(result.userAnswer);
                    userOption = !isNaN(userIndex) && options[userIndex] ? { text: options[userIndex] } : null;
                  } else {
                    correctOption = options.find(opt => opt.is_correct);
                    userOption = options.find(opt => opt.option_id === result.userAnswer);
                  }
                  
                  return (
                    <div key={result.questionId} className="border border-red-200 rounded-lg p-4 bg-red-50">
                      <div className="mb-3">
                        <span className="text-sm font-semibold text-red-600">
                          Question {results.findIndex(r => r.questionId === result.questionId) + 1}:
                        </span>
                        <p className="text-gray-800 mt-1">{result.question.question_text}</p>
                      </div>
                      
                      <div className="space-y-2 mb-3">
                        <div className="flex items-start">
                          <span className="text-sm font-semibold text-red-600 mr-2">Your Answer:</span>
                          <span className="text-sm text-red-700">
                            {userOption ? userOption.text : 'Not answered'}
                          </span>
                        </div>
                        <div className="flex items-start">
                          <span className="text-sm font-semibold text-green-600 mr-2">Correct Answer:</span>
                          <span className="text-sm text-green-700">
                            {correctOption?.text}
                          </span>
                        </div>
                      </div>
                      
                      {result.question.explanation && (
                        <div className="bg-white border border-gray-200 rounded p-3">
                          <span className="text-sm font-semibold text-gray-700">Explanation:</span>
                          <p className="text-sm text-gray-600 mt-1">{result.question.explanation}</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 p-4 flex justify-between">
          <button
            onClick={onRetakeTest}
            className="px-6 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
          >
            Retake Test
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close Results
          </button>
        </div>
      </div>
    </div>
  );
}
