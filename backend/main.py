from datetime import timedelta
from typing import Annotated
from dotenv import load_dotenv
from pydantic import BaseModel

from backend.models import Event, UploadEvent, EventUpvotes, EventFollowing
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from backend.models import *
from backend.utils.auth import *
from backend.utils.db import *
from fastapi.staticfiles import StaticFiles

load_dotenv()

import schedule

from fastapi import Depends, FastAPI, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from backend.email_tasks import schedule_event_reminder

from sqlalchemy import select, or_, and_, func

from backend.email_reminder import send_event_notifications

# import threading
# from backend.scheduler import run_scheduler

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

event_details = {
           "start_time": "6:40",
           "address": "address",
           "city": "city",
           "state": "state"
       }
      
       # Schedule the task
schedule_event_reminder.delay('rashinkarapurv@gmail.com',"hello",event_details,'2025-06-06')



@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/register", response_model=Token)
async def register_user(user: UserCreate, session: SessionDep) -> Token:
    user_in_db = get_user(session, user.username)
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# JSON login model
class UserLogin(BaseModel):
    username: str
    password: str


@app.post("/api/login", response_model=Token)
async def json_login(user_data: UserLogin, session: SessionDep) -> Token:
    """
    Authenticate a user using JSON credentials
    """
    user = authenticate_user(session, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


class EventCreate(BaseModel):
    event_name: str
    event_description: str
    start_date: datetime
    end_date: datetime
    category: str
    registration_start: datetime
    registration_end: datetime
    address: str
    city: str
    state: str
    latitude: float  # Optional latitude
    longitude: float
    max_capacity: int
    type: str  # Default to 0 if not provided


@app.post("/event/create", response_model=Event)
async def create_event(
    event: EventCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    with Session(engine) as session:
        db_event = Event(
            event_name=event.event_name,
            organiser=current_user.username,  # Set organiser from current user
            event_description=event.event_description,
            start_date=event.start_date,
            end_date=event.end_date,
            category=event.category,
            registration_start=event.registration_start,
            registration_end=event.registration_end,
            address=event.address,
            city=event.city,
            state=event.state,
            isAccepted=False,
            isRejected=False,
            isFlagged=False,
            latitude=event.latitude,
            longitude=event.longitude,
            max_capacity=event.max_capacity,
            type=event.type,
        )
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event


from backend.models import EventUpdate  # Ensure correct import


class EventUpdateModel(BaseModel):
    """
    Model for updating event fields. All fields are optional.
    """

    event_name: Optional[str] = None
    event_description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_capacity: Optional[int] = None  # Optional max capacity field


@app.put("/event/edit/{event_id}", response_model=EventUpdate)
async def update_event(
    event_id: int,
    event_update: EventUpdateModel,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Update an event. Only provided fields will be updated.
    If the event does not exist, no changes are made and a 404 is returned.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        if db_event.organiser != current_user.username:
            raise HTTPException(
                status_code=403, detail="Not authorized to edit this event"
            )
        event_data = event_update.model_dump(exclude_unset=True)
        if not event_data:
            return db_event  # No changes if no fields provided
        for key, value in event_data.items():
            setattr(db_event, key, value)
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event


class EventResponse(BaseModel):
    id: int
    organiser: str
    event_name: str
    event_description: str
    start_date: datetime
    end_date: datetime
    category: str
    registration_start: datetime
    registration_end: datetime
    address: str
    city: str
    state: str
    isAccepted: bool
    isRejected: bool
    isFlagged: bool
    latitude: float
    longitude: float
    max_capacity: int

    class Config:
        orm_mode = True
        from_attributes = True


@app.get("/events/", response_model=list[EventResponse])
async def get_all_events():
    """
    Retrieve all events from the database that are accepted and not flagged.
    """
    with Session(engine) as session:
        events = (
            session.exec(
                select(Event).where(Event.isAccepted == True, Event.isFlagged == False)
            )
            .scalars()
            .all()
        )
        # Convert ORM objects to Pydantic models
        return [EventResponse.from_orm(event) for event in events]


@app.get("/event/{event_id}", response_model=dict)
async def get_event(event_id: int):
    """
    Retrieve a specific event by its ID, along with the list of images posted for the event.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Fetch images for this event
        images = (
            session.exec(select(UploadEvent).where(UploadEvent.event_id == event_id))
            .scalars()
            .all()
        )
        image_filenames = [img.filename for img in images]

        # Convert Event object to dictionary
        from fastapi.encoders import jsonable_encoder

        event_dict = jsonable_encoder(db_event)

        # Return event data and image filenames
        return {"event": event_dict, "images": image_filenames}


@app.delete("/event/delete/{event_id}", response_model=dict)
async def delete_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Delete an event. Only the organiser can delete their event.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        if db_event.organiser != current_user.username:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this event"
            )
        session.delete(db_event)
        session.commit()
        return {"detail": "Event deleted successfully"}


@app.get("/admin/event/accept/{event_id}", response_model=Event)
async def accept_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Accept an event. Only admin can accept events.
    """
    if not current_user.isAdmin:
        raise HTTPException(
            status_code=403, detail="Not authorized to accept this event"
        )

    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        db_event.isAccepted = True
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event


@app.get("/admin/event/reject/{event_id}", response_model=Event)
async def reject_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Reject an event. Only admin can reject events.
    """
    if not current_user.isAdmin:
        raise HTTPException(
            status_code=403, detail="Not authorized to reject this event"
        )

    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        db_event.isRejected = True
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event


@app.get("/admin/requestevents", response_model=list[EventResponse])
async def get_all_request_events(
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Retrieve all events from the database that are not accepted or rejected.
   Only admin users can access this endpoint.
   """
   if not current_user.isAdmin:
       raise HTTPException(status_code=403, detail="Not authorized to view requested events")
   with Session(engine) as session:
       events = session.exec(
           select(Event).where(Event.isAccepted == False, Event.isRejected == False)
       ).scalars().all()
       return [EventResponse.from_orm(event) for event in events]


@app.get("/admin/event/flag/{event_id}", response_model=Event)
async def flag_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Reject an event. Only admin can reject events.
    """
    if not current_user.isAdmin:
        raise HTTPException(status_code=403, detail="Not authorized to Flag this event")

    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        db_event.isFlagged = True
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event


@app.get("/event/user/{username}", response_model=list[Event])
async def get_user_events(username: str):
    """
    Retrieve all accepted events created by a specific user.
    """
    with Session(engine) as session:
        events = (
            session.exec(
                select(Event).where(
                    Event.organiser == username,
                    Event.isAccepted == True,
                    Event.isFlagged == False,
                )
            )
            .scalars()
            .all()
        )
        return events


@app.get("/search/{searchterm}", response_model=list[Event])
async def search_events(searchterm: str):
    """
    Search for accepted events by event name (case-insensitive, partial match).
    """
    with Session(engine) as session:
        events = (
            session.exec(
                select(Event).where(
                    Event.isAccepted == True,
                    func.lower(Event.event_name).contains(searchterm.lower()),
                )
            )
            .scalars()
            .all()
        )
        return events


@app.get("/admin/usersearch/{searchterm}", response_model=list[UserPublic])
async def admin_search_users(
   searchterm: str,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Admin search for users by username or email (case-insensitive, partial match).
   Only admin users can access this endpoint.
   """
   if not getattr(current_user, "isAdmin", False):
       raise HTTPException(status_code=403, detail="Not authorized to search users")
   with Session(engine) as session:
       users = session.exec(
           select(User).where(
               or_(
                   func.lower(User.username).contains(searchterm.lower()),
                   func.lower(User.email).contains(searchterm.lower())
               )
           )
       ).scalars().all()
       return [UserPublic.model_validate(user) for user in users]


class EventRegister(BaseModel):
    count: int


@app.post("/event/{event_id}/register", response_model=dict)
async def register_user_to_event(
    registration: EventRegister,
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Register the current user to an event using the EventRegistered DB model.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        event_registration = EventRegistered(
            username=current_user.username,
            event_id=event_id,
            email=current_user.email,
            phone=current_user.phone,
            count=registration.count,
        )
        session.add(event_registration)
        session.commit()

        event_details = {
           "start_time": db_event.start_date.strftime("%I:%M %p"),
           "address": db_event.address,
           "city": db_event.city,
           "state": db_event.state
       }
      
       # Schedule the task
        schedule_event_reminder.delay(
           current_user.email,
           db_event.event_name,
           event_details,
           db_event.start_date.strftime('%Y-%m-%d')
       )


        new_follow = EventFollowing(event_id=event_id, username=current_user.username)
        session.add(new_follow)
        session.commit()
        
        return {"detail": "Event followed successfully"}


@app.get("/event/{event_id}/registered", response_model=dict)
async def is_user_registered_for_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Check if the current user is registered for a specific event.
    Returns {"registered": True} or {"registered": False}
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        registration = session.exec(
            select(EventRegistered).where(
                EventRegistered.event_id == event_id,
                EventRegistered.username == current_user.username,
            )
        ).first()
        return {"registered": registration is not None}


@app.post("/event/{event_id}/upload")
async def upload_file(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: SessionDep,
    event_id: int,
):
    # check if it is a file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided",
        )
    if not file.filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    content = await file.read()
    filename = (
        current_user.username
        + "_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_"
        + file.filename
    )
    with open("uploads/" + filename, "wb") as f:
        f.write(content)

    upload = UploadEvent(
        filename=filename,
        content_type=file.content_type,  # type: ignore
        size=len(content),
        event_id=event_id,
    )
    session.add(upload)
    session.commit()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }


@app.get("/event/{event_id}/organizer", response_model=UserBase)
async def get_event_organizer(event_id: int):
    """
    Get the organizer of a specific event by event ID.
    Also increments the event's total views by 1.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        # Increment total views
        if hasattr(db_event, "total_views"):
            db_event.total_views = (db_event.total_views or 0) + 1
            session.add(db_event)
            session.commit()
            session.refresh(db_event)
        organizer = session.get(User, db_event.organiser)
        if not organizer:
            raise HTTPException(status_code=404, detail="Organizer not found")
        return UserBase.model_validate(organizer)


@app.post("/event/{event_id}/upvote", response_model=dict)
async def upvote_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Upvote an event. If the user has already upvoted, it will not add a duplicate.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Check if the user has already upvoted
        existing_upvote = session.exec(
            select(EventUpvotes).where(
                EventUpvotes.event_id == event_id,
                EventUpvotes.username == current_user.username,
            )
        ).first()

        if existing_upvote:
            return {"detail": "Already upvoted"}

        new_upvote = EventUpvotes(event_id=event_id, username=current_user.username)
        session.add(new_upvote)
        session.commit()

        return {"detail": "Event upvoted successfully"}


@app.post("/event/{event_id}/follow", response_model=dict)
async def follow_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Follow an event. If the user has already followed, it will not add a duplicate.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Check if the user has already followed
        existing_follow = session.exec(
            select(EventFollowing).where(
                EventFollowing.event_id == event_id,
                EventFollowing.username == current_user.username,
            )
        ).first()

        if existing_follow:
            return {"detail": "Already following"}

        new_follow = EventFollowing(event_id=event_id, username=current_user.username)
        session.add(new_follow)
        session.commit()

        return {"detail": "Event followed successfully"}


import razorpay

# setup from environment variables
import os

razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)


@app.post("/razorpay/create_order")
async def create_order(
    current_user: Annotated[User, Depends(get_current_active_user)],
    tier_id: int,
    quantity: int,
    session: SessionDep,
):
    """
    Create a Razorpay order for a specific tier and quantity.
    """

    tier = session.get(EventTiers, tier_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    amount = tier.tier_price * quantity * 100

    order_data = {
        "amount": amount,  # Amount in paise
        "currency": "INR",
        "notes": {
            "tier_id": tier_id,
            "quantity": quantity,
        },
    }

    session.add(
        PendingTickets(
            tier_id=tier_id,
            price=tier.tier_price,
            quantity=quantity,
            username=current_user.username,
        )
    )
    session.commit()

    order = razorpay_client.order.create(data=order_data)  # type: ignore

    return {
        "order_id": order["id"],
        "amount": order["amount"],
    }


@app.post("/razorpay/verify_payment")
async def verify_payment(
    current_user: Annotated[User, Depends(get_current_active_user)],
    payment_id: str,
    order_id: str,
    signature: str,
    session: SessionDep,
):
    """
    Verify a Razorpay payment signature.
    """

    try:
        razorpay_client.utility.verify_payment_signature(  # type: ignore
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
        # grab from pending tickets and add to tickets
        pending_ticket = session.exec(
            select(PendingTickets).where(
                PendingTickets.username == current_user.username,
                PendingTickets.tier_id == int(order_id.split("_")[-1]),
            )
        ).first()
        if not pending_ticket:
            raise HTTPException(status_code=404, detail="Pending ticket not found")
        # Create a new Ticket object
        ticket = UserEventTickets(
            username=current_user.username,
            tier_id=pending_ticket.tier_id,
            price=pending_ticket.price,
            quantity=pending_ticket.quantity,
        )
        session.add(ticket)
        session.delete(pending_ticket)
        session.commit()

        return {"status": "success", "message": "Payment verified and ticket created"}

    except razorpay.errors.SignatureVerificationError:  # type: ignore
        raise HTTPException(status_code=400, detail="Invalid payment signature")

@app.get("/user/followed-events", response_model=list[EventResponse])
async def get_user_followed_events(
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Retrieve all events that the current user is following.
   """
   with Session(engine) as session:
       # First, find all event IDs that the user is following
       followed_event_records = session.exec(
           select(EventFollowing).where(
               EventFollowing.username == current_user.username
           )
       ).scalars().all()
      
       followed_event_ids = [record.event_id for record in followed_event_records]
      
       if not followed_event_ids:
           return []
      
       # Then, retrieve the actual event data for those IDs
       events = session.exec(
           select(Event).where(
               Event.id.in_(followed_event_ids),
               Event.isAccepted == True,
               Event.isFlagged == False
           )
       ).scalars().all()
      
       return [EventResponse.from_orm(event) for event in events]
  
# First, add this Pydantic model for tier creation requests
class TierCreate(BaseModel):
   tier_name: str
   tier_price: float
   quantity: int


@app.post("/event/{event_id}/tiers", response_model=EventTiers)
async def create_event_tier(
   event_id: int,
   tier: TierCreate,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Create a new pricing tier for an event.
   Only the event organizer can create tiers.
   """
   with Session(engine) as session:
       # Check if the event exists
       db_event = session.get(Event, event_id)
       if not db_event:
           raise HTTPException(status_code=404, detail="Event not found")
      
       # Check if the current user is the organizer
       if db_event.organiser != current_user.username:
           raise HTTPException(
               status_code=403,
               detail="Only the event organizer can create tiers"
           )
      
       # Create the new tier
       new_tier = EventTiers(
           event_id=event_id,
           tier_name=tier.tier_name,
           tier_price=tier.tier_price,
           quantity=tier.quantity
       )
      
       # Add and commit to database
       session.add(new_tier)
       session.commit()
       session.refresh(new_tier)
      
       return new_tier
  
@app.get("/event/{event_id}/tiers", response_model=list[EventTiers])
async def get_event_tiers(event_id: int):
   """
   Retrieve all pricing tiers for a specific event.
   """
   with Session(engine) as session:
       # Fetch the event tiers
       tiers = session.exec(
           select(EventTiers).where(EventTiers.event_id == event_id)
       ).scalars().all()
      
       return tiers
  


class FeedbackCreate(BaseModel):
   feedback: str


@app.post("/event/{event_id}/feedback", response_model=dict)
async def submit_event_feedback(
   event_id: int,
   feedback_data: FeedbackCreate,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Submit feedback for an event.
   Users can only provide feedback once per event.
   """
   with Session(engine) as session:
       # Check if the event exists
       db_event = session.get(Event, event_id)
       if not db_event:
           raise HTTPException(status_code=404, detail="Event not found")
      
       # Check if the user has already provided feedback for this event
       existing_feedback = session.exec(
           select(QuickFeedback).where(
               QuickFeedback.event_id == event_id,
               QuickFeedback.username == current_user.username
           )
       ).first()
      
       if existing_feedback:
           # Update existing feedback instead of error
           existing_feedback.feedback = feedback_data.feedback
           session.add(existing_feedback)
           session.commit()
           return {"detail": "Feedback updated successfully"}
      
       # Create new feedback entry
       new_feedback = QuickFeedback(
           event_id=event_id,
           username=current_user.username,
           feedback=feedback_data.feedback
       )
      
       session.add(new_feedback)
       session.commit()
      
       return {"detail": "Feedback submitted successfully"}
  
@app.get("/event/{event_id}/feedback", response_model=dict)
async def get_event_feedback_summary(event_id: int):
    """
    Retrieve feedback for a specific event, grouped and counted by feedback content.
    Returns a dictionary with event_id and a nested dictionary of feedback counts.
    """
    with Session(engine) as session:
        # Fetch the feedback for the event
        feedbacks = session.exec(
            select(QuickFeedback).where(QuickFeedback.event_id == event_id)
        ).scalars().all()
        
        # Count occurrences of each feedback
        feedback_counts = {}
        for fb in feedbacks:
            if fb.feedback in feedback_counts:
                feedback_counts[fb.feedback] += 1
            else:
                feedback_counts[fb.feedback] = 1
        
        # Create the result dictionary
        result = {
            "event_id": event_id,
            "feedback": feedback_counts
        }
        
        return result
  
@app.get("/event/{event_id}/upvotes", response_model=int)
async def get_event_upvotes(event_id: int):
   """
   Get the total number of upvotes for a specific event.
   """
   with Session(engine) as session:
       # Count the number of upvotes for the event
       upvote_count = session.exec(
           select(func.count(EventUpvotes.event_id)).where(EventUpvotes.event_id == event_id)
       ).scalar_one_or_none() or 0
      
       return upvote_count
  
@app.get("/event/{event_id}/followers", response_model=int)
async def get_event_followers(event_id: int):
   """
   Get the total number of followers for a specific event.
   """
   with Session(engine) as session:
       # Count the number of followers for the event
       follower_count = session.exec(
           select(func.count(EventFollowing.event_id)).where(EventFollowing.event_id == event_id)
       ).scalar_one_or_none() or 0
      
       return follower_count
  
# First add this Pydantic model for the request body
class IssueCreate(BaseModel):
   category: str
   description: str
   latitude: Optional[float] = None
   longitude: Optional[float] = None
   personal: str  # For contact information or personal notes


@app.post("/issues/create", response_model=Issue)
async def create_issue(
   issue_data: IssueCreate,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Create a new community issue report.
   Requires authentication.
   """
   with Session(engine) as session:
       # Create new issue
       new_issue = Issue(
           category=issue_data.category,
           description=issue_data.description,
           latitude=issue_data.latitude,
           longitude=issue_data.longitude,
           personal=issue_data.personal
           # status and hidden will use their default values
       )
      
       session.add(new_issue)
       session.commit()
       session.refresh(new_issue)
      
       return new_issue
  
@app.get("/issues/", response_model=list[Issue])
async def get_all_issues():
   """
   Retrieve all community issues that are not hidden.
   """
   with Session(engine) as session:
       issues = session.exec(
           select(Issue).where(Issue.hidden == False)
       ).scalars().all()
       return issues
  
@app.get("/admin/issues/hidden", response_model=list[Issue])
async def get_all_hidden_issues(
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Retrieve all community issues that are hidden.
   Only admin users can access this endpoint.
   """
   if not getattr(current_user, "isAdmin", False):
       raise HTTPException(status_code=403, detail="Not authorized to view hidden issues")
   with Session(engine) as session:
       issues = session.exec(
           select(Issue).where(Issue.hidden == True)
       ).scalars().all()
       return issues


@app.get("/issues/{issue_id}", response_model=Issue)
async def get_issue(issue_id: int):
   """
   Retrieve a specific community issue by its ID.
   """
   with Session(engine) as session:
       issue = session.get(Issue, issue_id)
       if not issue:
           raise HTTPException(status_code=404, detail="Issue not found")
       return issue
  
@app.put("/issues/edit/{issue_id}", response_model=Issue)
async def update_issue(
   issue_id: int,
   issue_update: IssueCreate,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Update a community issue. Only the creator can update their issue.
   """
   with Session(engine) as session:
       db_issue = session.get(Issue, issue_id)
       if not db_issue:
           raise HTTPException(status_code=404, detail="Issue not found")
      
       # Update fields
       db_issue.category = issue_update.category
       db_issue.description = issue_update.description
       db_issue.latitude = issue_update.latitude
       db_issue.longitude = issue_update.longitude
       db_issue.personal = issue_update.personal
      
       session.add(db_issue)
       session.commit()
       session.refresh(db_issue)
      
       return db_issue
  
@app.delete("/issues/delete/{issue_id}", response_model=dict)
async def delete_issue(
   issue_id: int,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Delete a community issue. Only the creator can delete their issue.
   """
   with Session(engine) as session:
       db_issue = session.get(Issue, issue_id)
       if not db_issue:
           raise HTTPException(status_code=404, detail="Issue not found")
       if db_issue.creator != current_user.username:
           raise HTTPException(status_code=403, detail="Not authorized to delete this issue")
      
       session.delete(db_issue)
       session.commit()
      
       return {"detail": "Issue deleted successfully"}
  
@app.get("/issues/{issue_id}/upvotes", response_model=int)
async def get_issue_upvotes(issue_id: int):
   """
   Get the total number of upvotes for a specific community issue.
   """
   with Session(engine) as session:
       # Count the number of upvotes for the issue
       upvote_count = session.exec(
           select(func.count(IssueUpvotes.issue_id)).where(IssueUpvotes.issue_id == issue_id)
       ).scalar_one_or_none() or 0
      
       return upvote_count
  
@app.post("/issues/{issue_id}/upvote", response_model=dict)
async def upvote_issue(
   issue_id: int,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Upvote a community issue. If the user has already upvoted, it will not add a duplicate.
   """
   with Session(engine) as session:
       db_issue = session.get(Issue, issue_id)
       if not db_issue:
           raise HTTPException(status_code=404, detail="Issue not found")
      
       # Check if the user has already upvoted
       existing_upvote = session.exec(
           select(IssueUpvotes).where(
               IssueUpvotes.issue_id == issue_id,
               IssueUpvotes.username == current_user.username
           )
       ).first()
      
       if existing_upvote:
           return {"detail": "Already upvoted"}
      
       new_upvote = IssueUpvotes(issue_id=issue_id, username=current_user.username)
       session.add(new_upvote)
       session.commit()
      
       return {"detail": "Issue upvoted successfully"}
  
@app.post("/issues/{issue_id}/spam", response_model=dict)
async def mark_issue_as_spam(
   issue_id: int,
   current_user: Annotated[User, Depends(get_current_active_user)],
):
   """
   Mark a community issue as spam. If an issue receives more than 5 spam reports, it becomes hidden.
   """
   with Session(engine) as session:
       db_issue = session.get(Issue, issue_id)
       if not db_issue:
           raise HTTPException(status_code=404, detail="Issue not found")
       # Check if already marked as spam by this user
       existing_spam = session.exec(
           select(IssueSpam).where(
               IssueSpam.issue_id == issue_id,
               IssueSpam.username == current_user.username
           )
       ).first()
       if existing_spam:
           return {"detail": "Already marked as spam"}
      
       spam_entry = IssueSpam(issue_id=issue_id, username=current_user.username)
       session.add(spam_entry)
       session.commit()


       # Count total spam reports for this issue
       spam_count = session.exec(
           select(func.count(IssueSpam.issue_id)).where(IssueSpam.issue_id == issue_id)
       ).scalar_one_or_none() or 0


       # If more than 5 spam reports, hide the issue
       if spam_count > 5 and not db_issue.hidden:
           db_issue.hidden = True
           session.add(db_issue)
           session.commit()
           return {"detail": "Issue marked as spam and hidden due to multiple reports"}


       return {"detail": "Issue marked as spam"}





