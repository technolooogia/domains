import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

class EnhancedFileDB:
    """File-based database system (SQLite3 alternative)"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Define file paths
        self.domains_file = self.data_dir / "domains.json"
        self.searches_file = self.data_dir / "searches.json"
        self.analytics_file = self.data_dir / "analytics.json"
        self.config_file = self.data_dir / "config.json"
        
        # Initialize files
        self.init_files()
    
    def init_files(self):
        """Initialize JSON files if they don't exist"""
        default_data = {
            self.domains_file: {"domains": [], "last_updated": datetime.now().isoformat()},
            self.searches_file: {"searches": [], "last_updated": datetime.now().isoformat()},
            self.analytics_file: {
                "total_searches": 0,
                "total_domains_found": 0,
                "total_domains_checked": 0,
                "last_updated": datetime.now().isoformat()
            },
            self.config_file: {
                "app_version": "2.0.0",
                "created": datetime.now().isoformat(),
                "settings": {
                    "auto_save": True,
                    "max_results": 10000,
                    "cache_duration": 3600
                }
            }
        }
        
        for file_path, data in default_data.items():
            if not file_path.exists():
                self.write_json_file(file_path, data)
    
    def read_json_file(self, file_path):
        """Safely read JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Error reading {file_path}: {e}")
            return {}
    
    def write_json_file(self, file_path, data):
        """Safely write JSON file"""
        try:
            # Create backup before writing
            if file_path.exists():
                backup_path = file_path.with_suffix('.json.backup')
                file_path.rename(backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
        except Exception as e:
            st.error(f"Error writing {file_path}: {e}")
            return False
    
    def save_domain(self, domain_data):
        """Save domain to database"""
        try:
            data = self.read_json_file(self.domains_file)
            
            # Add metadata
            domain_data['id'] = len(data.get('domains', [])) + 1
            domain_data['saved_at'] = datetime.now().isoformat()
            
            # Add to domains list
            if 'domains' not in data:
                data['domains'] = []
            
            data['domains'].append(domain_data)
            data['last_updated'] = datetime.now().isoformat()
            
            # Write back to file
            success = self.write_json_file(self.domains_file, data)
            
            if success:
                # Update analytics
                self.update_analytics('domain_added')
            
            return success
            
        except Exception as e:
            st.
