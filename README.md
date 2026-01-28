# Job Application Tracker

Automatically tracks job applications from Gmail and maintains an Excel spreadsheet using local LLM.

## Features
- Fetches job application emails from Gmail
- Extracts key info using local Ollama models (default: deepseek-r1:1.5b)
- Updates Excel spreadsheet with application data (Date, Company, Job Title, Status)
- Runs hourly with smart scheduling

## Installation

### Prerequisites
- Python 3.13
- WSL2 (if on Windows)
- Gmail account

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd AIApplicationTrackerFromGmail
```

### 2. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # WSL2/Linux
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Ollama
```bash
# WSL2/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull the model
ollama pull deepseek-r1:1.5b
```

### 5. Set Up Gmail OAuth

#### a) Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

#### b) Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure OAuth consent screen if prompted:
   - User Type: External
   - App name: Job Application Tracker
   - Add your email as test user
4. Application type: Desktop app
5. Name: Job Tracker
6. Download credentials as `credentials.json`
7. Move `credentials.json` to project root

### 6. First Run (Generate Token)
```bash
python app/main.py
```
- Browser window will open for Gmail authentication
- Sign in and grant permissions
- `token.json` will be created automatically
- First run fetches last 7 days of emails

## Usage

### Run the Tracker
```bash
python app/main.py
```

The tracker will:
1. On first run: Fetch emails from last 7 days
2. Create `tests/output/applications.xlsx`
3. Schedule hourly checks (runs at 1 minute past each hour)
4. Each hour: Check for new application emails from the last day

### Stop the Tracker
Press `Ctrl+C` to stop the scheduler.

### View Results
Open `tests/output/applications.xlsx` to see your tracked applications.

## Configuration

Edit these environment variables (or modify code defaults):
```bash
export GMAIL_CREDENTIALS_PATH="credentials.json"  # Path to credentials
export OUTPUT_PATH="tests/output/applications.xlsx"  # Output file
export LLM_MODEL="deepseek-r1:1.5b"  # Ollama model to use
export DAYS_TO_FETCH="7"  # Days to fetch on first run
export EMAIL_QUERY="application"  # Gmail search query
```

## Testing

Test individual components:
```bash
# Test Gmail connection
python tests/test_gmail_client.py

# Test email summarization
python tests/test_summarizer.py

# Test Excel writing
python tests/test_sheet_manager.py
```

## Project Structure
```
.
├── app/
│   ├── __init__.py
│   ├── gmail_client.py       # Gmail API authentication & email fetching
│   ├── email_summarizer.py   # LLM-based email extraction
│   ├── sheet_manager.py      # Excel file management
│   ├── main.py               # Main scheduler (Ollama)
│   ├── main_local.py         # Alternative local runner
│   └── main_cloud.py         # Alternative cloud API runner
├── tests/
│   ├── test_gmail_client.py
│   ├── test_summarizer.py
│   └── test_sheet_manager.py
├── requirements.txt
├── credentials.json          # Gmail OAuth (gitignored)
├── token.json               # Gmail token (gitignored)
└── README.md
```

## Customization

### Change LLM Model
```bash
# Pull different model
ollama pull deepseek-r1:8b

# Update in code or set env var
export LLM_MODEL="deepseek-r1:8b"
```

### Change Email Query
Modify the `EMAIL_QUERY` to filter different emails:
```bash
export EMAIL_QUERY="job application OR interview OR offer"
```

### Change Schedule
Edit `app/main.py` line with `scheduler.add_job()`:
```python
# Run every 30 minutes
scheduler.add_job(run_job_tracker, 'cron', minute='*/30', ...)

# Run every 6 hours
scheduler.add_job(run_job_tracker, 'cron', hour='*/6', minute=0, ...)
```

## Configuration

All settings can be edited in `app/config.py`:
```python
# Gmail OAuth Credentials
GMAIL_CREDENTIALS_PATH = 'credentials.json'

# Output Excel File Path
OUTPUT_PATH = 'tests/output/applications.xlsx'

# LLM Model Configuration
LLM_MODEL = 'deepseek-r1:1.5b'

# Email Fetch Settings
DAYS_TO_FETCH = 7               # Days to fetch on first run
EMAIL_QUERY = 'application'     # Gmail search query

# Scheduler Settings
SCHEDULE_MINUTE = 1             # Minute past the hour to run (0-59)
SCHEDULE_HOUR = '*'             # Hour to run (* for every hour, or specific like '9,17')

# Date Format
DATE_FORMAT = 'DD.MM.YYYY'
```

### Common Customizations

**Run every 30 minutes:**
```python
SCHEDULE_MINUTE = '*/30'
SCHEDULE_HOUR = '*'
```

**Run twice daily (9 AM and 5 PM):**
```python
SCHEDULE_MINUTE = 0             # setting 5 will run the tracker 5 minutes after the schedule hour
SCHEDULE_HOUR = '9,17'          # 24-hr format for hours
```

**Change email search:**
```python
EMAIL_QUERY = 'job application OR interview OR offer'
```

**Use different Ollama model:**
```python
LLM_MODEL = 'deepseek-r1:8b'  # Remember to: ollama pull deepseek-r1:8b
```

## Troubleshooting

### Gmail Authentication Issues
- Delete `token.json` and run again to re-authenticate
- Check OAuth consent screen has your email as test user
- Make sure Gmail API is enabled in Google Cloud Console

### Ollama Connection Issues
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
pkill ollama
ollama serve &
```

### No Emails Found
- Check your Gmail search query matches your emails
- Verify date range (first run checks 7 days by default)
- Test with: `python tests/test_gmail_client.py`

### Excel File Issues
- Make sure `tests/output/` directory exists
- Check write permissions
- Delete existing Excel file to start fresh

## Data Format

The Excel file contains:
- **Date**: DD.MM.YYYY format
- **Company**: Company name
- **Job Title**: Position applied for
- **Status**: Applied, Rejected, Interview Scheduled, Offer Received

Duplicates based on Date + Company + Job Title are automatically removed.

## License

MIT