import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app
from app.services.auth_service import AuthService
from app.auth_models_simple import User, UserCreate, UserLogin

client = TestClient(app)

class TestAuthEndpoints:
    """Test cases for authentication endpoints"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.test_mobile = "9876543210"
        self.test_password = "testpassword123"
        self.test_otp = "123456"
        self.test_user_data = {
            "id": "user123",
            "mobile": self.test_mobile,
            "created_at": "2026-01-22T10:00:00Z",
            "is_active": True
        }

    @patch('app.services.auth_service.AuthService.send_otp')
    def test_send_otp_success(self, mock_send_otp):
        """Test successful OTP sending"""
        mock_send_otp.return_value = True
        
        response = client.post(
            "/api/v1/auth/send-otp",
            json={"mobile": self.test_mobile}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        assert "expires_in" in data
        mock_send_otp.assert_called_once_with(self.test_mobile)

    def test_send_otp_invalid_mobile(self):
        """Test OTP sending with invalid mobile number"""
        response = client.post(
            "/api/v1/auth/send-otp",
            json={"mobile": "123"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @patch('app.services.auth_service.AuthService.send_otp')
    def test_send_otp_service_failure(self, mock_send_otp):
        """Test OTP sending when service fails"""
        mock_send_otp.return_value = False
        
        response = client.post(
            "/api/v1/auth/send-otp",
            json={"mobile": self.test_mobile}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Failed to send OTP" in data["detail"]

    @patch('app.services.auth_service.AuthService.verify_otp')
    def test_verify_otp_success(self, mock_verify_otp):
        """Test successful OTP verification"""
        mock_verify_otp.return_value = True
        
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={"mobile": self.test_mobile, "otp": self.test_otp}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP verified successfully"
        assert data["valid"] is True
        mock_verify_otp.assert_called_once_with(self.test_mobile, self.test_otp)

    @patch('app.services.auth_service.AuthService.verify_otp')
    def test_verify_otp_invalid(self, mock_verify_otp):
        """Test OTP verification with invalid OTP"""
        mock_verify_otp.return_value = False
        
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={"mobile": self.test_mobile, "otp": "000000"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid or expired OTP" in data["detail"]

    def test_verify_otp_invalid_format(self):
        """Test OTP verification with invalid OTP format"""
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={"mobile": self.test_mobile, "otp": "123"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @patch('app.services.auth_service.AuthService.register_user')
    @patch('app.services.auth_service.AuthService.verify_otp')
    def test_register_success(self, mock_verify_otp, mock_register_user):
        """Test successful user registration"""
        mock_verify_otp.return_value = True
        mock_user = User(**self.test_user_data)
        mock_register_user.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": self.test_mobile,
                "password": self.test_password,
                "otp": self.test_otp
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert "token_type" in data
        assert data["user"]["mobile"] == self.test_mobile
        assert data["token_type"] == "bearer"

    @patch('app.services.auth_service.AuthService.verify_otp')
    def test_register_invalid_otp(self, mock_verify_otp):
        """Test registration with invalid OTP"""
        mock_verify_otp.return_value = False
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": self.test_mobile,
                "password": self.test_password,
                "otp": "000000"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid OTP" in data["detail"]

    def test_register_invalid_password(self):
        """Test registration with invalid password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": self.test_mobile,
                "password": "123",  # Too short
                "otp": self.test_otp
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @patch('app.services.auth_service.AuthService.authenticate_user')
    def test_login_success(self, mock_authenticate_user):
        """Test successful user login"""
        mock_user = User(**self.test_user_data)
        mock_authenticate_user.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": self.test_mobile,
                "password": self.test_password
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert "token_type" in data
        assert data["user"]["mobile"] == self.test_mobile
        assert data["token_type"] == "bearer"

    @patch('app.services.auth_service.AuthService.authenticate_user')
    def test_login_invalid_credentials(self, mock_authenticate_user):
        """Test login with invalid credentials"""
        mock_authenticate_user.return_value = None
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "mobile": self.test_mobile,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid credentials" in data["detail"]

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        response = client.post(
            "/api/v1/auth/login",
            json={"mobile": self.test_mobile}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @patch('app.services.auth_service.AuthService.register_user')
    @patch('app.services.auth_service.AuthService.verify_otp')
    def test_register_duplicate_user(self, mock_verify_otp, mock_register_user):
        """Test registration with existing mobile number"""
        mock_verify_otp.return_value = True
        mock_register_user.side_effect = ValueError("User already exists")
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "mobile": self.test_mobile,
                "password": self.test_password,
                "otp": self.test_otp
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "User already exists" in data["detail"]

class TestAuthService:
    """Test cases for AuthService class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.auth_service = AuthService()
        self.test_mobile = "9876543210"
        self.test_password = "testpassword123"
        self.test_otp = "123456"

    @patch('app.services.otp_service.OTPService.send_otp')
    def test_send_otp_success(self, mock_send_otp):
        """Test successful OTP sending"""
        mock_send_otp.return_value = True
        
        result = self.auth_service.send_otp(self.test_mobile)
        
        assert result is True
        mock_send_otp.assert_called_once_with(self.test_mobile)

    @patch('app.services.otp_service.OTPService.send_otp')
    def test_send_otp_failure(self, mock_send_otp):
        """Test OTP sending failure"""
        mock_send_otp.return_value = False
        
        result = self.auth_service.send_otp(self.test_mobile)
        
        assert result is False

    @patch('app.services.otp_service.OTPService.verify_otp')
    def test_verify_otp_success(self, mock_verify_otp):
        """Test successful OTP verification"""
        mock_verify_otp.return_value = True
        
        result = self.auth_service.verify_otp(self.test_mobile, self.test_otp)
        
        assert result is True
        mock_verify_otp.assert_called_once_with(self.test_mobile, self.test_otp)

    @patch('app.services.otp_service.OTPService.verify_otp')
    def test_verify_otp_invalid(self, mock_verify_otp):
        """Test OTP verification with invalid OTP"""
        mock_verify_otp.return_value = False
        
        result = self.auth_service.verify_otp(self.test_mobile, "000000")
        
        assert result is False

    @patch('app.database.get_database')
    @patch('bcrypt.hashpw')
    def test_register_user_success(self, mock_hashpw, mock_get_db):
        """Test successful user registration"""
        mock_hashpw.return_value = b'hashed_password'
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.users = mock_collection
        mock_collection.find_one.return_value = None  # User doesn't exist
        mock_collection.insert_one.return_value = Mock(inserted_id="user123")
        mock_get_db.return_value = mock_db
        
        user = self.auth_service.register_user(self.test_mobile, self.test_password, self.test_otp)
        
        assert user is not None
        assert user.mobile == self.test_mobile
        mock_collection.insert_one.assert_called_once()

    @patch('app.database.get_database')
    def test_register_user_duplicate(self, mock_get_db):
        """Test registration with existing user"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.users = mock_collection
        mock_collection.find_one.return_value = {"mobile": self.test_mobile}  # User exists
        mock_get_db.return_value = mock_db
        
        with pytest.raises(ValueError, match="User already exists"):
            self.auth_service.register_user(self.test_mobile, self.test_password, self.test_otp)

    @patch('app.database.get_database')
    @patch('bcrypt.checkpw')
    def test_authenticate_user_success(self, mock_checkpw, mock_get_db):
        """Test successful user authentication"""
        mock_checkpw.return_value = True
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.users = mock_collection
        mock_collection.find_one.return_value = {
            "_id": "user123",
            "mobile": self.test_mobile,
            "password_hash": "hashed_password",
            "created_at": "2026-01-22T10:00:00Z",
            "is_active": True
        }
        mock_get_db.return_value = mock_db
        
        user = self.auth_service.authenticate_user(self.test_mobile, self.test_password)
        
        assert user is not None
        assert user.mobile == self.test_mobile
        mock_checkpw.assert_called_once()

    @patch('app.database.get_database')
    def test_authenticate_user_not_found(self, mock_get_db):
        """Test authentication with non-existent user"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.users = mock_collection
        mock_collection.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        user = self.auth_service.authenticate_user(self.test_mobile, self.test_password)
        
        assert user is None

    @patch('app.database.get_database')
    @patch('bcrypt.checkpw')
    def test_authenticate_user_wrong_password(self, mock_checkpw, mock_get_db):
        """Test authentication with wrong password"""
        mock_checkpw.return_value = False
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.users = mock_collection
        mock_collection.find_one.return_value = {
            "_id": "user123",
            "mobile": self.test_mobile,
            "password_hash": "hashed_password",
            "created_at": "2026-01-22T10:00:00Z",
            "is_active": True
        }
        mock_get_db.return_value = mock_db
        
        user = self.auth_service.authenticate_user(self.test_mobile, "wrongpassword")
        
        assert user is None

    def test_create_access_token(self):
        """Test JWT token creation"""
        user_id = "user123"
        
        token = self.auth_service.create_access_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @patch('jwt.decode')
    def test_verify_token_success(self, mock_decode):
        """Test successful token verification"""
        mock_decode.return_value = {"user_id": "user123", "exp": 9999999999}
        
        user_id = self.auth_service.verify_token("valid_token")
        
        assert user_id == "user123"

    @patch('jwt.decode')
    def test_verify_token_invalid(self, mock_decode):
        """Test token verification with invalid token"""
        mock_decode.side_effect = Exception("Invalid token")
        
        user_id = self.auth_service.verify_token("invalid_token")
        
        assert user_id is None
