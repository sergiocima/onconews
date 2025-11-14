#!/usr/bin/env python3
"""
Google News RSS Fetcher - Estrae notizie da Google News via RSS
"""
import requests
import feedparser
import logging
from typing import List, Dict
from datetime import datetime
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class GoogleNewsFetcher:
    """Fetcher per Google News tramite RSS"""

    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://news.google.com/rss/search"
        self.language = "it"
        self.country = "IT"

    def fetch_keyword(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """
        Recupera articoli da Google News per una keyword

        Args:
            keyword: Keyword di ricerca
            max_results: Numero massimo di risultati

        Returns:
            Lista di articoli normalizzati
        """
        try:
            # Costruisci query
            query = f"{keyword} when:7d"  # Ultimi 7 giorni
            encoded_query = quote_plus(query)

            # URL RSS Google News
            rss_url = f"{self.base_url}?q={encoded_query}&hl={self.language}&gl={self.country}&ceid={self.country}:{self.language}"

            logger.debug(f"Fetching Google News RSS: {keyword}")

            # Parse RSS feed
            feed = feedparser.parse(rss_url)

            articles = []
            for entry in feed.entries[:max_results]:
                article = self._normalize_entry(entry, keyword)
                if article:
                    articles.append(article)

            logger.info(f"Google News: {len(articles)} articles for '{keyword}'")
            return articles

        except Exception as e:
            logger.error(f"Error fetching Google News for '{keyword}': {e}")
            return []

    def _normalize_entry(self, entry, keyword: str) -> Dict:
        """
        Normalizza un entry RSS nel formato standard

        Args:
            entry: Entry RSS da feedparser
            keyword: Keyword che ha generato questo risultato

        Returns:
            Dizionario normalizzato
        """
        try:
            # Estrai URL originale (Google News fa redirect)
            url = entry.get('link', '')

            # Pulisci URL Google News redirect
            if 'news.google.com' in url and '/articles/' in url:
                # Prova a estrarre URL originale da RSS (spesso presente)
                url = entry.get('source', {}).get('href', url)

            # Estrai source name
            source_name = entry.get('source', {}).get('title', 'Google News')

            # Estrai data pubblicazione
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6]).isoformat()

            return {
                'url': url,
                'title': entry.get('title', ''),
                'source': {
                    'name': source_name
                },
                'author': None,  # RSS Google News non ha author
                'description': entry.get('summary', ''),
                'publishedAt': published_at,
                'content': None,
                'urlToImage': None,
                'keywords_matched': keyword
            }

        except Exception as e:
            logger.debug(f"Error normalizing Google News entry: {e}")
            return None

    def fetch_all_keywords(self, keywords: List[str], max_per_keyword: int = 50) -> List[Dict]:
        """
        Recupera articoli per tutte le keywords

        Args:
            keywords: Lista di keywords
            max_per_keyword: Massimo risultati per keyword

        Returns:
            Lista di tutti gli articoli (deduplica per URL)
        """
        all_articles = []
        seen_urls = set()

        logger.info(f"Starting Google News fetch for {len(keywords)} keywords")

        for keyword in keywords:
            articles = self.fetch_keyword(keyword, max_results=max_per_keyword)

            # Deduplica
            for article in articles:
                url = article['url']
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append(article)

        logger.info(f"Google News: Total {len(all_articles)} unique articles")
        return all_articles
