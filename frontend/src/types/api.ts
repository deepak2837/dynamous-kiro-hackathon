// API Types
export interface UploadResponse {
  session_id: string;
  message: string;
  files_uploaded: number;
}

export interface UploadRestrictionResponse {
  upload_allowed: boolean;
  message?: string;
  remaining_seconds?: number;
  restriction_settings: {
    enabled: boolean;
    cooldown_minutes: number;
  };
}

export interface ProcessingStatusResponse {
  session_id: string;
  status: SessionStatus;
  progress?: ProcessingProgress;
  message?: string;
  error_message?: string;
  email_notification_enabled: boolean;
}

export interface ProcessingProgress {
  current_step: ProcessingStep;
  step_progress: number;
  overall_progress: number;
  estimated_time_remaining?: number;
  pages_processed?: number;
  total_pages?: number;
  step_message?: string;
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

export enum ProcessingStep {
  UPLOAD_COMPLETE = "upload_complete",
  FILE_ANALYSIS = "file_analysis", 
  OCR_PROCESSING = "ocr_processing",
  AI_PROCESSING = "ai_processing",
  GENERATING_QUESTIONS = "generating_questions",
  GENERATING_MOCK_TESTS = "generating_mock_tests",
  GENERATING_MNEMONICS = "generating_mnemonics",
  GENERATING_CHEAT_SHEETS = "generating_cheat_sheets",
  GENERATING_NOTES = "generating_notes",
  FINALIZING = "finalizing",
  COMPLETED = "completed",
  FAILED = "failed"
}

// Enums
export enum ProcessingMode {
  AI_ONLY = "ai_only"
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
