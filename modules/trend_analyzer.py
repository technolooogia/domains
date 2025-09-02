import requests
from pytrends.request import TrendReq
import pandas as pd
from textblob import TextBlob
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

class TrendAnalyzer:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.news_api_key = "YOUR_NEWS_API_KEY"  # Get from newsapi.org
        
    def get_trend_score(self, keyword):
        """Calculate comprehensive trend score (0-100)"""
        scores = {
            'google_trends': self.get_google_trend_score(keyword),
            'social_media': self.get_social_media_score(keyword),
            'news_mentions': self.get_news_mention_score(keyword),
            'search_volume': self.get_search_volume_score(keyword),
            'commercial_intent': self.get_commercial_intent_score(keyword)
        }
        
        # Weighted average
        weights = {
            'google_trends': 0.25,
            'social_media': 0.20,
            'news_mentions': 0.20,
            'search_volume': 0.20,
            'commercial_intent': 0.15
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores if scores[key])
        return min(100, max(0, total_score))
    
    def get_google_trend_score(self, keyword):
        """Get Google Trends score"""
        try:
            self.pytrends.build_payload([keyword], timeframe='today 3-m')
            data = self.pytrends.interest_over_time()
            
            if not data.empty:
                recent_avg = data[keyword].tail(4).mean()
                overall_avg = data[keyword].mean()
                
                # Score based on recent vs overall performance
                if overall_avg > 0:
                    trend_ratio = recent_avg / overall_avg
                    return min(100, trend_ratio * 50)
            
            return 0
        except:
            return 0
    
    def get_social_media_score(self, keyword):
        """Analyze social media mentions and sentiment"""
        try:
            # Twitter mentions (requires API)
            twitter_score = self.get_twitter_mentions(keyword)
            
            # Reddit mentions
            reddit_score = self.get_reddit_mentions(keyword)
            
            # Instagram hashtag popularity
            instagram_score = self.get_instagram_score(keyword)
            
            return (twitter_score + reddit_score + instagram_score) / 3
        except:
            return 0
    
    def get_twitter_mentions(self, keyword):
        """Get Twitter mention score"""
        try:
            # Implement Twitter API v2 search
            # This requires Twitter API credentials
            url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}&max_results=100"
            # Add your Twitter bearer token
            headers = {"Authorization": "Bearer YOUR_TWITTER_BEARER_TOKEN"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                tweet_count = data.get('meta', {}).get('result_count', 0)
                return min(100, tweet_count * 2)  # Scale appropriately
            
            return 0
        except:
            return 0
    
    def get_reddit_mentions(self, keyword):
        """Get Reddit mention score"""
        try:
            url = f"https://www.reddit.com/search.json?q={keyword}&sort=new&limit=100"
            headers = {'User-Agent': 'DomainHunter/1.0'}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                post_count = len(data.get('data', {}).get('children', []))
                
                # Calculate engagement score
                total_score = 0
                for post in data['data']['children']:
                    post_data = post['data']
                    score = post_data.get('score', 0)
                    comments = post_data.get('num_comments', 0)
                    total_score += score + (comments * 2)
                
                return min(100, total_score / 10)
            
            return 0
        except:
            return 0
    
    def get_news_mention_score(self, keyword):
        """Get news mention score"""
        try:
            url = f"https://newsapi.org/v2/everything?q={keyword}&from={datetime.now() - timedelta(days=30)}&sortBy=popularity&apiKey={self.news_api_key}"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                article_count = data.get('totalResults', 0)
                
                # Analyze sentiment of headlines
                sentiment_scores = []
                for article in data.get('articles', [])[:20]:
                    headline = article.get('title', '')
                    sentiment = TextBlob(headline).sentiment.polarity
                    sentiment_scores.append(sentiment)
                
                avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
                sentiment_bonus = max(0, avg_sentiment * 20)  # Positive sentiment bonus
                
                return min(100, (article_count / 10) + sentiment_bonus)
            
            return 0
        except:
            return 0
    
    def get_search_volume_score(self, keyword):
        """Estimate search volume score"""
        try:
            # Use Google Keyword Planner API or similar
            # For now, use Google Trends as proxy
            self.pytrends.build_payload([keyword])
            suggestions = self.pytrends.suggestions(keyword)
            
            if suggestions:
                # Higher number of suggestions indicates higher search volume
                return min(100, len(suggestions) * 5)
            
            return 0
        except:
            return 0
    
    def get_commercial_intent_score(self, keyword):
        """Analyze commercial intent of keyword"""
        commercial_indicators = [
            'buy', 'purchase', 'price', 'cost', 'cheap', 'discount',
            'deal', 'sale', 'shop', 'store', 'market', 'service',
            'product', 'solution', 'software', 'app', 'tool'
        ]
        
        # Check if keyword contains commercial terms
        keyword_lower = keyword.lower()
        commercial_score = sum(10 for indicator in commercial_indicators 
                             if indicator in keyword_lower)
        
        # Check related searches for commercial intent
        try:
            self.pytrends.build_payload([keyword])
            related_queries = self.pytrends.related_queries()
            
            if keyword in related_queries and related_queries[keyword]['top'] is not None:
                related_terms = related_queries[keyword]['top']['query'].tolist()
                for term in related_terms[:10]:
                    commercial_score += sum(5 for indicator in commercial_indicators 
                                          if indicator in term.lower())
        except:
            pass
        
        return min(100, commercial_score)
    
    def get_domain_value_estimate(self, domain):
        """Estimate domain value based on multiple factors"""
        keyword = domain.split('.')[0]
        
        factors = {
            'length': self.score_domain_length(domain),
            'memorability': self.score_memorability(keyword),
            'brandability': self.score_brandability(keyword),
            'seo_potential': self.get_trend_score(keyword),
            'extension_value': self.score_extension(domain),
            'similar_sales': self.get_similar_sales_data(keyword)
        }
        
        # Calculate weighted value estimate
        base_value = sum(factors.values()) / len(factors)
        
        # Apply multipliers based on extension
        extension = domain.split('.')[-1]
        multipliers = {'.com': 3.0, '.ai': 2.5, '.io': 2.0, '.co': 1.8, '.net': 1.5}
        multiplier = multipliers.get(f'.{extension}', 1.0)
        
        estimated_value = base_value * multiplier * 10  # Scale to dollar amount
        return max(50, min(50000, estimated_value))  # Cap between $50-$50k
    
    def score_domain_length(self, domain):
        """Score based on domain length (shorter is better)"""
        name_length = len(domain.split('.')[0])
        if name_length <= 4:
            return 100
        elif name_length <= 6:
            return 80
        elif name_length <= 8:
            return 60
        elif name_length <= 10:
            return 40
        else:
            return 20
    
    def score_memorability(self, keyword):
        """Score memorability factors"""
        score = 50  # Base score
        
        # Bonus for pronounceable
        vowels = sum(1 for char in keyword.lower() if char in 'aeiou')
        consonants = len(keyword) - vowels
        if vowels > 0 and consonants > 0:
            score += 20
        
        # Penalty for numbers/hyphens
        if any(char.isdigit() or char == '-' for char in keyword):
            score -= 30
        
        # Bonus for dictionary words
        try:
            from nltk.corpus import words
            english_words = set(words.words())
            if keyword.lower() in english_words:
                score += 30
        except:
            pass
        
        return max(0, min(100, score))
