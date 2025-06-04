from datetime import timedelta
from typing import Annotated
from dotenv import load_dotenv
from pydantic import BaseModel

from backend.models import Event , UploadEvent
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from backend.models import *
from backend.utils.auth import *
from backend.utils.db import *
from backend.email_reminder import send_event_notifications

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, status,UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware


from sqlalchemy import select, or_, and_, func

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
   img_url: str


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
           img_url=event.img_url,
           isAccepted=False,
            isRejected=False,
            isFlagged=False,
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
    img_url: Optional[str] = None

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
            raise HTTPException(status_code=403, detail="Not authorized to edit this event")
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
    img_url: str
    isAccepted: bool
    isRejected: bool
    isFlagged: bool

    class Config:
        orm_mode = True
        from_attributes = True

@app.get("/events/", response_model=list[EventResponse])
async def get_all_events():
   """
   Retrieve all events from the database that are accepted and not flagged.
   """
   with Session(engine) as session:
        events = session.exec(
    select(Event).where(Event.isAccepted == True, Event.isFlagged == False)
).scalars().all()
        # Convert ORM objects to Pydantic models
        return [EventResponse.from_orm(event) for event in events]
    

@app.get("/event/{event_id}", response_model=Event)
async def get_event(event_id: int):
    """
    Retrieve a specific event by its ID.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        return db_event


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
            raise HTTPException(status_code=403, detail="Not authorized to delete this event")
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
        raise HTTPException(status_code=403, detail="Not authorized to accept this event")
    
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
        raise HTTPException(status_code=403, detail="Not authorized to reject this event")
    
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
async def get_all_request_events():
    """
    Retrieve all events from the database that are not accepted or rejected.
    """
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
        events = session.exec(
            select(Event).where(
                Event.organiser == username,
                Event.isAccepted == True,
                Event.isFlagged == False
            )
        ).scalars().all()
        return events

@app.get("/search/{searchterm}", response_model=list[Event])
async def search_events(searchterm: str):
    """
    Search for accepted events by event name (case-insensitive, partial match).
    """
    with Session(engine) as session:
        events = session.exec(
            select(Event).where(
                Event.isAccepted == True,
                Event.isFlagged == False,
                func.lower(Event.event_name).contains(searchterm.lower())
            )
        ).scalars().all()
        return events
    
@app.get("/admin/usersearch/{searchterm}", response_model=list[UserPublic])
async def admin_search_users(
    searchterm: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Admin search for users by username or email (case-insensitive, partial match).
    """
    if not current_user.isAdmin:
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
        db_event = session.get(Event,event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        event_registration = EventRegistered(
            username=current_user.username,
            event_id=event_id,
            email= current_user.email,
            phone= current_user.phone,
            count= registration.count
        )
        session.add(event_registration)
        session.commit()
        return {"detail": "User registered to event successfully"}
    
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
                EventRegistered.username == current_user.username
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

@app.get("/event/{event_id}/organizer",response_model=UserBase)
async def get_event_organizer(event_id: int):
    """
    Get the organizer of a specific event by event ID.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        organizer = session.get(User, db_event.organiser)
        if not organizer:
            raise HTTPException(status_code=404, detail="Organizer not found")
        return UserBase.model_validate(organizer)

