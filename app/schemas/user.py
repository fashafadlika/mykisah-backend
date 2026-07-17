from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str
    birthdate: Optional[date] = None


