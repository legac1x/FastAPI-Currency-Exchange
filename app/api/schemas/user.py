from pydantic import BaseModel

class UserPydantic(BaseModel):
    username: str
    hashed_password: str
    email: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    username: str
    email: str