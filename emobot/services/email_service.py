"""
Email service for the emobot assistant using Gmail API.
Handles sending and reading emails.
"""
import os
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from emobot.core.config import logger, GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH

# If modifying these scopes, delete token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

class EmailService:
    def __init__(self):
        """Initialize the Gmail service."""
        self.creds = None
        self.service = None
        self.configured = False
        self.sender_email = "me"

        if not GMAIL_CREDENTIALS_PATH:
            logger.warning("GMAIL_CREDENTIALS_PATH not set in .env. Gmail service will not be available.")
            return

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if GMAIL_TOKEN_PATH and os.path.exists(GMAIL_TOKEN_PATH):
            try:
                with open(GMAIL_TOKEN_PATH, 'rb') as token:
                    self.creds = pickle.load(token)
            except Exception as e:
                logger.error(f"Error loading token.json: {e}. Will attempt to re-authenticate.")
                self.creds = None

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}. Need to re-authenticate.")
                    self._run_auth_flow() # Attempt re-authentication
            else:
                self._run_auth_flow() # Run initial authentication

            # Save the credentials for the next run
            if self.creds and GMAIL_TOKEN_PATH:
                try:
                    with open(GMAIL_TOKEN_PATH, 'wb') as token:
                        pickle.dump(self.creds, token)
                    logger.info(f"Credentials saved to {GMAIL_TOKEN_PATH}")
                except Exception as e:
                    logger.error(f"Error saving token.json: {e}")
        
        if self.creds and self.creds.valid:
            try:
                self.service = build('gmail', 'v1', credentials=self.creds)
                self.configured = True
                logger.info("Gmail service initialized successfully.")
                # Optionally, get the actual email address of the authenticated user
                profile = self.service.users().getProfile(userId='me').execute()
                self.sender_email = profile.get('emailAddress', 'me')
                logger.info(f"Authenticated as: {self.sender_email}")
            except HttpError as error:
                logger.error(f"An error occurred building Gmail service: {error}")
                self.configured = False
            except Exception as e:
                logger.error(f"An unexpected error occurred building Gmail service: {e}")
                self.configured = False
        else:
            logger.error("Gmail authentication failed or credentials not valid.")
            self.configured = False

    def _run_auth_flow(self):
        """Runs the OAuth 2.0 authentication flow."""
        if not os.path.exists(GMAIL_CREDENTIALS_PATH):
            logger.error(f"Credentials file not found at {GMAIL_CREDENTIALS_PATH}. Cannot authenticate.")
            return
        try:
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_PATH, SCOPES)
            # Switch from run_console() to run_local_server()
            # self.creds = flow.run_console() # Use run_console for CLI-based auth
            self.creds = flow.run_local_server(port=0) # Use run_local_server for browser-based auth
            logger.info("Authentication flow completed using local server.")
        except Exception as e:
            logger.error(f"Error during authentication flow: {e}")
            self.creds = None


    async def send_email(self, to_address: str, subject: str, body_html: str, body_text: str = None) -> bool:
        """
        Sends an email using Gmail API.
        Args:
            to_address: The recipient's email address.
            subject: The subject of the email.
            body_html: The HTML content of the email.
            body_text: Optional plain text content for multipart.
        Returns:
            True if the email was sent successfully, False otherwise.
        """
        if not self.configured or not self.service:
            logger.error("Gmail service not configured or service object not available. Cannot send email.")
            return False

        try:
            message = MIMEMultipart('alternative')
            message['to'] = to_address
            message['from'] = self.sender_email # Authenticated user's email
            message['subject'] = subject

            if body_text:
                part1 = MIMEText(body_text, 'plain')
                message.attach(part1)
            
            part2 = MIMEText(body_html, 'html')
            message.attach(part2)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': raw_message}
            
            # Use asyncio.to_thread for blocking call
            sent_message = await asyncio.to_thread(
                self.service.users().messages().send(userId="me", body=create_message).execute
            )
            logger.info(f"Email sent successfully to {to_address}. Message ID: {sent_message['id']}")
            return True
        except HttpError as error:
            logger.error(f"An HTTP error occurred sending email: {error}")
        except Exception as e:
            logger.error(f"An unexpected error occurred sending email: {e}")
        return False

    async def read_unread_emails(self, max_results: int = 5) -> list:
        """
        Reads a list of unread emails.
        Args:
            max_results: Maximum number of unread emails to fetch.
        Returns:
            A list of dictionaries, each representing an unread email with subject, sender, and snippet.
        """
        if not self.configured or not self.service:
            logger.error("Gmail service not configured. Cannot read emails.")
            return []

        emails_data = []
        try:
            # Use asyncio.to_thread for blocking call
            results = await asyncio.to_thread(
                self.service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute
            )
            messages = results.get('messages', [])

            if not messages:
                logger.info("No unread messages found.")
                return []

            for msg_summary in messages:
                # Use asyncio.to_thread for blocking call
                msg = await asyncio.to_thread(
                    self.service.users().messages().get(userId='me', id=msg_summary['id']).execute
                )
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'N/A')
                sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'N/A')
                snippet = msg.get('snippet', 'N/A')
                emails_data.append({'id': msg['id'], 'subject': subject, 'from': sender, 'snippet': snippet})
            
            logger.info(f"Fetched {len(emails_data)} unread emails.")
            return emails_data
        except HttpError as error:
            logger.error(f"An HTTP error occurred reading emails: {error}")
        except Exception as e:
            logger.error(f"An unexpected error occurred reading emails: {e}")
        return []

# Example of how to run auth flow if needed (typically done once manually or via a setup script)
# if __name__ == '__main__':
#     # This part is for manual testing or initial auth setup.
#     # Ensure .env has GMAIL_CREDENTIALS_PATH and GMAIL_TOKEN_PATH set.
#     # GMAIL_CREDENTIALS_PATH should point to your downloaded credentials.json
#     # GMAIL_TOKEN_PATH is where the token will be saved (e.g., "token.pickle" or "token.json")
#     print("Attempting to initialize EmailService for auth flow...")
#     # Load .env variables if not already loaded by a main application
#     from dotenv import load_dotenv
#     load_dotenv() 
#     email_service = EmailService()
#     if email_service.configured:
#         print("Gmail Service configured successfully.")
#         # Example: Test reading emails
#         # loop = asyncio.get_event_loop()
#         # unread = loop.run_until_complete(email_service.read_unread_emails())
#         # print("Unread emails:", unread)
#     else:
#         print("Gmail Service configuration failed. Check logs and ensure credentials/token paths are correct.")
#         print("If this is the first run, you might need to complete the OAuth2 flow in your console.")