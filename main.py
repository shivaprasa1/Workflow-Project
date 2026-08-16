from fastapi import FastAPI      # importing a packaging
from app.routers import register  #to include register page into main file 

app = FastAPI()                # create object or var to store fastapi application

app.include_router(register.router)     #link the apirouter (bunch of api's) to this main appliction 


@app.get('/')                  #create get endpoint           
def home():
    return {
        "project": "Smart Workflow Management System",
        "company": "Heartiest Mind Technologies",
        "version": "1.0.0",
        "status": "Running"
       
    }



