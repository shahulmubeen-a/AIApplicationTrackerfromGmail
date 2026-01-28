import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gmail_client import GmailClient
from src.email_summarizer import EmailSummarizer
from src.sheet_manager import SheetManager

client = GmailClient(credentials_path='credentials.json')
summarizer = EmailSummarizer(model='deepseek-r1:8b')
sheet_manager = SheetManager(output_path ='tests/output/applications.xlsx')

emails = client.fetch_emails(days=1, query='application')
extracted_data = summarizer.summarize_emails(emails[0:5])  # Summarize first 5 emails for testing
sheet_path = sheet_manager.write_to_excel(extracted_data)