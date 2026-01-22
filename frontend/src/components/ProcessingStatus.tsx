'use client'

import React, { useState, useEffect } from 'react'
import { ProcessingStatusResponse, ProcessingStep, SessionStatus } from '@/types/api'
import { StudyBuddyAPI } from '@/lib/studybuddy-api'
import { FiMail, FiCheck, FiX, FiLoader, FiClock } from 'react-icons/fi'

interface ProcessingStatusProps {
  sessionId: string
  onComplete: () => void
}

const STEP_LABELS: Record<ProcessingStep, string> = {
  [ProcessingStep.UPLOAD_COMPLETE]: "Files Uploaded",
  [ProcessingStep.FILE_ANALYSIS]: "Analyzing Files",
  [ProcessingStep.OCR_PROCESSING]: "OCR Processing",
  [ProcessingStep.AI_PROCESSING]: "AI Processing",
  [ProcessingStep.GENERATING_QUESTIONS]: "Generating Questions",
  [ProcessingStep.GENERATING_MOCK_TESTS]: "Creating Mock Tests",
  [ProcessingStep.GENERATING_MNEMONICS]: "Creating Mnemonics",
  [ProcessingStep.GENERATING_CHEAT_SHEETS]: "Creating Cheat Sheets",
  [ProcessingStep.GENERATING_NOTES]: "Compiling Notes",
  [ProcessingStep.FINALIZING]: "Finalizing",
  [ProcessingStep.COMPLETED]: "Completed",
  [ProcessingStep.FAILED]: "Failed"
}

const STEP_ICONS: Record<ProcessingStep, string> = {
  [ProcessingStep.UPLOAD_COMPLETE]: "📤",
  [ProcessingStep.FILE_ANALYSIS]: "🔍",
  [ProcessingStep.OCR_PROCESSING]: "📝",
  [ProcessingStep.AI_PROCESSING]: "🤖",
  [ProcessingStep.GENERATING_QUESTIONS]: "❓",
  [ProcessingStep.GENERATING_MOCK_TESTS]: "📊",
  [ProcessingStep.GENERATING_MNEMONICS]: "🧠",
  [ProcessingStep.GENERATING_CHEAT_SHEETS]: "📋",
  [ProcessingStep.GENERATING_NOTES]: "📖",
  [ProcessingStep.FINALIZING]: "✨",
  [ProcessingStep.COMPLETED]: "🎉",
  [ProcessingStep.FAILED]: "❌"
}

