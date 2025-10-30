from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel):
    email: str
    password: str

class UserVerifySchema(BaseModel):
    email: str
    verify_code: str
