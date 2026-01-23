import React, { useState } from 'react';
import { FiCalendar, FiClock, FiTarget, FiSettings } from 'react-icons/fi';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';

interface StudyPlanFormProps {
  onSubmit: (config: StudyPlanConfig) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

interface StudyPlanConfig {
  exam_date: string;
  daily_study_hours: number;
  study_days_per_week: number;
  subject_priorities: Record<string, number>;
  weak_areas: string[];
  preferred_study_times: string[];
  spaced_repetition_enabled: boolean;
}

const MEDICAL_SUBJECTS = [
  { value: 'anatomy', label: 'Anatomy' },
  { value: 'physiology', label: 'Physiology' },
  { value: 'biochemistry', label: 'Biochemistry' },
  { value: 'pathology', label: 'Pathology' },
  { value: 'pharmacology', label: 'Pharmacology' },
  { value: 'microbiology', label: 'Microbiology' },
  { value: 'forensic_medicine', label: 'Forensic Medicine' },
  { value: 'community_medicine', label: 'Community Medicine' }
];

const STUDY_TIME_SLOTS = [
  { value: 'early_morning', label: 'Early Morning (5-8 AM)' },
  { value: 'morning', label: 'Morning (8-12 PM)' },
  { value: 'afternoon', label: 'Afternoon (12-5 PM)' },
  { value: 'evening', label: 'Evening (5-8 PM)' },
  { value: 'night', label: 'Night (8-11 PM)' }
];

export default function StudyPlanForm({ onSubmit, onCancel, isLoading = false }: StudyPlanFormProps) {
  const [config, setConfig] = useState<StudyPlanConfig>({
    exam_date: '',
    daily_study_hours: 6,
    study_days_per_week: 6,
    subject_priorities: {},
    weak_areas: [],
    preferred_study_times: [],
    spaced_repetition_enabled: true
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const newErrors: Record<string, string> = {};
    
    if (!config.exam_date) {
      newErrors.exam_date = 'Exam date is required';
    } else {
      const examDate = new Date(config.exam_date);
      const today = new Date();
      if (examDate <= today) {
        newErrors.exam_date = 'Exam date must be in the future';
      }
    }
    
    if (config.daily_study_hours < 1 || config.daily_study_hours > 16) {
      newErrors.daily_study_hours = 'Daily study hours must be between 1 and 16';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    setErrors({});
    onSubmit(config);
  };

  const handleSubjectPriorityChange = (subject: string, priority: number) => {
    setConfig(prev => ({
      ...prev,
      subject_priorities: {
        ...prev.subject_priorities,
        [subject]: priority
      }
    }));
  };

  const handleWeakAreaToggle = (subject: string) => {
    setConfig(prev => ({
      ...prev,
      weak_areas: prev.weak_areas.includes(subject)
        ? prev.weak_areas.filter(area => area !== subject)
        : [...prev.weak_areas, subject]
    }));
  };

  const handleStudyTimeToggle = (timeSlot: string) => {
    setConfig(prev => ({
      ...prev,
      preferred_study_times: prev.preferred_study_times.includes(timeSlot)
        ? prev.preferred_study_times.filter(time => time !== timeSlot)
        : [...prev.preferred_study_times, timeSlot]
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-xl flex items-center justify-center">
              <FiCalendar className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Create Study Plan</h2>
              <p className="text-gray-600">Configure your personalized study schedule</p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-8">
          {/* Basic Configuration */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiTarget className="w-5 h-5 mr-2 text-pink-500" />
              Basic Configuration
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Exam Date *
                </label>
                <input
                  type="date"
                  value={config.exam_date}
                  onChange={(e) => setConfig(prev => ({ ...prev, exam_date: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                />
                {errors.exam_date && (
                  <p className="text-red-500 text-sm mt-1">{errors.exam_date}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Daily Study Hours
                </label>
                <input
                  type="number"
                  min="1"
                  max="16"
                  value={config.daily_study_hours}
                  onChange={(e) => setConfig(prev => ({ ...prev, daily_study_hours: parseInt(e.target.value) }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                />
                {errors.daily_study_hours && (
                  <p className="text-red-500 text-sm mt-1">{errors.daily_study_hours}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Study Days Per Week
              </label>
              <select
                value={config.study_days_per_week}
                onChange={(e) => setConfig(prev => ({ ...prev, study_days_per_week: parseInt(e.target.value) }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent"
              >
                <option value={5}>5 days (Weekdays only)</option>
                <option value={6}>6 days (Monday to Saturday)</option>
                <option value={7}>7 days (All week)</option>
              </select>
            </div>
          </div>

          {/* Subject Priorities */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiSettings className="w-5 h-5 mr-2 text-pink-500" />
              Subject Priorities
            </h3>
            
            <div className="grid md:grid-cols-2 gap-4">
              {MEDICAL_SUBJECTS.map(subject => (
                <div key={subject.value} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <span className="font-medium text-gray-700">{subject.label}</span>
                  <select
                    value={config.subject_priorities[subject.value] || 3}
                    onChange={(e) => handleSubjectPriorityChange(subject.value, parseInt(e.target.value))}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value={1}>Low</option>
                    <option value={2}>Below Average</option>
                    <option value={3}>Average</option>
                    <option value={4}>High</option>
                    <option value={5}>Very High</option>
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Weak Areas */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Weak Areas (Need Extra Focus)
            </h3>
            
            <div className="grid md:grid-cols-2 gap-3">
              {MEDICAL_SUBJECTS.map(subject => (
                <label key={subject.value} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors">
                  <input
                    type="checkbox"
                    checked={config.weak_areas.includes(subject.value)}
                    onChange={() => handleWeakAreaToggle(subject.value)}
                    className="w-4 h-4 text-pink-500 border-gray-300 rounded focus:ring-pink-500"
                  />
                  <span className="text-gray-700">{subject.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Preferred Study Times */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiClock className="w-5 h-5 mr-2 text-pink-500" />
              Preferred Study Times
            </h3>
            
            <div className="grid md:grid-cols-2 gap-3">
              {STUDY_TIME_SLOTS.map(timeSlot => (
                <label key={timeSlot.value} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors">
                  <input
                    type="checkbox"
                    checked={config.preferred_study_times.includes(timeSlot.value)}
                    onChange={() => handleStudyTimeToggle(timeSlot.value)}
                    className="w-4 h-4 text-pink-500 border-gray-300 rounded focus:ring-pink-500"
                  />
                  <span className="text-gray-700">{timeSlot.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Advanced Options */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Advanced Options</h3>
            
            <label className="flex items-center space-x-3 p-4 bg-gradient-to-r from-pink-50 to-fuchsia-50 rounded-xl cursor-pointer">
              <input
                type="checkbox"
                checked={config.spaced_repetition_enabled}
                onChange={(e) => setConfig(prev => ({ ...prev, spaced_repetition_enabled: e.target.checked }))}
                className="w-4 h-4 text-pink-500 border-gray-300 rounded focus:ring-pink-500"
              />
              <div>
                <span className="font-medium text-gray-900">Enable Spaced Repetition</span>
                <p className="text-sm text-gray-600">Automatically schedule review sessions for better retention</p>
              </div>
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              {isLoading ? 'Generating Plan...' : 'Generate Study Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
