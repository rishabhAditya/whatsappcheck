<<<<<<< HEAD
#TUNNEL used:https://pinggy.io/
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.utils.database import session, User, add_or_update_user

from app.utils.whatsapp_utils import process_whatsapp_message
# from app.utils.test import process_whatsapp_message
import json
=======

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.utils.whatsapp_utils import is_valid_whatsapp_message,process_whatsapp_message



>>>>>>> 37693cf6652e814c49a60b2d12da6ab1372128a6


def verify(request: Request):
    # Parse params from the webhook verification request
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    verify_token = "rishabh"

    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == verify_token:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
<<<<<<< HEAD
            # return PlainTextResponse(content=challenge, status_code=200)
            return Response(content=challenge)
=======
            return challenge
>>>>>>> 37693cf6652e814c49a60b2d12da6ab1372128a6
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        raise HTTPException(status_code=400, detail="Missing parameters")




app = FastAPI()

<<<<<<< HEAD
class UserCreate(BaseModel):
    phone_number: str
    name: str
    email: str

def get_db():
    db = session
    try:
        yield db
    finally:
        db.close()
=======

>>>>>>> 37693cf6652e814c49a60b2d12da6ab1372128a6

@app.get("/")
def home():
    return "WhatsApp OpenAI Webhook is listening!"
<<<<<<< HEAD
@app.get("/users/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Endpoint to add or update a user
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        add_or_update_user(user.phone_number, user.name, user.email)
        return {"message": "User added or updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
=======

>>>>>>> 37693cf6652e814c49a60b2d12da6ab1372128a6

@app.get("/webhook")
def webhook(request: Request):
    return verify(request)

<<<<<<< HEAD

@app.post("/webhook")
async def webhook(request: Request):
    # Log incoming messages
    body = await request.json()
    # print("Incoming webhook message:", json.dumps(body, indent=2))
    status_code  = process_whatsapp_message(body)
    return Response(status_code=status_code)


=======
@app.post("/webhook")
def handle_message(request: Request):
    body = request.json()
    if is_valid_whatsapp_message(body):
        process_whatsapp_message(body)
        return JSONResponse(content={"status": "ok"}, status_code=200)
    return JSONResponse(content={"status": "invalid message"}, status_code=400)



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

>>>>>>> 37693cf6652e814c49a60b2d12da6ab1372128a6
