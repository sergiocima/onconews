#!/usr/bin/env python3
"""
Script per verificare la qualità dei dati nel database
"""
import sqlite3
import sys

def check_database():
    """Verifica qualità testi nel database"""

    try:
        conn = sqlite3.connect('onconews.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("=" * 80)
        print("ANALISI DATABASE ONCONEWS")
        print("=" * 80)
        print()

        # Statistiche generali
        total = cursor.execute("SELECT COUNT(*) as count FROM news").fetchone()['count']
        with_text = cursor.execute("SELECT COUNT(*) as count FROM news WHERE full_text IS NOT NULL AND LENGTH(full_text) > 0").fetchone()['count']

        print(f"📊 STATISTICHE GENERALI")
        print(f"   Articoli totali: {total}")
        print(f"   Con full_text: {with_text}")
        print(f"   Senza full_text: {total - with_text}")
        print()

        if with_text == 0:
            print("⚠️  PROBLEMA: Nessun articolo ha il testo completo!")
            print("   Lo scraping probabilmente non è stato eseguito.")
            print()
            conn.close()
            return

        # Analisi lunghezze
        stats = cursor.execute("""
            SELECT
                AVG(LENGTH(full_text)) as media,
                MIN(LENGTH(full_text)) as minima,
                MAX(LENGTH(full_text)) as massima,
                AVG(LENGTH(description)) as media_desc
            FROM news
            WHERE full_text IS NOT NULL AND LENGTH(full_text) > 0
        """).fetchone()

        print(f"📏 LUNGHEZZA TESTI")
        print(f"   Media full_text: {int(stats['media'])} caratteri")
        print(f"   Minima: {int(stats['minima'])} caratteri")
        print(f"   Massima: {int(stats['massima'])} caratteri")
        print(f"   Media description: {int(stats['media_desc'] or 0)} caratteri")
        print()

        # Confronto description vs full_text
        print(f"🔍 CONFRONTO DESCRIPTION vs FULL_TEXT")
        same = cursor.execute("""
            SELECT COUNT(*) as count
            FROM news
            WHERE full_text IS NOT NULL
            AND description IS NOT NULL
            AND full_text = description
        """).fetchone()['count']

        similar = cursor.execute("""
            SELECT COUNT(*) as count
            FROM news
            WHERE full_text IS NOT NULL
            AND description IS NOT NULL
            AND LENGTH(full_text) - LENGTH(description) < 100
        """).fetchone()['count']

        print(f"   Articoli dove full_text = description: {same}")
        print(f"   Articoli dove differenza < 100 caratteri: {similar}")

        if same > 0 or similar > with_text * 0.5:
            print(f"   ⚠️  PROBLEMA: Lo scraping NON sta estraendo testo completo!")
            print(f"   Il campo full_text contiene solo la description di News API")
        else:
            print(f"   ✅ OK: Lo scraping sta funzionando correttamente")
        print()

        # Esempi concreti
        print(f"📄 ESEMPI DI ARTICOLI")
        print()

        articles = cursor.execute("""
            SELECT title,
                   LENGTH(description) as len_desc,
                   LENGTH(full_text) as len_full,
                   scraping_status,
                   url
            FROM news
            WHERE full_text IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 3
        """).fetchall()

        for i, art in enumerate(articles, 1):
            print(f"   {i}. {art['title'][:70]}...")
            print(f"      Description: {art['len_desc']} caratteri")
            print(f"      Full text: {art['len_full']} caratteri")
            print(f"      Status: {art['scraping_status']}")
            print(f"      Differenza: {art['len_full'] - art['len_desc']} caratteri")

            # Mostra primi 200 caratteri del full_text
            full = cursor.execute("SELECT full_text FROM news WHERE url = ?", (art['url'],)).fetchone()['full_text']
            print(f"      Inizio testo: {full[:200]}...")
            print()

        conn.close()

        print("=" * 80)

    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_database()
