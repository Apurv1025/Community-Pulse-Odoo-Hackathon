from celery import shared_task
from backend.celery_app import celery_app
import json
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from sqlmodel import Session, select
from backend.utils.db import engine
from backend.models import Event, EventUpdates, User, EventRegistered, EventFollowing

# Import the reminder function
from backend.email_reminder import send_event_reminder

# Constants
SMTP_USERNAME = "teamcommunitypulse319@gmail.com"
SMTP_PASSWORD = "uynl zloc dvrf zcwk"  # App password

@celery_app.task(bind=True, max_retries=3)
def send_event_reminder_notification(self, recipient, event_id):
    """
    Dedicated task for sending EVENT REMINDERS only.
    No update functionality here.
    """
    try:
        print(f"Processing reminder for event {event_id} to {recipient}")
        with Session(engine) as session:
            # Get event details
            event = session.get(Event, event_id)
            if not event:
                return {"status": "error", "message": f"Event {event_id} not found"}
            
            # Extract event details for reminder
            event_details = {
                "start_time": event.start_date.strftime("%I:%M %p on %Y-%m-%d"),
                "address": event.address,
                "city": event.city,
                "state": event.state,
                "description": event.description
            }
            
            # Send the reminder using the dedicated function
            result = send_event_reminder(recipient, event.event_name, event_details)
            
            return {"status": "success" if result else "failed", "recipient": recipient}
    except Exception as e:
        print(f"Error in reminder task: {str(e)}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

@celery_app.task(bind=True, max_retries=5)
def send_event_update_notification(self, recipient_email, event_id, update_id):
    """
    Dedicated task for sending EVENT UPDATES only.
    Completely separate from reminders.
    """
    print(f"Processing update notification for {recipient_email}, event {event_id}, update {update_id}")
    
    try:
        with Session(engine) as session:
            # Get update record
            update_record = session.get(EventUpdates, update_id)
            if not update_record:
                print(f"ERROR: Update record {update_id} not found in database")
                return {"status": "error", "message": f"Update record {update_id} not found"}
                
            # Get event details
            event = session.get(Event, event_id)
            if not event:
                print(f"ERROR: Event {event_id} not found in database")
                return {"status": "error", "message": f"Event {event_id} not found"}
            
            # Parse update data
            try:
                update_data = json.loads(update_record.LastUpdate)
                changes = update_data.get("changes", [])
                summary = update_data.get("summary", [])
            except Exception as e:
                return {"status": "error", "message": f"Failed to parse update data: {str(e)}"}
            
            # Send update email (completely separate from reminder emails)
            try:
                # Create message specifically for updates
                msg = MIMEMultipart()
                msg['From'] = SMTP_USERNAME
                msg['To'] = recipient_email
                msg['Subject'] = f"Event Update: {event.event_name}"
                
                # Create update-specific content
                updates_text = "\n".join([f"- {update}" for update in summary])
                location = ", ".join(filter(None, [event.address, event.city, event.state]))
                
                body = f"""
Hello!

An event you're following has been updated:
{event.event_name}

The following changes have been made:
{updates_text}

Updated Event Details:
- Time: {event.start_date.strftime("%I:%M %p on %Y-%m-%d")}
- Location: {location or 'TBD'}

We look forward to seeing you there!

Best regards,
Community Pulse Team
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Send the update email
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(SMTP_USERNAME, SMTP_PASSWORD)
                s.sendmail(SMTP_USERNAME, recipient_email, msg.as_string())
                s.quit()
                
                print(f"✅ Update email sent to {recipient_email} for event: {event.event_name}")
                return {"status": "success", "recipient": recipient_email}
                
            except Exception as e:
                print(f"Failed to send update email: {str(e)}")
                self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
                
    except Exception as e:
        print(f"ERROR in update notification task: {str(e)}")
        traceback.print_exc()
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

@celery_app.task
def schedule_event_reminders():
    """
    Daily task to check for events happening tomorrow and schedule reminders.
    Sends reminders exactly one day before each event's start date.
    """
    print("Running event reminder scheduler")
    
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
        
        scheduled_count = 0
        print(f"Found {len(events)} events happening tomorrow")
        
        for event in events:
            print(f"Processing event: {event.event_name} (ID: {event.id})")
            
            # Get all registered users and followers who should receive reminders
            recipients = set()
            
            # Get registered users
            registrations = session.exec(
                select(EventRegistered, User.email, User.username)
                .join(User, EventRegistered.username == User.username)
                .where(EventRegistered.event_id == event.id)
            ).all()
            
            for reg, email, username in registrations:
                if email:
                    print(f"Adding registered user: {username}")
                    recipients.add(email)
                    
            # Get followers
            followers = session.exec(
                select(EventFollowing, User.email, User.username)
                .join(User, EventFollowing.username == User.username)
                .where(EventFollowing.event_id == event.id)
            ).all()
            
            for follow, email, username in followers:
                if email:
                    print(f"Adding follower: {username}")
                    recipients.add(email)
            
            # Extract event details for the reminder
            event_details = {
                "start_time": event.start_date.strftime("%I:%M %p on %Y-%m-%d"),
                "address": event.address,
                "city": event.city,
                "state": event.state,
                "description": event.description
            }
            
            # Send reminders immediately for each recipient
            for recipient in recipients:
                try:
                    print(f"Sending reminder to {recipient} for event {event.id}")
                    
                    # Using the direct function to avoid scheduling complexity
                    success = send_event_reminder(recipient, event.event_name, event_details)
                    
                    if success:
                        scheduled_count += 1
                        print(f"Successfully sent reminder to {recipient}")
                    else:
                        print(f"Failed to send reminder to {recipient}")
                except Exception as e:
                    print(f"Error sending reminder to {recipient}: {str(e)}")
        
        print(f"Sent {scheduled_count} event reminders for events happening tomorrow")
        return {"status": "success", "sent_reminders": scheduled_count}

