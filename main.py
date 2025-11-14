#!/usr/bin/env python3
"""
OncoNews - Sistema di raccolta notizie su terapie antitumorali
Script principale per il fetch e scraping giornaliero
"""
import os
import sys
import yaml
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from database import NewsDatabase
from news_fetcher import NewsFetcher
from content_scraper import ContentScraper
from content_filter import ContentFilter
from google_news_fetcher import GoogleNewsFetcher
from reddit_fetcher import RedditFetcher


def setup_logging(config: dict):
    """Configura il sistema di logging"""
    log_level = getattr(logging, config['logging']['level'])
    log_file = config['logging']['file']

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_path: str = 'config.yaml') -> dict:
    """Carica la configurazione dal file YAML"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def fetch_news(api_key: str, config: dict, db: NewsDatabase, days_back: int = 1) -> int:
    """
    Recupera le notizie da TUTTE le fonti: News API, Google News, Reddit

    Args:
        api_key: Chiave API News API
        config: Configurazione
        db: Database instance
        days_back: Quanti giorni indietro cercare

    Returns:
        Numero di nuovi articoli inseriti
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("FASE 1: RECUPERO NOTIZIE DA TUTTE LE FONTI")
    logger.info("=" * 60)

    keywords = config['keywords']
    logger.info(f"Keywords configured: {len(keywords)}")

    all_articles = []

    # FONTE 1: News API
    try:
        logger.info("\n>>> Fonte 1/3: News API")
        fetcher = NewsFetcher(api_key, config)
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        newsapi_articles = fetcher.fetch_all_keywords(keywords, from_date=from_date)
        logger.info(f"News API: {len(newsapi_articles)} articles")
        all_articles.extend(newsapi_articles)
    except Exception as e:
        logger.error(f"News API failed: {e}")

    # FONTE 2: Google News
    try:
        logger.info("\n>>> Fonte 2/3: Google News RSS")
        google_fetcher = GoogleNewsFetcher(config)
        google_articles = google_fetcher.fetch_all_keywords(keywords, max_per_keyword=30)
        logger.info(f"Google News: {len(google_articles)} articles")
        all_articles.extend(google_articles)
    except Exception as e:
        logger.error(f"Google News failed: {e}")

    # FONTE 3: Reddit
    try:
        logger.info("\n>>> Fonte 3/3: Reddit")
        reddit_fetcher = RedditFetcher(config)
        reddit_posts = reddit_fetcher.fetch_all_subreddits(keywords)
        logger.info(f"Reddit: {len(reddit_posts)} posts")
        all_articles.extend(reddit_posts)
    except Exception as e:
        logger.error(f"Reddit failed: {e}")

    logger.info(f"\nTotal articles from all sources: {len(all_articles)}")

    # FILTRO INTELLIGENTE: Applica filtri prima dello scraping
    content_filter = ContentFilter(config)
    filtered_articles, rejected_articles = content_filter.filter_articles(all_articles)

    logger.info(f"After filtering: {len(filtered_articles)} articles kept, {len(rejected_articles)} rejected")

    # Inserisci nel database solo articoli filtrati (deduplica per URL)
    new_count = 0
    for article in filtered_articles:
        # Usa normalize_article se esiste il metodo, altrimenti usa l'articolo così com'è
        if db.insert_article(article):
            new_count += 1

    logger.info(f"New articles inserted into database: {new_count}")
    logger.info(f"Duplicates skipped: {len(filtered_articles) - new_count}")

    return new_count


def scrape_content(config: dict, db: NewsDatabase, max_articles: int = 100) -> int:
    """
    Scrape il testo completo degli articoli

    Args:
        config: Configurazione
        db: Database instance
        max_articles: Massimo numero di articoli da processare

    Returns:
        Numero di articoli processati con successo
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("FASE 2: SCRAPING TESTO COMPLETO")
    logger.info("=" * 60)

    scraper = ContentScraper(config)

    # Ottieni articoli da scrapare
    articles = db.get_articles_to_scrape(limit=max_articles)
    logger.info(f"Articles pending scraping: {len(articles)}")

    if not articles:
        logger.info("No articles to scrape")
        return 0

    # Scrape batch
    success_count = 0
    for i, article in enumerate(articles, 1):
        url = article['url']
        title = article['title']

        logger.info(f"Processing {i}/{len(articles)}: {title[:60]}...")

        result = scraper.scrape_article(url, title)

        if result['success']:
            db.update_full_text(url, result['text'], status='completed')
            success_count += 1
        else:
            error_msg = result.get('error', 'Unknown error')
            db.update_scraping_error(url, error_msg)
            logger.warning(f"  Failed: {error_msg}")

        # Pausa tra gli scraping per evitare rate limiting
        if i < len(articles):
            import time
            time.sleep(2)

    logger.info(f"Scraping completed: {success_count}/{len(articles)} successful")
    return success_count


def show_statistics(db: NewsDatabase):
    """Mostra statistiche sul database"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("STATISTICHE DATABASE")
    logger.info("=" * 60)

    stats = db.get_statistics()

    logger.info(f"Total articles: {stats['total_articles']}")
    logger.info(f"  - With full text: {stats['scraped_articles']}")
    logger.info(f"  - Pending scraping: {stats['pending_scraping']}")
    logger.info(f"  - Failed scraping: {stats['failed_scraping']}")

    if stats['top_sources']:
        logger.info("\nTop sources:")
        for source, count in list(stats['top_sources'].items())[:5]:
            logger.info(f"  - {source}: {count}")


def main():
    """Funzione principale"""
    # Carica variabili d'ambiente
    load_dotenv()

    # Carica configurazione
    config = load_config('config.yaml')
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("ONCONEWS - SISTEMA RACCOLTA NOTIZIE TERAPIE ANTITUMORALI")
    logger.info("=" * 60)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verifica API key
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        logger.error("ERROR: NEWS_API_KEY not found in environment variables")
        logger.error("Please create a .env file with: NEWS_API_KEY=your_api_key")
        sys.exit(1)

    # Valida API key
    logger.info("Validating News API key...")
    if not NewsFetcher.validate_api_key(api_key):
        logger.error("ERROR: Invalid News API key")
        sys.exit(1)
    logger.info("API key validated successfully")

    # Inizializza database
    db_path = config['database']['path']
    logger.info(f"Database: {db_path}")
    db = NewsDatabase(db_path)

    try:
        # Fase 1: Fetch notizie
        new_articles = fetch_news(api_key, config, db, days_back=7)

        # Fase 2: Scrape testo completo
        scraped_articles = scrape_content(config, db, max_articles=100)

        # Mostra statistiche
        show_statistics(db)

        logger.info("=" * 60)
        logger.info("COMPLETATO CON SUCCESSO")
        logger.info(f"  - Nuovi articoli trovati: {new_articles}")
        logger.info(f"  - Articoli scrapati: {scraped_articles}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"ERRORE CRITICO: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
