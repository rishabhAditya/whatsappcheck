import json
import requests
from dotenv import load_dotenv
import os
# from app.utils.llm_utils import generate_llm_response
from app.utils.database import add_or_update_user
from app.utils.validation_util import validate_email
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")

user_data = {}

def get_language_option_input(recipient):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Please select your preferred language:"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "en",
                                "title": "English"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "es",
                                "title": "Spanish"
                            }
                        }
                    ]
                }
            }
        })

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


def get_or_create_user_data(phone_number):
    """Initialize or get existing user data"""
    if phone_number not in user_data:
        user_data[phone_number] = {
            'message_list': [],
            'lang_selection': '',
            'email': None
        }
    return user_data[phone_number]



def debug_print_webhook(body):
    """Print detailed webhook information for debugging"""
    logger.info("Received webhook body:")
    logger.info(json.dumps(body, indent=2))

    # Extract and log specific parts
    entry = body.get("entry", [])
    logger.info(f"Number of entries: {len(entry)}")

    if entry:
        changes = entry[0].get("changes", [])
        logger.info(f"Number of changes: {len(changes)}")

        if changes:
            value = changes[0].get("value", {})
            logger.info("Value content:")
            logger.info(json.dumps(value, indent=2))


def extract_message(body):
    """Safely extract message from webhook body with detailed logging"""
    try:
        # Check if this is a status message
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        # Log the type of webhook
        logger.info(f"Webhook type: {value.get('messaging_product', 'unknown')}")

        # If this is a status update
        if "statuses" in value:
            logger.info("Received status update webhook")
            return None

        # If this is a message
        if "messages" in value:
            messages = value.get("messages", [])
            if messages:
                logger.info("Received message webhook")
                return messages[0]

        logger.info("No message found in webhook")
        return None

    except Exception as e:
        logger.error(f"Error extracting message: {str(e)}")
        return None


def process_whatsapp_message(body):
    """Process incoming webhook with enhanced error handling and logging"""
    # Log the entire webhook for debugging
    # debug_print_webhook(body)

    # Extract the message safely
    message = extract_message(body)

    # If no valid message, return success (to acknowledge receipt)
    if not message:
        logger.info("No processable message found, returning 200")
        return 200

    # Log the message details
    logger.info(f"Processing message: {json.dumps(message, indent=2)}")

    # Get user's phone number
    phone_number = message.get("from")
    if not phone_number:
        logger.error("No phone number found in message")
        return 200

    # Get or create user-specific data
    user = get_or_create_user_data(phone_number)

    try:
        # Handle text messages
        if message.get("type") == "text":
            return handle_text_message(message, user, phone_number)

        # Handle interactive messages
        elif message.get("type") == "interactive":
            return handle_interactive_message(message, user, phone_number)

        # Handle other message types
        else:
            logger.info(f"Unhandled message type: {message.get('type')}")
            return 200

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        error_message = get_text_message_input(
            recipient=phone_number,
            text='An error occurred. Please type "Hi" to start over.'
        )
        send_message(error_message)
        return 200


def handle_text_message(message, user, phone_number):
    """Handle text messages"""
    incoming_message = message["text"]["body"]
    logger.info(f"Handling text message from {phone_number}: {incoming_message}")

    user['message_list'].append(incoming_message)

    if incoming_message.lower() == "hi":
        message_data = get_language_option_input(recipient=phone_number)

    elif user['message_list'][-2] == "English" and user['lang_selection'] == "en":
        message_data = handle_english_email(incoming_message, user, phone_number)

    elif "@" in user['message_list'][-2] and user['lang_selection'] == "en":
        message_data = handle_english_name(incoming_message, user, phone_number)

    elif user['message_list'][-2] == "Spanish" and user['lang_selection'] == "es":
        message_data = handle_spanish_email(incoming_message, user, phone_number)

    elif "@" in user['message_list'][-2] and user['lang_selection'] == "es":
        message_data = handle_spanish_name(incoming_message, user, phone_number)

    else:
        message_data = get_text_message_input(
            recipient=phone_number,
            text='Some Error occurred. Type "Hi" to restart the process.'
        )
        user['message_list'] = []

    send_message(message_data)
    mark_message_as_read(message["id"], phone_number)
    return 200


def handle_interactive_message(message, user, phone_number):
    """Handle interactive messages"""
    selection = message["interactive"]["button_reply"]["title"]
    logger.info(f"Handling interactive message from {phone_number}: {selection}")

    user['message_list'].append(selection)

    if selection == "English":
        user['lang_selection'] = "en"
        message_data = get_text_message_input(
            recipient=phone_number,
            text="Enter your email"
        )
    else:
        user['lang_selection'] = "es"
        message_data = get_text_message_input(
            recipient=phone_number,
            text="Ingrese su correo electrónico"
        )

    send_message(message_data)
    return 200


def handle_english_email(email, user, phone_number):
    """Handle English email validation"""
    user['email'] = email
    if validate_email(user['email']):
        return get_text_message_input(
            recipient=phone_number,
            text="Enter your name"
        )
    else:
        user['message_list'].pop(-1)
        return get_text_message_input(
            recipient=phone_number,
            text="Oops! It looks like the email address you entered isn't valid. Please enter a valid email address (e.g., example@example.com)."
        )


def handle_spanish_email(email, user, phone_number):
    """Handle Spanish email validation"""
    user['email'] = email
    if validate_email(user['email']):
        return get_text_message_input(
            recipient=phone_number,
            text="Introduce tu nombre"
        )
    else:
        user['message_list'].pop(-1)
        return get_text_message_input(
            recipient=phone_number,
            text="Oh, parece que la dirección de correo electrónico que proporcionaste no es válida. Por favor, ingrese una dirección de correo electrónico válida (p. ej., example@example.com)."
        )


def handle_english_name(name, user, phone_number):
    """Handle English name submission"""
    add_or_update_user(phone_number, name, user['email'])
    user['message_list'] = []
    user['email'] = None
    return get_text_message_input(
        recipient=phone_number,
        text="Thank you, your details have been saved"
    )


def handle_spanish_name(name, user, phone_number):
    """Handle Spanish name submission"""
    add_or_update_user(phone_number, name, user['email'])
    user['message_list'] = []
    user['email'] = None
    return get_text_message_input(
        recipient=phone_number,
        text="Gracias, tus datos han sido guardados"
    )


def mark_message_as_read(message_id, phone_number):
    """Mark a message as read"""
    try:
        read_data = json.dumps({
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        })
        send_message(read_data)
    except Exception as e:
        logger.error(f"Error marking message as read: {str(e)}")

# [Previous helper functions remain the same: get_text_message_input, send_message, get_or_create_user_data, get_language_option_input]