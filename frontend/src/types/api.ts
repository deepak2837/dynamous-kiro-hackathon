// API Types
export interface UploadResponse {
  session_id: string;
  message: string;
  files_uploaded: number;
}

export interface ProcessingStatusResponse {
  session_id: string;
  status: SessionStatus;
  progress_percentage?: number;
  message?: string;
  error_message?: string;
}

export interface StudySession {
  session_id: string;
  user_id: string;
  session_name: string;
  files: string[];
  processing_mode: ProcessingMode;
  status: SessionStatus;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface Question {
  question_id: string;
  session_id: string;
  user_id: string;
  question_text: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  difficulty: DifficultyLevel;
  topic?: string;
  created_at: string;
}

export interface MockTest {
  test_id: string;
  session_id: string;
  user_id: string;
  test_name: string;
  questions: string[];
  duration_minutes: number;
  total_questions: number;
  created_at: string;
}

export interface Mnemonic {
  mnemonic_id: string;
  session_id: string;
  user_id: string;
  topic: string;
  mnemonic_text: string;
  explanation: string;
  key_terms: string[];
  created_at: string;
}

export interface CheatSheet {
  sheet_id: string;
  session_id: string;
  user_id: string;
  title: string;
  key_points: string[];
  high_yield_facts: string[];
  quick_references: Record<string, string>;
  created_at: string;
}

export interface Note {
  note_id: string;
  session_id: string;
  user_id: string;
  title: string;
  content: string;
  important_questions: string[];
  summary_points: string[];
  related_mnemonics: string[];
  created_at: string;
}

// Enums
export enum ProcessingMode {
  DEFAULT = "default",
  OCR = "ocr",
  AI_BASED = "ai_based"
}

export enum DifficultyLevel {
  EASY = "easy",
  MEDIUM = "medium",
  HARD = "hard"
}

export enum SessionStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

// Response Types
export interface SessionListResponse {
  sessions: StudySession[];
  total_count: number;
}

export interface QuestionListResponse {
  questions: Question[];
  total_count: number;
}

export interface MockTestListResponse {
  mock_tests: MockTest[];
  total_count: number;
}
