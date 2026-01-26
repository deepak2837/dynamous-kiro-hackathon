import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pymongo.collection import Collection
from bson import ObjectId
from app.auth_models_simple import UserDB, UserResponse, UserRole, OTPMethod
from app.database import get_database
from app.config import settings

class AuthService:
    """Authentication service for user management"""
    
    def __init__(self):
        self.db = None
        self.users_collection = None
    
    def get_db(self):
        if self.db is None:
            self.db = get_database()
            self.users_collection = self.db.users
        return self.db
    
    def normalize_phone_number(self, phone: str) -> str:
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
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_jwt_token(self, user_id: str, mobile_number: str) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'mobile_number': mobile_number,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def user_exists(self, mobile_number: str) -> tuple[bool, bool]:
        """Check if user exists and is verified"""
        self.get_db()
        mobile_number = self.normalize_phone_number(mobile_number)
        user = self.users_collection.find_one({"mobile_number": mobile_number})
        
        if user:
            return True, user.get("verified", False)
        return False, False
    
    async def create_user(self, user_data: dict) -> Optional[UserResponse]:
        """Create a new user"""
        try:
            # Normalize phone number
            user_data["mobile_number"] = self.normalize_phone_number(user_data["mobile_number"])
            
            # Hash password
            user_data["password_hash"] = self.hash_password(user_data.pop("password"))
            
            # Set timestamps
            user_data["created_at"] = datetime.utcnow()
            user_data["verified"] = True  # Set to True after OTP verification
            
            # Insert user
            result = self.users_collection.insert_one(user_data)
            
            if result.inserted_id:
                # Fetch created user
                user = self.users_collection.find_one({"_id": result.inserted_id})
                return self._user_to_response(user)
            
            return None
            
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    async def authenticate_user(self, mobile_number: str, password: str) -> Optional[UserResponse]:
        """Authenticate user with mobile number and password"""
        try:
            # Normalize phone number to ensure consistent format (e.g., +91xxxxxxxxxx)
            mobile_number = self.normalize_phone_number(mobile_number)
            
            # Find user by mobile number and ensure they are verified
            user = self.users_collection.find_one({
                "mobile_number": mobile_number,
                "verified": True  # Only allow verified users to login
            })
            
            # Verify password using bcrypt hash comparison
            if user and self.verify_password(password, user["password_hash"]):
                # Convert database user document to response format
                return self._user_to_response(user)
            
            # Return None if user not found or password incorrect
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return self._user_to_response(user)
            return None
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            return None
    
    async def get_user_by_mobile(self, mobile_number: str) -> Optional[UserResponse]:
        """Get user by mobile number"""
        try:
            mobile_number = self.normalize_phone_number(mobile_number)
            user = self.users_collection.find_one({"mobile_number": mobile_number})
            if user:
                return self._user_to_response(user)
            return None
        except Exception as e:
            print(f"Error getting user by mobile: {str(e)}")
            return None
    
    async def update_password(self, mobile_number: str, new_password: str) -> bool:
        """Update user password"""
        try:
            mobile_number = self.normalize_phone_number(mobile_number)
            password_hash = self.hash_password(new_password)
            
            result = self.users_collection.update_one(
                {"mobile_number": mobile_number},
                {
                    "$set": {
                        "password_hash": password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[UserResponse]:
        """Update user information"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                user = self.users_collection.find_one({"_id": ObjectId(user_id)})
                return self._user_to_response(user)
            
            return None
            
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return None
    
    def _user_to_response(self, user: dict) -> UserResponse:
        """Convert database user to response model"""
        return UserResponse(
            _id=user["_id"],
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
