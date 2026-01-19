import smtplib
import requests
import aiohttp
import secrets
import string
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime, timedelta
import os
from app.config import settings

class OTPService:
    """Service for sending OTP via SMS and Email"""
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random OTP"""
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    @staticmethod
    async def send_sms_otp(mobile_number: str, otp: str) -> bool:
        """Send OTP via SMS using Fast2SMS"""
        try:
            # Remove + from mobile number for Fast2SMS
            clean_number = mobile_number.replace('+', '')
            if clean_number.startswith('91'):
                clean_number = clean_number[2:]  # Remove country code for Indian numbers
            
            api_key = settings.FAST2SMS_API_KEY
            if not api_key:
                print("Fast2SMS API key not configured")
                return False
            
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            payload = {
                "sender_id": "FSTSMS",
                "message": f"Your StudyBuddy OTP is {otp}. Valid for 10 minutes. Do not share with anyone.",
                "language": "english",
                "route": "p",
                "numbers": clean_number
            }
            
            headers = {
                "authorization": api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"SMS sent successfully: {result}")
                return True
            else:
                print(f"SMS sending failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending SMS OTP: {str(e)}")
            return False
    
    @staticmethod
    async def send_email_via_gmail_api(email: str, otp: str, name: str = "User") -> bool:
        """Send OTP via Gmail API"""
        try:
            if not settings.gmail_api_key:
                return False
                
            # Create email content
            subject = "StudyBuddy - Your OTP Code"
            body = f"""Hello {name},

Your OTP code is: {otp}

This OTP is valid for 10 minutes. Please do not share this code with anyone.

If you didn't request this OTP, please ignore this email.

- StudyBuddy Team"""
            
            # Create email message
            message = {
                'raw': base64.urlsafe_b64encode(
                    f"To: {email}\r\n"
                    f"Subject: {subject}\r\n"
                    f"Content-Type: text/plain; charset=utf-8\r\n\r\n"
                    f"{body}".encode('utf-8')
                ).decode('utf-8')
            }
            
            # Send via Gmail API
            async with aiohttp.ClientSession() as session:
                url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/send?key={settings.gmail_api_key}"
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {settings.gmail_api_key}'
                }
                
                async with session.post(url, json=message, headers=headers) as response:
                    if response.status == 200:
                        print(f"Gmail API: Email OTP sent successfully to {email}")
                        return True
                    else:
                        print(f"Gmail API error: {response.status} - {await response.text()}")
                        return False
                        
        except Exception as e:
            print(f"Gmail API error: {str(e)}")
            return False
    
    @staticmethod
    async def send_email_otp(email: str, otp: str, name: str = "User") -> bool:
        """Send OTP via Email - tries Gmail API first, then SMTP"""
        # Try Gmail API first if available
        if settings.gmail_api_key:
            result = await OTPService.send_email_via_gmail_api(email, otp, name)
            if result:
                return True
            print("Gmail API failed, falling back to SMTP...")
        
        # Fall back to SMTP
        try:
            smtp_server = settings.SMTP_SERVER
            smtp_port = settings.SMTP_PORT
            smtp_username = settings.SMTP_USERNAME
            smtp_password = settings.SMTP_PASSWORD
            
            if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
                print("Email configuration not complete")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = email
            msg['Subject'] = "StudyBuddy - Your OTP Code"
            
            # Email body
            body = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2c3e50;">StudyBuddy - OTP Verification</h2>
                    <p>Hello {name},</p>
                    <p>Your OTP code is:</p>
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #e74c3c; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp}</h1>
                    </div>
                    <p>This OTP is valid for 10 minutes. Please do not share this code with anyone.</p>
                    <p>If you didn't request this OTP, please ignore this email.</p>
                    <hr style="margin: 30px 0;">
                    <p style="color: #7f8c8d; font-size: 12px;">
                        This is an automated email from StudyBuddy. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, email, text)
            server.quit()
            
            print(f"Email OTP sent successfully to {email}")
            return True
            
        except Exception as e:
            print(f"Error sending email OTP: {str(e)}")
            return False
    
    @staticmethod
    async def send_otp(mobile_number: str, otp: str, method: str, email: Optional[str] = None, name: str = "User") -> bool:
        """Send OTP via specified method"""
        if method == "sms":
            return await OTPService.send_sms_otp(mobile_number, otp)
        elif method == "email" and email:
            return await OTPService.send_email_otp(email, otp, name)
        else:
            print(f"Invalid OTP method: {method}")
            return False

class OTPManager:
    """In-memory OTP storage (replace with Redis in production)"""
    
    _otp_store = {}
    
    @classmethod
    def store_otp(cls, mobile_number: str, otp: str, method: str, purpose: str, 
                  email: Optional[str] = None, user_data: Optional[dict] = None, 
                  expires_in_minutes: int = 10):
        """Store OTP with expiration"""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        cls._otp_store[mobile_number] = {
            "otp": otp,
            "method": method,
            "email": email,
            "purpose": purpose,
            "user_data": user_data,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        print(f"OTP stored for {mobile_number}: {otp} (expires at {expires_at})")
    
    @classmethod
    def verify_otp(cls, mobile_number: str, otp: str, purpose: str) -> tuple[bool, Optional[dict]]:
        """Verify OTP and return user data if valid"""
        stored_data = cls._otp_store.get(mobile_number)
        
        if not stored_data:
            return False, None
        
        # Check if OTP expired
        if datetime.utcnow() > stored_data["expires_at"]:
            cls.clear_otp(mobile_number)
            return False, None
        
        # Check if OTP matches and purpose matches
        if stored_data["otp"] == otp and stored_data["purpose"] == purpose:
            user_data = stored_data.get("user_data")
            cls.clear_otp(mobile_number)  # Clear after successful verification
            return True, user_data
        
        return False, None
    
    @classmethod
    def clear_otp(cls, mobile_number: str):
        """Clear OTP for mobile number"""
        if mobile_number in cls._otp_store:
            del cls._otp_store[mobile_number]
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired OTPs"""
        current_time = datetime.utcnow()
        expired_numbers = [
            number for number, data in cls._otp_store.items()
            if current_time > data["expires_at"]
        ]
        
        for number in expired_numbers:
            cls.clear_otp(number)
        
        if expired_numbers:
            print(f"Cleaned up {len(expired_numbers)} expired OTPs")
