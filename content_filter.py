#!/usr/bin/env python3
"""
OncoNews - Content Filter
Sistema di filtri intelligente per escludere articoli non pertinenti PRIMA dello scraping
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime


class ContentFilter:
    """
    Filtra articoli in base a keyword positive e negative
    applicato PRIMA dello scraping per risparmiare risorse
    """

    def __init__(self, config: dict):
        """
        Inizializza il filtro con la configurazione

        Args:
            config: Dizionario di configurazione (da config.yaml)
        """
        self.logger = logging.getLogger(__name__)

        # Configurazione filtro
        filter_config = config.get('content_filter', {})
        self.enabled = filter_config.get('enabled', True)

        # Keyword da escludere (se presenti → SCARTA)
        self.excluded_keywords = [
            kw.lower() for kw in filter_config.get('excluded_keywords', [])
        ]

        # Keyword richieste (almeno una deve essere presente → ACCETTA)
        self.required_keywords = [
            kw.lower() for kw in filter_config.get('required_keywords', [])
        ]

        # Logging articoli filtrati
        self.log_filtered = filter_config.get('log_filtered', True)
        self.log_file = filter_config.get('log_file', 'filtered_articles.log')

        self.logger.info(f"ContentFilter initialized: enabled={self.enabled}")
        self.logger.info(f"  - Excluded keywords: {len(self.excluded_keywords)}")
        self.logger.info(f"  - Required keywords: {len(self.required_keywords)}")

    def should_keep_article(self, article: dict) -> tuple[bool, Optional[str]]:
        """
        Determina se un articolo dovrebbe essere mantenuto o scartato

        Args:
            article: Dizionario con i dati dell'articolo (deve avere 'title' e 'description')

        Returns:
            (bool, str): (True se da mantenere, False se da scartare, motivo del filtro)
        """
        if not self.enabled:
            return True, None

        title = (article.get('title') or '').lower()
        description = (article.get('description') or '').lower()
        combined_text = f"{title} {description}"

        # FILTRO 1: Controlla keyword NEGATIVE
        for excluded_kw in self.excluded_keywords:
            if excluded_kw in combined_text:
                reason = f"Excluded keyword found: '{excluded_kw}'"
                return False, reason

        # FILTRO 2: Controlla keyword POSITIVE (se configurate)
        if self.required_keywords:
            has_required = False
            for required_kw in self.required_keywords:
                if required_kw in combined_text:
                    has_required = True
                    break

            if not has_required:
                reason = "No required keyword found"
                return False, reason

        # Articolo valido!
        return True, None

    def filter_articles(self, articles: List[dict]) -> tuple[List[dict], List[dict]]:
        """
        Filtra una lista di articoli

        Args:
            articles: Lista di dizionari con i dati degli articoli

        Returns:
            (accepted, rejected): Tuple con lista articoli accettati e rifiutati
        """
        if not self.enabled:
            return articles, []

        accepted = []
        rejected = []

        for article in articles:
            keep, reason = self.should_keep_article(article)

            if keep:
                accepted.append(article)
            else:
                rejected.append({
                    'article': article,
                    'reason': reason
                })

        # Log statistiche
        self.logger.info(f"Content Filter Results:")
        self.logger.info(f"  - Total articles: {len(articles)}")
        self.logger.info(f"  - Accepted: {len(accepted)}")
        self.logger.info(f"  - Rejected: {len(rejected)}")

        # Log articoli rifiutati in dettaglio
        if rejected and self.log_filtered:
            self._log_rejected_articles(rejected)

        return accepted, rejected

    def _log_rejected_articles(self, rejected: List[dict]):
        """
        Scrive un log dettagliato degli articoli rifiutati

        Args:
            rejected: Lista di articoli rifiutati con motivi
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"Filter Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Rejected: {len(rejected)} articles\n")
                f.write(f"{'=' * 80}\n\n")

                for item in rejected:
                    article = item['article']
                    reason = item['reason']

                    f.write(f"TITLE: {article.get('title', 'N/A')}\n")
                    f.write(f"SOURCE: {article.get('source', {}).get('name', 'N/A')}\n")
                    f.write(f"URL: {article.get('url', 'N/A')}\n")
                    f.write(f"REASON: {reason}\n")
                    f.write(f"DESCRIPTION: {article.get('description', 'N/A')[:200]}\n")
                    f.write(f"{'-' * 80}\n\n")

        except Exception as e:
            self.logger.error(f"Error writing filtered articles log: {e}")

    def get_statistics(self) -> dict:
        """
        Restituisce statistiche sul filtro

        Returns:
            dict: Statistiche
        """
        return {
            'enabled': self.enabled,
            'excluded_keywords_count': len(self.excluded_keywords),
            'required_keywords_count': len(self.required_keywords),
            'log_filtered': self.log_filtered
        }
