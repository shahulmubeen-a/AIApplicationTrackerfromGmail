"""
Main orchestration script for job application tracker using local Ollama.
Fetches emails, extracts job application data, and updates Excel sheet.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from app.gmail_client import GmailClient
from app.email_summarizer import EmailSummarizer
from app.sheet_manager import SheetManager
from app import config

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
    
    # Determine days to fetch based on run type
    if is_initial_run:
        days = config.DAYS_TO_FETCH
        print(f"Initial run detected. Fetching emails from last {days} days.")
    else:
        days = 1
        print("Scheduled run detected. Fetching emails from today.")
    
    try:
        # Fetch emails
        print(f"Fetching emails from last {days} day(s) with query: '{config.EMAIL_QUERY}'")
        client = GmailClient(credentials_path=config.GMAIL_CREDENTIALS_PATH)
        emails = client.fetch_emails(days=days, query=config.EMAIL_QUERY)
        print(f"Fetched {len(emails)} emails")
        
        if not emails:
            print("No emails found. Exiting.")
            return
        
        # Extract job application data
        print(f"Extracting job application data using {config.LLM_MODEL}...")
        summarizer = EmailSummarizer(model=config.LLM_MODEL)
        extracted_data = summarizer.summarize_emails(emails)
        print(f"Extracted {len(extracted_data)} job applications")
        
        if not extracted_data:
            print("No job applications extracted. Exiting.")
            return
        
        # Write to Excel
        print(f"Writing to Excel: {config.OUTPUT_PATH}")
        sheet_manager = SheetManager(output_path=config.OUTPUT_PATH)
        sheet_manager.write_to_excel(extracted_data)
        
        print("Job application tracker completed successfully!")
        
    except Exception as e:
        print(f"Error running job tracker: {e}. Please try again.")
        raise


def main():
    """Run with smart scheduling: first run checks 7 days, then hourly at configured time."""
    
    # Check if this is the first run
    if is_first_run():
        run_job_tracker(is_initial_run=True)
        mark_first_run_complete()
        
        # Now schedule hourly checks
        print(f"\nFirst run completed. Setting up scheduler...")
        scheduler = BlockingScheduler()
        
        # Schedule to run based on config
        scheduler.add_job(
            run_job_tracker,
            'cron',
            hour=config.SCHEDULE_HOUR,
            minute=config.SCHEDULE_MINUTE,
            second=0,
            args=(False,),  # Not initial run
            id='hourly_email_check'
        )
        
        print(f"Scheduler started. Job will run at minute {config.SCHEDULE_MINUTE} past hour(s) {config.SCHEDULE_HOUR}. Press Ctrl+C to exit.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Scheduler stopped.")
    else:
        # Subsequent runs - start the scheduler
        print(f"Scheduler starting. Job will run at minute {config.SCHEDULE_MINUTE} past hour(s) {config.SCHEDULE_HOUR}. Press Ctrl+C to exit.")
        scheduler = BlockingScheduler()
        
        # Schedule based on config
        scheduler.add_job(
            run_job_tracker,
            'cron',
            hour=config.SCHEDULE_HOUR,
            minute=config.SCHEDULE_MINUTE,
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