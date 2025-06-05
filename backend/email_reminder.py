import os
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Email configuration for reminders only
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "teamcommunitypulse319@gmail.com"
SMTP_PASSWORD = "uynl zloc dvrf zcwk"  # App password

def send_event_reminder(recipient: str, event_name: str, event_details: dict) -> bool:
    """
    Send REMINDER notifications for events happening the next day.
    This function is completely separate from update notifications.
    """
    try:
        # Create message container for reminder
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient
        msg['Subject'] = f"Tomorrow's Event: {event_name}"
        
        # Create the body specifically for reminders
        location_parts = [
            event_details.get('address', ''),
            event_details.get('city', ''),
            event_details.get('state', '')
        ]
        location = ', '.join(filter(None, location_parts))
        
        # Reminder-specific template
        body = f"""
Hello!

This is a reminder that {event_name} is happening tomorrow!

Event Details:
- Time: {event_details.get('start_time', 'TBD')}
- Location: {location or 'TBD'}
- Description: {event_details.get('description', '')}

We look forward to seeing you there!

Best regards,
Community Pulse Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send the reminder email
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.starttls()
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        s.sendmail(SMTP_USERNAME, recipient, msg.as_string())
        s.quit()
        
        print(f"✅ Reminder email sent to {recipient} for event: {event_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send reminder email: {str(e)}")
        return False

# Add the missing function that's being imported in main.py
def send_event_notifications(recipient: str, event_name: str, event_details: dict) -> bool:
    """
    Send UPDATE notifications for events that have been modified.
    This function is completely separate from reminder notifications.
    """
    try:
        # Create message container for updates
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient
        msg['Subject'] = event_name  # Subject is passed with "UPDATE: " prefix already
        
        # Create the body specifically for updates
        location_parts = [
            event_details.get('address', ''),
            event_details.get('city', ''),
            event_details.get('state', '')
        ]
        location = ', '.join(filter(None, location_parts))
        
        # Include update-specific information
        updates_list = event_details.get('updates', [])
        updates_text = "\n".join([f"- {update}" for update in updates_list]) if updates_list else "No specific changes provided."
        
        # Update-specific template
        body = f"""
Hello!

An event you're following has been updated:

The following changes have been made:
{updates_text}

Updated Event Details:
- Time: {event_details.get('start_time', 'TBD')}
- Location: {location or 'TBD'}

We look forward to seeing you there!

Best regards,
Community Pulse Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send the update email
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.starttls()
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        s.sendmail(SMTP_USERNAME, recipient, msg.as_string())
        s.quit()
        
        print(f"✅ Update notification sent to {recipient} for event: {event_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send update notification: {str(e)}")
        return False


