"""
Class for managing spreadsheet operations.
"""

import pandas as pd
from typing import List, Dict
import os


class SheetManager:
    def __init__(self, output_path: str = "tests/output/applications.xlsx"):
        self.output_path = output_path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    def write_to_excel(self, applications: List[Dict]) -> str:
        """
        Write job application data to Excel file.
        If file exists, append new data and remove duplicates.
        Returns the path to the created/updated file.
        """
        if not applications:
            print("No applications to write.")
            return self.output_path
        
        # Create DataFrame from new applications
        new_df = pd.DataFrame(applications)
        
        # Filter out invalid entries (null dates, empty companies, etc.)
        initial_count = len(new_df)
        new_df = new_df[
            (new_df['date'].notna()) & 
            (new_df['date'] != 'null') & 
            (new_df['date'] != '') &
            (new_df['company'].notna()) & 
            (new_df['company'] != '') &
            (new_df['job_title'].notna()) & 
            (new_df['job_title'] != '')
        ]
        
        if len(new_df) < initial_count:
            print(f"Filtered out {initial_count - len(new_df)} invalid entries")
        
        if len(new_df) == 0:
            print("No valid applications after filtering.")
            return self.output_path
        
        # Rename columns to Title Case for consistency
        new_df = new_df.rename(columns={
            'date': 'Date',
            'company': 'Company',
            'job_title': 'Job Title',
            'status': 'Status'
        })
        
        # If file exists, load and merge
        if os.path.exists(self.output_path):
            existing_df = pd.read_excel(self.output_path)
            
            # Combine and drop duplicates based on Date, Company, Job Title
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(
                subset=['Date', 'Company', 'Job Title'],
                keep='last'
            )
        else:
            combined_df = new_df
        
        # Sort by Date (most recent first) - handle DD.MM.YYYY format
        try:
            combined_df['Date'] = pd.to_datetime(combined_df['Date'], dayfirst=True, errors='coerce')
            combined_df = combined_df.sort_values('Date', ascending=False)
            
        except Exception as e:
            print(f"Warning: Could not sort by date: {e}")
        
        # Write to Excel
        combined_df.to_excel(self.output_path, index=False, engine='openpyxl')
        
        print(f"Written {len(combined_df)} applications to {self.output_path}")
        return self.output_path
    
    def read_excel(self) -> pd.DataFrame:
        """Read existing Excel file."""
        if not os.path.exists(self.output_path):
            return pd.DataFrame(columns=['Date', 'Company', 'Job Title', 'Status'])
        
        return pd.read_excel(self.output_path)