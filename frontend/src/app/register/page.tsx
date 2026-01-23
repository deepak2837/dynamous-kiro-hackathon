"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { FiEye, FiEyeOff, FiLoader, FiPhone, FiMail, FiUser, FiBook, FiArrowRight, FiArrowLeft, FiAlertCircle, FiCheck, FiBriefcase } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

const RegisterPage = () => {
  const [step, setStep] = useState<'form' | 'otp'>('form');
  const [formData, setFormData] = useState({
    name: '',
    mobile_number: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student' as 'student' | 'doctor',
    otp_method: 'sms' as 'sms' | 'email',
    college_name: '',
    course: '',
    year: undefined as number | undefined,
    exam_name: '',
    hospital_name: '',
    speciality: '',
    experience: '',
  });
  const [otp, setOtp] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { register, sendOTP, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      router.push('/');
    }
  }, [user, router]);

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('Name is required');
      return false;
    }
    if (!formData.mobile_number.trim()) {
      setError('Mobile number is required');
      return false;
    }
    const cleanMobile = formData.mobile_number.replace(/\D/g, '');
    if (cleanMobile.length < 10) {
      setError('Please enter a valid mobile number');
      return false;
    }
    if (formData.otp_method === 'email' && !formData.email.trim()) {
      setError('Email is required when using email OTP');
      return false;
    }
    if (formData.otp_method === 'email' && formData.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        setError('Please enter a valid email address');
        return false;
      }
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (formData.role === 'student') {
      if (!formData.college_name.trim()) {
        setError('College name is required for students');
        return false;
      }
      if (!formData.course.trim()) {
        setError('Course is required for students');
        return false;
      }
      if (formData.course === 'Preparing for Exam' && !formData.exam_name.trim()) {
        setError('Exam name is required when preparing for exam');
        return false;
      }
      if (formData.course !== 'Preparing for Exam' && !formData.year) {
        setError('Year is required for students');
        return false;
      }
    } else if (formData.role === 'doctor') {
      if (!formData.hospital_name.trim()) {
        setError('Hospital name is required for doctors');
        return false;
      }
      if (!formData.speciality.trim()) {
        setError('Speciality is required for doctors');
        return false;
      }
      if (!formData.experience.trim()) {
        setError('Experience is required for doctors');
        return false;
      }
    }
    return true;
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const success = await sendOTP(
        formData.mobile_number,
        formData.otp_method,
        formData.otp_method === 'email' ? formData.email : undefined
      );
      if (success) {
        toast.success(`OTP sent to your ${formData.otp_method === 'email' ? 'email' : 'mobile number'}`);
        setStep('otp');
      } else {
        setError('Failed to send OTP. Please try again.');
      }
    } catch (err) {
      setError('Error sending OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    setIsLoading(true);
    try {
      const registrationData = {
        name: formData.name,
        mobile_number: formData.mobile_number,
        email: formData.otp_method === 'email' ? formData.email : undefined,
        password: formData.password,
        role: formData.role,
        otp_method: formData.otp_method,
        college_name: formData.role === 'student' ? formData.college_name : undefined,
        course: formData.role === 'student' ? formData.course : undefined,
        year: formData.role === 'student' && formData.course !== 'Preparing for Exam' ? formData.year : undefined,
        exam_name: formData.role === 'student' && formData.course === 'Preparing for Exam' ? formData.exam_name : undefined,
        hospital_name: formData.role === 'doctor' ? formData.hospital_name : undefined,
        speciality: formData.role === 'doctor' ? formData.speciality : undefined,
        experience: formData.role === 'doctor' ? formData.experience : undefined,
      };

      const success = await register(registrationData);
      if (success) {
        toast.success('Registration successful!');
        router.push('/');
      } else {
        setError('Registration failed. Please try again.');
      }
    } catch (err) {
      setError('Error during registration. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const popularCourses = [
    'Preparing for Exam', 'MBBS', 'MD', 'BDS', 'BAMS', 'BHMS', 'BPT', 'BOT',
    'BSc Nursing', 'BSc Medical Lab Technology', 'BSc Radiology', 'Other'
  ];

  const popularExams = [
    'NEET PG', 'NEET UG', 'AIIMS PG', 'JIPMER PG', 'FMGE',
    'USMLE Step 1', 'USMLE Step 2 CK', 'PLAB', 'MCAT', 'Other'
  ];

  const yearOptions = [1, 2, 3, 4, 5, 6];

  const inputClass = "w-full px-4 py-3 pl-12 bg-white/70 backdrop-blur-md border-2 border-pink-200/50 rounded-xl text-gray-800 placeholder-pink-300 transition-all duration-300 focus:outline-none focus:border-pink-400 focus:ring-4 focus:ring-pink-200/50 focus:bg-white";
  const selectClass = "w-full px-4 py-3 bg-white/70 backdrop-blur-md border-2 border-pink-200/50 rounded-xl text-gray-800 transition-all duration-300 focus:outline-none focus:border-pink-400 focus:ring-4 focus:ring-pink-200/50 focus:bg-white";
  const labelClass = "block text-sm font-semibold text-gray-700 mb-2";

  return (
    <div className="min-h-[80vh] py-12 px-4 sm:px-6 lg:px-8">
      {/* Decorative Elements */}
      <div className="fixed top-32 left-10 w-48 h-48 bg-pink-300/20 rounded-full blur-3xl animate-float pointer-events-none" />
      <div className="fixed bottom-20 right-10 w-64 h-64 bg-fuchsia-300/20 rounded-full blur-3xl animate-float animation-delay-500 pointer-events-none" />

      <div className="max-w-2xl mx-auto relative">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="relative inline-block mb-6">
            <div className="absolute inset-0 bg-gradient-to-r from-pink-400 to-fuchsia-500 rounded-3xl blur-xl opacity-50 animate-pulse" />
            <div className="relative w-20 h-20 bg-gradient-to-br from-pink-500 to-fuchsia-500 rounded-3xl flex items-center justify-center shadow-2xl shadow-pink-300/50 mx-auto">
              <span className="text-4xl">✨</span>
            </div>
          </div>
          <h2 className="text-4xl font-extrabold gradient-text mb-2">
            Join StudyBuddy
          </h2>
          <p className="text-gray-600">Create your account and start learning smarter</p>
          <p className="mt-3 text-sm text-gray-500">
            Already have an account?{' '}
            <Link href="/login" className="font-semibold text-pink-600 hover:text-pink-700 transition-colors">
              Sign in here
            </Link>
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center mb-8 space-x-4">
          <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold text-sm transition-all duration-300 ${step === 'form' ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg shadow-pink-300/50' : 'bg-emerald-500 text-white'}`}>
            {step === 'otp' ? <FiCheck className="w-5 h-5" /> : '1'}
          </div>
          <div className={`w-16 h-1 rounded-full ${step === 'otp' ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500' : 'bg-pink-200'}`} />
          <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold text-sm transition-all duration-300 ${step === 'otp' ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg shadow-pink-300/50' : 'bg-pink-100 text-pink-400'}`}>
            2
          </div>
        </div>

        {/* Registration Card */}
        <div className="card !p-8 animate-slide-up">
          {step === 'form' && (
            <form onSubmit={handleFormSubmit} className="space-y-6">
              {/* Basic Info Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className={labelClass}>Full Name *</label>
                  <div className="relative">
                    <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pink-400" />
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className={inputClass}
                      placeholder="Enter your full name"
                    />
                  </div>
                </div>
                <div>
                  <label className={labelClass}>Mobile Number *</label>
                  <div className="relative">
                    <FiPhone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pink-400" />
                    <input
                      type="tel"
                      required
                      value={formData.mobile_number}
                      onChange={(e) => handleInputChange('mobile_number', e.target.value)}
                      className={inputClass}
                      placeholder="Enter mobile number"
                    />
                  </div>
                </div>
              </div>

              {/* OTP Method */}
              <div>
                <label className={labelClass}>OTP Verification Method *</label>
                <div className="flex bg-pink-100/50 p-1.5 rounded-xl">
                  <button
                    type="button"
                    onClick={() => handleInputChange('otp_method', 'sms')}
                    className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-300 flex items-center justify-center space-x-2 ${formData.otp_method === 'sms' ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg' : 'text-pink-600 hover:bg-white/50'}`}
                  >
                    <FiPhone className="w-4 h-4" />
                    <span>SMS</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInputChange('otp_method', 'email')}
                    className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-300 flex items-center justify-center space-x-2 ${formData.otp_method === 'email' ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg' : 'text-pink-600 hover:bg-white/50'}`}
                  >
                    <FiMail className="w-4 h-4" />
                    <span>Email</span>
                  </button>
                </div>
              </div>

              {/* Email (if needed) */}
              {formData.otp_method === 'email' && (
                <div className="animate-slide-down">
                  <label className={labelClass}>Email Address *</label>
                  <div className="relative">
                    <FiMail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pink-400" />
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className={inputClass}
                      placeholder="Enter your email"
                    />
                  </div>
                </div>
              )}

              {/* Password Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className={labelClass}>Password *</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      className="w-full px-4 py-3 pr-12 bg-white/70 backdrop-blur-md border-2 border-pink-200/50 rounded-xl text-gray-800 transition-all focus:outline-none focus:border-pink-400 focus:ring-4 focus:ring-pink-200/50"
                      placeholder="Create password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-pink-400 hover:text-pink-600"
                    >
                      {showPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className={labelClass}>Confirm Password *</label>
                  <div className="relative">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      required
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      className="w-full px-4 py-3 pr-12 bg-white/70 backdrop-blur-md border-2 border-pink-200/50 rounded-xl text-gray-800 transition-all focus:outline-none focus:border-pink-400 focus:ring-4 focus:ring-pink-200/50"
                      placeholder="Confirm password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-pink-400 hover:text-pink-600"
                    >
                      {showConfirmPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Role Selection */}
              <div>
                <label className={labelClass}>I am a *</label>
                <div className="flex bg-pink-100/50 p-1.5 rounded-xl">
                  <button
                    type="button"
                    onClick={() => handleInputChange('role', 'student')}
                    className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-300 flex items-center justify-center space-x-2 ${formData.role === 'student' ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg' : 'text-pink-600 hover:bg-white/50'}`}
                  >
                    <FiBook className="w-4 h-4" />
                    <span>Student</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInputChange('role', 'doctor')}
                    className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-300 flex items-center justify-center space-x-2 ${formData.role === 'doctor' ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg' : 'text-pink-600 hover:bg-white/50'}`}
                  >
                    <FiBriefcase className="w-4 h-4" />
                    <span>Doctor</span>
                  </button>
                </div>
              </div>

              {/* Student Fields */}
              {formData.role === 'student' && (
                <div className="space-y-4 border-t-2 border-pink-100 pt-6 animate-slide-down">
                  <h3 className="text-lg font-bold gradient-text flex items-center">
                    <FiBook className="mr-2" /> Student Information
                  </h3>
                  <div>
                    <label className={labelClass}>College Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.college_name}
                      onChange={(e) => handleInputChange('college_name', e.target.value)}
                      className="input-field"
                      placeholder="Enter your college name"
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Course *</label>
                    <select
                      required
                      value={formData.course}
                      onChange={(e) => handleInputChange('course', e.target.value)}
                      className={selectClass}
                    >
                      <option value="">Select your course</option>
                      {popularCourses.map((course) => (
                        <option key={course} value={course}>{course}</option>
                      ))}
                    </select>
                  </div>
                  {formData.course === 'Preparing for Exam' ? (
                    <div>
                      <label className={labelClass}>Exam Name *</label>
                      <select
                        required
                        value={formData.exam_name}
                        onChange={(e) => handleInputChange('exam_name', e.target.value)}
                        className={selectClass}
                      >
                        <option value="">Select exam</option>
                        {popularExams.map((exam) => (
                          <option key={exam} value={exam}>{exam}</option>
                        ))}
                      </select>
                    </div>
                  ) : formData.course && (
                    <div>
                      <label className={labelClass}>Year of Study *</label>
                      <select
                        required
                        value={formData.year || ''}
                        onChange={(e) => handleInputChange('year', parseInt(e.target.value))}
                        className={selectClass}
                      >
                        <option value="">Select year</option>
                        {yearOptions.map((year) => (
                          <option key={year} value={year}>
                            {year === 1 ? '1st Year' : year === 2 ? '2nd Year' : year === 3 ? '3rd Year' : `${year}th Year`}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              )}

              {/* Doctor Fields */}
              {formData.role === 'doctor' && (
                <div className="space-y-4 border-t-2 border-pink-100 pt-6 animate-slide-down">
                  <h3 className="text-lg font-bold gradient-text flex items-center">
                    <FiBriefcase className="mr-2" /> Doctor Information
                  </h3>
                  <div>
                    <label className={labelClass}>Hospital Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.hospital_name}
                      onChange={(e) => handleInputChange('hospital_name', e.target.value)}
                      className="input-field"
                      placeholder="Enter your hospital name"
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Speciality *</label>
                    <input
                      type="text"
                      required
                      value={formData.speciality}
                      onChange={(e) => handleInputChange('speciality', e.target.value)}
                      className="input-field"
                      placeholder="Enter your speciality"
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Experience *</label>
                    <select
                      required
                      value={formData.experience}
                      onChange={(e) => handleInputChange('experience', e.target.value)}
                      className={selectClass}
                    >
                      <option value="">Select experience</option>
                      <option value="0-1 years">0-1 years</option>
                      <option value="1-3 years">1-3 years</option>
                      <option value="3-5 years">3-5 years</option>
                      <option value="5-10 years">5-10 years</option>
                      <option value="10+ years">10+ years</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="flex items-center space-x-2 text-rose-600 bg-rose-50 rounded-xl p-4 border border-rose-200 animate-slide-up">
                  <FiAlertCircle className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm font-medium">{error}</span>
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary py-4 text-lg font-bold flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <><FiLoader className="w-5 h-5 animate-spin" /><span>Sending OTP...</span></>
                ) : (
                  <><span>Continue</span><FiArrowRight className="w-5 h-5" /></>
                )}
              </button>
            </form>
          )}

          {/* OTP Step */}
          {step === 'otp' && (
            <form onSubmit={handleOTPSubmit} className="space-y-6 animate-slide-up">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-fuchsia-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-pink-300/50">
                  <span className="text-3xl">🔐</span>
                </div>
                <h3 className="text-2xl font-bold gradient-text">Verify OTP</h3>
                <p className="text-gray-600 mt-2">
                  Enter the 6-digit code sent to your {formData.otp_method === 'email' ? 'email' : 'mobile'}
                </p>
              </div>

              <div>
                <input
                  type="text"
                  maxLength={6}
                  required
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  className="w-full px-6 py-5 bg-white/80 border-3 border-pink-300 rounded-2xl text-center text-3xl font-bold tracking-[0.5em] text-pink-600 transition-all focus:outline-none focus:border-pink-500 focus:ring-4 focus:ring-pink-200/50"
                  placeholder="••••••"
                />
              </div>

              {error && (
                <div className="flex items-center space-x-2 text-rose-600 bg-rose-50 rounded-xl p-4 border border-rose-200">
                  <FiAlertCircle className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm font-medium">{error}</span>
                </div>
              )}

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setStep('form')}
                  className="btn-secondary flex-1 flex items-center justify-center space-x-2"
                >
                  <FiArrowLeft className="w-5 h-5" />
                  <span>Back</span>
                </button>
                <button
                  type="submit"
                  disabled={isLoading || otp.length !== 6}
                  className="btn-primary flex-1 flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <><FiLoader className="w-5 h-5 animate-spin" /><span>Creating...</span></>
                  ) : (
                    <><span>Create Account</span><FiCheck className="w-5 h-5" /></>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
