from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    DOCTOR = "doctor"
    ADMIN = "admin"

class OTPMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"

# Auth Request Models
class UserRegisterRequest(BaseModel):
    name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    password: str
    role: UserRole
    otp_method: OTPMethod = OTPMethod.SMS
    
    # Student fields
    college_name: Optional[str] = None
    course: Optional[str] = None
    year: Optional[int] = None
    exam_name: Optional[str] = None
    
    # Doctor fields
    hospital_name: Optional[str] = None
    speciality: Optional[str] = None
    experience: Optional[str] = None

class UserLoginRequest(BaseModel):
    mobile_number: str
    password: str

class SendOTPRequest(BaseModel):
    mobile_number: str
    otp_method: OTPMethod = OTPMethod.SMS
    email: Optional[EmailStr] = None

class VerifyOTPRequest(BaseModel):
    mobile_number: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    mobile_number: str
    otp_method: OTPMethod = OTPMethod.SMS
    email: Optional[EmailStr] = None

class ResetPasswordRequest(BaseModel):
    mobile_number: str
    otp: str
    new_password: str

class UserExistsRequest(BaseModel):
    mobile_number: str

# Auth Response Models
class UserResponse(BaseModel):
    id: str
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
