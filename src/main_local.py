"""
Main orchestration script for job application tracker.
Fetches emails, extracts job application data, and updates Excel sheet.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from src.gmail_client import GmailClient
from src.email_summarizer import EmailSummarizer
from src.sheet_manager import SheetManager

# Marker file to track first run
FIRST_RUN_MARKER = '.first_run_completed'


def is_first_run():
    """Check if this is the first run of the application."""
    
    return not os.path.exists(FIRST_RUN_MARKER)


def mark_first_run_complete():
    """Create marker file to indicate first run is complete."""

    with open(FIRST_RUN_MARKER, 'w') as f:
        f.write(datetime.now().isoformat())


def run_job_tracker(is_initial_run=False):
    """Main job to fetch emails and update spreadsheet."""
    print("Starting job application tracker...")
    
    # Initialize components
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    output_path = os.getenv('OUTPUT_PATH', 'tests/output/applications.xlsx')
    llm_model = os.getenv('LLM_MODEL', 'deepseek-r1:1.5b')
    days_to_fetch = int(os.getenv('DAYS_TO_FETCH', '7'))
    email_query = os.getenv('EMAIL_QUERY', 'application')
    
    # Determine days to fetch based on run type
    if is_initial_run:
        days = days_to_fetch
        print(f"Initial run detected. Fetching emails from last {days} days.")
    else:
        days = 1
        print("Scheduled run detected. Fetching emails from today.")
    
    try:
        # Fetch emails
        print(f"Fetching emails from last {days} day(s) with query: '{email_query}'")
        client = GmailClient(credentials_path=credentials_path)
        emails = client.fetch_emails(days=days, query=email_query)
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
    """Run with smart scheduling: first run checks 7 days, then hourly at 1 minute past."""

    # Check if running in GitHub Actions
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("Running in GitHub Actions - single execution mode")
        run_job_tracker(is_initial_run=False)
        return
    
    # Check if this is the first run
    if is_first_run():
        print("First run detected. Fetching emails from last 7 days...")
        run_job_tracker(is_initial_run=True)
        mark_first_run_complete()
        
        # Now schedule hourly checks
        print("\nFirst run completed. Setting up hourly scheduler...")
        scheduler = BlockingScheduler()
        
        # Schedule to run at 1 minute past every hour (00:01, 01:01, etc.)
        scheduler.add_job(
            run_job_tracker,
            'cron',
            minute=1,
            second=0,
            args=(False,),  # Not initial run
            id='hourly_email_check'
        )
        
        print("Scheduler started. Job will run at 1 minute past every hour. Press Ctrl+C to exit.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Scheduler stopped.")
    else:
        # Subsequent runs - start the scheduler
        print("Scheduler starting. Job will run at 1 minute past every hour. Press Ctrl+C to exit.")
        scheduler = BlockingScheduler()
        
        # Schedule to run at 1 minute past every hour
        scheduler.add_job(
            run_job_tracker,
            'cron',
            minute=1,
            second=0,
            args=(False,),  # Not initial run
            id='hourly_email_check'
        )
        
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Scheduler stopped.")

if __name__ == '__main__':
    main()