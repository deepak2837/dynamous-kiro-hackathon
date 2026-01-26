/**
 * Study Buddy App - TypeScript API Type Definitions
 * 
 * This module defines TypeScript interfaces and types for the Study Buddy App
 * API communication, ensuring type safety across the frontend application.
 * 
 * Types include:
 * - API request/response models
 * - Study session management
 * - Content models (questions, tests, mnemonics, etc.)
 * - Processing pipeline status tracking
 * - Medical content classification
 * 
 * All types are aligned with the backend Pydantic models for consistency.
 * 
 * Author: Study Buddy Team
 * Created: January 2026
 * License: MIT
 */

// API Response Types

/**
 * Response from file upload operations
 */
export interface UploadResponse {
  /** Unique session identifier for the upload */
  session_id: string;
  /** Success message */
  message: string;
  /** Number of files successfully uploaded */
  files_uploaded: number;
}

/**
 * Response for upload restriction checks
 */
export interface UploadRestrictionResponse {
  /** Whether upload is currently allowed */
  upload_allowed: boolean;
  /** Restriction message if upload not allowed */
  message?: string;
  /** Seconds remaining until next upload allowed */
  remaining_seconds?: number;
  /** Restriction configuration settings */
  restriction_settings: {
    enabled: boolean;
    cooldown_minutes: number;
  };
}

/**
 * Response for processing status queries
 */
export interface ProcessingStatusResponse {
  /** Session identifier */
  session_id: string;
  /** Current processing status */
  status: SessionStatus;
  /** Detailed progress information */
  progress?: ProcessingProgress;
  /** Status message */
  message?: string;
  /** Error message if processing failed */
  error_message?: string;
  /** Whether email notifications are enabled */
  email_notification_enabled: boolean;
}

/**
 * Detailed processing progress information
 */
export interface ProcessingProgress {
  /** Current step in the processing pipeline */
  current_step: ProcessingStep;
  /** Progress of current step (0-100) */
  step_progress: number;
  /** Overall progress across all steps (0-100) */
  overall_progress: number;
  /** Estimated time remaining in seconds */
  estimated_time_remaining?: number;
  /** Number of pages processed so far */
  pages_processed?: number;
  /** Total number of pages to process */
  total_pages?: number;
  /** Human-readable step message */
  step_message?: string;
}

/**
 * Study session data structure
 * 
 * Represents a complete study session with uploaded materials
 * and generated content for medical exam preparation.
 */
export interface StudySession {
  /** Unique session identifier */
  session_id: string;
  /** User who created the session */
  user_id: string;
  /** Human-readable session name */
  session_name: string;
  /** List of uploaded file paths */
  files: string[];
  /** Processing mode used for content generation */
  processing_mode: ProcessingMode;
  /** Current session status */
  status: SessionStatus;
  /** Session creation timestamp */
  created_at: string;
  /** Session completion timestamp */
  completed_at?: string;
  /** Error message if session failed */
  error_message?: string;
}

/**
 * Medical question model for MBBS exam preparation
 */
export interface Question {
  /** Unique question identifier */
  question_id: string;
  /** Associated study session */
  session_id: string;
  /** User who owns the question */
  user_id: string;
  /** The medical question text */
  question_text: string;
  /** Multiple choice options */
  options: string[];
  /** Index of correct answer (0-based) */
  correct_answer: number;
  /** Detailed explanation for the answer */
  explanation: string;
  /** Question difficulty level */
  difficulty: DifficultyLevel;
  /** Medical topic/subject area */
  topic?: string;
  /** Question creation timestamp */
  created_at: string;
}

/**
 * Mock test model for medical exam simulation
 */
export interface MockTest {
  /** Unique test identifier */
  test_id: string;
  /** Associated study session */
  session_id: string;
  /** User who owns the test */
  user_id: string;
  /** Auto-generated test name */
  test_name: string;
  /** List of question IDs in the test */
  questions: string[];
  /** Test duration in minutes */
  duration_minutes: number;
  /** Total number of questions */
  total_questions: number;
  /** Test creation timestamp */
  created_at: string;
}

/**
 * Mnemonic model for medical concept memorization
 */
