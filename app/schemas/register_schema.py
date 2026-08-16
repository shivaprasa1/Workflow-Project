from pydantic import BaseModel, EmailStr   #importing for validation

class RegisterRequest(BaseModel):
    name: str 
    email: EmailStr
    password: str
    department:str


class RegisterResponse(BaseModel):
    id:int
    name:str 
    email:str
    department:str