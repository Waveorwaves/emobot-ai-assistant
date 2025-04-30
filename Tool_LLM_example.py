import google.generativeai as genai
import requests
import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Substitute your API key here
genai.configure(api_key="AIzaSyBVAnfJ2pBNIliT7N2evGM16c7SZwtiUio")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send", 
    "https://www.googleapis.com/auth/documents"
    ]

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_credentials():
    """Get user credentials"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh the credential: {e}")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                 print(f"Error: Fail to find {CREDENTIALS_FILE}. Please download from Google Cloud Console.")
                 return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

# Weather API
def get_weather(city: str) -> str:
    url = "https://wttr.in/{}?format=3".format(city)
    response = requests.get(url)
    return response.text

# Gmail API
def send_email(sender: str, to: str, subject: str, message_text: str) -> str:
    creds = get_credentials()
    if not creds:
        return "Error: Failed to get credentials."
    service = build('gmail', 'v1', credentials=creds)
    message = (service.users().messages().send(userId='me',
               body={'raw': create_message_raw(to, subject, body)})
                .execute())
    print(f"Message Id: {message["id"]}")
    print(f"Message sent to {to}, subject: {subject}")

def create_message_raw(to, subject, body):
    """Create an email message in raw format"""
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['Subject'] = subject
    # base64url encode
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return encoded_message

def create_google_doc(title: str, content: str) -> str:
    """Use Google Docs API to create a new Google Doc"""
    creds = get_credentials()
    if not creds:
        return "Fail to get Google API credentials."
    service = build('docs', 'v1', credentials=creds)
    doc_body = {
        'title': title
    }
    doc = service.documents().create(body=doc_body).execute()
    doc_id = doc.get('documentId')
    print(f'Created the document, ID: {doc_id}')

    # Add contents
    if content:
        requests_body = [
            {
                'insertText': {
                    'location': {
                        'index': 1, # 插入到文档开头
                    },
                    'text': content + '\n' # 添加换行符
                }
            }
        ]
        service.documents().batchUpdate(documentId=doc_id, body={'requests': requests_body}).execute()
        print(f'Added contents to document: {doc_id}')

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return f"Created Google Doc '{title}', URL: {doc_url}"

# Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Get the weather for a given city",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "Chicago"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email to a given recipient",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "to": {"type": "STRING", "description": "Email of recipient"},
                "subject": {"type": "STRING", "description": "Email subject"},
                "message_text": {"type": "STRING", "description": "Email content"}
            },
            "required": ["to", "subject", "message_text"]
        }

    },
    {
        "name": "create_google_doc",
        "description": "Create a new Google Doc with a given title and content",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Title of the document"},
                "content": {"type": "STRING", "description": "Content of the document"}
            },
            "required": ["title"]
        }
    }
]

# Create model + tool
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-pro-exp-03-25",
    tools=tools,
)

# User interaction
chat = model.start_chat()

response = chat.send_message(
    "Help me get the weather for Chicago today",
    tool_config={"function_calling_config": {"mode": "AUTO"}}
)

# Check if the tool is called
if (response.candidates and
    response.candidates[0].content and
    response.candidates[0].content.parts and
    response.candidates[0].content.parts[0].function_call):

    tool_call = response.candidates[0].content.parts[0].function_call
    print(f"Gemini decides to use tool: {tool_call.name}({tool_call.args})")

    # Actual tool call
    if 'city' in tool_call.args:
        result = get_weather(tool_call.args['city'])

        # Construct the function response as a dictionary
        function_response_payload = {
            "function_response": {
                "name": tool_call.name,
                "response": {
                    "content": result,
                }
            }
        }

        followup = chat.send_message(
            content=function_response_payload
        )

        print("Gemini answer:", followup.text)
    else:
        print("Error: 'city' argument not found in tool call arguments.")
else:
    # Handle cases where Gemini responds directly or an error occurs
    try:
        print("Gemini direct answer (or error):", response.text)
    except ValueError:
         print("Gemini response did not contain text. Full response:", response)