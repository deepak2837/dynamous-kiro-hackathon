from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, Any, Annotated
from datetime import datetime
from enum import Enum
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string")
        return field_schema

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class UserRole(str, Enum):
    STUDENT = "student"
    DOCTOR = "doctor"
    ADMIN = "admin"

class OTPMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"

# Auth Request Models
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    role: UserRole
    otp_method: OTPMethod = OTPMethod.SMS
    
    # Student fields
    college_name: Optional[str] = None
    course: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=10)
    exam_name: Optional[str] = None
    
    # Doctor fields
    hospital_name: Optional[str] = None
    speciality: Optional[str] = None
    experience: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email_for_email_otp(cls, v, info):
        if info.data.get('otp_method') == OTPMethod.EMAIL and not v:
            raise ValueError('Email is required when using email OTP')
        return v

class UserLoginRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    password: str = Field(..., min_length=1)

class SendOTPRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp_method: OTPMethod = OTPMethod.SMS
    email: Optional[EmailStr] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_for_email_otp(cls, v, info):
        if info.data.get('otp_method') == OTPMethod.EMAIL and not v:
            raise ValueError('Email is required when using email OTP')
        return v

class VerifyOTPRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp: str = Field(..., min_length=6, max_length=6)

class ForgotPasswordRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp_method: OTPMethod = OTPMethod.SMS
    email: Optional[EmailStr] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_for_email_otp(cls, v, info):
        if info.data.get('otp_method') == OTPMethod.EMAIL and not v:
            raise ValueError('Email is required when using email OTP')
        return v

class ResetPasswordRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6)

class UserExistsRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')

# Auth Response Models
class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    mobile_number: str
    email: Optional[str] = None
    role: UserRole
    otp_method: OTPMethod
    verified: bool = False
    
    # Student fields
    college_name: Optional[str] = None
    course: Optional[str] = None
    year: Optional[int] = None
    exam_name: Optional[str] = None
    
    # Doctor fields
    hospital_name: Optional[str] = None
    speciality: Optional[str] = None
    experience: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 2592000  # 30 days
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    status: int = 200

class UserExistsResponse(BaseModel):
    exists: bool
    verified: Optional[bool] = None

# Database Models (for MongoDB)
class UserDB(BaseModel):
    name: str
    mobile_number: str
    email: Optional[str] = None
    password_hash: str
    role: UserRole
    otp_method: OTPMethod
    verified: bool = False
    
    # Student fields
    college_name: Optional[str] = None
    course: Optional[str] = None
    year: Optional[int] = None
    exam_name: Optional[str] = None
    
    # Doctor fields
    hospital_name: Optional[str] = None
    speciality: Optional[str] = None
    experience: Optional[str] = None
    
    # OTP fields
    otp: Optional[str] = None
    otp_expires: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class OTPStore(BaseModel):
    mobile_number: str
    otp: str
    otp_method: OTPMethod
    email: Optional[str] = None
    expires_at: datetime
    purpose: str  # "registration", "login", "forgot_password"
    user_data: Optional[dict] = None  # For registration flow
    created_at: datetime = Field(default_factory=datetime.utcnow)
