"""
Summarizes email content and parses them into JSON for further processing.
"""

import json
import ollama
from typing import List, Dict


class EmailSummarizer:
    def __init__(self, model: str = "deepseek-r1:8b"):
        self.model = model
    
    def summarize_emails(self, emails: List[Dict]) -> List[Dict]:
        """
        Process emails and extract job application information.
        Returns list of dicts with: date, company, job_title, status
        """
        applications = []
        
        for email in emails:
            try:
                application_data = self._extract_application_data(email)
                if application_data:
                    applications.append(application_data)
            except Exception as e:
                email_id = email.get('id') if isinstance(email, dict) else 'unknown'
                print(f"Error processing email {email_id}: {e}")
                continue
        
        return applications
    
    def _extract_application_data(self, email: Dict) -> Dict:
        """Extract structured job application data from a single email."""

        prompt = f"""
            Extract job application information from this email and return ONLY a JSON object with these exact fields:
            - date: application date (DD.MM.YYYY format)
            - company: company name
            - job_title: job position title
            - status: one of [Applied, Rejected, Interview Scheduled, Offer Received, Other]

            Email Details:
            From: {email.get('from', 'Unknown')}
            Subject: {email.get('subject', 'No subject')}
            Date: {email.get('date', 'Unknown')}
            Body:
            {email.get('body', email.get('snippet', ''))}

            Return ONLY valid JSON, no explanation or markdown:
            """

        response = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        
        content = response['message']['content']
        
        # Parse JSON response
        try:
            data = json.loads(content)
            
            # Validate required fields
            required_fields = ['date', 'company', 'job_title', 'status']
            if not all(field in data for field in required_fields):
                return {}
            
            return data
        
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from LLM response: {content}")
            return {}