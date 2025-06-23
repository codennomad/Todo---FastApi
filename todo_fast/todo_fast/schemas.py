from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserSchemas(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserDB(UserSchemas):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
