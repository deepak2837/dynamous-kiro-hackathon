import React, { useState, useEffect, useRef } from 'react';
import { Question } from '@/types/api';

interface MockTestInterfaceProps {
  questions: Question[];
  testName: string;
  duration: number;
  onSubmit: (answers: Record<string, string>, timeSpent: number) => void;
  onExit: () => void;
}

export default function MockTestInterface({ 
  questions, 
  testName, 
  duration, 
  onSubmit, 
  onExit 
}: MockTestInterfaceProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeLeft, setTimeLeft] = useState(duration * 60); // Convert to seconds
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startTime = useRef(Date.now());

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Fullscreen effect
  useEffect(() => {
    const enterFullscreen = async () => {
      if (containerRef.current && document.documentElement.requestFullscreen) {
        try {
          await document.documentElement.requestFullscreen();
          setIsFullscreen(true);
        } catch (err) {
          console.log('Fullscreen not supported');
        }
      }
    };

    enterFullscreen();

    // Handle fullscreen exit
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        setIsFullscreen(false);
        handleExit();
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    
    // Prevent context menu and shortcuts
    const preventActions = (e: KeyboardEvent) => {
      if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I') || 
          (e.ctrlKey && e.key === 'u') || e.key === 'F5') {
        e.preventDefault();
      }
    };

    document.addEventListener('keydown', preventActions);
    document.addEventListener('contextmenu', (e) => e.preventDefault());

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('keydown', preventActions);
      document.removeEventListener('contextmenu', (e) => e.preventDefault());
      if (document.fullscreenElement) {
        document.exitFullscreen();
      }
    };
  }, []);

  const handleSubmit = () => {
    const timeSpent = Math.floor((Date.now() - startTime.current) / 1000);
    onSubmit(answers, timeSpent);
  };

  const handleExit = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
    onExit();
  };

  const handleAnswerSelect = (questionId: string, optionId: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: optionId
    }));
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const currentQ = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  // Debug: Log the current question structure
  console.log('Current question:', currentQ);
  console.log('Options:', currentQ?.options);

  return (
    <div ref={containerRef} className="fixed inset-0 bg-white z-50 flex flex-col">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold">{testName}</h1>
          <p className="text-blue-100">Question {currentQuestion + 1} of {questions.length}</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`text-lg font-mono ${timeLeft < 300 ? 'text-red-200' : ''}`}>
            ⏱️ {formatTime(timeLeft)}
          </div>
          <button
            onClick={handleExit}
            className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-sm"
          >
            Exit Test
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-gray-200 h-2">
        <div 
          className="bg-blue-500 h-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Question Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-6 text-gray-800">
              {currentQ.question_text}
            </h2>
            
            <div className="space-y-3">
              {(currentQ.options || []).map((option, index) => {
                // Handle both string array and object array formats
                const isStringArray = typeof option === 'string';
                const optionId = isStringArray ? index.toString() : option.option_id;
                const optionText = isStringArray ? option : option.text;
                
                return (
                  <label
                    key={optionId}
                    className={`block p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      answers[currentQ.question_id] === optionId
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${currentQ.question_id}`}
                      value={optionId}
                      checked={answers[currentQ.question_id] === optionId}
                      onChange={() => handleAnswerSelect(currentQ.question_id, optionId)}
                      className="sr-only"
                    />
                    <div className="flex items-center">
                      <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                        answers[currentQ.question_id] === optionId
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300'
                      }`}>
                        {answers[currentQ.question_id] === optionId && (
                          <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5" />
                        )}
                      </div>
                      <span className="text-gray-800">
                        {String.fromCharCode(65 + index)}. {optionText}
                      </span>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-gray-50 p-4 flex justify-between items-center">
        <button
          onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
          disabled={currentQuestion === 0}
          className="btn-secondary disabled:opacity-50"
        >
          Previous
        </button>
        
        <div className="flex space-x-2">
          {questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestion(index)}
              className={`w-8 h-8 rounded text-sm ${
                index === currentQuestion
                  ? 'bg-blue-500 text-white'
                  : answers[questions[index].question_id]
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {index + 1}
            </button>
          ))}
        </div>

        {currentQuestion === questions.length - 1 ? (
          <button
            onClick={handleSubmit}
            className="btn-primary bg-green-600 hover:bg-green-700"
          >
            Submit Test
          </button>
        ) : (
          <button
            onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
            className="btn-primary"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
