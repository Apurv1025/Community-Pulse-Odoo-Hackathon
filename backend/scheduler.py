# import time
# import schedule
# from datetime import datetime
# from sqlmodel import Session, select
# from backend.models import Event, EventRegistered
# from backend.utils.db import engine
# from backend.email_reminder import send_event_notifications

# def check_and_notify_today_events():
#     """Check for today's events and send notifications to registered users"""
#     print(f"Running event check at {datetime.now()}")
    
#     with Session(engine) as session:
#         # Get today's events that are accepted and not flagged
#         today = datetime.now().date()
#         today_events = session.exec(
#             select(Event).where(
#                 Event.start_date == today,
#                 Event.isAccepted == True,
#                 Event.isFlagged == False
#             )
#         ).all()

#         for event in today_events:
#             # Get all registrations for this event
#             registrations = session.exec(
#                 select(EventRegistered).where(
#                     EventRegistered.event_id == event.id
#                 )
#             ).all()

#             print("register",registrations)

#             if registrations:
#                 # Collect recipient emails
#                 recipient_emails = [reg.email for reg in registrations]
                
#                 # Prepare event details
#                 event_details = {
#                     "start_time": event.start_date.strftime("%I:%M %p"),
#                     "address": event.address,
#                     "city": event.city,
#                     "state": event.state
#                 }

#                 # Send notifications
#                 success = send_event_notifications(
#                     recipient_emails,
#                     event.event_name,
#                     event_details
#                 )
                
#                 if success:
#                     print(f"Sent notifications for event: {event.event_name}")
#                 else:
#                     print(f"Failed to send notifications for event: {event.event_name}")

# def run_scheduler():
#     """Initialize and run the scheduler"""
#     # Schedule the notification check to run daily at 8 AM
#     schedule.every().day.at("13:49").do(check_and_notify_today_events)
    
#     print("Scheduler started. Running tasks...")
#     while True:
#         schedule.run_pending()
#         time.sleep(60)  # Wait for 60 seconds before next check