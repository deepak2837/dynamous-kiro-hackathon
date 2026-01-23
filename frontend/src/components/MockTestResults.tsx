import React from 'react';
import { Question } from '@/types/api';
import { FiCheck, FiX, FiClock, FiRefreshCw, FiAward, FiXCircle, FiMinusCircle } from 'react-icons/fi';

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
  const unanswered = totalQuestions - results.filter(r => r.userAnswer).length;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getScoreGradient = (percentage: number) => {
    if (percentage >= 80) return 'from-emerald-500 to-teal-500';
    if (percentage >= 60) return 'from-amber-500 to-orange-500';
    return 'from-rose-500 to-red-500';
  };

  const getScoreBg = (percentage: number) => {
    if (percentage >= 80) return 'bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-200';
    if (percentage >= 60) return 'bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200';
    return 'bg-gradient-to-br from-rose-50 to-red-50 border-rose-200';
  };

  const getEmoji = (percentage: number) => {
    if (percentage >= 80) return '🎉';
    if (percentage >= 60) return '👍';
    return '💪';
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="bg-white/95 backdrop-blur-xl rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl shadow-pink-500/20 border border-pink-100 animate-scale-in">
        {/* Header */}
        <div className={`bg-gradient-to-r ${getScoreGradient(percentage)} text-white p-8`}>
          <div className="flex justify-between items-start">
            <div className="flex items-center space-x-4">
              <div className="text-5xl animate-bounce-in">{getEmoji(percentage)}</div>
              <div>
                <h2 className="text-2xl font-bold mb-1">Test Results</h2>
                <h3 className="text-lg text-white/80">{testName}</h3>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-10 h-10 bg-white/20 hover:bg-white/30 rounded-xl flex items-center justify-center transition-all duration-200"
            >
              <FiX className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-8 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Score Summary */}
          <div className={`rounded-2xl border-2 p-8 mb-8 ${getScoreBg(percentage)}`}>
            <div className="text-center">
              <div className={`text-6xl font-black mb-2 bg-gradient-to-r ${getScoreGradient(percentage)} bg-clip-text text-transparent`}>
                {percentage}%
              </div>
              <div className="text-xl text-gray-700 mb-6">
                {correctAnswers} out of {totalQuestions} correct
              </div>
              <div className="flex justify-center gap-6 text-sm">
                <div className="bg-white/80 backdrop-blur-sm rounded-xl px-4 py-3 shadow-sm">
                  <FiClock className="w-4 h-4 text-pink-500 mx-auto mb-1" />
                  <span className="text-gray-500">Time Spent</span>
                  <p className="font-bold text-gray-900">{formatTime(timeSpent)}</p>
                </div>
                <div className="bg-white/80 backdrop-blur-sm rounded-xl px-4 py-3 shadow-sm">
                  <FiClock className="w-4 h-4 text-fuchsia-500 mx-auto mb-1" />
                  <span className="text-gray-500">Total Time</span>
                  <p className="font-bold text-gray-900">{formatTime(totalTime)}</p>
                </div>
                <div className="bg-white/80 backdrop-blur-sm rounded-xl px-4 py-3 shadow-sm">
                  <FiAward className="w-4 h-4 text-purple-500 mx-auto mb-1" />
                  <span className="text-gray-500">Efficiency</span>
                  <p className="font-bold text-gray-900">{Math.round((timeSpent / totalTime) * 100)}%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Breakdown */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200 rounded-2xl p-5 text-center">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                <FiCheck className="w-6 h-6 text-emerald-600" />
              </div>
              <div className="text-3xl font-bold text-emerald-600">{correctAnswers}</div>
              <div className="text-sm text-emerald-700 font-medium">Correct</div>
            </div>
            <div className="bg-gradient-to-br from-rose-50 to-red-50 border-2 border-rose-200 rounded-2xl p-5 text-center">
              <div className="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                <FiXCircle className="w-6 h-6 text-rose-600" />
              </div>
              <div className="text-3xl font-bold text-rose-600">{wrongAnswers.length}</div>
              <div className="text-sm text-rose-700 font-medium">Incorrect</div>
            </div>
            <div className="bg-gradient-to-br from-gray-50 to-slate-50 border-2 border-gray-200 rounded-2xl p-5 text-center">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                <FiMinusCircle className="w-6 h-6 text-gray-600" />
              </div>
              <div className="text-3xl font-bold text-gray-600">{unanswered}</div>
              <div className="text-sm text-gray-700 font-medium">Unanswered</div>
            </div>
          </div>

          {/* Wrong Answers Details */}
          {wrongAnswers.length > 0 && (
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-900 mb-5 flex items-center">
                <span className="w-10 h-10 bg-rose-100 rounded-xl flex items-center justify-center mr-3">
                  <FiX className="w-5 h-5 text-rose-600" />
                </span>
                Review Incorrect Answers ({wrongAnswers.length})
              </h3>
              <div className="space-y-4">
                {wrongAnswers.map((result, index) => {
                  const rawOptions = result.question.options || {};

                  let correctOption: { text: string } | null = null;
                  let userOption: { text: string } | null = null;
                  const correctAnswer = String(result.question.correct_answer || 'A');
                  const userAnswer = result.userAnswer;

                  if (Array.isArray(rawOptions)) {
                    if (rawOptions.length > 0 && typeof rawOptions[0] === 'string') {
                      const correctIndex = parseInt(correctAnswer) || 0;
                      correctOption = { text: (rawOptions as string[])[correctIndex] || '' };
                      const userIndex = parseInt(userAnswer);
                      userOption = !isNaN(userIndex) && rawOptions[userIndex] ? { text: (rawOptions as string[])[userIndex] } : null;
                    } else {
                      const optArr = rawOptions as { option_id?: string; is_correct?: boolean; text?: string }[];
                      const correct = optArr.find(opt => opt.is_correct || opt.option_id === correctAnswer);
                      correctOption = correct ? { text: correct.text || '' } : null;
                      const user = optArr.find(opt => opt.option_id === userAnswer);
                      userOption = user ? { text: user.text || '' } : null;
                    }
                  } else if (typeof rawOptions === 'object') {
                    correctOption = { text: (rawOptions as Record<string, string>)[correctAnswer] || '' };
                    userOption = userAnswer ? { text: (rawOptions as Record<string, string>)[userAnswer] || '' } : null;
                  }

                  return (
                    <div key={result.questionId} className="card !border-rose-200 !bg-rose-50/50">
                      <div className="mb-4">
                        <span className="text-sm font-bold text-rose-600 bg-rose-100 px-3 py-1 rounded-full">
                          Question {results.findIndex(r => r.questionId === result.questionId) + 1}
                        </span>
                        <p className="text-gray-800 mt-3 font-medium">{result.question.question_text}</p>
                      </div>

                      <div className="grid sm:grid-cols-2 gap-3 mb-4">
                        <div className="bg-rose-100/50 rounded-xl p-4 border border-rose-200">
                          <span className="text-xs font-semibold text-rose-600 uppercase">Your Answer</span>
                          <p className="text-rose-800 font-medium mt-1">
                            {userOption ? userOption.text : 'Not answered'}
                          </p>
                        </div>
                        <div className="bg-emerald-100/50 rounded-xl p-4 border border-emerald-200">
                          <span className="text-xs font-semibold text-emerald-600 uppercase">Correct Answer</span>
                          <p className="text-emerald-800 font-medium mt-1">
                            {correctOption?.text}
                          </p>
                        </div>
                      </div>

                      {result.question.explanation && (
                        <div className="bg-white rounded-xl p-4 border border-pink-100">
                          <span className="text-sm font-bold text-pink-600">💡 Explanation</span>
                          <p className="text-sm text-gray-600 mt-2 leading-relaxed">{result.question.explanation}</p>
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
        <div className="bg-pink-50/50 border-t border-pink-100 p-6 flex justify-between">
          <button
            onClick={onRetakeTest}
            className="btn-secondary flex items-center space-x-2"
          >
            <FiRefreshCw className="w-5 h-5" />
            <span>Retake Test</span>
          </button>
          <button
            onClick={onClose}
            className="btn-primary flex items-center space-x-2"
          >
            <FiCheck className="w-5 h-5" />
            <span>Close Results</span>
          </button>
        </div>
      </div>
    </div>
  );
}
