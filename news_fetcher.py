"""
Modulo per il recupero delle notizie tramite News API
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Gestisce il recupero delle notizie da News API"""

    def __init__(self, api_key: str, config: Dict):
        self.api_key = api_key
        self.config = config
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_news_for_keyword(self, keyword: str, from_date: Optional[str] = None) -> List[Dict]:
        """
        Recupera notizie per una specifica keyword

        Args:
            keyword: Parola chiave da cercare
            from_date: Data di inizio ricerca (formato YYYY-MM-DD)

        Returns:
            Lista di articoli trovati
        """
        if from_date is None:
            # Default: ultimi 7 giorni
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        params = {
            'q': keyword,
            'apiKey': self.api_key,
            'language': self.config['news_api']['language'],
            'sortBy': self.config['news_api']['sort_by'],
            'pageSize': self.config['news_api']['page_size'],
            'from': from_date
        }

        try:
            logger.info(f"Fetching news for keyword: '{keyword}' from {from_date}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data['status'] != 'ok':
                logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return []

            articles = data.get('articles', [])
            logger.info(f"Found {len(articles)} articles for '{keyword}'")

            # Aggiungi la keyword matched a ogni articolo
            for article in articles:
                article['keywords_matched'] = keyword

            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news for '{keyword}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error for '{keyword}': {e}")
            return []

    def fetch_all_keywords(self, keywords: List[str], from_date: Optional[str] = None,
                          delay_between_requests: float = 1.0) -> List[Dict]:
        """
        Recupera notizie per tutte le keywords configurate

        Args:
            keywords: Lista di keywords da cercare
            from_date: Data di inizio ricerca
            delay_between_requests: Pausa tra le richieste (secondi) per evitare rate limiting

        Returns:
            Lista di tutti gli articoli trovati (deduplicati per URL)
        """
        all_articles = []
        seen_urls = set()

        for i, keyword in enumerate(keywords):
            logger.info(f"Processing keyword {i+1}/{len(keywords)}: '{keyword}'")

            articles = self.fetch_news_for_keyword(keyword, from_date)

            # Deduplica per URL
            new_articles = 0
            for article in articles:
                url = article.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append(article)
                    new_articles += 1

            logger.info(f"  → {new_articles} new unique articles (total: {len(all_articles)})")

            # Pausa tra le richieste per evitare rate limiting
            if i < len(keywords) - 1:
                time.sleep(delay_between_requests)

        logger.info(f"Total unique articles fetched: {len(all_articles)}")
        return all_articles

    def normalize_article(self, article: Dict) -> Dict:
        """
        Normalizza i dati dell'articolo nel formato del database

        Args:
            article: Dati grezzi da News API

        Returns:
            Dizionario normalizzato
        """
        return {
            'url': article.get('url'),
            'title': article.get('title'),
            'source_name': article.get('source', {}).get('name'),
            'author': article.get('author'),
            'published_at': article.get('publishedAt'),
            'description': article.get('description'),
            'keywords_matched': article.get('keywords_matched'),
            'language': self.config['news_api']['language']
        }

    def get_rate_limit_info(self) -> Dict:
        """
        Ottiene informazioni sui limiti di utilizzo dell'API
        (Nota: News API non fornisce queste info via API, solo via dashboard)

        Returns:
            Dizionario con informazioni disponibili
        """
        return {
            'note': 'Check your News API dashboard for rate limit details',
            'free_tier_limit': '100 requests per day',
            'developer_tier_limit': '250 requests per day',
            'business_tier_limit': 'Check your plan'
        }

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Valida la chiave API facendo una richiesta di test

        Args:
            api_key: Chiave API da validare

        Returns:
            True se la chiave è valida, False altrimenti
        """
        try:
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    'q': 'test',
                    'apiKey': api_key,
                    'pageSize': 1
                },
                timeout=10
            )
            data = response.json()
            return data.get('status') == 'ok'
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False
