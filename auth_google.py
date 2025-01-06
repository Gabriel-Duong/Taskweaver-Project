from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the required scope for Google Slides API
SCOPES = ['https://www.googleapis.com/auth/presentations']

def authenticate_google_slides():
    """
    Authenticate and return the Google Slides API service object.
    """
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save the token for future use
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    service = build('slides', 'v1', credentials=creds)
    print("✅ Google Slides API Authenticated Successfully!")
    return service

if __name__ == '__main__':
    authenticate_google_slides()
