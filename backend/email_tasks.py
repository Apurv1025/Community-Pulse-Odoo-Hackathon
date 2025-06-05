from celery import Celery
import os

# Initialize Celery
celery_app = Celery('backend')

# Configure using Redis
celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks explicitly to ensure they're registered
@celery_app.on_after_configure.connect
def setup_imports(sender, **kwargs):
    # Register task modules explicitly
    sender.import_module('backend.email_tasks')

from celery import shared_task
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select
from backend.utils.db import engine
from backend.models import Event, EventUpdates, User, EventRegistered, EventFollowing

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "teamcommunitypulse319@gmail.com"
SMTP_PASSWORD = "uynl zloc dvrf zcwk"  # App password

@celery_app.task(name="send_event_update_notification")
def send_event_update_notification(recipient_email, event_id, update_id):
    """
    Send notification about event updates
    """
    print(f"Sending update notification to {recipient_email} for event {event_id}")
    
    try:
        with Session(engine) as session:
            # Get event update record
            update_record = session.get(EventUpdates, update_id)
            if not update_record:
                print(f"Update record {update_id} not found")
                return {"status": "error", "message": "Update record not found"}
            
            # Get event details
            event = session.get(Event, event_id)
            if not event:
                print(f"Event {event_id} not found")
                return {"status": "error", "message": "Event not found"}
            
            # Parse update data
            try:
                update_data = json.loads(update_record.LastUpdate)
                changes = update_data.get("changes", [])
                summary = update_data.get("summary", [])
            except Exception as e:
                print(f"Error parsing update data: {str(e)}")
                return {"status": "error", "message": f"Failed to parse update data: {str(e)}"}
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = SMTP_USERNAME
            msg['To'] = recipient_email
            msg['Subject'] = f"Event Update: {event.event_name}"
            
            # Create simple HTML content
            updates_text = "\n".join([f"- {update}" for update in summary])
            body = f"""
Hello!

An event you're following has been updated:
{event.event_name}

Changes:
{updates_text}

Best regards,
Community Pulse Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Successfully sent update notification to {recipient_email}")
            return {"status": "success", "recipient": recipient_email}
    except Exception as e:
        print(f"❌ Error sending update notification: {str(e)}")
        return {"status": "error", "message": str(e)}

# Make sure your task is defined with the exact name being called
@celery_app.task(name="schedule_event_reminders")
def schedule_event_reminders(recipient_email=None, event_id=None):
    """
    Send reminders for events.
    Can either:
    1. Process all events happening tomorrow (when called with no args)
    2. Send a reminder to a specific user for a specific event (when called with args)
    """
    print(f"Running schedule_event_reminders with recipient={recipient_email}, event_id={event_id}")
    
    # If specific user and event are provided, send targeted reminder
    if recipient_email and event_id:
        with Session(engine) as session:
            # Get event details
            event = session.get(Event, event_id)
            if not event:
                print(f"Event {event_id} not found")
                return {"status": "error", "message": f"Event {event_id} not found"}
            
            # Create event details dict for the reminder
            event_details = {
                "start_time": event.start_date.strftime("%I:%M %p on %Y-%m-%d"),
                "address": event.address,
                "city": event.city,
                "state": event.state,
                "description": event.event_description  # Changed from event.description
            }
            
            # Send reminder to specific user
            from backend.email_reminder import send_event_reminder
            result = send_event_reminder(recipient_email, event.event_name, event_details)
            return {"status": "success" if result else "failed"}
    
    # Otherwise run the daily check for all tomorrow's events (original implementation)
    else:
        from datetime import datetime, timedelta
        
        print("Running daily event reminder scheduler")
        
        # Calculate tomorrow's date
        tomorrow = datetime.now().date() + timedelta(days=1)
        tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time())
        
        with Session(engine) as session:
            # Find all events happening tomorrow
            events = session.exec(
                select(Event)
                .where(
                    Event.start_date >= tomorrow_start,
                    Event.start_date <= tomorrow_end,
                    Event.isAccepted == True,
                    Event.isFlagged == False
                )
            ).all()
            
            print(f"Found {len(events)} events happening tomorrow")
            sent_count = 0
            
            for event in events:
                # Get all participants
                participants = set()
                
                # Get registered users
                registrations = session.exec(
                    select(EventRegistered, User.email)
                    .join(User, EventRegistered.username == User.username)
                    .where(EventRegistered.event_id == event.id)
                ).all()
                
                for reg, email in registrations:
                    if email:
                        participants.add(email)
                        
                # Get followers
                followers = session.exec(
                    select(EventFollowing, User.email)
                    .join(User, EventFollowing.username == User.username)
                    .where(EventFollowing.event_id == event.id)
                ).all()
                
                for follow, email in followers:
                    if email:
                        participants.add(email)
                
                # Event details
                location = ", ".join(filter(None, [event.address, event.city, event.state]))
                event_details = {
                    "start_time": event.start_date.strftime("%I:%M %p on %Y-%m-%d"),
                    "address": event.address,
                    "city": event.city,
                    "state": event.state,
                    "description": event.event_description  # Changed from event.description
                }
                
                # Send reminders
                from backend.email_reminder import send_event_reminder
                
                for recipient in participants:
                    try:
                        sent = send_event_reminder(recipient, event.event_name, event_details)
                        if sent:
                            sent_count += 1
                    except Exception as e:
                        print(f"Error sending reminder to {recipient}: {str(e)}")
                
            print(f"Successfully sent {sent_count} reminders")
            return {"status": "success", "sent_reminders": sent_count}

@celery_app.task(name="send_registration_confirmation")
def send_registration_confirmation(recipient_email, event_id):
    """
    Send a confirmation email when a user registers for an event.
    This is separate from the scheduled reminders.
    """
    print(f"Sending registration confirmation to {recipient_email} for event {event_id}")
    
    try:
        with Session(engine) as session:
            # Get event details
            event = session.get(Event, event_id)
            if not event:
                print(f"Event {event_id} not found")
                return {"status": "error", "message": "Event not found"}
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = SMTP_USERNAME
            msg['To'] = recipient_email
            msg['Subject'] = f"Registration Confirmed: {event.event_name}"
            
            # Create simple confirmation email
            location = ", ".join(filter(None, [event.address, event.city, event.state]))
            event_date = event.start_date.strftime("%B %d, %Y at %I:%M %p")
            
            body = f"""
Hello!

Thank you for registering for {event.event_name}.

Event Details:
- Date: {event_date}
- Location: {location or 'TBD'}
- Description: {event.event_description}

You will receive a reminder before the event.

Best regards,
Community Pulse Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Successfully sent registration confirmation to {recipient_email}")
            return {"status": "success", "recipient": recipient_email}
    except Exception as e:
        print(f"❌ Error sending registration confirmation: {str(e)}")
        return {"status": "error", "message": str(e)}

