import React, { useState, useEffect } from 'react';
import { FiCalendar, FiClock, FiCheckCircle, FiCircle, FiTrendingUp, FiTarget, FiBook, FiPlay } from 'react-icons/fi';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';

interface StudyPlannerViewerProps {
  sessionId: string;
}

interface StudyTask {
  task_id: string;
  title: string;
  description: string;
  task_type: string;
  subject: string;
  estimated_duration: number;
  priority: number;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  content_ids: string[];
}

interface DailySchedule {
  date: string;
  total_study_time: number;
  tasks: StudyTask[];
  completed_tasks: number;
  total_tasks: number;
  progress_percentage: number;
}

interface StudyPlan {
  plan_id: string;
  session_id: string;
  plan_name: string;
  daily_schedules: DailySchedule[];
  total_study_days: number;
  total_study_hours: number;
  created_at: string;
}

interface StudyProgress {
  total_tasks: number;
  completed_tasks: number;
  overall_progress: number;
  streak_days: number;
}

export default function StudyPlannerViewer({ sessionId }: StudyPlannerViewerProps) {
  const [studyPlan, setStudyPlan] = useState<StudyPlan | null>(null);
  const [progress, setProgress] = useState<StudyProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStudyPlan();
  }, [sessionId]);

  const loadStudyPlan = async () => {
    setLoading(true);
    setError(null);

    try {
      const plan = await StudyBuddyAPI.getStudyPlan(sessionId);
      setStudyPlan(plan);

      if (plan.daily_schedules.length > 0) {
        setSelectedDate(plan.daily_schedules[0].date);
      }

      // Load progress
      const progressData = await StudyBuddyAPI.getStudyProgress(plan.plan_id);
      setProgress(progressData.progress);

    } catch (error: any) {
      console.error('Failed to load study plan:', error);

      // Check if it's a 404 error (no study plan exists)
      if (error?.response?.status === 404) {
        // No study plan exists - this is not an error, just no plan yet
        setStudyPlan(null);
        setError(null);  // Clear any error
      } else {
        setError('Failed to load study plan. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTaskStatusUpdate = async (taskId: string, status: string) => {
    try {
      await StudyBuddyAPI.updateTaskStatus(taskId, status);

      // Refresh the plan and progress
      await loadStudyPlan();

    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  const getTaskTypeIcon = (taskType: string) => {
    switch (taskType) {
      case 'review_questions': return '❓';
      case 'study_notes': return '📖';
      case 'practice_flashcards': return '🎴';
      case 'review_cheatsheet': return '📋';
      case 'mock_test': return '📊';
      case 'revision': return '🔄';
      default: return '📚';
    }
  };

  const getSubjectColor = (subject: string) => {
    const colors: Record<string, string> = {
      anatomy: 'bg-blue-100 text-blue-700',
      physiology: 'bg-green-100 text-green-700',
      biochemistry: 'bg-yellow-100 text-yellow-700',
      pathology: 'bg-red-100 text-red-700',
      pharmacology: 'bg-purple-100 text-purple-700',
      microbiology: 'bg-indigo-100 text-indigo-700',
      forensic_medicine: 'bg-gray-100 text-gray-700',
      community_medicine: 'bg-teal-100 text-teal-700',
      general: 'bg-pink-100 text-pink-700'
    };
    return colors[subject] || colors.general;
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const selectedSchedule = studyPlan?.daily_schedules.find(schedule => schedule.date === selectedDate);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-full animate-ping opacity-30" />
            <div className="relative w-16 h-16 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-full flex items-center justify-center">
              <FiCalendar className="w-8 h-8 text-white" />
            </div>
          </div>
          <p className="text-pink-600 font-medium">Loading study plan...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <div className="text-6xl mb-4">📅</div>
        <p className="text-gray-500 text-lg mb-4">{error}</p>
        <button
          onClick={loadStudyPlan}
          className="bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg transition-all duration-300"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!studyPlan) {
    return (
      <div className="text-center py-16 bg-gradient-to-br from-pink-50 to-fuchsia-50 rounded-2xl border-2 border-dashed border-pink-200">
        <div className="text-6xl mb-4 animate-float">📅</div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">No Study Plan Yet</h3>
        <p className="text-gray-500 text-lg mb-2">You haven't created a study plan for this session.</p>
        <p className="text-gray-400 text-sm">Click the "Create New Study Plan" button below to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Study Plan Header */}
      <div className="bg-gradient-to-r from-pink-50 to-fuchsia-50 border-2 border-pink-200 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{studyPlan.plan_name}</h2>
            <div className="flex flex-wrap gap-4 text-sm text-gray-600">
              <span className="flex items-center">
                <FiCalendar className="w-4 h-4 mr-1" />
                {studyPlan.total_study_days} days
              </span>
              <span className="flex items-center">
                <FiClock className="w-4 h-4 mr-1" />
                {studyPlan.total_study_hours} hours total
              </span>
              <span className="flex items-center">
                <FiTarget className="w-4 h-4 mr-1" />
                Created {new Date(studyPlan.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          {progress && (
            <div className="mt-4 md:mt-0 text-center">
              <div className="text-3xl font-bold text-pink-600">
                {Math.round(progress.overall_progress)}%
              </div>
              <div className="text-sm text-gray-600">
                {progress.completed_tasks} of {progress.total_tasks} tasks
              </div>
              {progress.streak_days > 0 && (
                <div className="text-sm text-orange-600 font-medium">
                  🔥 {progress.streak_days} day streak
                </div>
              )}
            </div>
          )}
        </div>

        {progress && (
          <div className="mt-4">
            <div className="w-full bg-pink-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-pink-500 to-fuchsia-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress.overall_progress}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Calendar Navigation */}
      <div className="bg-white rounded-2xl border border-pink-100 shadow-lg shadow-pink-100/20 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <FiCalendar className="w-5 h-5 mr-2 text-pink-500" />
          Study Schedule
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {studyPlan.daily_schedules.map((schedule, index) => {
            const date = new Date(schedule.date);
            const isSelected = selectedDate === schedule.date;
            const isCompleted = schedule.progress_percentage === 100;

            return (
              <button
                key={schedule.date}
                onClick={() => setSelectedDate(schedule.date)}
                className={`p-3 rounded-xl text-center transition-all duration-200 ${isSelected
                  ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg'
                  : isCompleted
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                  }`}
              >
                <div className="text-xs font-medium">
                  {date.toLocaleDateString('en-US', { weekday: 'short' })}
                </div>
                <div className="text-lg font-bold">
                  {date.getDate()}
                </div>
                <div className="text-xs">
                  {Math.round(schedule.progress_percentage)}%
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Daily Tasks */}
      {selectedSchedule && (
        <div className="bg-white rounded-2xl border border-pink-100 shadow-lg shadow-pink-100/20 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-900">
              Tasks for {new Date(selectedSchedule.date).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </h3>
            <div className="text-sm text-gray-600">
              Total: {formatDuration(selectedSchedule.total_study_time)}
            </div>
          </div>

          <div className="space-y-4">
            {selectedSchedule.tasks.map((task, index) => (
              <div
                key={task.task_id}
                className={`p-4 rounded-xl border-2 transition-all duration-200 ${task.status === 'completed'
                  ? 'border-green-200 bg-green-50'
                  : task.status === 'in_progress'
                    ? 'border-blue-200 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-pink-200'
                  }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <button
                      onClick={() => handleTaskStatusUpdate(
                        task.task_id,
                        task.status === 'completed' ? 'pending' : 'completed'
                      )}
                      className="mt-1 transition-colors"
                    >
                      {task.status === 'completed' ? (
                        <FiCheckCircle className="w-6 h-6 text-green-500" />
                      ) : (
                        <FiCircle className="w-6 h-6 text-gray-400 hover:text-pink-500" />
                      )}
                    </button>

                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-2xl">{getTaskTypeIcon(task.task_type)}</span>
                        <h4 className={`font-semibold ${task.status === 'completed' ? 'text-green-700 line-through' : 'text-gray-900'
                          }`}>
                          {task.title}
                        </h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSubjectColor(task.subject)}`}>
                          {task.subject.replace('_', ' ')}
                        </span>
                      </div>

                      <p className="text-gray-600 text-sm mb-3">{task.description}</p>

                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <FiClock className="w-4 h-4 mr-1" />
                          {formatDuration(task.estimated_duration)}
                        </span>
                        <span className="flex items-center">
                          <FiTrendingUp className="w-4 h-4 mr-1" />
                          Priority {task.priority}
                        </span>
                      </div>
                    </div>
                  </div>

                  {task.status === 'pending' && (
                    <button
                      onClick={() => handleTaskStatusUpdate(task.task_id, 'in_progress')}
                      className="bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
                    >
                      <FiPlay className="w-4 h-4" />
                      <span>Start</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {selectedSchedule.tasks.length === 0 && (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">🎉</div>
              <p className="text-gray-500">No tasks scheduled for this day</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
