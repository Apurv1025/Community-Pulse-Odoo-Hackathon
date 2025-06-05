from .celery_app import celery_app
from .email_reminder import send_event_notifications
from datetime import datetime, timedelta
from sqlmodel import Session, select
from backend.utils.db import engine
from backend.models import Event, EventUpdates
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

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
    Fetches event details from the database and schedules a task for future execution.
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
            datetime.strptime("06:35", '%H:%M').time()  # Changed to 6:35 AM
        )
        
        print(f"Scheduling reminder for: {execution_time}")
        
        # Calculate seconds until execution time
        now = datetime.now()
        if execution_time > now:
            # Schedule the actual email sending task for future execution
            send_email_notification.apply_async(
                args=[recipient, event_name, event_details],
                eta=execution_time  # This will execute at the specific future time
            )
            return f"Reminder scheduled for {execution_time}"
        else:
            # If the execution time is in the past, send immediately
            try:
                result = send_event_notifications(
                    recipient=recipient,
                    event_name=event_name,
                    event_details=event_details
                )
                return f"Execution time was in the past. Email sent immediately: {result}"
            except Exception as e:
                return f"Error sending email: {str(e)}"

@celery_app.task
def send_event_update_notification(recipient_email, event_id, update_id):
    """
    Dedicated task for sending event update notifications using the EventUpdates record.
    This completely separates update emails from standard notifications.
    """
    try:
        with Session(engine) as session:
            # Get event update record
            update_record = session.get(EventUpdates, update_id)
            if not update_record:
                return {"status": "error", "message": f"Update record {update_id} not found"}
                
            # Get event details
            event = session.get(Event, event_id)
            if not event:
                return {"status": "error", "message": f"Event {event_id} not found"}
            
            # Parse the update data
            try:
                update_data = json.loads(update_record.LastUpdate)
                changes = update_data.get("changes", [])
                summary = update_data.get("summary", [])
            except (json.JSONDecodeError, AttributeError):
                return {"status": "error", "message": "Invalid update data format"}
            
            # Debug info
            print(f"Sending update email to {recipient_email} for event {event_id}, update {update_id}")
            print(f"Summary: {summary}")
            
            # Handle potential None values for event data
            event_name = event.event_name or "Unnamed Event"
            
            # Safely handle date/time formatting to avoid NoneType errors
            date_str = "To be determined"
            time_str = "To be determined"
            if event.start_date:
                try:
                    date_str = event.start_date.strftime('%A, %B %d, %Y')
                    time_str = event.start_date.strftime('%I:%M %p')
                except Exception as e:
                    print(f"Date formatting error: {str(e)}")
            
            # Create message container
            msg = MIMEMultipart()
            msg['From'] = "teamcommunitypulse319@gmail.com"
            msg['To'] = recipient_email
            msg['Subject'] = f"Event Update: {event_name}"
            
            # Safely create location string
            location_parts = []
            if event.address:
                location_parts.append(event.address)
            if event.city:
                location_parts.append(event.city)
            if event.state:
                location_parts.append(event.state)
            location = ", ".join(location_parts) if location_parts else "Location TBD"
            
            # Create update list items with error handling
            update_items = ""
            for change in summary:
                if change:  # Only add non-empty items
                    update_items += f"<li>{change}</li>"
            
            # If no changes found, add a placeholder
            if not update_items:
                update_items = "<li>Event details have been modified</li>"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="color: #3a86ff;">Event Update Alert</h2>
                    <p>The event <strong>{event_name}</strong> has been updated.</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #3a86ff;">What Changed:</h3>
                    <ul style="padding-left: 20px;">
                    {update_items}
                    </ul>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h3 style="color: #3a86ff;">Updated Event Details:</h3>
                    <p><strong>Date:</strong> {date_str}</p>
                    <p><strong>Time:</strong> {time_str}</p>
                    <p><strong>Location:</strong> {location}</p>
                </div>
                
                <p style="color: #666;">This update was sent because you're registered for or following this event.</p>
            </body>
            </html>
            """
            
            # Create plain text version with error handling
            text_changes = ""
            for change in summary:
                if change:
                    text_changes += f"- {change}\n"
            if not text_changes:
                text_changes = "- Event details have been modified\n"
                
            text_content = f"""
            EVENT UPDATE ALERT
            
            The event "{event_name}" has been updated.
            
            WHAT CHANGED:
            {text_changes}
            
            UPDATED EVENT DETAILS:
            Date: {date_str}
            Time: {time_str}
            Location: {location}
            
            This update was sent because you're registered for or following this event.
            """
            
            # Attach parts to message
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email using SMTP with proper error handling
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            # Use hardcoded password as fallback if environment variable is not set
            email_password = os.getenv("EMAIL_PASSWORD", "uynl zloc dvrf zcwk")
            if not email_password:
                return {"status": "error", "message": "Email password not configured", "recipient": recipient_email}
                
            try:
                server.login("teamcommunitypulse319@gmail.com", email_password)
                server.send_message(msg)
                server.quit()
                return {"status": "success", "recipient": recipient_email}
            except smtplib.SMTPAuthenticationError:
                return {
                    "status": "error", 
                    "message": "SMTP authentication failed. Check credentials and Gmail settings.", 
                    "recipient": recipient_email
                }
    except Exception as e:
        return {"status": "error", "message": str(e), "recipient": recipient_email}

