#!/bin/bash
# Setup script per OncoNews su VPS

set -e

echo "=========================================="
echo "OncoNews - Setup Script"
echo "=========================================="
echo ""

# Controlla se siamo root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Non eseguire questo script come root!"
    echo "   Esegui come utente normale"
    exit 1
fi

# Controlla Python
echo "1. Verifica Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato!"
    echo "   Installalo con: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION trovato"

# Crea virtual environment
echo ""
echo "2. Creazione virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment già esistente, rimuovilo se vuoi ricrearlo"
else
    python3 -m venv venv
    echo "✓ Virtual environment creato"
fi

# Attiva virtual environment
source venv/bin/activate

# Aggiorna pip
echo ""
echo "3. Aggiornamento pip..."
pip install --upgrade pip -q

# Installa dipendenze
echo ""
echo "4. Installazione dipendenze..."
pip install -r requirements.txt -q

# Download NLTK data
echo ""
echo "5. Download NLTK data..."
python3 << END
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt', quiet=True)
print("✓ NLTK punkt downloaded")
END

# Configura .env
echo ""
echo "6. Configurazione .env..."
if [ -f ".env" ]; then
    echo "⚠️  File .env già esistente"
else
    cp .env.example .env
    echo "✓ File .env creato da .env.example"
    echo ""
    echo "⚠️  IMPORTANTE: Modifica il file .env e inserisci la tua NEWS_API_KEY!"
    echo "   nano .env"
fi

# Rendi eseguibili gli script
echo ""
echo "7. Configurazione permessi script..."
chmod +x main.py
chmod +x analyze.py
echo "✓ Permessi configurati"

# Test installazione
echo ""
echo "8. Test installazione..."
python3 << END
try:
    import requests
    import yaml
    from bs4 import BeautifulSoup
    from newspaper import Article
    from dotenv import load_dotenv
    print("✓ Tutte le dipendenze importate correttamente")
except ImportError as e:
    print(f"❌ Errore import: {e}")
    exit(1)
END

echo ""
echo "=========================================="
echo "✓ Setup completato!"
echo "=========================================="
echo ""
echo "Prossimi passi:"
echo "1. Modifica .env con la tua API key:"
echo "   nano .env"
echo ""
echo "2. (Opzionale) Personalizza le keywords in config.yaml:"
echo "   nano config.yaml"
echo ""
echo "3. Test del sistema:"
echo "   python3 main.py"
echo ""
echo "4. Analizza i dati raccolti:"
echo "   python3 analyze.py"
echo ""
echo "5. Configura esecuzione automatica giornaliera:"
echo "   crontab -e"
echo "   Aggiungi: 0 8 * * * cd $(pwd) && $(pwd)/venv/bin/python3 main.py >> onconews_cron.log 2>&1"
echo ""
