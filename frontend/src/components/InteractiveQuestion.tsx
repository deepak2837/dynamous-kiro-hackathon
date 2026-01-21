'use client';

import { useState } from 'react';
import { Question, DifficultyLevel } from '@/types/api';

interface InteractiveQuestionProps {
  question: Question;
  index: number;
}

export default function InteractiveQuestion({ question, index }: InteractiveQuestionProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);

  // Debug: Log the question data
  console.log('Question data:', question);

  // Handle both API formats: question_text (from database) or question (from AI)
  const questionText = question.question_text || (question as any).question || '';
  const difficulty = question.difficulty || 'medium';
  const topic = question.topic || '';
  const explanation = question.explanation || '';
  
  // Handle options - can be array or object
  const options = question.options || [];
  const correctAnswer = question.correct_answer || 0;
  
  console.log('Options type:', typeof options, 'Options:', options);
  console.log('Correct answer:', correctAnswer);
  
  // Convert options to array format with proper structure
  let optionsArray: Array<{option_id: string, text: string, is_correct: boolean}> = [];
  
  if (Array.isArray(options)) {
    // Options is an array of strings
    optionsArray = options.map((optText: string, idx: number) => ({
      option_id: String.fromCharCode(65 + idx), // A, B, C, D
      text: optText,
      is_correct: idx === correctAnswer
    }));
  } else if (typeof options === 'object' && options !== null) {
    // Options is an object like {A: "text", B: "text"}
    optionsArray = Object.entries(options).map(([key, value], idx) => ({
      option_id: key,
      text: value as string,
      is_correct: key === correctAnswer || idx === correctAnswer
    }));
  }
  
  console.log('Final optionsArray:', optionsArray);

  const handleOptionSelect = (optionId: string) => {
    if (showResult) return; // Don't allow changing after showing result
    
    setSelectedOption(optionId);
    setShowResult(true);
  };

  const resetQuestion = () => {
    setSelectedOption(null);
    setShowResult(false);
  };

  const getDifficultyClass = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getOptionClass = (option: any, optIndex: number) => {
    const optionKey = option.option_id || String.fromCharCode(65 + optIndex);
    const isCorrect = option.is_correct || optionKey === correctAnswer;
    const isSelected = selectedOption === optionKey;

    if (!showResult) {
      return `p-3 rounded-lg border-2 cursor-pointer transition-colors ${
        isSelected 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      }`;
    }

    // After showing result
    if (isCorrect) {
      return 'p-3 rounded-lg border-2 border-green-500 bg-green-50';
    } else if (isSelected && !isCorrect) {
      return 'p-3 rounded-lg border-2 border-red-500 bg-red-50';
    } else {
      return 'p-3 rounded-lg border-2 border-gray-200 bg-gray-50 opacity-60';
    }
  };

  return (
    <div className="card">
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-medium text-gray-900 text-lg">
          Q{index + 1}. {questionText || 'Question text not available'}
        </h3>
        <div className="flex space-x-2">
          <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyClass(difficulty)}`}>
            {difficulty}
          </span>
          {topic && (
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
              {topic}
            </span>
          )}
        </div>
      </div>

      {optionsArray.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 p-3 rounded mb-4">
          <p className="text-yellow-800">No options available for this question.</p>
          <p className="text-xs text-gray-600 mt-2">Debug: Options type: {typeof options}, Value: {JSON.stringify(options)}</p>
        </div>
      ) : (
        <div className="space-y-3 mb-4">
          {optionsArray.map((option, optIndex) => {
            const isCorrect = option.is_correct;
            const isSelected = selectedOption === option.option_id;
            
            return (
              <div
                key={optIndex}
                className={getOptionClass(option, optIndex)}
                onClick={() => handleOptionSelect(option.option_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="font-medium mr-3">
                      {option.option_id}.
                    </span>
                    <span>{option.text}</span>
                  </div>
                  {showResult && (
                    <div className="flex items-center">
                      {isCorrect && (
                        <span className="text-green-600 text-xl">✓</span>
                      )}
                      {isSelected && !isCorrect && (
                        <span className="text-red-600 text-xl">✗</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showResult && (
        <div className="space-y-3">
          {/* Result indicator */}
          <div className={`p-3 rounded-lg ${
            selectedOption === correctAnswer || 
            optionsArray.find(opt => (opt.option_id || String.fromCharCode(65 + optionsArray.indexOf(opt))) === selectedOption)?.is_correct
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center">
              {selectedOption === correctAnswer || 
               optionsArray.find(opt => (opt.option_id || String.fromCharCode(65 + optionsArray.indexOf(opt))) === selectedOption)?.is_correct ? (
                <>
                  <span className="text-green-600 text-xl mr-2">🎉</span>
                  <span className="text-green-800 font-medium">Correct!</span>
                </>
              ) : (
                <>
                  <span className="text-red-600 text-xl mr-2">❌</span>
                  <span className="text-red-800 font-medium">Incorrect</span>
                </>
              )}
            </div>
          </div>

          {/* Explanation */}
          {explanation && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">Explanation:</h4>
              <p className="text-blue-800 text-sm leading-relaxed">{explanation}</p>
            </div>
          )}

          {/* Reset button */}
          <div className="flex justify-end">
            <button
              onClick={resetQuestion}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
