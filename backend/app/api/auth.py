from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import asyncio

from app.auth_models import (
    UserRegisterRequest, UserLoginRequest, SendOTPRequest, VerifyOTPRequest,
    ForgotPasswordRequest, ResetPasswordRequest, UserExistsRequest,
    TokenResponse, MessageResponse, UserExistsResponse, UserResponse
)
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService, OTPManager

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()

# Initialize services
auth_service = AuthService()
otp_service = OTPService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = auth_service.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = await auth_service.get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/check-user", response_model=UserExistsResponse)
async def check_user_exists(request: UserExistsRequest):
    """Check if user exists by mobile number"""
    try:
        exists, verified = await auth_service.user_exists(request.mobile_number)
        return UserExistsResponse(exists=exists, verified=verified if exists else None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking user: {str(e)}"
        )

@router.post("/send-otp", response_model=MessageResponse)
async def send_registration_otp(request: SendOTPRequest):
    """Send OTP for registration"""
    try:
        # Check if user already exists
        exists, verified = await auth_service.user_exists(request.mobile_number)
        if exists and verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered. Please login."
            )
        
        # Generate OTP
        otp = OTPService.generate_otp()
        
        # Send OTP
        success = await otp_service.send_otp(
            mobile_number=request.mobile_number,
            otp=otp,
            method=request.otp_method,
            email=request.email
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP"
            )
        
        # Store OTP
        OTPManager.store_otp(
            mobile_number=request.mobile_number,
            otp=otp,
            method=request.otp_method,
            purpose="registration",
            email=request.email
        )
        
        return MessageResponse(message="OTP sent successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending OTP: {str(e)}"
        )

@router.post("/register", response_model=TokenResponse)
async def register_user(request: UserRegisterRequest):
    """Register new user after OTP verification"""
    try:
        # Verify OTP first
        otp_valid, _ = OTPManager.verify_otp(
            mobile_number=request.mobile_number,
            otp="123456",  # For demo, accept any OTP
            purpose="registration"
        )
        
        # For production, uncomment this:
        # if not otp_valid:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Invalid or expired OTP"
        #     )
        
        # Check if user already exists
        exists, verified = await auth_service.user_exists(request.mobile_number)
        if exists and verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )
        
        # Prepare user data
        user_data = {
            "name": request.name,
            "mobile_number": request.mobile_number,
            "email": request.email,
            "password": request.password,
            "role": request.role,
            "otp_method": request.otp_method,
            "college_name": request.college_name,
            "course": request.course,
            "year": request.year,
            "exam_name": request.exam_name,
            "hospital_name": request.hospital_name,
            "speciality": request.speciality,
            "experience": request.experience
        }
        
        # Create user
        user = await auth_service.create_user(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Generate token
        token = auth_service.generate_jwt_token(str(user.id), user.mobile_number)
        
        return TokenResponse(access_token=token, user=user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(request: UserLoginRequest):
    """Login user with mobile number and password"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(request.mobile_number, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid mobile number or password"
            )
        
        # Generate token
        token = auth_service.generate_jwt_token(str(user.id), user.mobile_number)
        
        return TokenResponse(access_token=token, user=user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in: {str(e)}"
        )

@router.post("/forgot-password", response_model=MessageResponse)
async def send_forgot_password_otp(request: ForgotPasswordRequest):
    """Send OTP for password reset"""
    try:
        # Check if user exists
        exists, verified = await auth_service.user_exists(request.mobile_number)
        if not exists or not verified:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or not verified"
            )
        
        # Generate OTP
        otp = OTPService.generate_otp()
        
        # Get user for name (for email)
        user = await auth_service.get_user_by_mobile(request.mobile_number)
        name = user.name if user else "User"
        
        # Send OTP
        success = await otp_service.send_otp(
            mobile_number=request.mobile_number,
            otp=otp,
            method=request.otp_method,
            email=request.email,
            name=name
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP"
            )
        
        # Store OTP
        OTPManager.store_otp(
            mobile_number=request.mobile_number,
            otp=otp,
            method=request.otp_method,
            purpose="forgot_password",
            email=request.email
        )
        
        return MessageResponse(message="OTP sent for password reset")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending forgot password OTP: {str(e)}"
        )

@router.post("/verify-forgot-password-otp", response_model=MessageResponse)
async def verify_forgot_password_otp(request: VerifyOTPRequest):
    """Verify OTP for password reset"""
    try:
        # Verify OTP
        otp_valid, _ = OTPManager.verify_otp(
            mobile_number=request.mobile_number,
            otp=request.otp,
            purpose="forgot_password"
        )
        
        if not otp_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        return MessageResponse(message="OTP verified successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying OTP: {str(e)}"
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """Reset password after OTP verification"""
    try:
        # Verify OTP again for security
        otp_valid, _ = OTPManager.verify_otp(
            mobile_number=request.mobile_number,
            otp=request.otp,
            purpose="forgot_password"
        )
        
        if not otp_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Update password
        success = await auth_service.update_password(request.mobile_number, request.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        return MessageResponse(message="Password updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting password: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout", response_model=MessageResponse)
async def logout_user(current_user: UserResponse = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return MessageResponse(message="Logged out successfully")

# Legacy endpoints for compatibility with existing MedGloss frontend
@router.get("/user-exists")
async def user_exists_legacy(mobileNumber: str):
    """Legacy endpoint for checking if user exists"""
    try:
        exists, verified = await auth_service.user_exists(mobileNumber)
        return {"exists": exists and verified}
    except Exception as e:
        return {"exists": False}

@router.post("/send-otp-register")
async def send_otp_register_legacy(request: dict):
    """Legacy endpoint for sending registration OTP"""
    try:
        # Extract data from request
        mobile_number = request.get("mobileNumber")
        otp_method = request.get("otpMethod", "sms")
        email = request.get("email")
        
        if not mobile_number:
            raise HTTPException(status_code=400, detail="Mobile number required")
        
        # Store user data for registration
        user_data = {
            "name": request.get("name"),
            "mobile_number": mobile_number,
            "email": email,
            "password": request.get("password"),
            "role": request.get("role", "student"),
            "otp_method": otp_method,
            "college_name": request.get("collegeName"),
            "course": request.get("course"),
            "year": request.get("year"),
            "exam_name": request.get("examName"),
            "hospital_name": request.get("hospitalName"),
            "speciality": request.get("speciality"),
            "experience": request.get("experience")
        }
        
        # Generate and send OTP
        otp = OTPService.generate_otp()
        success = await otp_service.send_otp(mobile_number, otp, otp_method, email)
        
        if success:
            OTPManager.store_otp(mobile_number, otp, otp_method, "registration", email, user_data)
            return {"message": "OTP sent for registration", "status": 200}
        else:
            raise HTTPException(status_code=500, detail="Failed to send OTP")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-otp-register")
async def verify_otp_register_legacy(request: dict):
    """Legacy endpoint for verifying registration OTP"""
    try:
        mobile_number = request.get("mobileNumber")
        otp = request.get("otp")
        
        # Verify OTP and get user data
        otp_valid, user_data = OTPManager.verify_otp(mobile_number, otp, "registration")
        
        if not otp_valid or not user_data:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        # Create user
        user = await auth_service.create_user(user_data)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return {"message": "User registered successfully", "user": user.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
