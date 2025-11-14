#!/usr/bin/env python3
"""
Script di utilità per analizzare i dati raccolti
"""
import sqlite3
from datetime import datetime
from database import NewsDatabase


def print_separator():
    print("=" * 70)


def show_statistics():
    """Mostra statistiche dettagliate"""
    db = NewsDatabase('onconews.db')
    stats = db.get_statistics()

    print_separator()
    print("STATISTICHE DATABASE ONCONEWS")
    print_separator()
    print(f"\nTotale articoli: {stats['total_articles']}")
    print(f"  - Con testo completo: {stats['scraped_articles']}")
    print(f"  - In attesa di scraping: {stats['pending_scraping']}")
    print(f"  - Scraping fallito: {stats['failed_scraping']}")

    if stats['top_sources']:
        print("\nTop 10 fonti:")
        for source, count in stats['top_sources'].items():
            print(f"  {count:3d} | {source}")


def show_recent_articles(limit=10):
    """Mostra gli ultimi articoli raccolti"""
    conn = sqlite3.connect('onconews.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, source_name, published_at, scraping_status,
               LENGTH(full_text) as text_length
        FROM news
        ORDER BY published_at DESC
        LIMIT ?
    """, (limit,))

    print_separator()
    print(f"ULTIMI {limit} ARTICOLI")
    print_separator()

    for row in cursor.fetchall():
        status_icon = "✓" if row['scraping_status'] == 'completed' else "○"
        text_info = f"{row['text_length']} char" if row['text_length'] else "no text"
        date = row['published_at'][:10] if row['published_at'] else "N/A"

        print(f"\n{status_icon} [{date}] {row['source_name']}")
        print(f"  {row['title'][:65]}...")
        print(f"  Status: {row['scraping_status']} | {text_info}")

    conn.close()


def search_by_keyword(keyword):
    """Cerca articoli per keyword nel titolo o descrizione"""
    conn = sqlite3.connect('onconews.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, source_name, published_at, url
        FROM news
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY published_at DESC
        LIMIT 20
    """, (f'%{keyword}%', f'%{keyword}%'))

    results = cursor.fetchall()

    print_separator()
    print(f"RICERCA: '{keyword}' - {len(results)} risultati")
    print_separator()

    for row in results:
        date = row['published_at'][:10] if row['published_at'] else "N/A"
        print(f"\n[{date}] {row['source_name']}")
        print(f"  {row['title']}")
        print(f"  {row['url']}")

    conn.close()


def export_to_csv(output_file='onconews_export.csv'):
    """Esporta tutti gli articoli in CSV"""
    import csv

    db = NewsDatabase('onconews.db')
    articles = db.export_for_analysis()

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if not articles:
            print("Nessun articolo da esportare")
            return

        writer = csv.DictWriter(f, fieldnames=articles[0].keys())
        writer.writeheader()
        writer.writerows(articles)

    print(f"\n✓ Esportati {len(articles)} articoli in: {output_file}")


def show_failed_scraping():
    """Mostra articoli con scraping fallito"""
    conn = sqlite3.connect('onconews.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, url, scraping_error
        FROM news
        WHERE scraping_status = 'failed'
        ORDER BY fetched_at DESC
        LIMIT 20
    """)

    results = cursor.fetchall()

    print_separator()
    print(f"SCRAPING FALLITI - {len(results)} articoli")
    print_separator()

    for row in results:
        print(f"\n✗ {row['title'][:60]}...")
        print(f"  URL: {row['url']}")
        print(f"  Error: {row['scraping_error']}")

    conn.close()


def interactive_menu():
    """Menu interattivo"""
    while True:
        print_separator()
        print("ONCONEWS - ANALISI DATI")
        print_separator()
        print("\n1. Mostra statistiche")
        print("2. Ultimi articoli")
        print("3. Cerca per keyword")
        print("4. Esporta in CSV")
        print("5. Scraping falliti")
        print("0. Esci")

        choice = input("\nScelta: ").strip()

        if choice == '1':
            show_statistics()
        elif choice == '2':
            limit = input("Quanti articoli? [10]: ").strip()
            limit = int(limit) if limit else 10
            show_recent_articles(limit)
        elif choice == '3':
            keyword = input("Keyword da cercare: ").strip()
            if keyword:
                search_by_keyword(keyword)
        elif choice == '4':
            filename = input("Nome file [onconews_export.csv]: ").strip()
            filename = filename if filename else 'onconews_export.csv'
            export_to_csv(filename)
        elif choice == '5':
            show_failed_scraping()
        elif choice == '0':
            print("\nArrivederci!")
            break
        else:
            print("\nScelta non valida")

        input("\nPremi ENTER per continuare...")


if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterrotto dall'utente")
    except FileNotFoundError:
        print("\nERRORE: Database onconews.db non trovato!")
        print("Esegui prima main.py per creare il database.")
