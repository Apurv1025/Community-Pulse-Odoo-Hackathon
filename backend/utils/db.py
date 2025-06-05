import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine, select
from backend.models import *


# Use absolute path for SQLite database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sqlite_file_name = os.path.join(BASE_DIR, "database.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    from backend.utils.auth import get_password_hash

    SQLModel.metadata.create_all(engine)

    # Use a direct session for initialization to avoid generator issues
    with Session(engine) as session:
        # Check if user exists
        stmt = select(User).where(User.username == "johndoe")
        user = session.exec(stmt).first()

        if not user:
            # Create new user
            session.add(
                User(
                    username="johndoe",
                    email="john@doe.com",
                    phone="+91 1234567890",
                    isAdmin=False,
                    isVerifiedOrganizer=False,
                    disabled=False,
                    password=get_password_hash("secret"),
                )
            )
            session.commit()
        # Check if user exists
        stmt = select(User).where(User.username == "admin")
        user = session.exec(stmt).first()

        if not user:
            # Create new user
            session.add(
                User(
                    username="admin",
                    email="admin@example.com",
                    phone="+91 1234567890",
                    isAdmin=True,
                    isVerifiedOrganizer=False,
                    disabled=False,
                    password=get_password_hash("admin"),
                )
            )
            session.commit()


SessionDep = Annotated[Session, Depends(get_session)]
