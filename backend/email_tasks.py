from .celery_app import celery_app
from .email_reminder import send_event_notifications
from datetime import datetime, timedelta

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
@celery_app.task
def schedule_event_reminder(recipient, event_name, event_details, target_date_str):
    """
    Schedule an email notification for a day before the event.
    """
    # Parse target date
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
    
    # Calculate reminder date (day before event)
    reminder_date = target_date - timedelta(days=1)
    
    # Create exact execution time (8:00 AM on day before event)
    execution_time = datetime.combine(
        reminder_date.date(), 
        datetime.strptime('6:35', '%H:%M').time()
    )
    
    print(f"Scheduling reminder for: {execution_time}")
    
    # Check if scheduled time is in the future
    now = datetime.now()
    if execution_time > now:
        # Use ETA instead of countdown for more precise timing
        send_email_notification.apply_async(
            args=[recipient, event_name, event_details],
            eta=execution_time  # Exact timestamp for execution
        )
        return f"Email scheduled for {execution_time}"
    else:
        # If time has passed, send immediately
        send_email_notification.delay(recipient, event_name, event_details)
        return "Email sent immediately (scheduled time has passed)"
    
