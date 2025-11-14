#!/usr/bin/env python3
"""
Test scraping per articolo specifico
"""
from newspaper import Article
import sys

url = "https://www.hwupgrade.it/news/scienza-tecnologia/terapia-genica-one-shot-abbatte-colesterolo-e-trigliceridi-prima-sperimentazione-umana-riuscita_146091.html"

print(f"Testing scraping for: {url}\n")

try:
    article = Article(url)
    article.download()
    article.parse()

    print(f"✓ Download successful")
    print(f"Title: {article.title}")
    print(f"Authors: {article.authors}")
    print(f"Publish date: {article.publish_date}")
    print(f"Text length: {len(article.text)} characters")
    print(f"\nFirst 500 characters of text:")
    print("=" * 60)
    print(article.text[:500])
    print("=" * 60)
    print(f"\nLast 500 characters of text:")
    print("=" * 60)
    print(article.text[-500:])
    print("=" * 60)

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