export interface Mnemonic {
  /** Unique mnemonic identifier */
  mnemonic_id: string;
  /** Associated study session */
  session_id: string;
  /** User who owns the mnemonic */
  user_id: string;
  /** Medical topic or concept */
  topic: string;
  /** The memory aid text */
  mnemonic_text: string;
  /** Explanation of how the mnemonic works */
  explanation: string;
  /** Key terms highlighted in the mnemonic */
  key_terms: string[];
  /** Mnemonic creation timestamp */
  created_at: string;
}

/**
 * Cheat sheet model for quick reference study materials
 */
export interface CheatSheet {
  /** Unique cheat sheet identifier */
  sheet_id: string;
  /** Associated study session */
  session_id: string;
  /** User who owns the cheat sheet */
  user_id: string;
  /** Descriptive title for the content area */
  title: string;
  /** Essential facts and concepts */
  key_points: string[];
  /** Most important exam-relevant information */
  high_yield_facts: string[];
  /** Key-value mappings for rapid lookup */
  quick_references: Record<string, string>;
  /** Cheat sheet creation timestamp */
  created_at: string;
}

/**
 * Compiled study notes model for comprehensive review
 */
export interface Note {
  /** Unique note identifier */
  note_id: string;
  /** Associated study session */
  session_id: string;
  /** User who owns the note */
  user_id: string;
  /** Descriptive title for the notes */
  title: string;
  /** Main compiled content */
  content: string;
  /** References to key questions */
  important_questions: string[];
  /** Condensed summary information */
  summary_points: string[];
  /** Associated memory aids */
  related_mnemonics: string[];
  /** Note creation timestamp */
  created_at: string;
}

/**
 * Flashcard model for spaced repetition learning
 */
export interface Flashcard {
  /** Unique flashcard identifier */
  flashcard_id: string;
  /** Associated study session */
  session_id: string;
  /** User who owns the flashcard */
  user_id: string;
  /** Question or prompt side */
  front_text: string;
  /** Answer or explanation side */
  back_text: string;
  /** Medical subject category */
  category: MedicalCategory;
  /** Learning difficulty level */
  difficulty: DifficultyLevel;
  /** Specific medical topic */
  medical_topic?: string;
  /** Phonetic pronunciation guide */
  pronunciation?: string;
  /** Spaced repetition algorithm data */
  spaced_repetition_data: SpacedRepetitionData;
  /** Flashcard creation timestamp */
  created_at: string;
}

/**
 * Spaced repetition algorithm data for optimal review timing
 */
export interface SpacedRepetitionData {
  /** Ease factor for the flashcard (difficulty multiplier) */
  ease_factor: number;
  /** Current review interval in days */
  interval: number;
  /** Number of successful repetitions */
  repetitions: number;
  /** Next scheduled review date */
  next_review_date: string;
  /** Last review timestamp */
  last_reviewed: string | null;
}

/**
 * Flashcard review submission for spaced repetition
 */
export interface FlashcardReview {
  /** Quality rating 0-5 for spaced repetition algorithm */
  quality: number;
  /** Time spent reviewing in seconds */
  time_spent: number;
}

// Processing Pipeline Enums

/**
 * Processing steps in the AI content generation pipeline
 */
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
  GENERATING_FLASHCARDS = "generating_flashcards",
  FINALIZING = "finalizing",
  COMPLETED = "completed",
  FAILED = "failed"
}

/**
 * Processing modes for content generation
 */
export enum ProcessingMode {
  AI_ONLY = "ai_only"
}

/**
 * Difficulty levels for medical content
 */
export enum DifficultyLevel {
  EASY = "easy",
  MEDIUM = "medium",
  HARD = "hard"
}

/**
 * Study session status values
 */
export enum SessionStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

/**
 * Medical subject categories for content classification
 */
export type MedicalCategory = 'anatomy' | 'pharmacology' | 'pathology' | 'physiology' | 'clinical';

// API Response Types

/**
 * Response for session history listings
 */
export interface SessionListResponse {
  sessions: StudySession[];
  total_count: number;
}

/**
 * Response for question listings
 */
export interface QuestionListResponse {
  questions: Question[];
  total_count: number;
}

/**
 * Response for mock test listings
 */
export interface MockTestListResponse {
  mock_tests: MockTest[];
  total_count: number;
}

/**
 * Response for flashcard listings
 */
export interface FlashcardListResponse {
  flashcards: Flashcard[];
  total_count: number;
}
