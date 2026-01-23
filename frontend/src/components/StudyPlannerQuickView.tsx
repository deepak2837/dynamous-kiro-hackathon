'use client';

import React, { useState, useEffect } from 'react';
import { FiCalendar, FiClock, FiTarget, FiTrendingUp, FiArrowRight, FiPlus } from 'react-icons/fi';
import Link from 'next/link';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';
import { useAuth } from '@/contexts/AuthContext';

interface StudyPlan {
    plan_id: string;
    session_id: string;
    plan_name: string;
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

interface StudyPlannerQuickViewProps {
    maxPlans?: number;
}

export default function StudyPlannerQuickView({ maxPlans = 3 }: StudyPlannerQuickViewProps) {
    const { user } = useAuth();
    const [plans, setPlans] = useState<{ plan: StudyPlan; progress?: StudyProgress }[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (user) {
            loadStudyPlans();
        }
    }, [user]);

    const loadStudyPlans = async () => {
        setLoading(true);
        try {
            // Directly fetch user's study plans with the new endpoint
            const response = await StudyBuddyAPI.getUserStudyPlans(maxPlans);

            if (response?.plans && response.plans.length > 0) {
                setPlans(response.plans);
            } else {
                setPlans([]);
            }
        } catch (err) {
            console.error('Failed to load study plans:', err);
            setPlans([]);
        } finally {
            setLoading(false);
        }
    };

    if (!user) return null;

    if (loading) {
        return (
            <div className="card animate-pulse">
                <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-pink-200 rounded-2xl"></div>
                    <div className="flex-1">
                        <div className="h-4 bg-pink-100 rounded w-1/3 mb-2"></div>
                        <div className="h-3 bg-pink-50 rounded w-1/2"></div>
                    </div>
                </div>
            </div>
        );
    }

    // No plans - show create button
    if (plans.length === 0) {
        return (
            <div className="card bg-gradient-to-br from-pink-50 to-fuchsia-50 border-2 border-dashed border-pink-200">
                <div className="text-center py-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                        <FiCalendar className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Start Your Study Journey</h3>
                    <p className="text-gray-500 text-sm mb-4">Create a personalized study plan to track your progress</p>
                    <Link
                        href="/study-planner"
                        className="btn-primary inline-flex items-center space-x-2"
                    >
                        <FiPlus className="w-4 h-4" />
                        <span>Create Study Plan</span>
                    </Link>
                </div>
            </div>
        );
    }

    // Show plans with progress
    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-gray-900 flex items-center">
                    <FiCalendar className="w-5 h-5 mr-2 text-pink-500" />
                    Your Study Plans
                </h3>
                <Link
                    href="/study-planner"
                    className="text-sm text-pink-600 hover:text-pink-700 font-medium flex items-center"
                >
                    View All <FiArrowRight className="w-4 h-4 ml-1" />
                </Link>
            </div>

            <div className="grid gap-4">
                {plans.map(({ plan, progress }) => (
                    <Link
                        key={plan.plan_id}
                        href="/study-planner"
                        className="card group hover:border-pink-300 transition-all duration-300"
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                                    <FiCalendar className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h4 className="font-semibold text-gray-900 group-hover:text-pink-600 transition-colors">
                                        {plan.plan_name}
                                    </h4>
                                    <div className="flex items-center space-x-3 text-sm text-gray-500">
                                        <span className="flex items-center">
                                            <FiTarget className="w-3 h-3 mr-1" />
                                            {plan.total_study_days} days
                                        </span>
                                        <span className="flex items-center">
                                            <FiClock className="w-3 h-3 mr-1" />
                                            {plan.total_study_hours} hours
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {progress && (
                                <div className="text-right">
                                    <div className="text-2xl font-bold text-pink-600">
                                        {Math.round(progress.overall_progress)}%
                                    </div>
                                    <div className="text-xs text-gray-500">
                                        {progress.completed_tasks}/{progress.total_tasks} tasks
                                    </div>
                                    {progress.streak_days > 0 && (
                                        <div className="text-xs text-orange-500 font-medium flex items-center justify-end">
                                            <FiTrendingUp className="w-3 h-3 mr-1" />
                                            {progress.streak_days} day streak
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {progress && (
                            <div className="mt-3">
                                <div className="w-full bg-pink-100 rounded-full h-2">
                                    <div
                                        className="bg-gradient-to-r from-pink-500 to-fuchsia-500 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${progress.overall_progress}%` }}
                                    />
                                </div>
                            </div>
                        )}
                    </Link>
                ))}
            </div>
        </div>
    );
}
