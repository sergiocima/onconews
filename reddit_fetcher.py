#!/usr/bin/env python3
"""
Reddit Fetcher - Estrae discussioni da subreddit rilevanti
"""
import requests
import logging
from typing import List, Dict
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class RedditFetcher:
    """Fetcher per discussioni Reddit"""

    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': config['scraping']['user_agent']
        }
        # Subreddit rilevanti (italiani e internazionali)
        self.subreddits = [
            'italy',           # Reddit italiano generale
            'ItalyInformatica',  # Può avere discussioni su salute/tech
            'cancer',          # Discussioni su cancro
            'CancerFamilySupport',  # Supporto famiglie
            'AskDocs',         # Domande mediche
            'medicine',        # Medicina generale
            'Health',          # Salute
        ]

    def fetch_subreddit(self, subreddit: str, keywords: List[str], time_filter: str = 'week', limit: int = 100) -> List[Dict]:
        """
        Cerca post in un subreddit con keywords

        Args:
            subreddit: Nome del subreddit
            keywords: Lista di keywords da cercare
            time_filter: Filtro temporale (hour, day, week, month, year, all)
            limit: Massimo numero di risultati

        Returns:
            Lista di post normalizzati
        """
        posts = []

        try:
            for keyword in keywords:
                # Costruisci query
                search_query = keyword
                url = f"{self.base_url}/r/{subreddit}/search.json"

                params = {
                    'q': search_query,
                    'restrict_sr': 'true',  # Cerca solo in questo subreddit
                    'sort': 'new',
                    't': time_filter,
                    'limit': min(limit, 100)  # Reddit max 100 per request
                }

                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                if 'data' in data and 'children' in data['data']:
                    for post in data['data']['children']:
                        post_data = post.get('data', {})
                        normalized = self._normalize_post(post_data, subreddit, keyword)
                        if normalized:
                            posts.append(normalized)

                # Rate limiting gentile
                time.sleep(1)

            logger.info(f"Reddit r/{subreddit}: {len(posts)} posts found")
            return posts

        except Exception as e:
            logger.error(f"Error fetching Reddit r/{subreddit}: {e}")
            return []

    def _normalize_post(self, post: Dict, subreddit: str, keyword: str) -> Dict:
        """
        Normalizza un post Reddit nel formato standard

        Args:
            post: Dati del post da Reddit API
            subreddit: Subreddit di provenienza
            keyword: Keyword che ha generato questo risultato

        Returns:
            Dizionario normalizzato
        """
        try:
            # URL completo del post
            permalink = post.get('permalink', '')
            url = f"https://www.reddit.com{permalink}" if permalink else None

            # Titolo
            title = post.get('title', '')

            # Testo del post (selftext)
            selftext = post.get('selftext', '')

            # Data pubblicazione
            created_utc = post.get('created_utc')
            published_at = datetime.fromtimestamp(created_utc).isoformat() if created_utc else None

            # Autore
            author = post.get('author', 'unknown')

            # Score (upvotes - downvotes)
            score = post.get('score', 0)

            # Numero commenti
            num_comments = post.get('num_comments', 0)

            # Costruisci description combinando selftext e stats
            description = f"{selftext[:200]}... [{score} upvotes, {num_comments} comments]" if selftext else f"[{score} upvotes, {num_comments} comments]"

            return {
                'url': url,
                'title': title,
                'source': {
                    'name': f'Reddit r/{subreddit}'
                },
                'author': f'u/{author}',
                'description': description,
                'publishedAt': published_at,
                'content': selftext,  # Salviamo il testo completo del post
                'urlToImage': None,
                'keywords_matched': keyword,
                'reddit_score': score,
                'reddit_comments': num_comments
            }

        except Exception as e:
            logger.debug(f"Error normalizing Reddit post: {e}")
            return None

    def fetch_all_subreddits(self, keywords: List[str]) -> List[Dict]:
        """
        Cerca in tutti i subreddit configurati

        Args:
            keywords: Lista di keywords da cercare

        Returns:
            Lista di tutti i post (deduplica per URL)
        """
        all_posts = []
        seen_urls = set()

        logger.info(f"Starting Reddit fetch across {len(self.subreddits)} subreddits")

        for subreddit in self.subreddits:
            posts = self.fetch_subreddit(subreddit, keywords, time_filter='week', limit=50)

            # Deduplica
            for post in posts:
                url = post.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_posts.append(post)

            # Pausa tra subreddit per non sovraccaricare Reddit
            time.sleep(2)

        logger.info(f"Reddit: Total {len(all_posts)} unique posts")
        return all_posts
