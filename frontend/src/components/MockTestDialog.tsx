import React from 'react';
import { FiClock, FiFileText, FiAlertTriangle, FiPlay, FiX } from 'react-icons/fi';

interface MockTestDialogProps {
  testName: string;
  totalQuestions: number;
  duration: number;
  onStart: () => void;
  onCancel: () => void;
}

export default function MockTestDialog({
  testName,
  totalQuestions,
  duration,
  onStart,
  onCancel
}: MockTestDialogProps) {
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="bg-white/95 backdrop-blur-xl rounded-3xl p-8 max-w-md w-full shadow-2xl shadow-pink-500/20 border border-pink-100 animate-scale-in">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="relative inline-block mb-4">
            <div className="absolute inset-0 bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-2xl blur-lg opacity-50 animate-pulse" />
            <div className="relative w-20 h-20 bg-gradient-to-br from-pink-500 to-fuchsia-500 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-4xl">📝</span>
            </div>
          </div>
          <h2 className="text-2xl font-bold gradient-text mb-2">
            Start Mock Test
          </h2>
          <h3 className="text-lg text-gray-700 font-medium">
            {testName}
          </h3>
        </div>

        {/* Test Info */}
        <div className="space-y-3 mb-6">
          <div className="flex items-center justify-between p-4 bg-pink-50/50 rounded-xl border border-pink-100">
            <span className="text-gray-600 flex items-center">
              <FiFileText className="w-5 h-5 mr-2 text-pink-500" />
              Total Questions
            </span>
            <span className="font-bold text-gray-900 bg-white px-3 py-1 rounded-lg shadow-sm">{totalQuestions}</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-fuchsia-50/50 rounded-xl border border-fuchsia-100">
            <span className="text-gray-600 flex items-center">
              <FiClock className="w-5 h-5 mr-2 text-fuchsia-500" />
              Duration
            </span>
            <span className="font-bold text-gray-900 bg-white px-3 py-1 rounded-lg shadow-sm">{duration} minutes</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-purple-50/50 rounded-xl border border-purple-100">
            <span className="text-gray-600 flex items-center">
              ⏱️ Time per question
            </span>
            <span className="font-bold text-gray-900 bg-white px-3 py-1 rounded-lg shadow-sm">
              ~{Math.round(duration / totalQuestions * 60)}s
            </span>
          </div>
        </div>

        {/* Important Instructions */}
        <div className="bg-amber-50/80 border-2 border-amber-200 rounded-2xl p-5 mb-8">
          <div className="flex items-start space-x-3">
            <FiAlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-amber-800 mb-3">Important Instructions</p>
              <ul className="space-y-2 text-sm text-amber-700">
                <li className="flex items-start">
                  <span className="text-amber-500 mr-2">•</span>
                  Test opens in fullscreen mode
                </li>
                <li className="flex items-start">
                  <span className="text-amber-500 mr-2">•</span>
                  Timer starts immediately
                </li>
                <li className="flex items-start">
                  <span className="text-amber-500 mr-2">•</span>
                  Exiting fullscreen auto-submits
                </li>
                <li className="flex items-start">
                  <span className="text-amber-500 mr-2">•</span>
                  Navigate questions freely
                </li>
                <li className="flex items-start">
                  <span className="text-amber-500 mr-2">•</span>
                  Auto-submit when time expires
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={onCancel}
            className="flex-1 btn-secondary flex items-center justify-center space-x-2"
          >
            <FiX className="w-5 h-5" />
            <span>Cancel</span>
          </button>
          <button
            onClick={onStart}
            className="flex-1 btn-primary flex items-center justify-center space-x-2"
          >
            <FiPlay className="w-5 h-5" />
            <span>Start Test</span>
          </button>
        </div>
      </div>
    </div>
  );
}
