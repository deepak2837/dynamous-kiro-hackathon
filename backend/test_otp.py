#!/usr/bin/env python3
"""
Test script for OTP services (Email and SMS)
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.otp_service import OTPService

async def test_email_otp():
    """Test email OTP service"""
    print("Testing Email OTP...")
    
    test_email = "peenu000@gmail.com"
    test_otp = "123456"
    test_name = "Test User"
    
    try:
        result = await OTPService.send_email_otp(test_email, test_otp, test_name)
        if result:
            print(f"✅ Email OTP sent successfully to {test_email}")
        else:
            print(f"❌ Failed to send email OTP to {test_email}")
    except Exception as e:
        print(f"❌ Email OTP error: {str(e)}")

async def test_sms_otp():
    """Test SMS OTP service"""
    print("Testing SMS OTP...")
    
    test_mobile = "9468151064"
    test_otp = "654321"
    
    try:
        result = await OTPService.send_sms_otp(test_mobile, test_otp)
        if result:
            print(f"✅ SMS OTP sent successfully to {test_mobile}")
        else:
            print(f"❌ Failed to send SMS OTP to {test_mobile}")
    except Exception as e:
        print(f"❌ SMS OTP error: {str(e)}")

async def main():
    """Run OTP service tests"""
    print("🧪 Starting OTP Service Tests\n")
    
    # Test email OTP
    await test_email_otp()
    print()
    
    # Test SMS OTP
    await test_sms_otp()
    print()
    
    print("🏁 OTP Service Tests Complete")

if __name__ == "__main__":
    asyncio.run(main())
