import requests
from bs4 import BeautifulSoup
import json
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random

class PriceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.registrars = {
            'godaddy': self.scrape_godaddy,
            'namecheap': self.scrape_namecheap,
            'hostinger': self.scrape_hostinger,
            'porkbun': self.scrape_porkbun,
            'namesilo': self.scrape_namesilo
        }
        self.setup_selenium()
    
    def setup_selenium(self):
        """Setup headless Chrome for JavaScript-heavy sites"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def get_price(self, domain):
        """Get the lowest price from all registrars"""
        prices = {}
        
        for registrar, scraper_func in self.registrars.items():
            try:
                price = scraper_func(domain)
                if price:
                    prices[registrar] = price
                time.sleep(random.uniform(1, 3))  # Rate limiting
            except Exception as e:
                print(f"Error scraping {registrar}: {e}")
                continue
        
        return min(prices.values()) if prices else None
    
    def scrape_godaddy(self, domain):
        """Scrape GoDaddy pricing"""
        try:
            url = f"https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={domain}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                price_element = soup.find('span', {'data-cy': 'price-display'})
                if price_element:
                    price_text = price_element.text.strip()
                    return self.extract_price(price_text)
            
            # Fallback to Selenium for JavaScript content
            return self.scrape_with_selenium(url, 'span[data-cy="price-display"]')
            
        except Exception as e:
            return None
    
    def scrape_namecheap(self, domain):
        """Scrape Namecheap pricing"""
        try:
            url = f"https://www.namecheap.com/domains/registration/results/?domain={domain}"
            response = self.session.get(url, timeout=15)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            price_element = soup.find('span', class_='price')
            if price_element:
                return self.extract_price(price_element.text)
            
            return None
        except:
            return None
    
    def scrape_hostinger(self, domain):
        """Scrape Hostinger pricing"""
        try:
            url = f"https://www.hostinger.com/domain-checker?domain={domain}"
            
            # Hostinger requires JavaScript, use Selenium
            self.driver.get(url)
            time.sleep(3)
            
            price_elements = self.driver.find_elements_by_css_selector('.price')
            if price_elements:
                price_text = price_elements[0].text
                return self.extract_price(price_text)
            
            return None
        except:
            return None
    
    def scrape_porkbun(self, domain):
        """Scrape Porkbun pricing (often cheapest)"""
        try:
            url = f"https://porkbun.com/checkout/search?q={domain}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'pricing' in data:
                    return float(data['pricing']['registration'])
            
            return None
        except:
            return None
    
    def scrape_namesilo(self, domain):
        """Scrape NameSilo pricing"""
        try:
            url = f"https://www.namesilo.com/domain/search-domains?query={domain}"
            response = self.session.get(url, timeout=15)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            price_element = soup.find('span', class_='domain_price')
            if price_element:
                return self.extract_price(price_element.text)
            
            return None
        except:
            return None
    
    def scrape_with_selenium(self, url, selector):
        """Use Selenium for JavaScript-heavy sites"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            element = self.driver.find_element_by_css_selector(selector)
            if element:
                return self.extract_price(element.text)
            
            return None
        except:
            return None
    
    def extract_price(self, price_text):
        """Extract numeric price from text"""
        import re
        price_match = re.search(r'\$?(\d+\.?\d*)', price_text.replace(',', ''))
        return float(price_match.group(1)) if price_match else None
    
    async def get_prices_async(self, domains):
        """Async price checking for bulk operations"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for domain in domains:
                for registrar in self.registrars:
                    tasks.append(self.scrape_async(session, domain, registrar))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self.process_async_results(results)
