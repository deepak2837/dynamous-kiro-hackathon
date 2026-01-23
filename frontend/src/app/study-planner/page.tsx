'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import StudyPlannerViewer from '@/components/StudyPlannerViewer';
import StudyPlanForm from '@/components/StudyPlanForm';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';
import { FiCalendar, FiPlus, FiArrowLeft, FiRefreshCw } from 'react-icons/fi';
import Link from 'next/link';

export default function StudyPlannerPage() {
    const { user, isLoading } = useAuth();
    const router = useRouter();
    const [showPlanForm, setShowPlanForm] = useState(false);
    const [planGenerating, setPlanGenerating] = useState(false);
    const [planExists, setPlanExists] = useState(false);
    const [latestPlanId, setLatestPlanId] = useState<string | null>(null);
    const [refreshKey, setRefreshKey] = useState(0);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [checkingPlan, setCheckingPlan] = useState(true);

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!isLoading && !user) {
            router.push('/login');
        }
    }, [user, isLoading, router]);

    // Check if user has a study plan
    useEffect(() => {
        if (user) {
            checkUserPlan();
        }
    }, [user, refreshKey]);

    const checkUserPlan = async () => {
        setCheckingPlan(true);
        try {
            const response = await StudyBuddyAPI.getUserStudyPlans(1);
            if (response?.plans && response.plans.length > 0) {
                setPlanExists(true);
                setLatestPlanId(response.plans[0].plan?.plan_id);
            } else {
                setPlanExists(false);
                setLatestPlanId(null);
            }
        } catch (error) {
            console.error('Failed to check user plan:', error);
            setPlanExists(false);
        } finally {
            setCheckingPlan(false);
        }
    };

    const handleCreatePlan = () => {
        setShowPlanForm(true);
    };

    const handlePlanFormSubmit = async (config: any) => {
        setPlanGenerating(true);
        try {
            // Use 'user' as a special session_id to indicate user-level plan
            await StudyBuddyAPI.generateStudyPlan('user-plan', config);
            setShowPlanForm(false);
            setPlanExists(true);
            setSuccessMessage('Study plan created successfully! 🎉');
            setRefreshKey(prev => prev + 1);

            // Auto-hide success message
            setTimeout(() => setSuccessMessage(null), 5000);
        } catch (error) {
            console.error('Failed to generate study plan:', error);
            alert('Failed to generate study plan. Please try again.');
        } finally {
            setPlanGenerating(false);
        }
    };

    const handlePlanFormCancel = () => {
        setShowPlanForm(false);
    };

    // Show loading while checking auth
    if (isLoading || checkingPlan) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                    <div className="relative w-20 h-20 mx-auto mb-6">
                        <div className="absolute inset-0 bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-full animate-ping opacity-30" />
                        <div className="relative w-20 h-20 bg-gradient-to-r from-pink-500 to-fuchsia-500 rounded-full flex items-center justify-center">
                            <FiCalendar className="w-10 h-10 text-white" />
                        </div>
                    </div>
                    <p className="text-pink-600 font-medium animate-pulse">Loading Study Planner...</p>
                </div>
            </div>
        );
    }

    // Don't render if not authenticated
    if (!user) {
        return null;
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Link
                        href="/"
                        className="flex items-center space-x-2 text-gray-600 hover:text-pink-600 transition-colors"
                    >
                        <FiArrowLeft className="w-5 h-5" />
                        <span>Back to Home</span>
                    </Link>
                </div>
                <div className="flex items-center space-x-3">
                    <button
                        onClick={() => setRefreshKey(prev => prev + 1)}
                        className="btn-ghost flex items-center space-x-2"
                    >
                        <FiRefreshCw className="w-4 h-4" />
                        <span>Refresh</span>
                    </button>
                </div>
            </div>

            {/* Page Title */}
            <div className="text-center py-4">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-3xl shadow-xl shadow-pink-200/50 mb-4">
                    <FiCalendar className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Study Planner</h1>
                <p className="text-gray-600">Manage your personalized study schedule and track progress</p>
            </div>

            {/* Success Message */}
            {successMessage && (
                <div className="bg-green-100 border border-green-300 text-green-800 px-6 py-4 rounded-xl flex items-center justify-between animate-slide-up">
                    <div className="flex items-center space-x-3">
                        <span className="text-2xl">✅</span>
                        <span className="font-medium">{successMessage}</span>
                    </div>
                    <button
                        onClick={() => setSuccessMessage(null)}
                        className="text-green-600 hover:text-green-800"
                    >
                        ✕
                    </button>
                </div>
            )}

            {/* Main Content */}
            {planExists ? (
                <div className="space-y-6">
                    {/* Study Plan Viewer - using 'user-plan' as session ID for user-level plans */}
                    <StudyPlannerViewer key={refreshKey} sessionId="user-plan" />

                    {/* Update/Create New Button */}
                    <div className="text-center py-4">
                        <button
                            onClick={handleCreatePlan}
                            className="bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white px-8 py-4 rounded-xl font-medium hover:shadow-lg transition-all duration-300 flex items-center space-x-3 mx-auto"
                        >
                            <FiRefreshCw className="w-5 h-5" />
                            <span>Update Study Plan</span>
                        </button>
                    </div>
                </div>
            ) : (
                /* No Plan - Show Create Option */
                <div className="card bg-gradient-to-br from-pink-50 to-fuchsia-50 border-2 border-dashed border-pink-200 text-center py-12">
                    <div className="w-20 h-20 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                        <FiCalendar className="w-10 h-10 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-3">No Study Plan Yet</h2>
                    <p className="text-gray-500 text-lg mb-6 max-w-md mx-auto">
                        Create a personalized study plan to organize your learning journey and track your progress.
                    </p>
                    <button
                        onClick={handleCreatePlan}
                        className="btn-primary text-lg px-8 py-4 inline-flex items-center space-x-3"
                    >
                        <FiPlus className="w-5 h-5" />
                        <span>Create Study Plan</span>
                    </button>
                </div>
            )}

            {/* Study Plan Form Modal */}
            {showPlanForm && (
                <StudyPlanForm
                    onSubmit={handlePlanFormSubmit}
                    onCancel={handlePlanFormCancel}
                    isLoading={planGenerating}
                />
            )}

            {/* Help Section */}
            <div className="bg-gray-50 rounded-xl p-6 mt-8">
                <h3 className="font-semibold text-gray-900 mb-3">About Study Planner</h3>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div>
                        <h4 className="font-medium text-gray-900 mb-1">📅 Daily Tasks</h4>
                        <p className="text-gray-600">View and complete daily study tasks tailored to your goals</p>
                    </div>
                    <div>
                        <h4 className="font-medium text-gray-900 mb-1">📊 Progress Tracking</h4>
                        <p className="text-gray-600">Track your study streaks and overall progress</p>
                    </div>
                    <div>
                        <h4 className="font-medium text-gray-900 mb-1">🎯 Exam Preparation</h4>
                        <p className="text-gray-600">Aligned with your target exam date for optimal scheduling</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
