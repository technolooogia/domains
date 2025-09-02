import sqlite3
import pandas as pd
from datetime import datetime
import json

class DomainDatabase:
    def __init__(self, db_path='data/domains.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Available domains table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS available_domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE,
                extension TEXT,
                price REAL,
                registrar TEXT,
                trend_score REAL,
                brandability_score REAL,
                estimated_value REAL,
                keywords TEXT,
                found_date TIMESTAMP,
                status TEXT DEFAULT 'available'
            )
        ''')
        
        # Search history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_date TIMESTAMP,
                keywords_used TEXT,
                domains_checked INTEGER,
                domains_found INTEGER,
                avg_price REAL,
                search_duration REAL
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT,
                registrar TEXT,
                price REAL,
                check_date TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_available_domain(self, domain_data):
        """Save available domain to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO available_domains 
            (domain, extension, price, registrar, trend_score, brandability_score, 
             estimated_value, keywords, found_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            domain_data['domain'],
            domain_data['extension'],
            domain_data['price'],
            domain_data['registrar'],
            domain_data['trend_score'],
            domain_data['brandability_score'],
            domain_data['estimated_value'],
            json.dumps(domain_data['keywords']),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def get_top_domains(self, limit=100, sort_by='trend_score'):
        """Get top domains by specified criteria"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT * FROM available_domains 
            WHERE status = 'available'
            ORDER BY {sort_by} DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        
        return df
    
    def get_analytics(self):
        """Get search analytics"""
        conn = sqlite3.connect(self.db_path)
        
        analytics = {
            'total_domains_found': conn.execute('SELECT COUNT(*) FROM available_domains').fetchone()[0],
            'avg_price': conn.execute('SELECT AVG(price) FROM available_domains').fetchone()[0],
            'top_extensions': pd.read_sql_query('''
                SELECT extension, COUNT(*) as count 
                FROM available_domains 
                GROUP BY extension 
                ORDER BY count DESC
            ''', conn),
            'price_distribution': pd.read_sql_query('''
                SELECT 
                    CASE 
                        WHEN price < 10 THEN 'Under $10'
                        WHEN price < 20 THEN '$10-$20'
                        WHEN price < 30 THEN '$20-$30'
                        ELSE 'Over $30'
                    END as price_range,
                    COUNT(*) as count
                FROM available_domains
                GROUP BY price_range
            ''', conn)
        }
        
        conn.close()
        return analytics
