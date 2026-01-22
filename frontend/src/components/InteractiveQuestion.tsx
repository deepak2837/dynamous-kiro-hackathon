'use client';

import { useState } from 'react';
import { Question, DifficultyLevel } from '@/types/api';
import { FiCheck, FiX, FiRotateCcw, FiChevronDown } from 'react-icons/fi';

interface InteractiveQuestionProps {
  question: Question;
  index: number;
}

export default function InteractiveQuestion({ question, index }: InteractiveQuestionProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);

  const questionText = question.question_text || (question as any).question || '';
  const difficulty = question.difficulty || 'medium';
  const topic = question.topic || '';
  const explanation = question.explanation || '';
  const options = question.options || [];
  const correctAnswer = question.correct_answer || 0;

  // Convert options to array format with proper structure
  let optionsArray: Array<{ option_id: string, text: string, is_correct: boolean }> = [];

  if (Array.isArray(options)) {
    optionsArray = options.map((optText: string, idx: number) => ({
      option_id: String.fromCharCode(65 + idx),
      text: optText,
      is_correct: idx === correctAnswer
    }));
  } else if (typeof options === 'object' && options !== null) {
    optionsArray = Object.entries(options).map(([key, value], idx) => ({
      option_id: key,
      text: value as string,
      is_correct: key === String(correctAnswer) || idx === correctAnswer
    }));
  }

  const handleOptionSelect = (optionId: string) => {
    if (showResult) return;
    setSelectedOption(optionId);
    setShowResult(true);
  };

  const resetQuestion = () => {
    setSelectedOption(null);
    setShowResult(false);
  };

  const getDifficultyStyle = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'medium':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'hard':
        return 'bg-rose-100 text-rose-700 border-rose-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const isCorrectAnswer = optionsArray.find(opt => opt.option_id === selectedOption)?.is_correct || false;

  return (
    <div className="card group">
      {/* Question Header */}
      <div className="flex flex-wrap justify-between items-start gap-3 mb-5">
        <div className="flex items-center space-x-3">
          <span className="w-10 h-10 bg-gradient-to-br from-pink-500 to-fuchsia-500 rounded-xl flex items-center justify-center text-white font-bold shadow-lg shadow-pink-200/50">
            {index + 1}
          </span>
          <h3 className="font-semibold text-gray-900 text-lg leading-relaxed">
            {questionText || 'Question text not available'}
          </h3>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getDifficultyStyle(difficulty)}`}>
            {difficulty}
          </span>
          {topic && (
            <span className="bg-pink-100 text-pink-700 px-3 py-1 rounded-full text-xs font-medium border border-pink-200">
              {topic}
            </span>
          )}
        </div>
      </div>

      {optionsArray.length === 0 ? (
        <div className="bg-amber-50 border-2 border-amber-200 p-4 rounded-xl mb-4">
          <p className="text-amber-700 font-medium">No options available for this question.</p>
        </div>
      ) : (
        <div className="space-y-3 mb-5">
          {optionsArray.map((option, optIndex) => {
            const isCorrect = option.is_correct;
            const isSelected = selectedOption === option.option_id;

            let optionStyles = '';
            if (!showResult) {
              optionStyles = isSelected
                ? 'border-pink-500 bg-gradient-to-r from-pink-50 to-fuchsia-50 shadow-md'
                : 'border-gray-200 hover:border-pink-300 hover:bg-pink-50/50';
            } else if (isCorrect) {
              optionStyles = 'border-emerald-500 bg-emerald-50';
            } else if (isSelected && !isCorrect) {
              optionStyles = 'border-rose-500 bg-rose-50';
            } else {
              optionStyles = 'border-gray-200 bg-gray-50 opacity-60';
            }

            return (
              <div
                key={optIndex}
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 ${optionStyles} ${!showResult ? 'hover:scale-[1.01]' : ''}`}
                onClick={() => handleOptionSelect(option.option_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold text-sm transition-all ${isSelected && !showResult
                        ? 'border-pink-500 bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white'
                        : showResult && isCorrect
                          ? 'border-emerald-500 bg-emerald-500 text-white'
                          : showResult && isSelected && !isCorrect
                            ? 'border-rose-500 bg-rose-500 text-white'
                            : 'border-gray-300 text-gray-500'
                      }`}>
                      {showResult && isCorrect ? (
                        <FiCheck className="w-4 h-4" />
                      ) : showResult && isSelected && !isCorrect ? (
                        <FiX className="w-4 h-4" />
                      ) : (
                        option.option_id
                      )}
                    </div>
                    <span className={`font-medium ${showResult && isCorrect ? 'text-emerald-700' :
                        showResult && isSelected && !isCorrect ? 'text-rose-700' : 'text-gray-700'
                      }`}>
                      {option.text}
                    </span>
                  </div>
                  {showResult && isCorrect && (
                    <span className="text-emerald-500 text-lg">✓</span>
                  )}
                  {showResult && isSelected && !isCorrect && (
                    <span className="text-rose-500 text-lg">✗</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Result Section */}
      {showResult && (
        <div className="space-y-4 animate-slide-up">
          {/* Result Banner */}
          <div className={`p-4 rounded-xl flex items-center space-x-3 ${isCorrectAnswer
              ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-2 border-emerald-200'
              : 'bg-gradient-to-r from-rose-50 to-red-50 border-2 border-rose-200'
            }`}>
            {isCorrectAnswer ? (
              <>
                <span className="text-3xl animate-bounce-in">🎉</span>
                <span className="text-emerald-700 font-bold text-lg">Correct!</span>
              </>
            ) : (
              <>
                <span className="text-3xl">😔</span>
                <span className="text-rose-700 font-bold text-lg">Incorrect</span>
              </>
            )}
          </div>

          {/* Explanation */}
          {explanation && (
            <div className="bg-gradient-to-r from-pink-50 to-fuchsia-50 border-2 border-pink-200 rounded-xl p-5">
              <h4 className="font-bold text-pink-700 mb-2 flex items-center">
                <span className="mr-2">💡</span>
                Explanation
              </h4>
              <p className="text-gray-700 leading-relaxed">{explanation}</p>
            </div>
          )}

          {/* Reset Button */}
          <div className="flex justify-end">
            <button
              onClick={resetQuestion}
              className="flex items-center space-x-2 px-4 py-2 text-pink-600 hover:text-pink-700 hover:bg-pink-50 rounded-xl transition-all duration-200 font-medium"
            >
              <FiRotateCcw className="w-4 h-4" />
              <span>Try Again</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
