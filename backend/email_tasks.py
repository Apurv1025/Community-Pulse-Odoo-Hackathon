from .celery_app import celery_app
from .email_reminder import send_event_notifications
from datetime import datetime, timedelta
from sqlmodel import Session, select
from backend.utils.db import engine
from backend.models import Event

@celery_app.task(bind=True, max_retries=3)
def send_email_notification(self, recipient, event_name, event_details):
    """
    Celery task to send an event notification email.
    Includes retry logic on failure.
    """
    try:
        result = send_event_notifications(recipient, event_name, event_details)
        return {"status": "success" if result else "failed"}
    except Exception as exc:
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery_app.task
def schedule_event_reminder(recipient, event_id):
    """
    Schedule an email notification for a day before the event.
    Fetches event details from the database.
    """
    # Open a session to query the database
    with Session(engine) as session:
        # Fetch event from the database using SQLModel pattern
        event = session.get(Event, event_id)
        if not event:
            return f"Event with id {event_id} not found."
            
        # Extract event details
        event_name = event.event_name
        target_date = event.start_date
        
        # Create event_details dictionary
        event_details = {
            "start_time": target_date.strftime("%I:%M %p"),
            "address": event.address,
            "city": event.city,
            "state": event.state
        }
        
        # Calculate reminder date (day before event)
        reminder_date = target_date - timedelta(days=1)
        
        # Create exact execution time (6:35 AM on day before event)
        execution_time = datetime.combine(
            reminder_date.date(),
            datetime.strptime('06:35', '%H:%M').time()
        )
        
        print(f"Scheduling reminder for: {execution_time}")
        
        # Schedule the email task
        from backend.email_reminder import send_event_notifications
        
        # Send email notification
        try:
            result = send_event_notifications(
                recipient=recipient,
                event_name=event_name,
                event_details=event_details
            )
            return f"Email sent: {result}"
        except Exception as e:
            return f"Error sending email: {str(e)}"

