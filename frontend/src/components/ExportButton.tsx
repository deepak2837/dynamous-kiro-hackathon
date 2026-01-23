import React, { useState } from 'react';
import { FiDownload, FiLoader, FiX } from 'react-icons/fi';
import { StudyBuddyAPI } from '@/lib/studybuddy-api';

interface ExportButtonProps {
  sessionId: string;
  contentType: 'questions' | 'notes' | 'cheatsheet' | 'mnemonics';
  label?: string;
  className?: string;
}

export default function ExportButton({ 
  sessionId, 
  contentType, 
  label,
  className = '' 
}: ExportButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleExport = async () => {
    if (isDownloading) return;
    
    setIsDownloading(true);
    setError(null);
    
    try {
      let blob: Blob;
      let filename: string;
      
      switch (contentType) {
        case 'questions':
          blob = await StudyBuddyAPI.downloadQuestionsPdf(sessionId);
          filename = `questions_${sessionId}.pdf`;
          break;
        case 'notes':
          blob = await StudyBuddyAPI.downloadNotesPdf(sessionId);
          filename = `notes_${sessionId}.pdf`;
          break;
        case 'cheatsheet':
          blob = await StudyBuddyAPI.downloadCheatsheetPdf(sessionId);
          filename = `cheatsheet_${sessionId}.pdf`;
          break;
        case 'mnemonics':
          blob = await StudyBuddyAPI.downloadMnemonicsPdf(sessionId);
          filename = `mnemonics_${sessionId}.pdf`;
          break;
        default:
          throw new Error('Invalid content type');
      }
      
      downloadFile(blob, filename);
    } catch (error) {
      console.error('Failed to download PDF:', error);
      setError('Failed to download PDF. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const defaultLabel = label || `Export ${contentType.charAt(0).toUpperCase() + contentType.slice(1)} PDF`;

  return (
    <div className="relative">
      <button
        onClick={handleExport}
        disabled={isDownloading}
        className={`
          inline-flex items-center space-x-2 px-4 py-2 
          bg-gradient-to-r from-pink-500 to-fuchsia-500 
          text-white font-medium rounded-lg 
          hover:shadow-lg hover:scale-105 
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-all duration-300
          ${className}
        `}
      >
        {isDownloading ? (
          <FiLoader className="w-4 h-4 animate-spin" />
        ) : (
          <FiDownload className="w-4 h-4" />
        )}
        <span>{isDownloading ? 'Generating...' : defaultLabel}</span>
      </button>
      
      {error && (
        <div className="absolute top-full left-0 mt-2 p-3 bg-rose-50 border border-rose-200 rounded-lg shadow-lg z-10 min-w-full">
          <div className="flex items-start space-x-2">
            <FiX className="w-4 h-4 text-rose-500 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-rose-700">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-xs text-rose-600 hover:text-rose-800 mt-1"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
