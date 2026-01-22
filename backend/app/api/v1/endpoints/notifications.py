from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class EmailNotificationRequest(BaseModel):
    email: EmailStr

@router.post("/sessions/{session_id}/enable-email-notification")
async def enable_email_notification(
    session_id: str,
    request: EmailNotificationRequest
):
    """Enable email notification for session completion"""
    try:
        db = get_database()
        
        # Update session with email notification settings
        result = await db.study_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "email_notification_enabled": True,
                    "notification_email": request.email
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Email notification enabled for session {session_id}: {request.email}")
        
        return {"message": "Email notification enabled successfully"}
        
    except Exception as e:
        logger.error(f"Failed to enable email notification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enable email notification")

@router.post("/send-completion-email/{session_id}")
async def send_completion_email(session_id: str):
    """Send completion email for a session"""
    try:
        db = get_database()
        
        # Get session details
        session = await db.study_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.get("email_notification_enabled") or not session.get("notification_email"):
            return {"message": "Email notification not enabled for this session"}
        
        # Get content counts
        questions_count = await db.questions.count_documents({"session_id": session_id})
        mnemonics_count = await db.mnemonics.count_documents({"session_id": session_id})
        cheat_sheets_count = await db.cheat_sheets.count_documents({"session_id": session_id})
        mock_tests_count = await db.mock_tests.count_documents({"session_id": session_id})
        
        # Send actual email using SMTP
        success = await _send_actual_completion_email(
            session['notification_email'],
            session.get('session_name', 'Study Session'),
            questions_count, mnemonics_count, cheat_sheets_count, mock_tests_count
        )
        
        if success:
            logger.info(f"📧 Completion email sent to {session['notification_email']} for session {session_id}")
            return {"message": "Completion email sent successfully"}
        else:
            logger.error(f"❌ Failed to send completion email to {session['notification_email']}")
            raise HTTPException(status_code=500, detail="Failed to send email")
        
    except Exception as e:
        logger.error(f"Failed to send completion email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")

async def _send_actual_completion_email(email: str, session_name: str, questions: int, mnemonics: int, cheat_sheets: int, mock_tests: int) -> bool:
    """Send actual completion email using SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from app.config import settings
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = settings.smtp_username
        msg['To'] = email
        msg['Subject'] = '🎉 Your Study Materials are Ready!'
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">🎉 Your Study Materials are Ready!</h2>
                
                <p>Great news! Your study materials have been successfully generated.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Session: {session_name}</h3>
                    
                    <h4 style="color: #34495e;">Generated Content:</h4>
                    <ul style="list-style-type: none; padding: 0;">
                        <li style="padding: 5px 0;">📝 <strong>{questions} Questions</strong></li>
                        <li style="padding: 5px 0;">🧠 <strong>{mnemonics} Mnemonics</strong></li>
                        <li style="padding: 5px 0;">📋 <strong>{cheat_sheets} Cheat Sheets</strong></li>
                        <li style="padding: 5px 0;">📊 <strong>{mock_tests} Mock Tests</strong></li>
                    </ul>
                </div>
                
                <p style="margin: 30px 0;">
                    <a href="#" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Access Your Materials
                    </a>
                </p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #7f8c8d; font-size: 12px;">
                    This is an automated email from Study Buddy. Your study materials are ready for review.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email using SMTP
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        text = msg.as_string()
        server.sendmail(settings.smtp_username, email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send completion email: {str(e)}")
        return False
