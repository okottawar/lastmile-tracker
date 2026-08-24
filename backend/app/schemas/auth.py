from pydantic import BaseModel, EmailStr, Field
from app.models.enums import UserRole
class UserRegister(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    phone: str|None=None
    password: str = Field(min_length=8)
    role: UserRole = UserRole.CUSTOMER
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: int
    name: str
class UserOut(BaseModel):
    id: int; name: str; email: EmailStr; phone: str|None; role: UserRole
    class Config: from_attributes=True
