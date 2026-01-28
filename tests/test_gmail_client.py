import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.gmail_client import GmailClient

client = GmailClient(credentials_path='credentials.json')
print('Gmail Client initialized.')

emails = client.fetch_emails(days=1, query='application')

print(f"Fetched {len(emails)} emails.")

print(f"Sample Email: {emails[0] if emails else 'No emails found.'}")