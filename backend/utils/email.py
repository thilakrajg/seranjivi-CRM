import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

class EmailConfig:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@salescrm.com')

async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """Send email using SMTP"""
    try:
        config = EmailConfig()
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = config.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add plain text body
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(config.smtp_server, config.smtp_port)
        server.starttls()
        server.login(config.smtp_username, config.smtp_password)
        text = msg.as_string()
        server.sendmail(config.from_email, to_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

async def send_user_invitation_email(email: str, full_name: str, temp_password: str):
    """Send user invitation email"""
    subject = "Welcome to Sales CRM - Your Account Details"
    
    # HTML email template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Welcome to Sales CRM</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #0A2A43;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
                border-radius: 0 0 8px 8px;
            }}
            .button {{
                display: inline-block;
                background-color: #0A2A43;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Welcome to Sales CRM</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{full_name}</strong>,</p>
            
            <p>Your account has been created in the Sales CRM system. You can now access the platform with the following credentials:</p>
            
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Login URL:</strong> <a href="http://localhost:3000/login">http://localhost:3000/login</a></p>
                <p><strong>Username:</strong> {email}</p>
                <p><strong>Temporary Password:</strong> <code style="background-color: #fff; padding: 2px 4px; border-radius: 3px;">{temp_password}</code></p>
            </div>
            
            <p><strong>Important:</strong> You will be required to change your password upon first login for security purposes.</p>
            
            <div style="text-align: center;">
                <a href="http://localhost:3000/login" class="button">Login to Sales CRM</a>
            </div>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; 2024 Sales CRM. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    text_body = f"""
    Dear {full_name},
    
    Your account has been created in the Sales CRM system.
    
    Login URL: http://localhost:3000/login
    Username: {email}
    Temporary Password: {temp_password}
    
    You will be required to change your password upon first login.
    
    Best regards,
    Sales CRM Team
    """
    
    return await send_email(email, subject, text_body, html_body)
