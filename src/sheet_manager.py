"""
Class for managing spreadsheet operations.
"""

import pandas as pd
from typing import List, Dict
import os


class SheetManager:
    def __init__(self, sheet_path: str = "tests/output/applications.xlsx"):
        self.sheet_path = sheet_path
        os.makedirs(os.path.dirname(sheet_path), exist_ok=True)
    
    def write_to_excel(self, applications: List[Dict]) -> str:
        """
        Write job application data to Excel file.
        If file exists, append new data and remove duplicates.
        Returns the path to the created/updated file.
        """
        if not applications:
            print("No applications to write.")
            return self.sheet_path
        
        # Create DataFrame from new applications
        new_df = pd.DataFrame(applications)
        
        # Ensure columns are in the right order
        columns = ['date', 'company', 'job_title', 'status']
        new_df = new_df[columns]
        
        # If file exists, load and merge
        if os.path.exists(self.sheet_path):
            existing_df = pd.read_excel(self.sheet_path)
            
            # Combine and drop duplicates based on date, company, job_title
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(
                subset=['date', 'company', 'job_title'],
                keep='last'
            )
        else:
            combined_df = new_df
        
        # Sort by date (most recent first)
        combined_df['date'] = pd.to_datetime(combined_df['date'], dayfirst=True)
        combined_df = combined_df.sort_values('date', ascending=False)
        
        # Write to Excel
        combined_df.to_excel(self.sheet_path, index=False, engine='openpyxl')
        
        print(f"Written {len(combined_df)} applications to {self.sheet_path}")
        return self.sheet_path
    
    def read_excel(self) -> pd.DataFrame:
        """Read existing Excel file."""
        if not os.path.exists(self.sheet_path):
            return pd.DataFrame(columns=['date', 'company', 'job_title', 'status'])
        
        return pd.read_excel(self.sheet_path)