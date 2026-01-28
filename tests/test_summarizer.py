import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gmail_client import GmailClient
from src.email_summarizer import EmailSummarizer

client = GmailClient(credentials_path='credentials.json')
print('Gmail Client initialized.')

summarizer = EmailSummarizer(model='deepseek-r1:8b')
print('Email Summarizer initialized.')

emails = client.fetch_emails(days=1, query='application')
print(f"Fetched {len(emails)} emails for summarization.")

summarized_data = summarizer.summarize_emails([emails[0]]) # Summarize first email for testing

print(f"Summarized Data: {summarized_data}")