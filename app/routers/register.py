from fastapi import APIRouter, status                 #import pakaging that add many api's  and also adding status to add http code 
from app.schemas.register_schema import RegisterRequest , RegisterResponse  #for validation importing schemas

router=APIRouter(prefix="/employees",
                 tags=["Employees"])   #create object to store that apirouter

# @router.post('/')            # post endpoint
# def register(user:RegisterRequest):    
    
#     return {
#         'message':'Employee Registered Successfully',
#         'employee': user
#     }
   

@router.post("/", response_model=RegisterResponse , 
             status_code=status.HTTP_201_CREATED)   # adding 201 status code 
def create_employee(employee: RegisterRequest):

    return {
        "id": 1,
        "name": employee.name,
        "email": employee.email,
        "department": employee.department
    }

  
@router.get("/")
def get_employees(department: str | None = None): #QUERY PARA
    return {
        "message": "Employees fetched successfully",
        "department": department
    }


@router.get("/{employee_id}")   #PATH PARA
def get_employee(employee_id:int):
    return {
        "employee_id": employee_id
    }