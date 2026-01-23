"""
Study Plan models for the Study Buddy application.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class StudyTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class StudyTaskType(str, Enum):
    REVIEW_QUESTIONS = "review_questions"
    STUDY_NOTES = "study_notes"
    PRACTICE_FLASHCARDS = "practice_flashcards"
    REVIEW_CHEATSHEET = "review_cheatsheet"
    MOCK_TEST = "mock_test"
    REVISION = "revision"

class MedicalSubject(str, Enum):
    ANATOMY = "anatomy"
    PHYSIOLOGY = "physiology"
    BIOCHEMISTRY = "biochemistry"
    PATHOLOGY = "pathology"
    PHARMACOLOGY = "pharmacology"
    MICROBIOLOGY = "microbiology"
    FORENSIC_MEDICINE = "forensic_medicine"
    COMMUNITY_MEDICINE = "community_medicine"
    GENERAL = "general"

class StudyTask(BaseModel):
    task_id: str
    title: str
    description: str
    task_type: StudyTaskType
    subject: MedicalSubject = MedicalSubject.GENERAL
    estimated_duration: int
    priority: int = 1
    content_ids: List[str] = Field(default_factory=list)
    status: StudyTaskStatus = StudyTaskStatus.PENDING
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

class DailySchedule(BaseModel):
    date: date
    total_study_time: int
    tasks: List[StudyTask] = Field(default_factory=list)
    completed_tasks: int = 0
    total_tasks: int = 0
    progress_percentage: float = 0.0

class StudyPlanConfig(BaseModel):
    exam_date: date
    daily_study_hours: float
    study_days_per_week: int = 6
    subject_priorities: Dict[str, int] = Field(default_factory=dict)
    weak_areas: List[str] = Field(default_factory=list)
    preferred_study_times: List[str] = Field(default_factory=list)
    spaced_repetition_enabled: bool = True
    
    @validator('exam_date')
    def exam_date_must_be_future(cls, v):
        if v <= date.today():
            raise ValueError('Exam date must be in the future')
        return v
    
    @validator('daily_study_hours')
    def daily_study_hours_must_be_reasonable(cls, v):
        if v < 0.5 or v > 16:
            raise ValueError('Daily study hours must be between 0.5 and 16 hours')
        return v
    
    @validator('study_days_per_week')
    def study_days_per_week_must_be_valid(cls, v):
        if v < 1 or v > 7:
            raise ValueError('Study days per week must be between 1 and 7')
        return v

class StudyPlan(BaseModel):
    plan_id: str
    session_id: str
    user_id: str
    plan_name: str
    config: StudyPlanConfig
    daily_schedules: List[DailySchedule] = []
    total_study_days: int
    total_study_hours: float
    subjects_covered: List[str] = []
    spaced_repetition_schedule: Dict[str, List[str]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class StudyProgress(BaseModel):
    plan_id: str
    user_id: str
    total_tasks: int = 0
    completed_tasks: int = 0
    overall_progress: float = 0.0
    daily_progress: Dict[str, float] = {}
    subject_progress: Dict[str, float] = {}
    streak_days: int = 0
    last_study_date: Optional[date] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response models
class StudyPlanRequest(BaseModel):
    session_id: str
    config: StudyPlanConfig
    plan_name: Optional[str] = None

class StudyPlanResponse(BaseModel):
    plan: StudyPlan
    message: str

class TaskUpdateRequest(BaseModel):
    task_id: str
    status: StudyTaskStatus
    notes: Optional[str] = None

class ProgressResponse(BaseModel):
    progress: StudyProgress
    recent_activity: List[Dict[str, Any]] = []
    recommendations: List[str] = []
