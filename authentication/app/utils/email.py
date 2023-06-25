import base64
import os
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import dotenv_values

env = dotenv_values(".env")

CLIENT_ID = env["CLIENT_ID"]
CLIENT_SECRET = env["CLIENT_SECRET"]
ACCESS_TOKEN = env["ACCESS_TOKEN"]
REFRESH_TOKEN = env["REFRESH_TOKEN"]

def create_message(to, subject, message_text):
    """Create a message for sending an email."""
    message = MIMEText(message_text, 'html')
    message['to'] = to
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(to, subject, body):
    """Send an email using Gmail API."""
    credentials = Credentials.from_authorized_user_info(
        {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "token": ACCESS_TOKEN,
            "refresh_token": REFRESH_TOKEN,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )
    service = build('gmail', 'v1', credentials=credentials)
    message = create_message(to, subject, body)
    service.users().messages().send(userId="me", body=message).execute()
    try:
        message = create_message(to, subject, body)
        service.users().messages().send(userId="me", body=message).execute()
        return True
    except:
        return False
