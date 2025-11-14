#!/bin/bash
# Script di deploy automatico OncoNews su VPS OVH
# Uso: ./deploy_ovh.sh

set -e  # Esci in caso di errore

echo "=================================================="
echo "  ONCONEWS - Deploy Automatico su VPS OVH"
echo "=================================================="
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi colorati
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# 1. Verifica dipendenze
print_info "Verifico dipendenze di sistema..."

if ! command -v python3 &> /dev/null; then
    print_error "Python3 non trovato. Installazione in corso..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
    print_success "Python3 installato"
else
    print_success "Python3 già installato: $(python3 --version)"
fi

# 2. Verifica se siamo nella directory giusta
if [ ! -f "main.py" ]; then
    print_error "Errore: esegui questo script dalla directory onconews!"
    exit 1
fi
print_success "Directory corretta"

# 3. Crea virtual environment
print_info "Creazione ambiente virtuale Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment creato"
else
    print_success "Virtual environment già esistente"
fi

# 4. Attiva venv e installa dipendenze
print_info "Installazione dipendenze Python..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_success "Dipendenze installate"

# 5. Download NLTK data
print_info "Download dati NLTK..."
python3 -c "import nltk; nltk.download('punkt', quiet=True)" 2>/dev/null
print_success "Dati NLTK scaricati"

# 6. Verifica file .env
if [ ! -f ".env" ]; then
    print_error "File .env non trovato!"
    echo ""
    echo "Crea il file .env con il seguente contenuto:"
    echo "NEWS_API_KEY=la_tua_chiave_api"
    echo ""
    read -p "Inserisci la tua News API key: " api_key
    echo "NEWS_API_KEY=$api_key" > .env
    print_success "File .env creato"
else
    print_success "File .env trovato"
fi

# 7. Test del sistema
print_info "Test del sistema..."
echo ""
python3 main.py
echo ""

# 8. Configurazione cron
print_info "Vuoi configurare l'esecuzione automatica giornaliera? (y/n)"
read -p "> " setup_cron

if [ "$setup_cron" = "y" ] || [ "$setup_cron" = "Y" ]; then
    CURRENT_DIR=$(pwd)
    PYTHON_PATH="$CURRENT_DIR/venv/bin/python3"
    LOG_PATH="$HOME/onconews_cron.log"

    CRON_CMD="0 8 * * * cd $CURRENT_DIR && $PYTHON_PATH main.py >> $LOG_PATH 2>&1"

    # Verifica se cron è già configurato
    if crontab -l 2>/dev/null | grep -q "main.py"; then
        print_info "Cron già configurato, lo aggiorno..."
        (crontab -l 2>/dev/null | grep -v "main.py"; echo "$CRON_CMD") | crontab -
    else
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    fi

    print_success "Cron configurato: esecuzione giornaliera alle 8:00"
    echo ""
    echo "Log del cron: $LOG_PATH"
    echo "Verifica cron con: crontab -l"
fi

# 9. Riepilogo
echo ""
echo "=================================================="
echo "  SETUP COMPLETATO CON SUCCESSO!"
echo "=================================================="
echo ""
echo "📁 Directory progetto: $(pwd)"
echo "🐍 Python: $PYTHON_PATH"
echo "📊 Database: $(pwd)/onconews.db"
echo "📝 Log: $(pwd)/onconews.log"
echo ""
echo "Comandi utili:"
echo "  - Attiva venv:  source venv/bin/activate"
echo "  - Esegui:       python3 main.py"
echo "  - Analisi:      python3 analyze.py"
echo "  - Log:          tail -f onconews.log"
echo "  - Cron log:     tail -f ~/onconews_cron.log"
echo ""
print_success "Tutto pronto! 🚀"
