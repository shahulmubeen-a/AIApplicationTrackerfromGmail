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
        
        # Ensure columns are in the right order with Title Case
        columns = ['Date', 'Company', 'Job Title', 'Status']
        
        # Rename columns to Title Case
        new_df.columns = ['Date', 'Company', 'Job Title', 'Status']
        new_df = new_df[columns]
        
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
        
        # Sort by Date (most recent first)
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        combined_df = combined_df.sort_values('Date', ascending=False)
        
        # Write to Excel
        combined_df.to_excel(self.output_path, index=False, engine='openpyxl')
        
        print(f"Written {len(combined_df)} applications to {self.output_path}")
        return self.output_path
    
    def read_excel(self) -> pd.DataFrame:
        """Read existing Excel file."""
        if not os.path.exists(self.output_path):
            return pd.DataFrame(columns=['Date', 'Company', 'Job Title', 'Status'])
        
        return pd.read_excel(self.output_path)