import json
import requests
from dotenv import load_dotenv
import os
from app.utils.llm_utils import generate_llm_response
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

VERSION = os.getenv("VERSION")


def generate_response(response):
    # Return text in uppercase
    return response.upper()


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    response = requests.post(url, data=data, headers=headers, verify=False)
    if response.status_code == 200:
        print("Status:", response.status_code)
        print("Content-type:", response.headers["content-type"])
        print("Body:", response.text)
        return response
    else:
        print(response.status_code)
        print(response.text)
        return response


def process_whatsapp_message(body):
    # Check if the webhook request contains a message
    message = (body.get("entry", [{}])[0]
    .get("changes", [{}])[0]
    .get("value", {})
    .get("messages", [{}])[0])

    # Check if the incoming message contains text
    if message.get("type") == "text":
        try:
            # Get the incoming message text
            incoming_message = message["text"]["body"]
            # Generate response in uppercase
            # response_text = generate_response(incoming_message)
            response_text =  generate_llm_response(incoming_message)
            # Prepare the message data
            message_data = get_text_message_input(
                recipient=message["from"],
                text=response_text
            )
            # Send the message
            send_message(message_data)

            # Mark message as read
            read_data = json.dumps({
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message["id"]
            })
            send_message(read_data)
            return 200
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return 500

    return 200
