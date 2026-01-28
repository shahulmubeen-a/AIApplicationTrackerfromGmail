# Job Application Tracker

Automatically tracks job applications from Gmail and maintains an Excel spreadsheet using local LLM.

## Features
- Fetches job application emails from Gmail
- Extracts key info using local Ollama models (default: deepseek-r1:1.5b)
- Updates Excel spreadsheet with application data (Date, Company, Job Title, Status)
- Runs hourly with smart scheduling
- Configurable via simple config file
- Automatic duplicate detection and removal

## Installation

### Prerequisites
- Python 3.13
- WSL2 (if on Windows)
- Gmail account

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd AIApplicationTrackerFromGmail


### 2. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # WSL2/Linux
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
3. Schedule hourly checks (runs at 1 minute past each hour by default)
4. Each scheduled run: Check for new application emails from the last day

### Stop the Tracker
Press `Ctrl+C` to stop the scheduler.

### View Results
Open `tests/output/applications.xlsx` to see your tracked applications.

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
SCHEDULE_MINUTE = 0             # 0 runs at exactly the hour, 5 would run 5 minutes past
SCHEDULE_HOUR = '9,17'          # 24-hour format
```

**Run every 6 hours:**
```python
SCHEDULE_MINUTE = 0
SCHEDULE_HOUR = '*/6'
```

**Change email search query:**
```python
EMAIL_QUERY = 'job application OR interview OR offer'
```

**Use different Ollama model:**
```python
LLM_MODEL = 'deepseek-r1:8b'  # Remember to: ollama pull deepseek-r1:8b
```

**Change output location:**
```python
OUTPUT_PATH = '/path/to/your/applications.xlsx'
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

## Data Format

The Excel file contains:
- **Date**: DD.MM.YYYY format
- **Company**: Company name
- **Job Title**: Position applied for
- **Status**: Applied, Rejected, Interview Scheduled, Offer Received

Duplicates based on Date + Company + Job Title are automatically removed, keeping the most recent entry.

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

# Test Ollama
ollama list
```

### No Emails Found
- Check your Gmail search query matches your emails
- Verify date range (first run checks 7 days by default in `config.py`)
- Test with: `python tests/test_gmail_client.py`
- Try broader search query: `EMAIL_QUERY = 'application OR job OR interview'`

### Excel File Issues
- Make sure `tests/output/` directory exists (created automatically)
- Check write permissions
- Delete existing Excel file to start fresh
- Verify `OUTPUT_PATH` in `config.py` is correct

### LLM Extraction Issues
- Check Ollama is running: `ollama list`
- Verify model is downloaded: `ollama pull deepseek-r1:1.5b`
- Try a different model in `config.py`
- Check extraction with: `python tests/test_summarizer.py`

### Column Mismatch Error
If you see "Length mismatch: Expected axis has X elements, new values have Y elements":
- This was fixed in the updated `sheet_manager.py`
- Delete the existing Excel file and run again
- The new version doesn't force column renaming

### Scheduler Not Running
- Check if `.first_run_completed` exists - delete it to reset
- Verify `SCHEDULE_MINUTE` and `SCHEDULE_HOUR` in `config.py`
- Check console output for scheduler confirmation message

## Advanced Usage

### Reset First Run
To re-fetch the last 7 days of emails:
```bash
rm .first_run_completed
python app/main.py
```

### Manual Single Run (No Scheduler)
Edit `app/main.py` and modify the `main()` function to just call:
```python
def main():
    run_job_tracker(is_initial_run=True)
```

### Custom Email Processing
Edit `app/email_summarizer.py` to customize how emails are processed and what data is extracted.

### Using Different Date Formats
Edit `DATE_FORMAT` in `app/config.py`. Note: You'll need to update the date parsing logic in `sheet_manager.py` accordingly.

## Tips

- The tracker uses Gmail's search syntax - learn more at [Gmail Search Operators](https://support.google.com/mail/answer/7190)
- First run might take longer depending on number of emails
- Ollama models run locally - no data sent to external servers (except Gmail API)
- Excel file is updated incrementally - existing data is preserved
- For best results, use specific email queries like `"application" OR "applied" OR "applied for"`

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
```
