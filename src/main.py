"""
Main orchestration script for job application tracker.
Fetches emails, extracts job application data, and updates Excel sheet.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apscheduler.schedulers.blocking import BlockingScheduler
from src.gmail_client import GmailClient
from src.email_summarizer import EmailSummarizer
from src.sheet_manager import SheetManager


def run_job_tracker():
    """Main job to fetch emails and update spreadsheet."""
    print("Starting job application tracker...")
    
    # Initialize components
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    output_path = os.getenv('OUTPUT_PATH', 'tests/output/applications.xlsx')
    llm_model = os.getenv('LLM_MODEL', 'deepseek-r1:8b')
    days_to_fetch = int(os.getenv('DAYS_TO_FETCH', '7'))
    email_query = os.getenv('EMAIL_QUERY', 'application')
    
    try:
        # Fetch emails
        print(f"Fetching emails from last {days_to_fetch} days with query: '{email_query}'")
        client = GmailClient(credentials_path=credentials_path)
        emails = client.fetch_emails(days=days_to_fetch, query=email_query)
        print(f"Fetched {len(emails)} emails")
        
        if not emails:
            print("No emails found. Exiting.")
            return
        
        # Extract job application data
        print(f"Extracting job application data using {llm_model}...")
        summarizer = EmailSummarizer(model=llm_model)
        extracted_data = summarizer.summarize_emails(emails)
        print(f"Extracted {len(extracted_data)} job applications")
        
        if not extracted_data:
            print("No job applications extracted. Exiting.")
            return
        
        # Write to Excel
        print(f"Writing to Excel: {output_path}")
        sheet_manager = SheetManager(output_path=output_path)
        sheet_manager.write_to_excel(extracted_data)
        
        print("Job application tracker completed successfully!")
        
    except Exception as e:
        print(f"Error running job tracker: {e}. Please try again.")
        raise


def main():
    """Run once or schedule based on environment variable."""
    schedule_enabled = os.getenv('SCHEDULE_ENABLED', 'false').lower() == 'true'
    
    if schedule_enabled:
        # Run on a schedule
        schedule_hours = int(os.getenv('SCHEDULE_HOURS', '24'))
        print(f"Scheduling job to run every {schedule_hours} hours")
        
        scheduler = BlockingScheduler()
        scheduler.add_job(run_job_tracker, 'interval', hours=schedule_hours)
        
        # Run immediately on startup
        run_job_tracker()
        
        # Start scheduler
        print("Scheduler started. Press Ctrl+C to exit.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Scheduler stopped.")
    else:
        # Run once
        print("Running job tracker once...")
        run_job_tracker()

if __name__ == '__main__':
    main()