from sqlmodel import SQLModel, Field


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

# class User(SQLModel):
#     id: int | None = Field(default=None, primary_key=True)
#     username: str = Field(index=True, unique=True)
#     email: str | None = Field(default=None, index=True)
#     full_name: str | None = Field(default=None)
#     disabled: bool | None = Field(default=None)


# class UserInDB(SQLModel, table=True):
#     __tablename__ = "users"  # type: ignore
#     id: int | None = Field(default=None, primary_key=True)
#     username: str = Field(index=True, unique=True)
#     email: str = Field(index=True)
#     full_name: str
#     disabled: bool = Field(default=False)
#     hashed_password: str
