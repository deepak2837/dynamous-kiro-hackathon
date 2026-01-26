/**
 * Study Buddy File Upload Component
 * 
 * Provides comprehensive file upload functionality for medical study materials.
 * Supports drag-and-drop, file validation, processing mode selection, and
 * topic-based content generation for MBBS exam preparation.
 * 
 * Features:
 * - Multi-format file support (PDF, images, PPTX)
 * - Drag-and-drop interface with visual feedback
 * - File size and type validation
 * - Processing mode selection (AI-only)
 * - Topic-based text input mode
 * - Email notification options
 * - Upload restrictions and rate limiting
 * - Real-time file preview and management
 * 
 * @component
 * @param {FileUploadProps} props - Component props
 * @param {Function} props.onUploadSuccess - Callback when upload succeeds
 * @param {Function} props.onUploadError - Callback when upload fails
 * @returns {JSX.Element} File upload interface with drag-and-drop zone
 * 
 * @example
 * ```tsx
 * <FileUpload
 *   onUploadSuccess={(sessionId) => console.log('Uploaded:', sessionId)}
 *   onUploadError={(error) => console.error('Error:', error)}
 * />
 * ```
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { ProcessingMode } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';
import { useAuth } from '@/contexts/AuthContext';
import { FiUploadCloud, FiFile, FiX, FiMail, FiEdit3, FiZap } from 'react-icons/fi';

/**
 * Props for the FileUpload component
 */
interface FileUploadProps {
  /** Callback function called when upload succeeds with session ID */
  onUploadSuccess: (sessionId: string) => void;
  /** Callback function called when upload fails with error message */
  onUploadError: (error: string) => void;
}

/**
 * File size limits configuration from backend
 */
interface FileLimits {
  pdf: { max_size_mb: number; description: string };
  image: { max_size_mb: number; description: string };
  slide: { max_size_mb: number; description: string };
}

