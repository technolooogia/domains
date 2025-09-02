import requests
import random
import time
from datetime import datetime, timedelta
import json
from textblob import TextBlob
import numpy as np
import streamlit as st

class EnhancedTrendAnalyzer:
    """Enhanced trend analysis for domain keywords"""
    
    def __init__(self):
        self.trending_cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
    def calculate_trend_score(self, keyword):
        """Calculate comprehensive trend score (0-100)"""
        scores = {
            'search_volume': self.get_search_volume_score(keyword),
            'social_mentions': self.get_social_media_score(keyword),
            'news_mentions': self.get_news_mention_score(keyword),
            'commercial_intent': self.get_commercial_intent_score(keyword),
            'growth_trend': self.get_growth_trend_score(keyword)
        }
        
        # Weighted average
        weights = {
            'search_volume': 0.25,
            'social_mentions': 0.20,
            'news_mentions': 0.20,
            'commercial_intent': 0.20,
            'growth_trend': 0.15
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores if scores[key] is not None)
        return min(100, max(0, int(total_score)))
    
    def get_search_volume_score(self, keyword):
        """Estimate search volume score"""
        # Simulate search volume based on keyword characteristics
        base_score = random.randint(30, 80)
        
        # High-value keywords get bonus
        high_value_terms = [
            'ai', 'crypto', 'nft', 'web3', 'blockchain', 'defi',
            'health', 'fitness', 'finance', 'invest', 'tech', 'app'
        ]
        
        if any(term in keyword.lower() for term in high_value_terms):
            base_score += random.randint(10, 20)
        
        # Length penalty (very long keywords typically have lower search volume)
        if len(keyword) > 15:
            base_score -= 10
        elif len(keyword) < 4:
            base_score -= 5
        
        return min(100, max(0, base_score))
    
    def get_social_media_score(self, keyword):
        """Analyze social media mentions and sentiment"""
        try:
            # Simulate social media analysis
            base_mentions = random.randint(50, 500)
            
            # Trending topics get more mentions
            trending_keywords = [
                'ai', 'chatgpt', 'crypto', 'bitcoin', 'nft', 'web3',
                'metaverse', 'sustainability', 'climate', 'remote'
            ]
            
            if any(trend in keyword.lower() for trend in trending_keywords):
                base_mentions *= random.uniform(2, 5)
            
            # Convert mentions to score (0-100)
            score = min(100, int(base_mentions / 10))
            
            return score
            
        except Exception:
            return random.randint(40, 70)
    
    def get_news_mention_score(self, keyword):
        """Get news mention score"""
        try:
            # Simulate news analysis
            news_score = random.randint(20, 90)
            
            # Tech and finance keywords often in news
            news_heavy_topics = [
                'ai', 'artificial', 'intelligence', 'crypto', 'bitcoin',
                'climate', 'health', 'finance', 'economy', 'tech'
            ]
            
            if any(topic in keyword.lower() for topic in news_heavy_topics):
                news_score += random.randint(5, 15)
            
            return min(100, news_score)
            
        except Exception:
            return random.randint(30, 60)
    
    def get_commercial_intent_score(self, keyword):
        """Analyze commercial intent of keyword"""
        commercial_indicators = [
            'buy', 'purchase', 'price', 'cost', 'cheap', 'discount',
            'deal', 'sale', 'shop', 'store', 'market', 'service',
            'product', 'solution', 'software', 'app', 'tool', 'platform'
        ]
        
        # Check for commercial terms
        commercial_score = 0
        keyword_lower = keyword.lower()
        
        for indicator in commercial_indicators:
            if indicator in keyword_lower:
                commercial_score += 15
        
        # Industry-specific commercial terms
        industry_terms = {
            'tech': ['app', 'software', 'platform', 'tool', 'api', 'saas'],
            'health': ['care', 'treatment', 'therapy', 'supplement', 'service'],
            'finance': ['invest', 'trading', 'bank', 'pay', 'fund', 'wealth']
        }
        
        for industry, terms in industry_terms.items():
            if any(term in keyword_lower for term in terms):
                commercial_score += 10
                break
        
        # Base commercial potential
        if not commercial_score:
            commercial_score = random.randint(20, 50)
        
        return min(100, commercial_score)
    
    def get_growth_trend_score(self, keyword):
        """Analyze growth trend of keyword"""
        # Simulate growth trend analysis
        growth_categories = {
            'explosive': ['ai', 'chatgpt', 'nft', 'web3', 'metaverse'],
            'strong': ['crypto', 'defi', 'sustainability', 'remote', 'digital'],
            'steady': ['health', 'fitness', 'finance', 'tech', 'app'],
            'declining': ['flash', 'cd', 'dvd', 'fax']
        }
        
        keyword_lower = keyword.lower()
        
        for category, terms in growth_categories.items():
            if any(term in keyword_lower for term in terms):
                if category == 'explosive':
                    return random.randint(85, 100)
                elif category == 'strong':
                    return random.randint(70, 90)
                elif category == 'steady':
                    return random.randint(50, 75)
                elif category == 'declining':
                    return random.randint(10, 40)
        
        # Default growth score
        return random.randint(40, 70)
    
    def get_market_value_estimate(self, domain, trend_score):
        """Estimate market value based on trends and domain characteristics"""
        keyword = domain.split('.')[0]
        extension = domain.split('.')[-1]
        
        # Base value calculation
        base_value = trend_score * random.uniform(8, 25)
        
        # Length bonus/penalty
        if len(keyword) <= 4:
            base_value *= 2.5  # Short domains are premium
        elif len(keyword) <= 6:
            base_value *= 1.8
        elif len(keyword) <= 8:
            base_value *= 1.3
        elif len(keyword) > 12:
            base_value *= 0.7  # Long domains less valuable
        
        # Extension multipliers
        extension_multipliers = {
            'com': 3.0,
            'ai': 2.5,
            'io': 2.0,
            'co': 1.8,
            'net': 1.5,
            'org': 1.3,
            'tech': 1.4,
            'app': 1.6
        }
        
        multiplier = extension_multipliers.get(extension, 1.0)
        estimated_value = base_value * multiplier
        
        # Industry-specific bonuses
        industry_bonuses = {
            'ai': 1.5,
            'crypto': 1.4,
            'health': 1.3,
            'finance': 1.3,
            'tech': 1.2
        }
        
        for industry, bonus in industry_bonuses.items():
            if industry in keyword.lower():
                estimated_value *= bonus
                break
        
        # Brandability bonus
        brandability_score = self.calculate_brandability_score(keyword)
        if brandability_score > 80:
            estimated_value *= 1.3
        elif brandability_score > 60:
            estimated_value *= 1.1
        
        return max(100, min(100000, int(estimated_value)))
    
    def calculate_brandability_score(self, keyword):
        """Calculate how brandable a keyword is"""
        score = 50  # Base score
        
        # Length scoring
        length = len(keyword)
        if 4 <= length <= 8:
            score += 25
        elif 9 <= length <= 10:
            score += 15
        elif length < 4:
            score += 10
        else:
            score -= 10
        
        # Pronounceability
        vowels = sum(1 for char in keyword.lower() if char in 'aeiou')
        consonants = length - vowels
        
        if vowels > 0 and consonants > 0:
            vowel_ratio = vowels / length
            if 0.2 <= vowel_ratio <= 0.6:  # Good vowel/consonant balance
                score += 20
        
        # Avoid numbers and special characters
        if any(char.isdigit() or char in '-_' for char in keyword):
            score -= 25
        
        # Dictionary word bonus
        common_words = [
            'smart', 'quick', 'fast', 'easy', 'simple', 'pro', 'max',
            'ultra', 'super', 'mega', 'best', 'top', 'prime', 'elite'
        ]
        
        if keyword.lower() in common_words:
            score += 15
        
        # Memorable patterns
        if len(set(keyword.lower())) < len(keyword) * 0.7:  # Some repeated letters
            score += 10
        
        return max(0, min(100, score))
    
    def get_competitor_analysis(self, keyword):
        """Analyze competitor domains"""
        # Simulate competitor analysis
        competitors = []
        
        # Generate some realistic competitor domains
        extensions = ['com', 'net', 'org', 'io', 'co']
        prefixes = ['get', 'my', 'the', 'pro', 'best']
        suffixes = ['app', 'hub', 'pro', 'ly', 'io']
        
        for i in range(random.randint(3, 8)):
            if random.choice([True, False]):
                # Prefix variation
                competitor = f"{random.choice(prefixes)}{keyword}.{random.choice(extensions)}"
            else:
                # Suffix variation
                competitor = f"{keyword}{random.choice(suffixes)}.{random.choice(extensions)}"
            
            competitors.append({
                'domain': competitor,
                'estimated_traffic': random.randint(1000, 50000),
                'domain_authority': random.randint(20, 80),
                'backlinks': random.randint(100, 10000)
            })
        
        return competitors
    
    def get_seasonal_trends(self, keyword):
        """Analyze seasonal trends for keyword"""
        # Simulate seasonal data
        months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        
        seasonal_data = []
        base_interest = random.randint(40, 80)
        
        for i, month in enumerate(months):
            # Add seasonal variation
            if keyword.lower() in ['fitness', 'health', 'diet']:
                # Health keywords peak in January (New Year resolutions)
                if i == 0:  # January
                    interest = base_interest + random.randint(20, 40)
                else:
                    interest = base_interest + random.randint(-10, 15)
            elif keyword.lower() in ['crypto', 'invest', 'finance']:
                # Finance keywords more stable with slight end-of-year increase
                if i >= 10:  # Nov-Dec
                    interest = base_interest + random.randint(5, 20)
                else:
                    interest = base_interest + random.randint(-5, 10)
            else:
                # General variation
                interest = base_interest + random.randint(-15, 20)
            
            seasonal_data.append({
                'month': month,
                'interest': max(0, min(100, interest))
            })
        
        return seasonal_data
    
    def get_trending_keywords_by_category(self, category):
        """Get trending keywords for specific category"""
        trending_by_category = {
            'tech': [
                'ai', 'machine learning', 'blockchain', 'quantum computing',
                'edge computing', 'iot', 'cybersecurity', 'cloud native'
            ],
            'health': [
                'telemedicine', 'mental health', 'personalized medicine',
                'wearable tech', 'nutrition tracking', 'meditation'
            ],
            'finance': [
                'defi', 'cryptocurrency', 'robo advisor', 'fintech',
                'digital banking', 'payment solutions', 'insurtech'
            ],
            'ai': [
                'chatgpt', 'generative ai', 'computer vision', 'nlp',
                'neural networks', 'deep learning', 'ai ethics'
            ]
        }
        
        return trending_by_category.get(category.lower(), [])
