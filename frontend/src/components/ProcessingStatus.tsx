'use client'

import React, { useState, useEffect } from 'react'
import { ProcessingStatusResponse, ProcessingStep, SessionStatus } from '@/types/api'
import { StudyBuddyAPI } from '@/lib/studybuddy-api'

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
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const progress = status.progress
  const isCompleted = status.status === SessionStatus.COMPLETED
  const isFailed = status.status === SessionStatus.FAILED

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">
            Processing Status
          </h3>
          {progress?.total_pages && (
            <span className="text-sm text-gray-600">
              {progress.pages_processed || 0} / {progress.total_pages} pages
            </span>
          )}
        </div>

        {/* Overall Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${isFailed ? 'bg-red-500' : isCompleted ? 'bg-green-500' : 'bg-blue-500'
              }`}
            style={{ width: `${progress?.overall_progress || 0}%` }}
          ></div>
        </div>

        {/* Current Step */}
        {progress && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                {STEP_LABELS[progress.current_step]}
              </span>
              <span className="text-sm text-gray-600">
                {progress.step_progress}%
              </span>
            </div>
          </div>
        )}

        {/* Status Message */}
        <div className="text-sm text-gray-600 mb-4">
          {progress?.step_message || status.message}
        </div>

        {/* Estimated Time */}
        {progress?.estimated_time_remaining && !isCompleted && !isFailed && (
          <div className="text-sm text-gray-500">
            Estimated time remaining: {formatTime(progress.estimated_time_remaining)}
          </div>
        )}

        {/* Error Message */}
        {status.error_message && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
            {status.error_message}
          </div>
        )}
      </div>

      {/* Email Notification Section */}
      {!isCompleted && !isFailed && !emailEnabled && (
        <div className="border-t pt-4">
          {!showEmailOption ? (
            <button
              onClick={() => setShowEmailOption(true)}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Get notified by email when processing is complete
            </button>
          ) : (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
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
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${notificationError ? 'border-red-300' : 'border-gray-300'
                    }`}
                  disabled={isEnablingNotification}
                />
                {notificationError && (
                  <p className="mt-1 text-sm text-red-600">{notificationError}</p>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={enableEmailNotification}
                  disabled={!email || isEnablingNotification}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
                >
                  {isEnablingNotification ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Enabling...
                    </>
                  ) : (
                    'Enable Notifications'
                  )}
                </button>
                <button
                  onClick={() => {
                    setShowEmailOption(false)
                    setNotificationError(null)
                  }}
                  disabled={isEnablingNotification}
                  className="px-4 py-2 bg-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-400 disabled:opacity-50"
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
        <div className="border-t pt-4">
          <div className="flex items-center text-sm text-green-600">
            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Email notifications enabled
          </div>
        </div>
      )}

      {/* Completion Status */}
      {isCompleted && (
        <div className="border-t pt-4">
          <div className="flex items-center text-sm text-green-600">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Processing completed successfully!
          </div>
        </div>
      )}
    </div>
  )
}

export default ProcessingStatus
