/**
 * Study Buddy API Client
 * 
 * Centralized API client for all Study Buddy App backend communication.
 * Provides type-safe methods for file upload, processing status, content retrieval,
 * and session management for medical study materials.
 * 
 * Features:
 * - File upload with processing mode selection
 * - Real-time processing status tracking
 * - Content retrieval (questions, tests, mnemonics, etc.)
 * - Session history management
 * - Flashcard study system integration
 * - Export functionality
 * 
 * All methods return properly typed responses matching backend API contracts.
 * 
 * @example
 * ```typescript
 * // Upload files
 * const response = await StudyBuddyAPI.uploadFiles(files, ProcessingMode.AI_ONLY, userId);
 * 
 * // Get processing status
 * const status = await StudyBuddyAPI.getProcessingStatus(sessionId);
 * 
 * // Retrieve questions
 * const questions = await StudyBuddyAPI.getQuestions(sessionId);
 * ```
 */

import apiClient from './api';
import {
  UploadResponse,
  UploadRestrictionResponse,
  ProcessingStatusResponse,
  StudySession,
  SessionListResponse,
  QuestionListResponse,
  MockTestListResponse,
  Question,
  MockTest,
  Mnemonic,
  CheatSheet,
  Note,
  Flashcard,
  FlashcardReview,
  FlashcardListResponse,
  ProcessingMode
} from '@/types/api';

export class StudyBuddyAPI {
  // File Upload Operations
  
  /**
   * Check if user is allowed to upload files (rate limiting check).
   * 
   * @param userId - User identifier
   * @returns Upload restriction status and remaining cooldown time
   */
  static async checkUploadAllowed(userId: string): Promise<UploadRestrictionResponse> {
    const response = await apiClient.get(`/upload/check-upload-allowed/${userId}`);
    return response.data;
  }

