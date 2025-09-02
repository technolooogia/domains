import whois
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time
import random

class DomainChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.rate_limit_delay = 0.5
        self.proxies = self.load_proxies()
        
    def is_available(self, domain):
        """Check if domain is available using multiple methods"""
        methods = [
            self.check_whois,
            self.check_registrar_api,
            self.check_dns_resolution
        ]
        
        for method in methods:
            try:
                result = method(domain)
                if result is not None:
                    return result
            except Exception as e:
                continue
                
        return False
    
    def check_whois(self, domain):
        """Primary method: WHOIS lookup"""
        try:
            time.sleep(random.uniform(0.1, self.rate_limit_delay))
            w = whois.whois(domain)
            
            # Domain is available if no registrar or creation date
            if not w.registrar and not w.creation_date:
                return True
            return False
            
        except whois.parser.PywhoisError:
            return True  # Domain likely available
        except Exception:
            return None  # Uncertain, try next method
    
    def check_registrar_api(self, domain):
        """Secondary method: Registrar APIs"""
        apis = {
            'namecheap': f'https://api.namecheap.com/xml.response?ApiUser=test&ApiKey=test&UserName=test&Command=namecheap.domains.check&ClientIp=127.0.0.1&DomainList={domain}',
            'godaddy': f'https://api.godaddy.com/v1/domains/available?domain={domain}'
        }
        
        for provider, url in apis.items():
            try:
                response = self.session.get(url, timeout=10)
                if 'available' in response.text.lower():
                    return True
            except:
                continue
        return None
    
    def check_dns_resolution(self, domain):
        """Tertiary method: DNS resolution"""
        try:
            import socket
            socket.gethostbyname(domain)
            return False  # Domain resolves, likely taken
        except socket.gaierror:
            return True   # Domain doesn't resolve, likely available
        except:
            return None
    
    async def check_bulk_async(self, domains):
        """Async bulk checking for speed"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_domain_async(session, domain) for domain in domains]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
    
    def load_proxies(self):
        """Load proxy list for rate limit avoidance"""
        # Add your proxy sources here
        return []
