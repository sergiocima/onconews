# OncoNews - Sistema di Raccolta Notizie Terapie Antitumorali

Sistema automatizzato per il recupero e l'analisi di notizie riguardanti nuove terapie antitumorali da fonti italiane.

## 📋 Caratteristiche

- ✅ Raccolta automatica giornaliera da News API
- ✅ Estrazione testo completo dagli articoli
- ✅ Keywords configurabili
- ✅ Database SQLite per storage efficiente
- ✅ Logging completo delle operazioni
- ✅ Pronto per analisi con SBERT

## 🖥️ Requisiti VPS Consigliati

### Configurazione Raccomandata

**Hetzner Cloud CX22** - 5,83€/mese
- 2 vCPU
- 4GB RAM
- 40GB SSD
- Traffico illimitato
- Ubuntu 22.04 LTS

### Configurazione Minima

- 1 vCPU
- 2GB RAM
- 20GB storage
- Sistema operativo: Ubuntu 20.04+ o Debian 11+

## 🚀 Setup su VPS

### 1. Connessione alla VPS

```bash
ssh root@your_vps_ip
```

### 2. Aggiornamento Sistema

```bash
apt update && apt upgrade -y
```

### 3. Installazione Python e Dipendenze

```bash
# Installa Python 3.10+
apt install -y python3 python3-pip python3-venv git

# Verifica versione Python
python3 --version
```

### 4. Creazione Utente (Sicurezza)

```bash
# Crea utente dedicato
adduser onconews
usermod -aG sudo onconews

# Passa al nuovo utente
su - onconews
```

### 5. Clone del Repository

```bash
# Se hai git configurato
cd ~
git clone <your_repo_url>
cd sbert/onconews

# Oppure carica i file manualmente via SFTP
```

### 6. Setup Ambiente Python

```bash
# Crea virtual environment
python3 -m venv venv

# Attiva virtual environment
source venv/bin/activate

# Installa dipendenze
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data (richiesto da newspaper3k)
python3 -c "import nltk; nltk.download('punkt')"
```

### 7. Configurazione API Key

```bash
# Copia il file .env.example
cp .env.example .env

# Modifica con il tuo editor preferito
nano .env
```

Inserisci la tua chiave API:
```
NEWS_API_KEY=la_tua_chiave_api_qui
```

**Ottieni la tua chiave gratis:** https://newsapi.org/register

### 8. Test del Sistema

```bash
# Test manuale
python3 main.py
```

Il sistema dovrebbe:
1. Validare la chiave API
2. Recuperare notizie dalle keywords configurate
3. Fare scraping del testo completo
4. Salvare tutto nel database `onconews.db`
5. Mostrare statistiche finali

### 9. Configurazione Esecuzione Automatica (Cron)

```bash
# Apri crontab
crontab -e

# Aggiungi questa linea per esecuzione giornaliera alle 8:00
0 8 * * * cd /home/onconews/sbert/onconews && /home/onconews/sbert/onconews/venv/bin/python3 main.py >> /home/onconews/onconews_cron.log 2>&1
```

**Nota:** Modifica i percorsi in base alla tua installazione.

#### Altre Schedulazioni Possibili

```bash
# Ogni 6 ore
0 */6 * * * cd /path/to/onconews && venv/bin/python3 main.py

# Ogni giorno alle 9:00 e 18:00
0 9,18 * * * cd /path/to/onconews && venv/bin/python3 main.py

# Ogni lunedì alle 10:00
0 10 * * 1 cd /path/to/onconews && venv/bin/python3 main.py
```

### 10. Monitoraggio e Manutenzione

```bash
# Visualizza log in tempo reale
tail -f onconews.log

# Visualizza log cron
tail -f ~/onconews_cron.log

# Verifica database
sqlite3 onconews.db "SELECT COUNT(*) FROM news;"

# Backup database
cp onconews.db onconews_backup_$(date +%Y%m%d).db
```

## 📊 Struttura Database

```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source_name TEXT,
    author TEXT,
    published_at TIMESTAMP,
    description TEXT,
    full_text TEXT,
    keywords_matched TEXT,
    fetched_at TIMESTAMP,
    scraping_status TEXT,
    scraping_error TEXT,
    language TEXT
);
```

## ⚙️ Configurazione

### Modificare Keywords

Modifica il file `config.yaml`:

```yaml
keywords:
  - "immunoterapia"
  - "CAR-T"
  - "tumore polmone"
  # Aggiungi le tue keywords qui
```

### Escludere Domini

```yaml
excluded_domains:
  - "spam-site.com"
  - "unreliable-source.com"
```

### Parametri Scraping

```yaml
scraping:
  timeout: 30  # Timeout in secondi
  max_retries: 3  # Numero di tentativi
```

## 🔍 Utilizzo dei Dati

### Esportare per Analisi

```python
from database import NewsDatabase

db = NewsDatabase('onconews.db')
articles = db.export_for_analysis()

# Ora puoi usare i dati con SBERT, pandas, etc.
for article in articles:
    print(f"{article['title']}: {len(article['full_text'])} caratteri")
```

### Statistiche

```python
stats = db.get_statistics()
print(f"Totale articoli: {stats['total_articles']}")
print(f"Con testo completo: {stats['scraped_articles']}")
```

## 🛡️ Sicurezza VPS

### Configurazione Firewall

```bash
# Abilita UFW
sudo ufw allow OpenSSH
sudo ufw enable

# Se serve accesso web (per future dashboard)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Backup Automatico

```bash
# Aggiungi a crontab backup settimanale
0 3 * * 0 cp /home/onconews/sbert/onconews/onconews.db /home/onconews/backups/onconews_$(date +\%Y\%m\%d).db
```

### Aggiornamenti Automatici

```bash
# Installa aggiornamenti automatici
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## 📈 Limiti News API

### Piano Gratuito
- 100 richieste/giorno
- Delay di 24h sulle notizie
- Massimo 100 risultati per richiesta

### Raccomandazioni
- Con ~20 keywords configurate = ~20 richieste/giorno
- Ben sotto il limite del piano gratuito
- Ideale per raccolta giornaliera

## 🐛 Troubleshooting

### Errore: "NEWS_API_KEY not found"
```bash
# Verifica che .env esista e contenga la chiave
cat .env
```

### Errore durante lo scraping
```bash
# Verifica connettività
curl -I https://www.google.com

# Alcuni siti potrebbero bloccare lo scraping
# Verifica i log per vedere quali siti falliscono
grep "Failed:" onconews.log
```

### Database locked
```bash
# Assicurati che non ci siano processi multipli
ps aux | grep main.py

# In caso, ferma il processo
pkill -f main.py
```

### Out of Memory
```bash
# Se la VPS ha poca RAM, crea swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 Support

Per problemi con:
- **News API**: https://newsapi.org/docs
- **VPS Hetzner**: https://docs.hetzner.com/

## 📝 Prossimi Passi

Dopo aver raccolto dati per alcuni giorni, potrai:
1. Implementare analisi di affidabilità con SBERT
2. Creare dashboard di visualizzazione
3. Impostare alert per notizie rilevanti
4. Fare analisi di sentiment e topic modeling

## 📄 Licenza

Uso personale. Rispetta i Terms of Service di News API e le politiche di scraping dei siti web.
