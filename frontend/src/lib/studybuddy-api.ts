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
  ProcessingMode
} from '@/types/api';

export class StudyBuddyAPI {
  // File Upload
  static async checkUploadAllowed(userId: string): Promise<UploadRestrictionResponse> {
    const response = await apiClient.get(`/upload/check-upload-allowed/${userId}`);
    return response.data;
  }

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
    // user_id will be obtained from JWT token on backend

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

  // Health Check
  static async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  }
}
