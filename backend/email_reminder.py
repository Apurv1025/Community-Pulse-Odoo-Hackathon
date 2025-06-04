import os
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

MAILTRAP_API_TOKEN = os.getenv("MAILTRAP_API_TOKEN")
MAILTRAP_API_URL = "https://sandbox.api.mailtrap.io/api/send/3696508"

def send_event_notifications(recipients: List[str], event_name: str, event_details: dict) -> bool:
    """Send event notifications using Mailtrap"""
    to_recipients = [{"email": email} for email in recipients]
    
    payload = {
        "from": {
            "email": "notifications@communitypulse.com",
            "name": "Community Pulse"
        },
        "to": to_recipients,
        "subject": f"Today's Event: {event_name}",
        "text": f"""
Hello!

This is a reminder that {event_name} is happening today!

Event Details:
- Time: {event_details['start_time']}
- Location: {event_details['address']}, {event_details['city']}, {event_details['state']}

We look forward to seeing you there!

Best regards,
Community Pulse Team
        """,
        "category": "Event Reminder"
    }

    headers = {
        "Authorization": f"Bearer {MAILTRAP_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(MAILTRAP_API_URL, headers=headers, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False