function ProcessingStatus({ sessionId, onComplete }: ProcessingStatusProps) {
  const [status, setStatus] = useState<ProcessingStatusResponse | null>(null)
  const [showEmailOption, setShowEmailOption] = useState(false)
  const [email, setEmail] = useState('')
  const [isEnablingNotification, setIsEnablingNotification] = useState(false)
  const [emailEnabled, setEmailEnabled] = useState(false)
  const [notificationError, setNotificationError] = useState<string | null>(null)

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const data = await StudyBuddyAPI.getProcessingStatus(sessionId)
        setStatus(data)
        setEmailEnabled(data.email_notification_enabled || false)

        if (data.status === SessionStatus.COMPLETED) {
          onComplete()
        }
      } catch (error) {
        console.error('Error fetching status:', error)
      }
    }

    pollStatus()
    const interval = setInterval(pollStatus, 2000)
    return () => clearInterval(interval)
  }, [sessionId, onComplete])

  const enableEmailNotification = async () => {
    if (!email.trim()) {
      setNotificationError('Please enter a valid email address')
      return
    }

    setIsEnablingNotification(true)
    setNotificationError(null)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/upload/enable-notification/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() })
      })

      if (response.ok) {
        setEmailEnabled(true)
        setShowEmailOption(false)
      } else {
        const errorData = await response.json().catch(() => ({}))
        setNotificationError(errorData.detail || 'Failed to enable email notification')
      }
    } catch (error) {
      console.error('Error enabling email notification:', error)
      setNotificationError('Network error. Please try again.')
    } finally {
      setIsEnablingNotification(false)
    }
  }

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  if (!status) {
    return (
      <div className="card flex items-center justify-center p-12">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-full animate-ping opacity-30" />
            <div className="relative w-16 h-16 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-full flex items-center justify-center">
              <FiLoader className="w-8 h-8 text-white animate-spin" />
            </div>
          </div>
          <p className="text-pink-600 font-medium">Loading status...</p>
        </div>
      </div>
    )
  }

  const progress = status.progress
  const isCompleted = status.status === SessionStatus.COMPLETED
  const isFailed = status.status === SessionStatus.FAILED

  return (
    <div className="card overflow-hidden">
      {/* Header with gradient */}
      <div className={`-mx-6 -mt-6 mb-6 p-6 ${isFailed ? 'bg-gradient-to-r from-rose-500 to-red-500' :
          isCompleted ? 'bg-gradient-to-r from-emerald-500 to-teal-500' :
            'bg-gradient-to-r from-pink-500 via-rose-500 to-fuchsia-500'
        }`}>
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">
              {progress ? STEP_ICONS[progress.current_step] : '🔄'}
            </div>
            <div>
              <h3 className="text-lg font-bold">
                {isCompleted ? 'Processing Complete!' : isFailed ? 'Processing Failed' : 'Processing Your Materials'}
              </h3>
              <p className="text-white/80 text-sm">
                {progress ? STEP_LABELS[progress.current_step] : 'Initializing...'}
              </p>
            </div>
          </div>
          {progress?.total_pages && (
            <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-xl">
              <span className="font-bold">{progress.pages_processed || 0}</span>
              <span className="text-white/80"> / {progress.total_pages} pages</span>
            </div>
          )}
        </div>
      </div>

      {/* Progress Section */}
      <div className="space-y-6">
        {/* Overall Progress Bar */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">Overall Progress</span>
            <span className="text-sm font-bold text-pink-600">{progress?.overall_progress || 0}%</span>
          </div>
          <div className="h-4 bg-pink-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 relative ${isFailed ? 'bg-gradient-to-r from-rose-500 to-red-500' :
                  isCompleted ? 'bg-gradient-to-r from-emerald-500 to-teal-500' :
                    'bg-gradient-to-r from-pink-500 via-rose-500 to-fuchsia-500'
                }`}
              style={{ width: `${progress?.overall_progress || 0}%` }}
            >
              {!isCompleted && !isFailed && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
              )}
            </div>
          </div>
        </div>

        {/* Current Step Progress */}
        {progress && !isCompleted && !isFailed && (
          <div className="bg-pink-50/50 rounded-2xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-pink-700 flex items-center">
                <span className="mr-2">{STEP_ICONS[progress.current_step]}</span>
                {STEP_LABELS[progress.current_step]}
              </span>
              <span className="text-sm font-bold text-pink-600">{progress.step_progress}%</span>
            </div>
            <div className="h-2 bg-pink-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-full transition-all duration-300"
                style={{ width: `${progress.step_progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Status Message */}
        <div className="flex items-center space-x-3 text-gray-600 bg-white/50 rounded-xl p-4">
          {!isCompleted && !isFailed && (
            <div className="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center animate-pulse">
              <div className="w-4 h-4 rounded-full bg-pink-500" />
            </div>
          )}
          <p className="flex-1">{progress?.step_message || status.message}</p>
        </div>

        {/* Estimated Time */}
        {progress?.estimated_time_remaining && !isCompleted && !isFailed && (
          <div className="flex items-center space-x-2 text-pink-600 bg-pink-50 rounded-xl p-4">
            <FiClock className="w-5 h-5" />
            <span className="font-medium">Estimated time remaining:</span>
            <span className="font-bold">{formatTime(progress.estimated_time_remaining)}</span>
          </div>
        )}

        {/* Error Message */}
        {status.error_message && (
          <div className="flex items-start space-x-3 text-rose-600 bg-rose-50 rounded-xl p-4 border border-rose-200">
            <FiX className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <p>{status.error_message}</p>
          </div>
        )}
      </div>

      {/* Email Notification Section */}
      {!isCompleted && !isFailed && !emailEnabled && (
        <div className="border-t border-pink-100 pt-6 mt-6">
          {!showEmailOption ? (
            <button
              onClick={() => setShowEmailOption(true)}
              className="w-full text-sm text-pink-600 hover:text-pink-700 font-medium flex items-center justify-center space-x-2 py-3 hover:bg-pink-50 rounded-xl transition-all duration-200"
            >
              <FiMail className="w-4 h-4" />
              <span>Get notified by email when processing is complete</span>
            </button>
          ) : (
            <div className="space-y-4 animate-slide-up">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    setNotificationError(null)
                  }}
                  placeholder="Enter your email"
                  className={`input-field ${notificationError ? 'border-rose-300 focus:border-rose-400 focus:ring-rose-200' : ''}`}
                  disabled={isEnablingNotification}
                />
                {notificationError && (
                  <p className="mt-2 text-sm text-rose-600 flex items-center">
                    <FiX className="w-4 h-4 mr-1" />
                    {notificationError}
                  </p>
                )}
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={enableEmailNotification}
                  disabled={!email || isEnablingNotification}
                  className="btn-primary flex-1 flex items-center justify-center space-x-2"
                >
                  {isEnablingNotification ? (
                    <>
                      <FiLoader className="w-4 h-4 animate-spin" />
                      <span>Enabling...</span>
                    </>
                  ) : (
                    <>
                      <FiMail className="w-4 h-4" />
                      <span>Enable Notifications</span>
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    setShowEmailOption(false)
                    setNotificationError(null)
                  }}
                  disabled={isEnablingNotification}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Email Enabled Status */}
      {emailEnabled && !isCompleted && (
        <div className="border-t border-pink-100 pt-6 mt-6">
          <div className="flex items-center text-emerald-600 bg-emerald-50 rounded-xl p-4">
            <FiCheck className="w-5 h-5 mr-3" />
            <span className="font-medium">Email notifications enabled</span>
          </div>
        </div>
      )}

      {/* Completion Status */}
      {isCompleted && (
        <div className="border-t border-emerald-100 pt-6 mt-6">
          <div className="flex items-center text-emerald-600 bg-emerald-50 rounded-xl p-4">
            <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center mr-4">
              <FiCheck className="w-6 h-6" />
            </div>
            <div>
              <p className="font-bold">Processing completed successfully!</p>
              <p className="text-sm text-emerald-500">Your study materials are ready to view.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProcessingStatus
