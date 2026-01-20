from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import bcrypt
import jwt
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId
from app.auth_models_simple import *
from app.services.otp_service import OTPService, OTPManager
from app.config import settings
from app.utils.error_logger import error_logger

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()

# Simple database connection
def get_db():
    client = pymongo.MongoClient(settings.mongodb_url)
    return client[settings.database_name]

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number format"""
    phone = phone.strip()
    if not phone.startswith('+'):
        if phone.startswith('91') and len(phone) == 12:
            phone = '+' + phone
        elif len(phone) == 10:
            phone = '+91' + phone
        else:
            phone = '+' + phone
    return phone

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_jwt_token(user_id: str, mobile_number: str) -> str:
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'mobile_number': mobile_number,
        'exp': datetime.utcnow() + timedelta(days=30),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(payload["user_id"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        mobile_number=user["mobile_number"],
        email=user.get("email"),
        role=UserRole(user["role"]),
        otp_method=OTPMethod(user.get("otp_method", "sms")),
        verified=user.get("verified", False),
        college_name=user.get("college_name"),
        course=user.get("course"),
        year=user.get("year"),
        exam_name=user.get("exam_name"),
        hospital_name=user.get("hospital_name"),
        speciality=user.get("speciality"),
        experience=user.get("experience"),
        created_at=user["created_at"],
        updated_at=user.get("updated_at")
    )

@router.post("/check-user", response_model=UserExistsResponse)
async def check_user_exists(request: UserExistsRequest):
    """Check if user exists by mobile number"""
    try:
        mobile_number = normalize_phone_number(user_request.mobile_number)
        db = get_db()
        user = db.users.find_one({"mobile_number": mobile_number})
        
        if user:
            return UserExistsResponse(exists=True, verified=user.get("verified", False))
        return UserExistsResponse(exists=False)
    except Exception as e:
        error_logger.log_error(e, "check_user_exists", additional_info={"mobile_number": request.mobile_number})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking user: {str(e)}"
        )

@router.post("/send-otp", response_model=MessageResponse)
async def send_registration_otp(otp_request: SendOTPRequest):
    """Send OTP for registration"""
    try:
        mobile_number = normalize_phone_number(request.mobile_number)
        
        # Check if user already exists
        db = get_db()
        user = db.users.find_one({"mobile_number": mobile_number})
        if user and user.get("verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered. Please login."
            )
        
        # Generate OTP
        otp = OTPService.generate_otp()
        
        # Send OTP (for demo, we'll just store it)
        print(f"📱 OTP for {mobile_number}: {otp}")
        
        # Store OTP
        OTPManager.store_otp(
            mobile_number=mobile_number,
            otp=otp,
            method=request.otp_method,
            purpose="registration",
            email=request.email
        )
        
        return MessageResponse(message="OTP sent successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        error_logger.log_error(e, "send_registration_otp", additional_info={"mobile_number": request.mobile_number, "otp_method": request.otp_method})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending OTP: {str(e)}"
        )

@router.post("/register", response_model=TokenResponse)
async def register_user(request: UserRegisterRequest):
    """Register new user after OTP verification"""
    try:
        mobile_number = normalize_phone_number(request.mobile_number)
        
        # For demo, skip OTP verification
        # In production, verify OTP here
        
        # Check if user already exists
        db = get_db()
        user = db.users.find_one({"mobile_number": mobile_number})
        if user and user.get("verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )
        
        # Prepare user data
        user_data = {
            "name": request.name,
            "mobile_number": mobile_number,
            "email": request.email,
            "password_hash": hash_password(request.password),
            "role": request.role,
            "otp_method": request.otp_method,
            "verified": True,
            "college_name": request.college_name,
            "course": request.course,
            "year": request.year,
            "exam_name": request.exam_name,
            "hospital_name": request.hospital_name,
            "speciality": request.speciality,
            "experience": request.experience,
            "created_at": datetime.utcnow()
        }
        
        # Create user
        result = db.users.insert_one(user_data)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Get created user
        user = db.users.find_one({"_id": result.inserted_id})
        user_response = UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            mobile_number=user["mobile_number"],
            email=user.get("email"),
            role=UserRole(user["role"]),
            otp_method=OTPMethod(user.get("otp_method", "sms")),
            verified=user.get("verified", False),
            college_name=user.get("college_name"),
            course=user.get("course"),
            year=user.get("year"),
            exam_name=user.get("exam_name"),
            hospital_name=user.get("hospital_name"),
            speciality=user.get("speciality"),
            experience=user.get("experience"),
            created_at=user["created_at"],
            updated_at=user.get("updated_at")
        )
        
        # Generate token
        token = generate_jwt_token(str(user["_id"]), user["mobile_number"])
        
        return TokenResponse(access_token=token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        error_logger.log_error(e, "register_user", additional_info={"mobile_number": request.mobile_number, "role": request.role})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(request: UserLoginRequest):
    """Login user with mobile number and password"""
    try:
        mobile_number = normalize_phone_number(request.mobile_number)
        
        # Find user
        db = get_db()
        user = db.users.find_one({
            "mobile_number": mobile_number,
            "verified": True
        })
        
        if not user or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid mobile number or password"
            )
        
        user_response = UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            mobile_number=user["mobile_number"],
            email=user.get("email"),
            role=UserRole(user["role"]),
            otp_method=OTPMethod(user.get("otp_method", "sms")),
            verified=user.get("verified", False),
            college_name=user.get("college_name"),
            course=user.get("course"),
            year=user.get("year"),
            exam_name=user.get("exam_name"),
            hospital_name=user.get("hospital_name"),
            speciality=user.get("speciality"),
            experience=user.get("experience"),
            created_at=user["created_at"],
            updated_at=user.get("updated_at")
        )
        
        # Generate token
        token = generate_jwt_token(str(user["_id"]), user["mobile_number"])
        
        return TokenResponse(access_token=token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        error_logger.log_error(e, "login_user", additional_info={"mobile_number": request.mobile_number})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout", response_model=MessageResponse)
async def logout_user(current_user: UserResponse = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return MessageResponse(message="Logged out successfully")

# Health check
@router.get("/health")
async def auth_health():
    """Auth service health check"""
    return {"status": "healthy", "service": "auth"}
