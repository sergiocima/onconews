# OncoNews - Quick Start Guide

Guida rapida per iniziare in 5 minuti.

## 🚀 Setup Locale (Test)

```bash
# 1. Vai nella directory
cd onconews

# 2. Esegui lo script di setup
./setup.sh

# 3. Configura la tua API key
nano .env
# Inserisci: NEWS_API_KEY=la_tua_chiave

# 4. Test
python3 main.py

# 5. Analizza i risultati
python3 analyze.py
```

## ☁️ Setup VPS (Produzione)

### Setup Iniziale VPS

```bash
# Connessione
ssh root@your_vps_ip

# Aggiornamento e installazione pacchetti base
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git

# Crea utente dedicato
adduser onconews
usermod -aG sudo onconews
su - onconews
```

### Deploy Applicazione

```bash
# Clone repo o carica file
cd ~
# ... carica i file nella directory ~/onconews

cd ~/onconews

# Setup automatico
./setup.sh

# Configura API key
nano .env
```

### Esecuzione Automatica

```bash
# Apri crontab
crontab -e

# Aggiungi (cambia percorsi se necessario):
0 8 * * * cd /home/onconews/onconews && /home/onconews/onconews/venv/bin/python3 main.py >> /home/onconews/onconews_cron.log 2>&1

# Salva e esci (Ctrl+X, Y, Enter in nano)
```

## 📊 Uso Quotidiano

### Verificare che tutto funzioni

```bash
# Controlla log
tail -f onconews.log

# Controlla cron log
tail -f ~/onconews_cron.log

# Statistiche database
python3 analyze.py
# Seleziona opzione 1
```

### Esportare dati per analisi

```python
from database import NewsDatabase

db = NewsDatabase('onconews.db')
articles = db.export_for_analysis()

# Usa con SBERT, pandas, etc.
for article in articles:
    print(article['title'])
    print(article['full_text'][:200])
```

### Backup Database

```bash
# Backup manuale
cp onconews.db onconews_backup_$(date +%Y%m%d).db

# Backup automatico settimanale (aggiungi a crontab)
0 3 * * 0 cp /home/onconews/onconews/onconews.db /home/onconews/backups/onconews_$(date +\%Y\%m\%d).db
```

## ⚙️ Personalizzazione

### Cambiare Keywords

```bash
nano config.yaml
```

Modifica la sezione `keywords:` con i tuoi termini.

### Cambiare Frequenza

Modifica il crontab:
- `0 8 * * *` = Ogni giorno alle 8:00
- `0 */6 * * *` = Ogni 6 ore
- `0 9,18 * * *` = Alle 9:00 e 18:00

## 🔍 Troubleshooting Veloce

### "NEWS_API_KEY not found"
```bash
cat .env
# Verifica che contenga: NEWS_API_KEY=...
```

### Script non parte da cron
```bash
# Verifica percorsi assoluti nel crontab
which python3
pwd
# Usa percorsi completi nel crontab
```

### Database locked
```bash
# Verifica processi attivi
ps aux | grep main.py
# Se necessario, termina
pkill -f main.py
```

### Out of memory
```bash
# Aggiungi swap (su VPS piccole)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Rendi permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 📈 VPS Consigliate

### Budget ~5€/mese
- **Hetzner CX22**: 2 vCPU, 4GB RAM, 40GB SSD - 5,83€/mese ⭐
- **Contabo VPS S**: 4 vCPU, 8GB RAM, 50GB SSD - 5€/mese

### Budget ~10€/mese
- **DigitalOcean Basic**: 2GB RAM, 1 vCPU, 50GB SSD - $12/mese
- **Hetzner CX32**: 4 vCPU, 8GB RAM, 80GB SSD - 11,06€/mese

## 📚 Documentazione Completa

Vedi `README.md` per la documentazione dettagliata.

## 🆘 Support

- News API: https://newsapi.org/docs
- Python: https://docs.python.org/3/
- SQLite: https://www.sqlite.org/docs.html
