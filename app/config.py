"""
Configuration settings for Job Application Tracker.
Edit these values to customize the application behavior.
"""

import os

# Gmail OAuth Credentials
GMAIL_CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')

# Output Excel File Path
OUTPUT_PATH = os.getenv('OUTPUT_PATH', 'tests/output/applications.xlsx')

# LLM Model Configuration
LLM_MODEL = os.getenv('LLM_MODEL', 'deepseek-r1:1.5b')

# Email Fetch Settings
DAYS_TO_FETCH = int(os.getenv('DAYS_TO_FETCH', '7'))                # Days to fetch on first run
EMAIL_QUERY = os.getenv('EMAIL_QUERY', 'application')               # Gmail search query

# Scheduler Settings
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', '1'))            # Minute past the hour to run the scheduler at (0-59)
SCHEDULE_HOUR = os.getenv('SCHEDULE_HOUR', '*')                     # Hour to run (* for every hour, or specific like '9,17')

# Format for dates in Excel
DATE_FORMAT = 'DD.MM.YYYY'