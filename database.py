"""
Gestione database per OncoNews (supporta SQLite e PostgreSQL)
"""
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Rileva automaticamente quale database usare
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    logger.info("Using PostgreSQL database")
else:
    logger.info("Using SQLite database")


class NewsDatabase:
    """Gestisce il database per le notizie oncologiche (SQLite o PostgreSQL)"""

    def __init__(self, db_path: str = "onconews.db"):
        self.db_path = db_path
        self.use_postgres = USE_POSTGRES
        self.database_url = DATABASE_URL

        if not self.use_postgres:
            self.init_database()

    def get_connection(self):
        """Ottiene una connessione al database (SQLite o PostgreSQL)"""
        if self.use_postgres:
            return psycopg2.connect(self.database_url)
        else:
            return sqlite3.connect(self.db_path)

    def init_database(self):
        """Inizializza il database creando le tabelle necessarie"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            # Schema PostgreSQL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    source_name TEXT,
                    author TEXT,
                    published_at TIMESTAMP,
                    description TEXT,
                    full_text TEXT,
                    keywords_matched TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scraping_status TEXT DEFAULT 'pending',
                    scraping_error TEXT,
                    language TEXT DEFAULT 'it'
                )
            """)
        else:
            # Schema SQLite
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    source_name TEXT,
                    author TEXT,
                    published_at TIMESTAMP,
                    description TEXT,
                    full_text TEXT,
                    keywords_matched TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scraping_status TEXT DEFAULT 'pending',
                    scraping_error TEXT,
                    language TEXT DEFAULT 'it'
                )
            """)

        # Indici per ottimizzare le query (compatibili con entrambi)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_published_at
            ON news(published_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_name
            ON news(source_name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scraping_status
            ON news(scraping_status)
        """)

        conn.commit()
        conn.close()

        db_type = "PostgreSQL" if self.use_postgres else "SQLite"
        logger.info(f"Database inizializzato: {db_type}")

    def article_exists(self, url: str) -> bool:
        """Verifica se un articolo esiste già nel database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            cursor.execute("SELECT COUNT(*) FROM news WHERE url = %s", (url,))
        else:
            cursor.execute("SELECT COUNT(*) FROM news WHERE url = ?", (url,))

        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def insert_article(self, article_data: Dict) -> bool:
        """
        Inserisce un nuovo articolo nel database

        Returns:
            True se inserito, False se già esistente o errore
        """
        if self.article_exists(article_data['url']):
            logger.debug(f"Articolo già esistente: {article_data['url']}")
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.use_postgres:
                cursor.execute("""
                    INSERT INTO news (
                        url, title, source_name, author, published_at,
                        description, keywords_matched, language
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    article_data['url'],
                    article_data['title'],
                    article_data.get('source_name'),
                    article_data.get('author'),
                    article_data.get('published_at'),
                    article_data.get('description'),
                    article_data.get('keywords_matched'),
                    article_data.get('language', 'it')
                ))
            else:
                cursor.execute("""
                    INSERT INTO news (
                        url, title, source_name, author, published_at,
                        description, keywords_matched, language
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data['url'],
                    article_data['title'],
                    article_data.get('source_name'),
                    article_data.get('author'),
                    article_data.get('published_at'),
                    article_data.get('description'),
                    article_data.get('keywords_matched'),
                    article_data.get('language', 'it')
                ))

            conn.commit()
            logger.info(f"Articolo inserito: {article_data['title'][:50]}...")
            return True
        except (psycopg2.IntegrityError if self.use_postgres else sqlite3.IntegrityError):
            logger.debug(f"Articolo duplicato (IntegrityError): {article_data['url']}")
            return False
        except Exception as e:
            logger.error(f"Errore inserimento articolo: {e}")
            return False
        finally:
            conn.close()

    def update_full_text(self, url: str, full_text: str, status: str = 'completed'):
        """Aggiorna il testo completo di un articolo dopo lo scraping"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.use_postgres:
                cursor.execute("""
                    UPDATE news
                    SET full_text = %s, scraping_status = %s
                    WHERE url = %s
                """, (full_text, status, url))
            else:
                cursor.execute("""
                    UPDATE news
                    SET full_text = ?, scraping_status = ?
                    WHERE url = ?
                """, (full_text, status, url))

            conn.commit()
            logger.debug(f"Testo aggiornato per: {url}")
        except Exception as e:
            logger.error(f"Errore aggiornamento testo: {e}")
        finally:
            conn.close()

    def update_scraping_error(self, url: str, error: str):
        """Registra un errore durante lo scraping"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.use_postgres:
                cursor.execute("""
                    UPDATE news
                    SET scraping_status = 'failed', scraping_error = %s
                    WHERE url = %s
                """, (error, url))
            else:
                cursor.execute("""
                    UPDATE news
                    SET scraping_status = 'failed', scraping_error = ?
                    WHERE url = ?
                """, (error, url))

            conn.commit()
        except Exception as e:
            logger.error(f"Errore registrazione errore scraping: {e}")
        finally:
            conn.close()

    def get_articles_to_scrape(self, limit: int = 100) -> List[Dict]:
        """Ottiene gli articoli che non hanno ancora il testo completo"""
        conn = self.get_connection()

        if self.use_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, url, title, source_name
                FROM news
                WHERE scraping_status = 'pending'
                ORDER BY published_at DESC
                LIMIT %s
            """, (limit,))
            articles = [dict(row) for row in cursor.fetchall()]
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, url, title, source_name
                FROM news
                WHERE scraping_status = 'pending'
                ORDER BY published_at DESC
                LIMIT ?
            """, (limit,))
            articles = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return articles

    def get_statistics(self) -> Dict:
        """Ottiene statistiche sul database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}

        # Totale articoli
        cursor.execute("SELECT COUNT(*) FROM news")
        stats['total_articles'] = cursor.fetchone()[0]

        # Articoli con testo completo
        cursor.execute("SELECT COUNT(*) FROM news WHERE scraping_status = 'completed'")
        stats['scraped_articles'] = cursor.fetchone()[0]

        # Articoli in attesa di scraping
        cursor.execute("SELECT COUNT(*) FROM news WHERE scraping_status = 'pending'")
        stats['pending_scraping'] = cursor.fetchone()[0]

        # Articoli con errore
        cursor.execute("SELECT COUNT(*) FROM news WHERE scraping_status = 'failed'")
        stats['failed_scraping'] = cursor.fetchone()[0]

        # Fonti principali
        cursor.execute("""
            SELECT source_name, COUNT(*) as count
            FROM news
            GROUP BY source_name
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_sources'] = dict(cursor.fetchall())

        conn.close()
        return stats

    def export_for_analysis(self, output_format: str = 'list') -> List[Dict]:
        """
        Esporta tutti gli articoli con testo completo per l'analisi

        Args:
            output_format: 'list' per lista di dict, 'dataframe' per pandas

        Returns:
            Lista di dizionari con i dati degli articoli
        """
        conn = self.get_connection()

        if self.use_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, url, title, source_name, author, published_at,
                description, full_text, keywords_matched, fetched_at
            FROM news
            WHERE scraping_status = 'completed' AND full_text IS NOT NULL
            ORDER BY published_at DESC
        """)

        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return articles
