"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { FiEye, FiEyeOff, FiLoader, FiPhone, FiMail, FiUser, FiBook } from 'react-icons/fi';
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
    // Student fields
    college_name: '',
    course: '',
    year: undefined as number | undefined,
    exam_name: '',
    // Doctor fields
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

  // Redirect if already authenticated
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

    // Role-specific validation
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

    if (!validateForm()) {
      return;
    }

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
      // Prepare registration data
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
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(''); // Clear error when user starts typing
  };

  const popularCourses = [
    'Preparing for Exam',
    'MBBS',
    'MD',
    'BDS',
    'BAMS',
    'BHMS',
    'BPT',
    'BOT',
    'BSc Nursing',
    'BSc Medical Lab Technology',
    'BSc Radiology',
    'BSc Optometry',
    'BSc Physiotherapy',
    'BSc Occupational Therapy',
    'Other'
  ];

  const popularExams = [
    'NEET PG',
    'NEET UG',
    'AIIMS PG',
    'JIPMER PG',
    'FMGE',
    'USMLE Step 1',
    'USMLE Step 2 CK',
    'PLAB',
    'MCAT',
    'Other'
  ];

  const yearOptions = [1, 2, 3, 4, 5, 6];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your StudyBuddy account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
              Sign in here
            </Link>
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          {step === 'form' && (
            <form onSubmit={handleFormSubmit} className="space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Full Name *
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="name"
                      name="name"
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="appearance-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter your full name"
                    />
                    <FiUser className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  </div>
                </div>

                <div>
                  <label htmlFor="mobile" className="block text-sm font-medium text-gray-700">
                    Mobile Number *
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="mobile"
                      name="mobile"
                      type="tel"
                      required
                      value={formData.mobile_number}
                      onChange={(e) => handleInputChange('mobile_number', e.target.value)}
                      className="appearance-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter your mobile number"
                    />
                    <FiPhone className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  </div>
                </div>
              </div>

              {/* OTP Method Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  How would you like to receive OTP? *
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="sms"
                      checked={formData.otp_method === 'sms'}
                      onChange={(e) => handleInputChange('otp_method', e.target.value)}
                      className="mr-2"
                    />
                    <FiPhone className="mr-1" />
                    SMS
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="email"
                      checked={formData.otp_method === 'email'}
                      onChange={(e) => handleInputChange('otp_method', e.target.value)}
                      className="mr-2"
                    />
                    <FiMail className="mr-1" />
                    Email
                  </label>
                </div>
              </div>

              {/* Email field (conditional) */}
              {formData.otp_method === 'email' && (
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email Address *
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className="appearance-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter your email address"
                    />
                    <FiMail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  </div>
                </div>
              )}

              {/* Password Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                    Password *
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <FiEyeOff /> : <FiEye />}
                    </button>
                  </div>
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                    Confirm Password *
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      required
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      className="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Confirm password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Role Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  I am a *
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="student"
                      checked={formData.role === 'student'}
                      onChange={(e) => handleInputChange('role', e.target.value)}
                      className="mr-2"
                    />
                    <FiBook className="mr-1" />
                    Student
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="doctor"
                      checked={formData.role === 'doctor'}
                      onChange={(e) => handleInputChange('role', e.target.value)}
                      className="mr-2"
                    />
                    <FiUser className="mr-1" />
                    Doctor
                  </label>
                </div>
              </div>

              {/* Student Fields */}
              {formData.role === 'student' && (
                <div className="space-y-4 border-t pt-4">
                  <h3 className="text-lg font-medium text-gray-900">Student Information</h3>
                  
                  <div>
                    <label htmlFor="college_name" className="block text-sm font-medium text-gray-700">
                      College Name *
                    </label>
                    <input
                      id="college_name"
                      name="college_name"
                      type="text"
                      required
                      value={formData.college_name}
                      onChange={(e) => handleInputChange('college_name', e.target.value)}
                      className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter your college name"
                    />
                  </div>

                  <div>
                    <label htmlFor="course" className="block text-sm font-medium text-gray-700">
                      Course *
                    </label>
                    <select
                      id="course"
                      name="course"
                      required
                      value={formData.course}
                      onChange={(e) => handleInputChange('course', e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    >
                      <option value="">Select your course</option>
                      {popularCourses.map((course) => (
                        <option key={course} value={course}>
                          {course}
                        </option>
                      ))}
                    </select>
                  </div>

                  {formData.course === 'Preparing for Exam' ? (
                    <div>
                      <label htmlFor="exam_name" className="block text-sm font-medium text-gray-700">
                        Exam Name *
                      </label>
                      <select
                        id="exam_name"
                        name="exam_name"
                        required
                        value={formData.exam_name}
                        onChange={(e) => handleInputChange('exam_name', e.target.value)}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      >
                        <option value="">Select exam</option>
                        {popularExams.map((exam) => (
                          <option key={exam} value={exam}>
                            {exam}
                          </option>
                        ))}
                      </select>
                    </div>
                  ) : formData.course && (
                    <div>
                      <label htmlFor="year" className="block text-sm font-medium text-gray-700">
                        Year of Study *
                      </label>
                      <select
                        id="year"
                        name="year"
                        required
                        value={formData.year || ''}
                        onChange={(e) => handleInputChange('year', parseInt(e.target.value))}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
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
                <div className="space-y-4 border-t pt-4">
                  <h3 className="text-lg font-medium text-gray-900">Doctor Information</h3>
                  
                  <div>
                    <label htmlFor="hospital_name" className="block text-sm font-medium text-gray-700">
                      Hospital Name *
                    </label>
                    <input
                      id="hospital_name"
                      name="hospital_name"
                      type="text"
                      required
                      value={formData.hospital_name}
                      onChange={(e) => handleInputChange('hospital_name', e.target.value)}
                      className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter your hospital name"
                    />
                  </div>

                  <div>
                    <label htmlFor="speciality" className="block text-sm font-medium text-gray-700">
                      Speciality *
                    </label>
                    <input
                      id="speciality"
                      name="speciality"
                      type="text"
                      required
                      value={formData.speciality}
                      onChange={(e) => handleInputChange('speciality', e.target.value)}
                      className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter your speciality"
                    />
                  </div>

                  <div>
                    <label htmlFor="experience" className="block text-sm font-medium text-gray-700">
                      Experience *
                    </label>
                    <select
                      id="experience"
                      name="experience"
                      required
                      value={formData.experience}
                      onChange={(e) => handleInputChange('experience', e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
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

              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <FiLoader className="animate-spin h-5 w-5 mx-auto" />
                ) : (
                  'Send OTP'
                )}
              </button>
            </form>
          )}

          {step === 'otp' && (
            <form onSubmit={handleOTPSubmit} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Verify OTP</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Enter the 6-digit OTP sent to your {formData.otp_method === 'email' ? 'email' : 'mobile number'}
                </p>
                
                <label htmlFor="otp" className="block text-sm font-medium text-gray-700">
                  OTP Code
                </label>
                <input
                  id="otp"
                  name="otp"
                  type="text"
                  maxLength={6}
                  required
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-center text-lg tracking-widest"
                  placeholder="000000"
                />
              </div>

              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setStep('form')}
                  className="flex-1 py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading || otp.length !== 6}
                  className="flex-1 py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <FiLoader className="animate-spin h-5 w-5 mx-auto" />
                  ) : (
                    'Create Account'
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
