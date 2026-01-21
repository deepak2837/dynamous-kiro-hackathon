'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { ProcessingMode } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';
import { useAuth } from '@/contexts/AuthContext';

interface FileUploadProps {
  onUploadSuccess: (sessionId: string) => void;
  onUploadError: (error: string) => void;
}

interface FileLimits {
  pdf: { max_size_mb: number; description: string };
  image: { max_size_mb: number; description: string };
  slide: { max_size_mb: number; description: string };
}

export default function FileUpload({ onUploadSuccess, onUploadError }: FileUploadProps) {
  const { user } = useAuth();
  const [files, setFiles] = useState<File[]>([]);
  const [processingMode, setProcessingMode] = useState<ProcessingMode>(ProcessingMode.OCR_AI);
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

  // Get user ID from authenticated user
  const userId = user?.id || '';

  // Don't render if no user
  if (!user) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600">Please login to upload files.</p>
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
      onUploadSuccess(response.session_id);

      // Reset form
      setFiles([]);

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
      onUploadSuccess(data.session_id);
      setTopicInput('');
    } catch (error: any) {
      onUploadError(error.message || 'Failed to process topic');
    } finally {
      setIsUploading(false);
    }
  };

  const isUploadDisabled = (inputMode === 'file' ? files.length === 0 : topicInput.trim().length < 3) || isUploading || !uploadRestriction.allowed;

  return (
    <div className="space-y-6">
      {/* Input Mode Toggle */}
      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setInputMode('file')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${inputMode === 'file'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
        >
          📁 Upload Files
        </button>
        <button
          onClick={() => setInputMode('topic')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${inputMode === 'topic'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
        >
          ✏️ Enter Topic
        </button>
      </div>

      {/* Upload Restriction Warning */}
      {!uploadRestriction.allowed && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-yellow-600">⚠️</span>
            <div>
              <p className="text-yellow-800 font-medium">Upload Restricted</p>
              <p className="text-yellow-700 text-sm">
                {uploadRestriction.message}
                {countdown > 0 && (
                  <span className="font-mono ml-2">({formatCountdown(countdown)})</span>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Topic Input Mode */}
      {inputMode === 'topic' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter a medical topic to generate study materials
            </label>
            <input
              type="text"
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              placeholder="e.g., Heart anatomy, Diabetes management, Cranial nerves..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={!uploadRestriction.allowed}
            />
            <p className="text-sm text-gray-500 mt-2">
              The AI will generate questions, notes, mnemonics, cheat sheets, and mock tests about this topic.
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">💡 Topic Ideas</h4>
            <div className="flex flex-wrap gap-2">
              {['Heart anatomy', 'Diabetes mellitus', 'Cranial nerves', 'Respiratory pathology', 'Antibiotics'].map(topic => (
                <button
                  key={topic}
                  onClick={() => setTopicInput(topic)}
                  className="text-sm px-3 py-1 bg-white border border-blue-300 rounded-full text-blue-700 hover:bg-blue-100 transition-colors"
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
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${!uploadRestriction.allowed
              ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
              : isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
        >
          <input {...getInputProps()} />
          <div className="space-y-2">
            <div className="text-4xl">📁</div>
            {!uploadRestriction.allowed ? (
              <p className="text-gray-500">Upload temporarily disabled</p>
            ) : isDragActive ? (
              <p className="text-blue-600">Drop the files here...</p>
            ) : (
              <div>
                <p className="text-gray-600">
                  Drag & drop files here, or <span className="text-blue-600">click to select</span>
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Supports PDF, JPG, PNG, PPTX (max 25 images per upload)
                </p>
                {fileLimits && (
                  <div className="text-xs text-gray-400 mt-2 space-y-1">
                    <div>PDF: max {fileLimits.pdf.max_size_mb}MB</div>
                    <div>Images: max {fileLimits.image.max_size_mb}MB</div>
                    <div>Slides: max {fileLimits.slide.max_size_mb}MB</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Selected Files - Only show in file mode */}
      {inputMode === 'file' && files.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900">Selected Files ({files.length})</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                <div className="flex items-center space-x-3">
                  <span className="text-sm">📄</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700 text-sm"
                  disabled={!uploadRestriction.allowed}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Mode Selection - Only for file upload */}
      {inputMode === 'file' && (
        <div className="space-y-3">
          <h3 className="font-medium text-gray-900">Processing Mode</h3>
          <div className="space-y-2">
            <label className="flex items-center space-x-3">
              <input
                type="radio"
                name="processingMode"
                value={ProcessingMode.OCR_AI}
                checked={processingMode === ProcessingMode.OCR_AI}
                onChange={(e) => setProcessingMode(e.target.value as ProcessingMode)}
                className="text-blue-600"
                disabled={!uploadRestriction.allowed}
              />
              <div>
                <span className="font-medium">OCR + AI Mode</span>
                <p className="text-sm text-gray-500">Enhanced extraction with AI processing for scanned documents</p>
              </div>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="radio"
                name="processingMode"
                value={ProcessingMode.AI_ONLY}
                checked={processingMode === ProcessingMode.AI_ONLY}
                onChange={(e) => setProcessingMode(e.target.value as ProcessingMode)}
                className="text-blue-600"
                disabled={!uploadRestriction.allowed}
              />
              <div>
                <span className="font-medium">AI Only Mode</span>
                <p className="text-sm text-gray-500">Direct AI processing for digital documents</p>
              </div>
            </label>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={inputMode === 'file' ? handleUpload : handleTopicSubmit}
        disabled={isUploadDisabled}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${isUploadDisabled
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
      >
        {isUploading ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Processing...</span>
          </div>
        ) : !uploadRestriction.allowed ? (
          `Upload Restricted ${countdown > 0 ? `(${formatCountdown(countdown)})` : ''}`
        ) : inputMode === 'file' ? (
          `Upload & Process ${files.length > 0 ? `(${files.length} files)` : ''}`
        ) : (
          `Generate Study Materials`
        )}
      </button>
    </div>
  );
}