export default function FileUpload({ onUploadSuccess, onUploadError }: FileUploadProps) {
  const { user } = useAuth();
  const [files, setFiles] = useState<File[]>([]);
  const [processingMode, setProcessingMode] = useState<ProcessingMode>(ProcessingMode.AI_ONLY);
  const [isUploading, setIsUploading] = useState(false);
  const [fileLimits, setFileLimits] = useState<FileLimits | null>(null);
  const [uploadRestriction, setUploadRestriction] = useState<{
    allowed: boolean;
    message?: string;
    remainingSeconds?: number;
  }>({ allowed: true });
  const [countdown, setCountdown] = useState<number>(0);
  const [inputMode, setInputMode] = useState<'file' | 'topic'>('file');
  const [topicInput, setTopicInput] = useState<string>('');
  const [notifyByEmail, setNotifyByEmail] = useState<boolean>(false);
  const [notificationEmail, setNotificationEmail] = useState<string>('');

  // Get user ID from authenticated user
  const userId = user?.id || '';

  // Don't render if no user - show authentication prompt
  if (!user) {
    return (
      <div className="card text-center p-12">
        <div className="text-6xl mb-4 animate-float">🔐</div>
        <p className="text-gray-600 text-lg">Please login to upload files.</p>
      </div>
    );
  }

  // Fetch file limits on component mount
  useEffect(() => {
    const fetchFileLimits = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/upload/file-limits`);
        const data = await response.json();
        setFileLimits(data.limits);
      } catch (error) {
        console.error('Failed to fetch file limits:', error);
      }
    };
    fetchFileLimits();
  }, []);

  const getFileTypeCategory = (filename: string): keyof FileLimits | null => {
    const ext = filename.toLowerCase().split('.').pop();
    switch (ext) {
      case 'pdf':
        return 'pdf';
      case 'jpg':
      case 'jpeg':
      case 'png':
        return 'image';
      case 'pptx':
      case 'ppt':
        return 'slide';
      default:
        return null;
    }
  };

  const validateFileSize = (file: File): string | null => {
    if (!fileLimits) return null;

    const category = getFileTypeCategory(file.name);
    if (!category) {
      return `File type not supported. Allowed: PDF, JPG, PNG, PPTX`;
    }

    const limit = fileLimits[category];
    const fileSizeMB = file.size / (1024 * 1024);

    if (fileSizeMB > limit.max_size_mb) {
      return `${limit.description} file '${file.name}' is too large (${fileSizeMB.toFixed(1)}MB). Maximum allowed: ${limit.max_size_mb}MB`;
    }

    return null;
  };

  // Check upload restrictions on component mount and periodically
  const checkUploadRestrictions = useCallback(async () => {
    try {
      const response = await StudyBuddyAPI.checkUploadAllowed(userId);
      setUploadRestriction({
        allowed: response.upload_allowed,
        message: response.message,
        remainingSeconds: response.remaining_seconds
      });

      if (response.remaining_seconds && response.remaining_seconds > 0) {
        setCountdown(response.remaining_seconds);
      }
    } catch (error) {
      console.error('Failed to check upload restrictions:', error);
    }
  }, [userId]);

  useEffect(() => {
    checkUploadRestrictions();
  }, [checkUploadRestrictions]);

  // Countdown timer
  useEffect(() => {
    if (countdown > 0) {
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            checkUploadRestrictions(); // Recheck when countdown ends
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [countdown, checkUploadRestrictions]);

  const formatCountdown = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  };

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (!uploadRestriction.allowed) {
      onUploadError(uploadRestriction.message || 'Upload not allowed at this time');
      return;
    }

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map(({ file, errors }) => {
        const errorMessages = errors.map((e: any) => {
          if (e.code === 'file-too-large') {
            return `File '${file.name}' is too large`;
          }
          if (e.code === 'file-invalid-type') {
            return `File '${file.name}' has unsupported type`;
          }
          return e.message;
        });
        return errorMessages.join(', ');
      });
      onUploadError(errors.join('; '));
      return;
    }

    // Validate file sizes with specific limits
    const validationErrors: string[] = [];
    const validFiles: File[] = [];

    // Count images in new files
    const newImageFiles = acceptedFiles.filter(file => {
      const ext = file.name.toLowerCase().split('.').pop();
      return ['jpg', 'jpeg', 'png'].includes(ext || '');
    });

    // Count existing images
    const existingImages = files.filter(file => {
      const ext = file.name.toLowerCase().split('.').pop();
      return ['jpg', 'jpeg', 'png'].includes(ext || '');
    });

    const totalImages = existingImages.length + newImageFiles.length;
    const maxImages = 25; // From backend config

    if (totalImages > maxImages) {
      onUploadError(`Too many images. Maximum ${maxImages} images allowed. You have ${existingImages.length} images and trying to add ${newImageFiles.length} more.`);
      return;
    }

    acceptedFiles.forEach(file => {
      const error = validateFileSize(file);
      if (error) {
        validationErrors.push(error);
      } else {
        validFiles.push(file);
      }
    });

    if (validationErrors.length > 0) {
      onUploadError(validationErrors.join('; '));
      return;
    }

    setFiles(prev => [...prev, ...validFiles]);
  }, [uploadRestriction.allowed, uploadRestriction.message, onUploadError, validateFileSize]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt']
    },
    maxSize: 100 * 1024 * 1024, // 100MB (will be validated more specifically)
    disabled: !uploadRestriction.allowed
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      onUploadError('Please select at least one file');
      return;
    }

    if (!uploadRestriction.allowed) {
      onUploadError(uploadRestriction.message || 'Upload not allowed at this time');
      return;
    }

    setIsUploading(true);
    try {
      const response = await StudyBuddyAPI.uploadFiles(files, processingMode, userId);

      // Enable email notification if requested
      if (notifyByEmail && notificationEmail.trim()) {
        try {
          await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/upload/enable-notification/${response.session_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: notificationEmail.trim() })
          });
        } catch (e) {
          console.error('Failed to enable email notification:', e);
        }
      }

      onUploadSuccess(response.session_id);

      // Reset form
      setFiles([]);
      setNotifyByEmail(false);
      setNotificationEmail('');

      // Recheck restrictions after successful upload
      setTimeout(checkUploadRestrictions, 1000);
    } catch (error: any) {
      const errorDetail = error.response?.data?.detail;
      if (typeof errorDetail === 'object' && errorDetail.restriction_active) {
        onUploadError(errorDetail.message);
        setCountdown(errorDetail.remaining_seconds || 0);
        checkUploadRestrictions();
      } else {
        onUploadError(typeof errorDetail === 'string' ? errorDetail : 'Upload failed');
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleTopicSubmit = async () => {
    if (!topicInput || topicInput.trim().length < 3) {
      onUploadError('Please enter a topic with at least 3 characters');
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('topic', topicInput.trim());
      formData.append('user_id', userId);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/text-input/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to submit topic');
      }

      const data = await response.json();

      // Enable email notification if requested
      if (notifyByEmail && notificationEmail.trim()) {
        try {
          await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/upload/enable-notification/${data.session_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: notificationEmail.trim() })
          });
        } catch (e) {
          console.error('Failed to enable email notification:', e);
        }
      }

      onUploadSuccess(data.session_id);
      setTopicInput('');
      setNotifyByEmail(false);
      setNotificationEmail('');
    } catch (error: any) {
      onUploadError(error.message || 'Failed to process topic');
    } finally {
      setIsUploading(false);
    }
  };

  const isUploadDisabled = (inputMode === 'file' ? files.length === 0 : topicInput.trim().length < 3) || isUploading || !uploadRestriction.allowed;

  const topicSuggestions = ['Heart anatomy', 'Diabetes mellitus', 'Cranial nerves', 'Respiratory pathology', 'Antibiotics'];

  return (
    <div className="space-y-6">
      {/* Input Mode Toggle */}
      <div className="flex bg-pink-100/50 backdrop-blur-sm p-1.5 rounded-2xl">
        <button
          onClick={() => setInputMode('file')}
          className={`flex-1 py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center space-x-2 ${inputMode === 'file'
            ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg shadow-pink-300/50'
            : 'text-pink-600 hover:bg-white/50'
            }`}
        >
          <FiUploadCloud className="w-5 h-5" />
          <span>Upload Files</span>
        </button>
        <button
          onClick={() => setInputMode('topic')}
          className={`flex-1 py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center space-x-2 ${inputMode === 'topic'
            ? 'bg-gradient-to-r from-pink-500 to-fuchsia-500 text-white shadow-lg shadow-pink-300/50'
            : 'text-pink-600 hover:bg-white/50'
            }`}
        >
          <FiEdit3 className="w-5 h-5" />
          <span>Enter Topic</span>
        </button>
      </div>

      {/* Upload Restriction Warning */}
      {!uploadRestriction.allowed && (
        <div className="bg-amber-50/80 backdrop-blur-sm border-2 border-amber-200 rounded-2xl p-5 animate-slide-up">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
            <div>
              <p className="text-amber-800 font-semibold">Upload Restricted</p>
              <p className="text-amber-700 text-sm">
                {uploadRestriction.message}
                {countdown > 0 && (
                  <span className="font-mono ml-2 bg-amber-200 px-2 py-0.5 rounded-lg">({formatCountdown(countdown)})</span>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Topic Input Mode */}
      {inputMode === 'topic' && (
        <div className="space-y-5 animate-slide-up">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Enter a medical topic to generate study materials
            </label>
            <input
              type="text"
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              placeholder="e.g., Heart anatomy, Diabetes management, Cranial nerves..."
              className="input-field text-lg"
              disabled={!uploadRestriction.allowed}
            />
            <p className="text-sm text-pink-400 mt-2">
              The AI will generate questions, notes, mnemonics, cheat sheets, and mock tests about this topic.
            </p>
          </div>

          <div className="card-glass !p-5">
            <h4 className="font-semibold text-pink-700 mb-3 flex items-center">
              <span className="mr-2">💡</span> Topic Ideas
            </h4>
            <div className="flex flex-wrap gap-2">
              {topicSuggestions.map(topic => (
                <button
                  key={topic}
                  onClick={() => setTopicInput(topic)}
                  className="text-sm px-4 py-2 bg-white border-2 border-pink-200 rounded-full text-pink-600 
                           hover:bg-pink-50 hover:border-pink-300 hover:scale-105 transition-all duration-200"
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* File Drop Zone - Only show in file mode */}
      {inputMode === 'file' && (
        <div
          {...getRootProps()}
          className={`relative border-3 border-dashed rounded-3xl p-10 text-center cursor-pointer transition-all duration-300 overflow-hidden
            ${!uploadRestriction.allowed
              ? 'border-gray-200 bg-gray-50/50 cursor-not-allowed'
              : isDragActive
                ? 'border-pink-500 bg-gradient-to-br from-pink-100/70 to-fuchsia-100/70 scale-[1.02] shadow-2xl shadow-pink-200/50'
                : 'border-pink-300/60 bg-gradient-to-br from-pink-50/50 to-fuchsia-50/50 hover:border-pink-400 hover:shadow-xl hover:shadow-pink-200/30'
            }`}
        >
          <input {...getInputProps()} />

          {/* Background decoration */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-4 right-4 w-20 h-20 bg-pink-200/30 rounded-full blur-2xl" />
            <div className="absolute bottom-4 left-4 w-24 h-24 bg-fuchsia-200/30 rounded-full blur-2xl" />
          </div>

          <div className="relative space-y-4">
            <div className={`text-6xl ${isDragActive ? 'animate-bounce' : 'animate-float'}`}>
              {isDragActive ? '📥' : '📁'}
            </div>
            {!uploadRestriction.allowed ? (
              <p className="text-gray-400 font-medium">Upload temporarily disabled</p>
            ) : isDragActive ? (
              <p className="text-pink-600 font-semibold text-lg">Drop the files here...</p>
            ) : (
              <div>
                <p className="text-gray-700 text-lg mb-2">
                  Drag & drop files here, or <span className="text-pink-600 font-semibold">click to select</span>
                </p>
                <p className="text-sm text-pink-400">
                  Supports PDF, JPG, PNG, PPTX (max 25 images per upload)
                </p>
                {fileLimits && (
                  <div className="flex justify-center gap-4 text-xs text-gray-400 mt-3">
                    <span className="bg-white/70 px-3 py-1 rounded-full">PDF: {fileLimits.pdf.max_size_mb}MB</span>
                    <span className="bg-white/70 px-3 py-1 rounded-full">Images: {fileLimits.image.max_size_mb}MB</span>
                    <span className="bg-white/70 px-3 py-1 rounded-full">Slides: {fileLimits.slide.max_size_mb}MB</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Selected Files - Only show in file mode */}
      {inputMode === 'file' && files.length > 0 && (
        <div className="space-y-3 animate-slide-up">
          <h3 className="font-semibold text-gray-900 flex items-center">
            <FiFile className="mr-2 text-pink-500" />
            Selected Files ({files.length})
          </h3>
          <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-white/70 backdrop-blur-sm p-4 rounded-xl border border-pink-100 group hover:shadow-md transition-all duration-200"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-xl flex items-center justify-center">
                    <span className="text-white text-sm">📄</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-pink-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-2 text-gray-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-all duration-200"
                  disabled={!uploadRestriction.allowed}
                >
                  <FiX className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Mode Selection - Only for file upload */}
      {inputMode === 'file' && (
        <div className="space-y-3">
          <h3 className="font-semibold text-gray-900">Processing Mode</h3>
          <label className="flex items-center space-x-4 p-4 bg-white/70 backdrop-blur-sm rounded-xl border-2 border-pink-200 cursor-pointer hover:border-pink-300 transition-all duration-200">
            <div className="relative">
              <input
                type="radio"
                name="processingMode"
                value={ProcessingMode.AI_ONLY}
                checked={processingMode === ProcessingMode.AI_ONLY}
                onChange={(e) => setProcessingMode(e.target.value as ProcessingMode)}
                className="sr-only"
                disabled={!uploadRestriction.allowed}
              />
              <div className={`w-5 h-5 rounded-full border-2 transition-all duration-200 ${processingMode === ProcessingMode.AI_ONLY ? 'border-pink-500 bg-pink-500' : 'border-pink-300'}`}>
                {processingMode === ProcessingMode.AI_ONLY && (
                  <div className="w-2 h-2 bg-white rounded-full mx-auto mt-1" />
                )}
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-fuchsia-500 rounded-xl flex items-center justify-center">
                <FiZap className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-semibold text-gray-900">AI Only Mode</span>
                <p className="text-sm text-gray-500">Direct AI processing for digital documents</p>
              </div>
            </div>
          </label>
        </div>
      )}

      {/* Email Notification Option */}
      <div className="card-glass !p-5">
        <label className="flex items-start space-x-4 cursor-pointer">
          <div className="relative mt-0.5">
            <input
              type="checkbox"
              checked={notifyByEmail}
              onChange={(e) => setNotifyByEmail(e.target.checked)}
              className="sr-only"
              disabled={!uploadRestriction.allowed || isUploading}
            />
            <div className={`w-6 h-6 rounded-lg border-2 transition-all duration-200 flex items-center justify-center
              ${notifyByEmail ? 'bg-gradient-to-br from-pink-500 to-fuchsia-500 border-pink-500' : 'border-pink-300 bg-white'}`}>
              {notifyByEmail && (
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </div>
          <div className="flex-1">
            <span className="font-semibold text-pink-700 flex items-center">
              <FiMail className="mr-2" />
              Get notified by email when processing is complete
            </span>
            <p className="text-sm text-pink-500 mt-1">
              Processing can take a few minutes. We'll email you when your study materials are ready.
            </p>
          </div>
        </label>

        {notifyByEmail && (
          <div className="mt-4 ml-10 animate-slide-down">
            <input
              type="email"
              value={notificationEmail}
              onChange={(e) => setNotificationEmail(e.target.value)}
              placeholder="Enter your email address"
              className="input-field"
              disabled={!uploadRestriction.allowed || isUploading}
            />
          </div>
        )}
      </div>

      {/* Submit Button */}
      <button
        onClick={inputMode === 'file' ? handleUpload : handleTopicSubmit}
        disabled={isUploadDisabled}
        className={`w-full py-4 px-6 rounded-2xl font-bold text-lg transition-all duration-300 
          ${isUploadDisabled
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'btn-primary'
          }`}
      >
        {isUploading ? (
          <div className="flex items-center justify-center space-x-3">
            <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Processing...</span>
          </div>
        ) : !uploadRestriction.allowed ? (
          `Upload Restricted ${countdown > 0 ? `(${formatCountdown(countdown)})` : ''}`
        ) : inputMode === 'file' ? (
          <span className="flex items-center justify-center space-x-2">
            <FiUploadCloud className="w-5 h-5" />
            <span>Upload & Process {files.length > 0 ? `(${files.length} files)` : ''}</span>
          </span>
        ) : (
          <span className="flex items-center justify-center space-x-2">
            <FiZap className="w-5 h-5" />
            <span>Generate Study Materials</span>
          </span>
        )}
      </button>
    </div>
  );
}
