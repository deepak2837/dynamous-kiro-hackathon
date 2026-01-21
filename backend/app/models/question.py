from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Union, Any
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class Question(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    session_id: str
    user_id: Optional[str] = "anonymous"
    question: str
    options: Dict[str, str]  # {"A": "option text", "B": "option text", ...}
    correct_answer: str = "A"
    explanation: Optional[str] = ""
    difficulty: DifficultyLevel = DifficultyLevel.medium
    topic: Optional[str] = "General"
    question_type: Optional[str] = "multiple_choice"
    created_at: Optional[datetime] = None
    
    @field_validator('difficulty', mode='before')
    @classmethod
    def normalize_difficulty(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v
    
    @field_validator('options', mode='before')
    @classmethod
    def normalize_options(cls, v):
        if isinstance(v, list):
            # Convert list of dicts to dict
            options_dict = {}
            for opt in v:
                if isinstance(opt, dict):
                    opt_id = opt.get("option_id", "").upper()
                    if not opt_id:
                        opt_id = opt.get("id", "A").upper()
                    options_dict[opt_id] = opt.get("text", str(opt))
            return options_dict
        return v
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_id(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
