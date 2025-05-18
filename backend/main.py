from datetime import timedelta
from typing import Annotated
from dotenv import load_dotenv
from pydantic import BaseModel

from backend.models import Event 
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from backend.models import *
from backend.utils.auth import *
from backend.utils.db import *

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

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
           img_url=event.img_url
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

@app.put("/events/edit/{event_id}", response_model=EventUpdate)
async def update_event(
    event_id: int,
    event_update: EventUpdateModel,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Update an event. Only provided fields will be updated.
    """
    with Session(engine) as session:
        db_event = session.get(Event, event_id)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        if db_event.organiser != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to edit this event")
        event_data = event_update.model_dump(exclude_unset=True)
        for key, value in event_data.items():
            setattr(db_event, key, value)
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event

@app.get("/events/", response_model=list[Event])
async def get_all_events():
    """
    Retrieve all events from the database.
    """
    with Session(engine) as session:
        events = session.exec(select(Event)).all()
        return events


