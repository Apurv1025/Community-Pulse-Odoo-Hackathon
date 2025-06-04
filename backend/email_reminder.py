import os
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import schedule
from datetime import datetime

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
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient
        msg['Subject'] = f"Tomorrow's Event: {event_name}"
        
        # Create the body of the message with safe dictionary access
        location_parts = [
            event_details.get('address', ''),
            event_details.get('city', ''),
            event_details.get('state', '')
        ]
        location = ', '.join(filter(None, location_parts))
        
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
    
def schedule_for_specific_date(
    target_date,
    target_time,
    recipient: str,
    event_name: str,
    event_details: dict
):
    """
    Schedule an email notification for a specific date and time.

    Args:
        target_date: The date to send the notification (datetime or str 'YYYY-MM-DD').
        target_time: The time to send the notification (str 'HH:MM').
        recipients: List of recipient email addresses.
        event_name: Name of the event.
        event_details: Dictionary with event details.
    """
    # Convert target_date to datetime if it's a string
    if isinstance(target_date, str):
        target_date = datetime.strptime(
            target_date,
            '%Y-%m-%d'
        )

    # Get the day name (monday, tuesday, etc.)
    day_name = target_date.strftime('%A').lower()

    # Create a one-time job wrapper
    def job_once():
        # Check if today is the target date
        if datetime.now().date() == target_date.date():
            send_event_notifications(
                recipient,
                event_name,
                event_details
                )
            print(
                f"Job executed for "
                f"{target_date.strftime('%Y-%m-%d')} "
                f"at {target_time}"
            )
            return schedule.CancelJob

    # Schedule the job for that specific day and time
    getattr(
        schedule.every(),
        day_name
    ).at(target_time).do(job_once)

    # Run the scheduler loop to execute pending jobs
    while True:
        schedule.run_pending()
        # Sleep for a short time to prevent high CPU usage
        import time
        time.sleep(30)

