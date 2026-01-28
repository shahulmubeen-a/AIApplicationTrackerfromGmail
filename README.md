# Job Application Tracker

Automatically tracks job applications from Gmail and maintains an Excel spreadsheet.

## Features
- Fetches job application emails from Gmail
- Extracts key info using deepseek-r1:1.5b (via Ollama)
- Updates Excel spreadsheet with application data
- Runs hourly via GitHub Actions

## Deployment (Free - GitHub Actions)

### 1. Get Gmail OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json`

### 2. Generate Token Locally
```bash
# Run once locally to authenticate
python src/main.py
```
This creates `token.json` after you authenticate in browser.

### 3. Add GitHub Secrets
In your repo: Settings → Secrets and variables → Actions

Add two secrets:
- `GMAIL_CREDENTIALS`: Paste entire contents of `credentials.json`
- `GMAIL_TOKEN`: Paste entire contents of `token.json`

### 4. Push to GitHub
```bash
git add .
git commit -m "Add GitHub Actions workflow"
git push
```

### 5. Enable Actions
- Go to Actions tab in your repo
- Click "I understand my workflows, go ahead and enable them"
- Manually trigger first run using "Run workflow" button

### 6. Download Results
After each run, download the spreadsheet from:
Actions → Latest workflow run → Artifacts → Download

## Configuration
Edit environment variables in `.github/workflows/job_tracker.yml`:
- `LLM_MODEL`: Model name (default: `deepseek-r1:1.5b`)
- `DAYS_TO_FETCH`: Days of email history (default: `1`)
- `EMAIL_QUERY`: Gmail search query (default: `application`)

## Local Development
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install and run Ollama, if you're using an Ollama model
sudo apt install ollama
ollama pull deepseek-r1:1.5b    # or any model you want to use, but update main_local.py to use that model

# Run tests
python tests/test_gmail_client.py
python tests/test_summarizer.py
python tests/test_sheet_manager.py

# Run locally with scheduler
python src/main.py
```
