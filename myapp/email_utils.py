"""
Email utility functions for sending OTP and notifications
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_otp_email(email_to, otp_code, purpose='login'):
    """
    Send OTP email using Django's email backend (preferred method)
    
    Args:
        email_to (str): Recipient email address
        otp_code (int): OTP code to send
        purpose (str): Purpose of OTP ('login', 'booking', etc.)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        subject = f'OTP for {purpose.upper()} - {otp_code}'
        
        html_message = f"""
        <html>
            <head></head>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #333;">OTP Verification</h2>
                    <p style="color: #666;">Your One-Time Password (OTP) for {purpose} is:</p>
                    
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #007bff; letter-spacing: 5px; margin: 0;">{otp_code}</h1>
                    </div>
                    
                    <p style="color: #666;">
                        This OTP is valid for 10 minutes. Do not share it with anyone.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 12px;">
                        If you didn't request this OTP, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        plain_message = f'Your OTP for {purpose} is: {otp_code}\n\nDo not share this with anyone.'
        
        # Try Django's email backend first (more reliable)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email_to],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"OTP email sent successfully to {email_to} for {purpose}")
        print(f"✓ OTP email sent to {email_to}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email_to}: {str(e)}")
        print(f"✗ Email error: {str(e)}")
        
        # Fallback to direct SMTP if Django backend fails
        return send_otp_email_direct_smtp(email_to, otp_code, purpose)


def send_otp_email_direct_smtp(email_to, otp_code, purpose='login'):
    """
    Fallback method: Send OTP email using direct SMTP connection
    
    Args:
        email_to (str): Recipient email address
        otp_code (int): OTP code to send
        purpose (str): Purpose of OTP
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email_to
        msg['Subject'] = f'OTP for {purpose.upper()} - {otp_code}'
        
        text = f"Your OTP for {purpose} is: {otp_code}\n\nDo not share this with anyone."
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>OTP Verification</h2>
                    <p>Your One-Time Password (OTP) for {purpose} is:</p>
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #007bff; letter-spacing: 5px;">{otp_code}</h1>
                    </div>
                    <p>This OTP is valid for 10 minutes.</p>
                </div>
            </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect to SMTP server
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(msg['From'], email_to, msg.as_string())
        
        logger.info(f"OTP email sent via SMTP to {email_to} for {purpose}")
        print(f"✓ OTP email sent via SMTP to {email_to}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Gmail authentication failed: {str(e)}")
        print(f"✗ Gmail Authentication Error: {str(e)}")
        print("Note: If using Gmail with 2FA, use an App Password instead of your regular password.")
        return False
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error while sending to {email_to}: {str(e)}")
        print(f"✗ SMTP Error: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error sending OTP to {email_to}: {str(e)}")
        print(f"✗ Unexpected Error: {str(e)}")
        return False
