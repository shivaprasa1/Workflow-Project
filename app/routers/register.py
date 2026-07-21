from fastapi import APIRouter    
from app.schemas.register_schema import RegisterRequest   #for validation importing schemas

router=APIRouter()

@router.post('/register')
def register(user: RegisterRequest):
    
    return {
        'message':'Employee Registered Successfully',
        'employee': user
    }
