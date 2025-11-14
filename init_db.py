#!/usr/bin/env python3
"""
Script di inizializzazione database per OncoNews
Crea le tabelle necessarie nel database PostgreSQL su Render
"""
import os
import sys
from database import NewsDatabase

def main():
    """Inizializza il database"""
    print("=" * 60)
    print("ONCONEWS - INIZIALIZZAZIONE DATABASE")
    print("=" * 60)

    # Verifica presenza DATABASE_URL
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ ERRORE: DATABASE_URL non trovata")
        print("Assicurati di aver configurato il database PostgreSQL su Render")
        sys.exit(1)

    print("✓ DATABASE_URL trovata")
    print(f"  Database: PostgreSQL")
    print()

    try:
        # Inizializza il database
        print("Creazione tabelle...")
        db = NewsDatabase()
        db.init_database()

        print()
        print("=" * 60)
        print("✅ DATABASE INIZIALIZZATO CON SUCCESSO")
        print("=" * 60)
        print()
        print("Tabelle create:")
        print("  - news (articoli)")
        print("  - Indici per ottimizzazione query")
        print()
        print("Il database è pronto per ricevere dati.")

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRORE DURANTE L'INIZIALIZZAZIONE")
        print("=" * 60)
        print(f"Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
