"""
Authentication module for Gmail API access.
"""
import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailClient:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = self.authenticate()

    def authenticate(self):
        """Authenticate and return Gmail API service."""
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)

    def fetch_emails(self, days=7, query: str = ""):
        """Fetch emails from the last N days with optional query filter."""
        after_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        search_query = f'after:{after_date}'
        
        if query:
            search_query = f'{search_query} {query}'
        
        results = self.service.users().messages().list(
            userId='me',
            q=search_query,
            maxResults=100
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            message = self.service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            email_data = {
                'id': message['id'],
                'thread_id': message['threadId'],
                'snippet': message.get('snippet', ''),
                'date': None,
                'from': None,
                'subject': None,
                'body': None
            }
            
            headers = message['payload'].get('headers', [])
            for header in headers:
                name = header['name'].lower()
                if name == 'date':
                    email_data['date'] = header['value']
                elif name == 'from':
                    email_data['from'] = header['value']
                elif name == 'subject':
                    email_data['subject'] = header['value']
            
            # Extract body - prefer text/plain, fall back to text/html
            import base64
            from bs4 import BeautifulSoup
            
            def decode_part(data):
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            def extract_from_parts(parts, mime_type='text/plain'):
                for part in parts:
                    if part['mimeType'] == mime_type and 'data' in part.get('body', {}):
                        return decode_part(part['body']['data'])
                    
                    if 'parts' in part:
                        result = extract_from_parts(part['parts'], mime_type)

                        if result:
                            return result
                        
                return None
            
            payload = message['payload']
            body_text = None
            
            if 'parts' in payload:
                # Try text/plain first
                body_text = extract_from_parts(payload['parts'], 'text/plain')

                # Fall back to text/html and strip tags
                if not body_text:
                    html_body = extract_from_parts(payload['parts'], 'text/html')
                    if html_body:
                        body_text = BeautifulSoup(html_body, 'html.parser').get_text(separator='\n', strip=True)
                        
            elif 'body' in payload and 'data' in payload['body']:
                body_text = decode_part(payload['body']['data'])

                if payload.get('mimeType') == 'text/html':
                    body_text = BeautifulSoup(body_text, 'html.parser').get_text(separator='\n', strip=True)
            
            email_data['body'] = body_text if body_text else email_data['snippet']
            
            emails.append(email_data)
        
        return emails