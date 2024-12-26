
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.utils.whatsapp_utils import is_valid_whatsapp_message,process_whatsapp_message





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
            return challenge
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        raise HTTPException(status_code=400, detail="Missing parameters")




app = FastAPI()



@app.get("/")
def home():
    return "WhatsApp OpenAI Webhook is listening!"


@app.get("/webhook")
def webhook(request: Request):
    return verify(request)

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

