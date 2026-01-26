import React, { useState, useEffect, useRef } from 'react';
import { Question } from '@/types/api';
import { FiClock, FiX, FiChevronLeft, FiChevronRight, FiCheck, FiAlertTriangle } from 'react-icons/fi';

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
  const [timeLeft, setTimeLeft] = useState(duration * 60);
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

  // Fullscreen effect - creates secure testing environment
  useEffect(() => {
    // Enter fullscreen mode for distraction-free testing
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

    // Handle fullscreen exit - automatically exit test if user leaves fullscreen
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        setIsFullscreen(false);
        handleExit();
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);

    // Prevent common cheating methods during test
    const preventActions = (e: KeyboardEvent) => {
      // Block F12 (dev tools), Ctrl+Shift+I (inspect), Ctrl+U (view source), F5 (refresh)
      if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I') ||
        (e.ctrlKey && e.key === 'u') || e.key === 'F5') {
        e.preventDefault();
      }
    };

    document.addEventListener('keydown', preventActions);
    document.addEventListener('contextmenu', (e) => e.preventDefault()); // Disable right-click

    // Cleanup event listeners on component unmount
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
  const answeredCount = Object.keys(answers).length;
  const isLowTime = timeLeft < 300;

  return (
    <div ref={containerRef} className="fixed inset-0 bg-gradient-to-br from-pink-50 via-fuchsia-50 to-purple-50 z-50 overflow-hidden">
      <div className="flex flex-col h-full">
        {/* Fixed Header */}
        <header className="flex-shrink-0 bg-gradient-to-r from-pink-500 via-rose-500 to-fuchsia-500 text-white shadow-xl shadow-pink-300/30">
          <div className="px-4 sm:px-6 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-3 sm:space-x-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center flex-shrink-0">
                  <span className="text-xl sm:text-2xl">📝</span>
                </div>
                <div className="min-w-0">
                  <h1 className="text-base sm:text-xl font-bold truncate max-w-[150px] sm:max-w-none">{testName}</h1>
                  <p className="text-pink-100 text-xs sm:text-sm">Q {currentQuestion + 1} / {questions.length}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2 sm:space-x-4">
                {/* Timer */}
                <div className={`flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 rounded-xl backdrop-blur-sm ${isLowTime ? 'bg-red-500/40 animate-pulse' : 'bg-white/20'
                  }`}>
                  <FiClock className={`w-4 h-4 sm:w-5 sm:h-5 ${isLowTime ? 'text-red-100' : ''}`} />
                  <span className={`font-mono text-sm sm:text-lg font-bold ${isLowTime ? 'text-red-100' : ''}`}>
                    {formatTime(timeLeft)}
                  </span>
                </div>
                {/* Exit Button */}
                <button
                  onClick={handleExit}
                  className="flex items-center space-x-1 sm:space-x-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm px-3 sm:px-4 py-2 rounded-xl transition-all duration-200"
                >
                  <FiX className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="hidden sm:inline text-sm">Exit</span>
                </button>
              </div>
            </div>
          </div>
          {/* Progress Bar */}
          <div className="h-1.5 bg-pink-600/50">
            <div
              className="h-full bg-white transition-all duration-500 relative"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent animate-shimmer" />
            </div>
          </div>
        </header>

        {/* Scrollable Content Area */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">
          <div className="max-w-3xl mx-auto">
            <div className="card animate-scale-in">
              {/* Question Header */}
              <div className="flex items-center justify-between mb-6">
                <span className="bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white px-4 py-1.5 rounded-full text-sm font-bold shadow-lg shadow-pink-200/50">
                  Question {currentQuestion + 1}
                </span>
                <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                  {answeredCount}/{questions.length} answered
                </span>
              </div>

              {/* Question Text */}
              <h2 className="text-lg sm:text-xl font-bold mb-8 text-gray-800 leading-relaxed">
                {currentQ.question_text}
              </h2>

              {/* Options */}
              <div className="space-y-3">
                {(() => {
                  const rawOptions = currentQ.options || {};
                  let optionsArray: { key: string; text: string }[] = [];

                  if (Array.isArray(rawOptions)) {
                    optionsArray = (rawOptions as any[]).map((opt, idx) => ({
                      key: typeof opt === 'string' ? String.fromCharCode(65 + idx) : (opt.option_id || String.fromCharCode(65 + idx)),
                      text: typeof opt === 'string' ? opt : (opt.text || '')
                    }));
                  } else if (typeof rawOptions === 'object') {
                    optionsArray = Object.entries(rawOptions).map(([key, value]) => ({
                      key,
                      text: value as string
                    }));
                  }

                  const questionId = (currentQ as any).question_id || (currentQ as any).id;
                  const selectedAnswer = answers[questionId];

                  return optionsArray.map((option) => (
                    <label
                      key={option.key}
                      className={`block p-4 sm:p-5 border-2 rounded-2xl cursor-pointer transition-all duration-300 group ${selectedAnswer === option.key
                          ? 'border-pink-500 bg-gradient-to-r from-pink-50 to-fuchsia-50 shadow-lg shadow-pink-100/50 scale-[1.01]'
                          : 'border-gray-200 hover:border-pink-300 hover:bg-pink-50/50 hover:scale-[1.005]'
                        }`}
                    >
                      <input
                        type="radio"
                        name={`question-${questionId}`}
                        value={option.key}
                        checked={selectedAnswer === option.key}
                        onChange={() => handleAnswerSelect(questionId, option.key)}
                        className="sr-only"
                      />
                      <div className="flex items-center">
                        <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 mr-3 sm:mr-4 flex items-center justify-center transition-all duration-300 flex-shrink-0 ${selectedAnswer === option.key
                            ? 'border-pink-500 bg-gradient-to-r from-pink-500 to-fuchsia-500'
                            : 'border-gray-300 group-hover:border-pink-300'
                          }`}>
                          {selectedAnswer === option.key ? (
                            <FiCheck className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                          ) : (
                            <span className="text-xs sm:text-sm font-bold text-gray-400 group-hover:text-pink-400">{option.key}</span>
                          )}
                        </div>
                        <span className={`text-sm sm:text-base font-medium leading-relaxed ${selectedAnswer === option.key ? 'text-pink-700' : 'text-gray-700'}`}>
                          {option.text}
                        </span>
                      </div>
                    </label>
                  ));
                })()}
              </div>
            </div>
          </div>
        </main>

        {/* Fixed Footer Navigation */}
        <footer className="flex-shrink-0 bg-white/90 backdrop-blur-xl border-t border-pink-100 shadow-lg">
          <div className="px-4 sm:px-6 py-4">
            <div className="max-w-3xl mx-auto">
              {/* Navigation Buttons */}
              <div className="flex justify-between items-center gap-3">
                <button
                  onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                  disabled={currentQuestion === 0}
                  className="btn-secondary flex items-center space-x-1 sm:space-x-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                >
                  <FiChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="hidden sm:inline">Previous</span>
                </button>

                {/* Question Navigator - scrollable on mobile */}
                <div className="flex-1 overflow-x-auto px-2">
                  <div className="flex justify-center gap-1.5 sm:gap-2 min-w-max mx-auto">
                    {questions.slice(0, Math.min(questions.length, 15)).map((q, index) => {
                      const qId = (q as any).question_id || (q as any).id;
                      const isAnswered = !!answers[qId];
                      const isCurrent = index === currentQuestion;

                      return (
                        <button
                          key={index}
                          onClick={() => setCurrentQuestion(index)}
                          className={`w-8 h-8 sm:w-10 sm:h-10 rounded-lg text-xs sm:text-sm font-bold transition-all duration-200 flex-shrink-0 ${isCurrent
                              ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg shadow-pink-200/50 scale-110'
                              : isAnswered
                                ? 'bg-emerald-500 text-white hover:scale-105'
                                : 'bg-gray-100 text-gray-600 hover:bg-pink-100 hover:text-pink-600'
                            }`}
                        >
                          {index + 1}
                        </button>
                      );
                    })}
                    {questions.length > 15 && (
                      <span className="text-gray-400 text-sm self-center">+{questions.length - 15}</span>
                    )}
                  </div>
                </div>

                {/* Next/Submit Button */}
                {currentQuestion === questions.length - 1 ? (
                  <button
                    onClick={handleSubmit}
                    className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-bold py-2.5 sm:py-3 px-4 sm:px-8 rounded-xl shadow-lg shadow-emerald-200/50 transition-all duration-300 hover:scale-105 flex items-center space-x-1 sm:space-x-2 text-sm sm:text-base"
                  >
                    <FiCheck className="w-4 h-4 sm:w-5 sm:h-5" />
                    <span>Submit</span>
                  </button>
                ) : (
                  <button
                    onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
                    className="btn-primary flex items-center space-x-1 sm:space-x-2 text-sm sm:text-base"
                  >
                    <span className="hidden sm:inline">Next</span>
                    <FiChevronRight className="w-4 h-4 sm:w-5 sm:h-5" />
                  </button>
                )}
              </div>

              {/* Unanswered Warning */}
              {answeredCount < questions.length && currentQuestion === questions.length - 1 && (
                <div className="mt-3 flex items-center justify-center space-x-2 text-amber-600 bg-amber-50 rounded-xl p-3">
                  <FiAlertTriangle className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="text-xs sm:text-sm font-medium">
                    {questions.length - answeredCount} unanswered question(s)
                  </span>
                </div>
              )}
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
