import requests
import random
import itertools
from pytrends.request import TrendReq
import nltk
from nltk.corpus import words
import tweepy
import json

class WordGenerator:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.tech_terms = self.load_tech_terms()
        self.health_terms = self.load_health_terms()
        self.finance_terms = self.load_finance_terms()
        self.food_terms = self.load_food_terms()
        
    def generate_combinations(self, sources, limit=10000):
        """Generate domain name combinations from various sources"""
        all_words = set()
        
        for source in sources:
            if source == 'Trending Keywords':
                all_words.update(self.get_trending_keywords())
            elif source == 'Tech Terms':
                all_words.update(self.tech_terms)
            elif source == 'Health Terms':
                all_words.update(self.health_terms)
            elif source == 'Finance Terms':
                all_words.update(self.finance_terms)
            elif source == 'Food Terms':
                all_words.update(self.food_terms)
            elif source == 'Made-up Words':
                all_words.update(self.generate_brandable_words())
        
        # Generate combinations
        combinations = []
        word_list = list(all_words)
        
        # Single words
        combinations.extend(word_list[:limit//4])
        
        # Two-word combinations
        for w1, w2 in itertools.combinations(word_list[:100], 2):
            if len(combinations) >= limit:
                break
            combinations.append(f"{w1}{w2}")
            combinations.append(f"{w1}-{w2}")
        
        # Prefixes and suffixes
        prefixes = ['get', 'my', 'the', 'pro', 'super', 'ultra', 'mega']
        suffixes = ['app', 'hub', 'lab', 'pro', 'ai', 'tech', 'ly']
        
        for word in word_list[:50]:
            for prefix in prefixes:
                combinations.append(f"{prefix}{word}")
            for suffix in suffixes:
                combinations.append(f"{word}{suffix}")
        
        return combinations[:limit]
    
    def get_trending_keywords(self):
        """Get trending keywords from multiple sources"""
        keywords = set()
        
        # Google Trends
        try:
            trending_searches = self.pytrends.trending_searches(pn='united_states')
            keywords.update(trending_searches[0].str.lower().str.replace(' ', '').tolist())
        except:
            pass
        
        # Twitter trends (requires API keys)
        keywords.update(self.get_twitter_trends())
        
        # Reddit trending
        keywords.update(self.get_reddit_trends())
        
        # News trending
        keywords.update(self.get_news_trends())
        
        return list(keywords)[:100]
    
    def get_twitter_trends(self):
        """Get Twitter trending topics"""
        try:
            # Add your Twitter API credentials
            api = tweepy.API(auth)
            trends = api.get_place_trends(1)[0]['trends']
            return [trend['name'].lower().replace('#', '').replace(' ', '') 
                   for trend in trends[:20]]
        except:
            return []
    
    def get_reddit_trends(self):
        """Get Reddit trending topics"""
        try:
            response = requests.get('https://www.reddit.com/r/all/hot.json', 
                                  headers={'User-Agent': 'DomainHunter'})
            data = response.json()
            titles = [post['data']['title'] for post in data['data']['children']]
            # Extract keywords from titles
            keywords = []
            for title in titles:
                words = title.lower().split()
                keywords.extend([w for w in words if len(w) > 3 and w.isalpha()])
            return list(set(keywords))[:50]
        except:
            return []
    
    def generate_brandable_words(self):
        """Generate brandable made-up words"""
        brandable = []
        
        # Consonant-vowel patterns
        consonants = 'bcdfghjklmnpqrstvwxyz'
        vowels = 'aeiou'
        
        patterns = ['cvcv', 'cvcvc', 'cvccv', 'ccvcv']
        
        for pattern in patterns:
            for _ in range(100):
                word = ''
                for char in pattern:
                    if char == 'c':
                        word += random.choice(consonants)
                    else:
                        word += random.choice(vowels)
                if 4 <= len(word) <= 8:
                    brandable.append(word)
        
        return brandable
    
    def load_tech_terms(self):
        """Load technology-related terms"""
        return [
            'ai', 'ml', 'blockchain', 'crypto', 'nft', 'web3', 'metaverse',
            'cloud', 'saas', 'api', 'sdk', 'devops', 'agile', 'scrum',
            'react', 'python', 'javascript', 'node', 'docker', 'kubernetes',
            'tensorflow', 'pytorch', 'opencv', 'nlp', 'computer', 'vision',
            'robotics', 'iot', 'edge', 'quantum', 'neural', 'deep', 'learning'
        ]
    
    def load_health_terms(self):
        """Load health and wellness terms"""
        return [
            'health', 'wellness', 'fitness', 'nutrition', 'diet', 'workout',
            'yoga', 'meditation', 'mindfulness', 'therapy', 'mental', 'physical',
            'organic', 'natural', 'supplement', 'vitamin', 'protein', 'keto',
            'vegan', 'paleo', 'detox', 'cleanse', 'immunity', 'recovery'
        ]
    
    def load_finance_terms(self):
        """Load finance and business terms"""
        return [
            'finance', 'invest', 'trading', 'crypto', 'bitcoin', 'ethereum',
            'defi', 'nft', 'portfolio', 'wealth', 'money', 'profit', 'revenue',
            'startup', 'business', 'entrepreneur', 'venture', 'capital',
            'stock', 'forex', 'commodity', 'bond', 'fund', 'asset'
        ]
    
    def load_food_terms(self):
        """Load food and beverage terms"""
        return [
            'food', 'recipe', 'cooking', 'chef', 'kitchen', 'restaurant',
            'cafe', 'coffee', 'tea', 'wine', 'beer', 'cocktail', 'organic',
            'fresh', 'local', 'farm', 'gourmet', 'artisan', 'craft', 'fusion'
        ]
