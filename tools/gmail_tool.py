from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from email.message import EmailMessage
from config.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN_URI, GOOGLE_SCOPE, GOOGLE_REFRESH_TOKEN
import base64
import re
import logging

logger = logging.getLogger(__name__)

def init_gmail_api():
    token_data = {
        "refresh_token": GOOGLE_REFRESH_TOKEN,
        "token_uri":GOOGLE_TOKEN_URI,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "scopes": GOOGLE_SCOPE,
        "universe_domain": "googleapis.com",
        "account": "",
    }
    creds = Credentials.from_authorized_user_info(token_data, ["https://www.googleapis.com/auth/gmail.compose"])

    if not creds.valid:
        if creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            raise RuntimeError("Gmail credentials are invalid and cannot be refreshed.")

    return build("gmail", "v1", credentials=creds)

def generate_token() -> dict:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": GOOGLE_TOKEN_URI,
            }
        },
        SCOPES,
    )

    creds = flow.run_local_server(port=0)

    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "expiry": creds.expiry.isoformat()
    }

@tool
def draft_email(subject: str, body: str, recipient: str) -> dict:
    """Create a Gmail DRAFT (not sent) with the subject, body, and recipient."""
    EMAIL_RE = re.compile(r"^[^@\s,<>]+@[^@\s,<>]+\.[A-Za-z]{2,}$")
    recipient = (recipient or "").strip()
    if not EMAIL_RE.match(recipient):
        message = {
            "status": "error",
            "message": (
                f"{recipient!r} is not a valid email address, so no draft was created. "
                "Ask the user who the email should go to, then call draft_email again with "
                "their real address. Do not substitute a placeholder or a guessed address."
            ),
        }
        print(message)
        return message

    service = init_gmail_api()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = recipient
    message["From"] = "lucbanjep@gmail.com"
    message["Subject"] = subject
    print(f"Creating Gmail draft to {recipient} with subject {subject!r} and body length {len(body)}")
    # File Attachment
    # try:
    #     _attach_file(message, "resume.pdf")
    # except OSError as e:
    #     return {"status": "error", "message": f"Could not read attachment: {e}"}

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"message": {"raw": encoded_message}}

    try:
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )
    except HttpError as error:
        logger.error("Gmail drafts.create failed: %s", error)
        print(error)
        return {"status": "error", "message": f"Gmail API error: {error}"}

    logger.info("Created draft %s to %s", draft["id"], recipient)

    return {
        "status": "success",
        "draft_id": draft["id"],
        "to": recipient,
        "subject": subject,
    }