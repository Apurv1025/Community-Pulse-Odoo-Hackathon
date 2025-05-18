from sqlmodel import SQLModel, Field
from datetime import datetime


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = Field(default=None, index=True)


class UserBase(SQLModel):
    username: str = Field(index=True,nullable=False ,unique=True,primary_key=True)
    email: str = Field(nullable=False, index=True)
    phone: str = Field(nullable=False, index=True)

class User(UserBase, table=True):
    isAdmin: bool = Field(default=False)
    isVerifiedOrganizer: bool = Field(default=False)
    disabled: bool = Field(default=False)
    password: str = Field(nullable=False)

class UserPublic(UserBase):
    isAdmin: bool = Field(default=False)
    isVerifiedOrganizer: bool = Field(default=False)
    disabled: bool = Field(default=False)    

class UserCreate(UserBase):
    password: str 

class Event(SQLModel,table=True):
    id: int | None = Field(default=None, primary_key=True)
    organiser: str = Field(foreign_key="user.username",nullable=False)
    event_name: str = Field(nullable=False)
    event_description: str = Field(nullable=False)
    start_date: datetime = Field(nullable=False)
    end_date: datetime = Field(nullable=False)
    category: str = Field(nullable=False)
    registration_start: datetime = Field(nullable=False)
    registration_end: datetime = Field(nullable=False)
    address: str = Field(nullable=False)
    city: str = Field(nullable=False)
    state: str = Field(nullable=False)
    img_url: str = Field(nullable=False)
    isAccepted: bool = Field(default=False)
    isRejected: bool = Field(default=False)
    isFlagged: bool = Field(default=False)


class EventUpdate(Event):
    id: int | None = Field(default=None, primary_key=True)
    organiser: str = Field(foreign_key="user.username",nullable=False)
    event_name: str = Field(nullable=False)
    event_description: str = Field(nullable=False)
    start_date: datetime = Field(nullable=False)
    end_date: datetime = Field(nullable=False)
    category: str = Field(nullable=False)
    registration_start: datetime = Field(nullable=False)
    registration_end: datetime = Field(nullable=False)
    address: str = Field(nullable=False)
    city: str = Field(nullable=False)
    state: str = Field(nullable=False)
    img_url: str = Field(nullable=False)
    isAccepted: bool = Field(default=False)
    isRejected: bool = Field(default=False)
    isFlagged: bool = Field(default=False)