  /**
   * Upload medical study files for AI processing.
   * 
   * @param files - Array of files to upload (PDF, images, PPTX)
   * @param processingMode - AI processing mode to use
   * @param userId - User identifier
   */
  static async uploadFiles(
    files: File[],
    processingMode: ProcessingMode,
    userId: string
  ): Promise<UploadResponse> {
    const formData = new FormData();

    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('processing_mode', processingMode);
    formData.append('user_id', userId);  // Send user_id to backend

    const response = await apiClient.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file upload processing
    });

    return response.data;
  }

  // Processing Status
  static async getProcessingStatus(sessionId: string): Promise<ProcessingStatusResponse> {
    const response = await apiClient.get(`/upload/status/${sessionId}`);
    return response.data;
  }

  // Sessions
  static async getUserSessions(
    userId: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<SessionListResponse> {
    const response = await apiClient.get('/sessions', {
      params: { user_id: userId, skip, limit }
    });
    return response.data;
  }

  static async getSession(sessionId: string): Promise<StudySession> {
    const response = await apiClient.get(`/sessions/${sessionId}`);
    return response.data;
  }

  static async deleteSession(sessionId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/sessions/${sessionId}`);
    return response.data;
  }

  // Questions
  static async getSessionQuestions(
    sessionId: string,
    skip: number = 0,
    limit: number = 50,
    difficulty?: string
  ): Promise<QuestionListResponse> {
    const response = await apiClient.get(`/questions/${sessionId}`, {
      params: { skip, limit, difficulty }
    });
    return response.data;
  }

  static async getQuestion(questionId: string): Promise<Question> {
    const response = await apiClient.get(`/questions/question/${questionId}`);
    return response.data;
  }

  // Mock Tests
  static async getSessionMockTests(
    sessionId: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<MockTestListResponse> {
    const response = await apiClient.get(`/mock-tests/${sessionId}`, {
      params: { skip, limit }
    });
    return response.data;
  }

  static async getMockTest(testId: string): Promise<{ test: MockTest; questions: Question[] }> {
    const response = await apiClient.get(`/mock-tests/test/${testId}`);
    return response.data;
  }

  // Mnemonics
  static async getSessionMnemonics(
    sessionId: string,
    skip: number = 0,
    limit: number = 20
  ): Promise<{ mnemonics: Mnemonic[]; total_count: number }> {
    const response = await apiClient.get(`/mnemonics/${sessionId}`, {
      params: { skip, limit }
    });
    return response.data;
  }

  static async getMnemonic(mnemonicId: string): Promise<Mnemonic> {
    const response = await apiClient.get(`/mnemonics/mnemonic/${mnemonicId}`);
    return response.data;
  }

  // Cheat Sheets
  static async getSessionCheatSheets(
    sessionId: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<{ cheat_sheets: CheatSheet[]; total_count: number }> {
    const response = await apiClient.get(`/cheat-sheets/${sessionId}`, {
      params: { skip, limit }
    });
    return response.data;
  }

  static async getCheatSheet(sheetId: string): Promise<CheatSheet> {
    const response = await apiClient.get(`/cheat-sheets/sheet/${sheetId}`);
    return response.data;
  }

  // Notes
  static async getSessionNotes(
    sessionId: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<{ notes: Note[]; total_count: number }> {
    const response = await apiClient.get(`/notes/${sessionId}`, {
      params: { skip, limit }
    });
    return response.data;
  }

  static async getNote(noteId: string): Promise<Note> {
    const response = await apiClient.get(`/notes/note/${noteId}`);
    return response.data;
  }

  // Flashcards
  static async getSessionFlashcards(
    sessionId: string,
    skip: number = 0,
    limit: number = 50
  ): Promise<FlashcardListResponse> {
    const response = await apiClient.get(`/flashcards/${sessionId}`, {
      params: { skip, limit }
    });
    return response.data;
  }

  static async reviewFlashcard(
    flashcardId: string,
    reviewData: FlashcardReview
  ): Promise<{ message: string; next_review_date: string; interval_days: number }> {
    const response = await apiClient.post(`/flashcards/${flashcardId}/review`, reviewData);
    return response.data;
  }

  static async getStudyFlashcards(
    sessionId: string,
    limit: number = 10
  ): Promise<FlashcardListResponse> {
    const response = await apiClient.get(`/flashcards/${sessionId}/study`, {
      params: { limit }
    });
    return response.data;
  }

  // Health Check
  static async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  }

  // Download PDFs
  static async downloadQuestionsPdf(sessionId: string): Promise<Blob> {
    const response = await apiClient.get(`/download/questions/${sessionId}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  static async downloadNotesPdf(sessionId: string): Promise<Blob> {
    const response = await apiClient.get(`/download/notes/${sessionId}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  static async downloadCheatsheetPdf(sessionId: string): Promise<Blob> {
    const response = await apiClient.get(`/download/cheatsheet/${sessionId}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  static async downloadMnemonicsPdf(sessionId: string): Promise<Blob> {
    const response = await apiClient.get(`/download/mnemonics/${sessionId}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Study Planner
  static async generateStudyPlan(sessionId: string, config: any): Promise<any> {
    const response = await apiClient.post('/study-planner/generate-plan', {
      session_id: sessionId,
      config: config
    }, {
      timeout: 1160000, // 60 seconds timeout for AI-powered study plan generation
    });
    return response.data;
  }

  static async getStudyPlan(sessionId: string): Promise<any> {
    const response = await apiClient.get(`/study-planner/plan/${sessionId}`);
    return response.data;
  }

  static async updateTaskStatus(taskId: string, status: string, notes?: string): Promise<any> {
    const response = await apiClient.post('/study-planner/update-task', {
      task_id: taskId,
      status: status,
      notes: notes
    });
    return response.data;
  }

  static async getStudyProgress(planId: string): Promise<any> {
    const response = await apiClient.get(`/study-planner/progress/${planId}`);
    return response.data;
  }

  // Get all user's study plans with progress
  static async getUserStudyPlans(limit: number = 10): Promise<any> {
    const response = await apiClient.get('/study-planner/user-plans', {
      params: { limit }
    });
    return response.data;
  }
}
