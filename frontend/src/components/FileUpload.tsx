'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { ProcessingMode } from '@/types/api';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';

interface FileUploadProps {
  onUploadSuccess: (sessionId: string) => void;
  onUploadError: (error: string) => void;
}

export default function FileUpload({ onUploadSuccess, onUploadError }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [processingMode, setProcessingMode] = useState<ProcessingMode>(ProcessingMode.DEFAULT);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadRestriction, setUploadRestriction] = useState<{
    allowed: boolean;
    message?: string;
    remainingSeconds?: number;
  }>({ allowed: true });
  const [countdown, setCountdown] = useState<number>(0);

  // TODO: Get actual user ID from auth context
  const userId = 'demo-user-123';

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

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (!uploadRestriction.allowed) {
      onUploadError(uploadRestriction.message || 'Upload not allowed at this time');
      return;
    }
    setFiles(prev => [...prev, ...acceptedFiles]);
  }, [uploadRestriction.allowed, uploadRestriction.message, onUploadError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
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

  const isUploadDisabled = files.length === 0 || isUploading || !uploadRestriction.allowed;

  return (
    <div className="space-y-6">
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

      {/* File Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          !uploadRestriction.allowed
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
                Supports PDF, JPG, PNG, PPTX (max 50MB each)
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Selected Files */}
      {files.length > 0 && (
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

      {/* Processing Mode Selection */}
      <div className="space-y-3">
        <h3 className="font-medium text-gray-900">Processing Mode</h3>
        <div className="space-y-2">
          <label className="flex items-center space-x-3">
            <input
              type="radio"
              name="processingMode"
              value={ProcessingMode.DEFAULT}
              checked={processingMode === ProcessingMode.DEFAULT}
              onChange={(e) => setProcessingMode(e.target.value as ProcessingMode)}
              className="text-blue-600"
              disabled={!uploadRestriction.allowed}
            />
            <div>
              <span className="font-medium">Default Mode</span>
              <p className="text-sm text-gray-500">Fast direct text extraction</p>
            </div>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="radio"
              name="processingMode"
              value={ProcessingMode.OCR}
              checked={processingMode === ProcessingMode.OCR}
              onChange={(e) => setProcessingMode(e.target.value as ProcessingMode)}
              className="text-blue-600"
              disabled={!uploadRestriction.allowed}
            />
            <div>
              <span className="font-medium">OCR Mode</span>
              <p className="text-sm text-gray-500">Enhanced extraction for scanned documents</p>
            </div>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="radio"
              name="processingMode"
              value={ProcessingMode.AI_BASED}
              checked={processingMode === ProcessingMode.AI_BASED}
              onChange={(e) => setProcessingMode(e.target.value as ProcessingMode)}
              className="text-blue-600"
              disabled={!uploadRestriction.allowed}
            />
            <div>
              <span className="font-medium">AI-Based Mode</span>
              <p className="text-sm text-gray-500">Context-aware intelligent processing</p>
            </div>
          </label>
        </div>
      </div>

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={isUploadDisabled}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
          isUploadDisabled
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        {isUploading ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Uploading...</span>
          </div>
        ) : !uploadRestriction.allowed ? (
          `Upload Restricted ${countdown > 0 ? `(${formatCountdown(countdown)})` : ''}`
        ) : (
          `Upload & Process ${files.length > 0 ? `(${files.length} files)` : ''}`
        )}
      </button>
    </div>
  );
}
