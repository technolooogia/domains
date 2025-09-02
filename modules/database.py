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
            st.error(f"Error saving domain: {e}")
            return False
    
    def get_domains(self, limit=None, filters=None):
        """Get domains with optional filtering"""
        try:
            data = self.read_json_file(self.domains_file)
            domains = data.get('domains', [])
            
            # Apply filters if provided
            if filters:
                filtered_domains = []
                for domain in domains:
                    # Price filter
                    if 'max_price' in filters and domain.get('price', 0) > filters['max_price']:
                        continue
                    
                    # Extension filter
                    if 'extension' in filters and domain.get('extension') != filters['extension']:
                        continue
                    
                    # Trend score filter
                    if 'min_trend_score' in filters and domain.get('trend_score', 0) < filters['min_trend_score']:
                        continue
                    
                    # Date filter
                    if 'date_from' in filters:
                        domain_date = datetime.fromisoformat(domain.get('saved_at', ''))
                        filter_date = datetime.fromisoformat(filters['date_from'])
                        if domain_date < filter_date:
                            continue
                    
                    filtered_domains.append(domain)
                
                domains = filtered_domains
            
            # Apply limit
            if limit:
                domains = domains[-limit:]  # Get most recent
            
            return domains
            
        except Exception as e:
            st.error(f"Error getting domains: {e}")
            return []
    
    def save_search(self, search_data):
        """Save search history"""
        try:
            data = self.read_json_file(self.searches_file)
            
            # Add metadata
            search_data['id'] = len(data.get('searches', [])) + 1
            search_data['timestamp'] = datetime.now().isoformat()
            
            # Add to searches list
            if 'searches' not in data:
                data['searches'] = []
            
            data['searches'].append(search_data)
            data['last_updated'] = datetime.now().isoformat()
            
            # Write back to file
            success = self.write_json_file(self.searches_file, data)
            
            if success:
                # Update analytics
                self.update_analytics('search_completed', search_data)
            
            return success
            
        except Exception as e:
            st.error(f"Error saving search: {e}")
            return False
    
    def get_searches(self, limit=None):
        """Get search history"""
        try:
            data = self.read_json_file(self.searches_file)
            searches = data.get('searches', [])
            
            if limit:
                searches = searches[-limit:]
            
            return searches
            
        except Exception as e:
            st.error(f"Error getting searches: {e}")
            return []
    
    def update_analytics(self, event_type, event_data=None):
        """Update analytics data"""
        try:
            data = self.read_json_file(self.analytics_file)
            
            if event_type == 'domain_added':
                data['total_domains_found'] = data.get('total_domains_found', 0) + 1
            
            elif event_type == 'search_completed':
                data['total_searches'] = data.get('total_searches', 0) + 1
                if event_data:
                    data['total_domains_checked'] = data.get('total_domains_checked', 0) + event_data.get('domains_checked', 0)
            
            data['last_updated'] = datetime.now().isoformat()
            
            return self.write_json_file(self.analytics_file, data)
            
        except Exception as e:
            st.error(f"Error updating analytics: {e}")
            return False
    
    def get_analytics(self):
        """Get analytics data"""
        try:
            data = self.read_json_file(self.analytics_file)
            domains = self.get_domains()
            
            # Calculate additional metrics
            if domains:
                prices = [d.get('price', 0) for d in domains if d.get('price')]
                trend_scores = [d.get('trend_score', 0) for d in domains if d.get('trend_score')]
                
                analytics = {
                    'total_domains': len(domains),
                    'total_searches': data.get('total_searches', 0),
                    'total_checked': data.get('total_domains_checked', 0),
                    'avg_price': sum(prices) / len(prices) if prices else 0,
                    'avg_trend_score': sum(trend_scores) / len(trend_scores) if trend_scores else 0,
                    'min_price': min(prices) if prices else 0,
                    'max_price': max(prices) if prices else 0,
                    'extensions_distribution': self.get_extensions_distribution(domains),
                    'recent_domains': domains[-10:] if domains else [],
                    'price_ranges': self.get_price_ranges(domains),
                    'trend_score_ranges': self.get_trend_score_ranges(domains)
                }
            else:
                analytics = {
                    'total_domains': 0,
                    'total_searches': data.get('total_searches', 0),
                    'total_checked': data.get('total_domains_checked', 0),
                    'avg_price': 0,
                    'avg_trend_score': 0,
                    'min_price': 0,
                    'max_price': 0,
                    'extensions_distribution': {},
                    'recent_domains': [],
                    'price_ranges': {},
                    'trend_score_ranges': {}
                }
            
            return analytics
            
        except Exception as e:
            st.error(f"Error getting analytics: {e}")
            return {}
    
    def get_extensions_distribution(self, domains):
        """Get distribution of domain extensions"""
        extensions = {}
        for domain in domains:
            ext = domain.get('extension', 'unknown')
            extensions[ext] = extensions.get(ext, 0) + 1
        return extensions
    
    def get_price_ranges(self, domains):
        """Get price range distribution"""
        ranges = {
            'under_20': 0,
            '20_to_50': 0,
            '50_to_100': 0,
            'over_100': 0
        }
        
        for domain in domains:
            price = domain.get('price', 0)
            if price < 20:
                ranges['under_20'] += 1
            elif price < 50:
                ranges['20_to_50'] += 1
            elif price < 100:
                ranges['50_to_100'] += 1
            else:
                ranges['over_100'] += 1
        
        return ranges
    
    def get_trend_score_ranges(self, domains):
        """Get trend score range distribution"""
        ranges = {
            'low_0_40': 0,
            'medium_40_70': 0,
            'high_70_90': 0,
            'excellent_90_100': 0
        }
        
        for domain in domains:
            score = domain.get('trend_score', 0)
            if score < 40:
                ranges['low_0_40'] += 1
            elif score < 70:
                ranges['medium_40_70'] += 1
            elif score < 90:
                ranges['high_70_90'] += 1
            else:
                ranges['excellent_90_100'] += 1
        
        return ranges
    
    def export_data(self, format='json'):
        """Export all data"""
        try:
            all_data = {
                'domains': self.get_domains(),
                'searches': self.get_searches(),
                'analytics': self.get_analytics(),
                'exported_at': datetime.now().isoformat()
            }
            
            if format == 'json':
                return json.dumps(all_data, indent=2, default=str)
            elif format == 'csv':
                # Convert domains to CSV
                if all_data['domains']:
                    df = pd.DataFrame(all_data['domains'])
                    return df.to_csv(index=False)
                else:
                    return "No data to export"
            
        except Exception as e:
            st.error(f"Error exporting data: {e}")
            return None
    
    def import_data(self, data, format='json'):
        """Import data from external source"""
        try:
            if format == 'json':
                imported_data = json.loads(data) if isinstance(data, str) else data
                
                # Import domains
                if 'domains' in imported_data:
                    for domain in imported_data['domains']:
                        self.save_domain(domain)
                
                # Import searches
                if 'searches' in imported_data:
                    search_data = self.read_json_file(self.searches_file)
                    search_data['searches'].extend(imported_data['searches'])
                    self.write_json_file(self.searches_file, search_data)
                
                return True
                
        except Exception as e:
            st.error(f"Error importing data: {e}")
            return False
    
    def cleanup_old_data(self, days_old=30):
        """Clean up old data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Clean domains
            domains_data = self.read_json_file(self.domains_file)
            original_count = len(domains_data.get('domains', []))
            
            domains_data['domains'] = [
                domain for domain in domains_data.get('domains', [])
                if datetime.fromisoformat(domain.get('saved_at', '')) > cutoff_date
            ]
            
            self.write_json_file(self.domains_file, domains_data)
            
            # Clean searches
            searches_data = self.read_json_file(self.searches_file)
            searches_data['searches'] = [
                search for search in searches_data.get('searches', [])
                if datetime.fromisoformat(search.get('timestamp', '')) > cutoff_date
            ]
            
            self.write_json_file(self.searches_file, searches_data)
            
            cleaned_count = original_count - len(domains_data['domains'])
            return cleaned_count
            
        except Exception as e:
            st.error(f"Error cleaning up data: {e}")
            return 0
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            stats = {}
            
            for file_path in [self.domains_file, self.searches_file, self.analytics_file]:
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    stats[file_path.name] = {
                        'size_bytes': file_size,
                        'size_kb': round(file_size / 1024, 2),
                        'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
            
            return stats
            
        except Exception as e:
            st.error(f"Error getting database stats: {e}")
            return {}

