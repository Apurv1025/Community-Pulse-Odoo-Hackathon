import os
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Your App Password

def send_event_notifications(recipients: List[str], event_name: str, event_details: dict) -> bool:
    """Send event notifications using SMTP"""
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['Subject'] = f"Tomorrow's Event: {event_name}"
        
        # Create the body of the message
        body = f"""
Hello!

This is a reminder that {event_name} is happening tomorrow!

Event Details:
- Time: {event_details['start_time']}
- Location: {event_details['address']}, {event_details['city']}, {event_details['state']}

We look forward to seeing you there!

Best regards,
Community Pulse Team
        """
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Send email to each recipient
            for recipient in recipients:
                msg['To'] = recipient
                text = msg.as_string()
                server.sendmail(SMTP_USERNAME, recipient, text)
                print(f"Successfully sent email to {recipient}")
                
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False