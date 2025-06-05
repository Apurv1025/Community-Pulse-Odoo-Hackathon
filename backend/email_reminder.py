import os
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import schedule
from datetime import datetime
# from backend.event_tasks import schedule_event_reminder, send_event_update_notification

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Your App Password

import smtplib
# creates SMTP session

def send_event_notifications(recipient: str, event_name: str, event_details: dict) -> bool:
    """Send event notifications using SMTP"""
    
    try:
        # Validate credentials
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("Error: Email credentials not configured in .env file")
            return False

        # Create message container
        msg = MIMEMultipart()
        msg['From'] = "teamcommunitypulse319@gmail.com"
        msg['To'] = recipient
        
        # Determine if this is an update or a reminder based on event_name
        is_update = event_name.startswith("UPDATE:")
        
        if is_update:
            msg['Subject'] = event_name  # "UPDATE: Event Name"
        else:
            msg['Subject'] = f"Tomorrow's Event: {event_name}"
        
        # Create the body of the message with safe dictionary access
        location_parts = [
            event_details.get('address', ''),
            event_details.get('city', ''),
            event_details.get('state', '')
        ]
        location = ', '.join(filter(None, location_parts))
        
        # Different body templates for updates vs reminders
        if is_update:
            # This is an update notification
            update_messages = event_details.get('updates', [])
            updates_text = "\n".join([f"- {update}" for update in update_messages])
            
            body = f"""
Hello!

An event you're following has been updated:
{event_name.replace("UPDATE: ", "")}

The following changes have been made:
{updates_text}

Updated Event Details:
- Time: {event_details.get('start_time', 'TBD')}
- Location: {location or 'TBD'}

We look forward to seeing you there!

Best regards,
Community Pulse Team
            """
        else:
            # This is a regular reminder
            body = f"""
Hello!

This is a reminder that {event_name} is happening tomorrow!

Event Details:
- Time: {event_details.get('start_time', 'TBD')}
- Location: {location or 'TBD'}

We look forward to seeing you there!

Best regards,
Community Pulse Team
            """
        
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
        s.starttls()
# Authentication
        # s.login("rashinkarapurv@gmail.com", "kmoi jzmc bmmm hwzf")
        try:
            s.login("teamcommunitypulse319@gmail.com", "uynl zloc dvrf zcwk")
        except smtplib.SMTPAuthenticationError:
            print("""
Authentication failed! Please check:
1. Your App Password is correctly set in .env file
2. You're using App Password, not regular Gmail password
3. Your Gmail account has 2-Step Verification enabled
            """)
            return False
            
        text = msg.as_string()
        s.sendmail(str(SMTP_USERNAME), recipient, text)
    
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


