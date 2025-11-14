# 🚀 Deploy OncoNews su Render.com

Guida completa per deployare OncoNews su **Render.com** con PostgreSQL.

---

## 📋 Cosa Verrà Deployato

### 1. **Web Service** - Visualizzatore Web
- Flask app per visualizzare articoli
- Sempre online 24/7
- URL pubblico accessibile da browser
- **Piano**: Free (750h/mese)

### 2. **Cron Job** - Raccolta Notizie
- Esecuzione automatica giornaliera alle 8:00 UTC
- Raccoglie notizie da News API, Google News, Reddit
- Salva nel database PostgreSQL
- **Piano**: Free

### 3. **PostgreSQL Database**
- Database gestito e automatico
- Backup automatici
- 1GB storage
- **Piano**: Free per 90 giorni, poi $7/mese

---

## 🎯 Prerequisiti

1. ✅ Account su [Render.com](https://render.com) (gratuito)
2. ✅ Repository Git (GitHub, GitLab, o Bitbucket)
3. ✅ News API Key da [NewsAPI.org](https://newsapi.org/register) (gratis)

---

## 📦 Metodo 1: Deploy Automatico con Blueprint (CONSIGLIATO)

### Step 1: Push del Codice su Git

```bash
# Se non hai ancora inizializzato git
git init
git add .
git commit -m "Initial commit - OncoNews ready for Render"

# Crea repository su GitHub e pusha
git remote add origin https://github.com/TUO_USERNAME/onconews.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy su Render

1. Vai su [dashboard.render.com](https://dashboard.render.com)
2. Click su **"New +"** → **"Blueprint"**
3. Connetti il tuo repository Git
4. Render rileverà automaticamente il file `render.yaml`
5. Click su **"Apply"**

### Step 3: Configura NEWS_API_KEY

Dopo il deploy iniziale:

1. Vai su **Dashboard Render**
2. Click sul servizio **"onconews-viewer"**
3. Vai su **Environment**
4. Aggiungi variabile:
   - Key: `NEWS_API_KEY`
   - Value: `la_tua_chiave_api`
5. Click su **"Save Changes"**
6. Ripeti per **"onconews-fetcher"** (cron job)

### Step 4: Inizializza Database

Il database viene creato automaticamente, ma devi inizializzare le tabelle:

1. Vai sul servizio **"onconews-viewer"**
2. Click sulla tab **"Shell"**
3. Esegui:
   ```bash
   python init_db.py
   ```

### Step 5: Test

1. Apri l'URL del tuo web service (es. `https://onconews-viewer.onrender.com`)
2. Dovresti vedere la pagina con 0 articoli
3. Attendi l'esecuzione del cron job (ore 8:00 UTC) o eseguilo manualmente:
   - Vai su **"onconews-fetcher"** → **"Manual Trigger"**

---

## 📦 Metodo 2: Deploy Manuale

### Step 1: Crea Database PostgreSQL

1. Dashboard Render → **"New +"** → **"PostgreSQL"**
2. Configura:
   - Name: `onconews-db`
   - Database: `onconews`
   - User: `onconews`
   - Region: scegli la più vicina
   - Plan: **Free**
3. Click **"Create Database"**
4. Copia la **Internal Database URL** (la userai dopo)

### Step 2: Crea Web Service

1. Dashboard → **"New +"** → **"Web Service"**
2. Connetti repository Git
3. Configura:
   - Name: `onconews-viewer`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn web_viewer:app`
   - Plan: **Free**
4. Environment Variables:
   - `DATABASE_URL`: [incolla Internal Database URL]
   - `NEWS_API_KEY`: [tua chiave API]
5. Click **"Create Web Service"**

### Step 3: Crea Cron Job

1. Dashboard → **"New +"** → **"Cron Job"**
2. Connetti repository Git
3. Configura:
   - Name: `onconews-fetcher`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Command: `python main.py`
   - Schedule: `0 8 * * *` (ore 8:00 UTC ogni giorno)
4. Environment Variables:
   - `DATABASE_URL`: [stessa di prima]
   - `NEWS_API_KEY`: [tua chiave API]
5. Click **"Create Cron Job"**

### Step 4: Inizializza Database

Come nel Metodo 1, esegui `python init_db.py` dalla shell del web service.

---

## ⚙️ Configurazione Schedulazione Cron

Per modificare quando gira il cron job, modifica `render.yaml`:

```yaml
# Ogni giorno alle 8:00 UTC
schedule: "0 8 * * *"

# Ogni 6 ore
schedule: "0 */6 * * *"

# Due volte al giorno (8:00 e 20:00 UTC)
schedule: "0 8,20 * * *"

# Ogni lunedì alle 10:00 UTC
schedule: "0 10 * * 1"
```

Sintassi Cron: `minuto ora giorno_mese mese giorno_settimana`

---

## 🔍 Monitoraggio e Debug

### Visualizza Log Web Service

1. Dashboard → **onconews-viewer** → **Logs**
2. Vedi richieste HTTP, errori, startup

### Visualizza Log Cron Job

1. Dashboard → **onconews-fetcher** → **Logs**
2. Vedi output di ogni esecuzione
3. Controlla errori durante fetch/scraping

### Esegui Cron Manualmente

1. Dashboard → **onconews-fetcher**
2. Click **"Manual Trigger"** (in alto a destra)
3. Utile per testare senza aspettare schedulazione

### Accedi al Database

1. Dashboard → **onconews-db** → **Info**
2. Usa **External Database URL** con un client PostgreSQL
3. O usa la **Shell** nel web service:
   ```bash
   python
   >>> from database import NewsDatabase
   >>> db = NewsDatabase()
   >>> stats = db.get_statistics()
   >>> print(stats)
   ```

---

## 💰 Costi e Limiti

### Piano Free Render

| Servizio | Limite | Costo |
|----------|--------|-------|
| Web Service | 750h/mese (1 istanza sempre online) | **Gratis** |
| Cron Job | Esecuzioni illimitate | **Gratis** |
| PostgreSQL | 1GB storage, 97h uptime/mese | **Gratis 90gg**, poi $7/mese |

### News API Limiti (Piano Free)

- 100 richieste/giorno
- Con ~45 keywords = ~45 richieste/giorno
- Ben sotto il limite ✅

### Raccomandazioni

- Il web service free va in "sleep" dopo 15min di inattività
- Il primo accesso dopo sleep richiede ~30 secondi
- Per evitare sleep: upgrade a piano Starter ($7/mese)
- Il database free scade dopo 90 giorni (poi $7/mese o migra altrove)

---

## 🔄 Migrare a Database Esterno Gratuito (Opzionale)

Per evitare il costo del database Render dopo 90 giorni:

### Opzione A: Supabase (Consigliato)

1. Crea account su [supabase.com](https://supabase.com)
2. Crea nuovo progetto
3. Vai su **Settings** → **Database**
4. Copia **Connection String** (URI format)
5. Su Render, aggiorna variabile `DATABASE_URL`
6. Esegui `python init_db.py`
7. ✅ Database gratuito per sempre!

### Opzione B: Neon.tech

1. Crea account su [neon.tech](https://neon.tech)
2. Crea progetto
3. Copia connection string
4. Aggiorna `DATABASE_URL` su Render
5. Esegui `python init_db.py`

Entrambi offrono **PostgreSQL gratuito permanente** con limiti generosi.

---

## 🛠️ Manutenzione

### Aggiornare Codice

```bash
# Modifica codice localmente
git add .
git commit -m "Update: descrizione modifiche"
git push

# Render rileverà automaticamente le modifiche e rifarà deploy
```

### Modificare Keywords

1. Modifica `config.yaml` localmente
2. Commit e push
3. Render aggiornerà automaticamente

### Backup Database

Render fa backup automatici, ma per sicurezza:

1. Dashboard → **onconews-db** → **Backups**
2. Click **"Create Manual Backup"**
3. O esporta con script:
   ```bash
   python -c "from database import NewsDatabase; db = NewsDatabase(); import json; articles = db.export_for_analysis(); open('backup.json', 'w').write(json.dumps(articles, indent=2, default=str))"
   ```

### Ripristinare da Backup

Se devi ricreare il database:

1. Esegui `python init_db.py`
2. Usa uno script di import (da creare se necessario)

---

## 🐛 Troubleshooting

### Errore: "NEWS_API_KEY not found"

- Verifica di aver configurato la variabile d'ambiente
- Controlla che non ci siano spazi extra nel valore
- Riavvia il servizio dopo le modifiche

### Database: "relation 'news' does not exist"

- Devi eseguire `python init_db.py`
- Eseguilo dalla Shell del web service

### Web Service non si avvia

1. Controlla i log per errori
2. Verifica che `requirements.txt` sia corretto
3. Testa localmente con:
   ```bash
   pip install -r requirements.txt
   gunicorn web_viewer:app
   ```

### Cron Job fallisce

1. Controlla log del cron job
2. Verifica API key valida
3. Testa localmente con `python main.py`
4. Controlla connessione database

### Web Service va in sleep

- Normale per piano free
- Upgrade a Starter ($7/mese) per evitarlo
- O usa servizio di ping esterno (es. UptimeRobot)

---

## 📊 Struttura File Progetto

```
onconews/
├── render.yaml              # Configurazione Render (IMPORTANTE)
├── requirements.txt         # Dipendenze Python
├── config.yaml             # Keywords e filtri
├── .env.example            # Template variabili d'ambiente
├── init_db.py              # Script inizializzazione DB
├── main.py                 # Script raccolta notizie (cron)
├── web_viewer.py           # Flask web app
├── database.py             # Gestione DB (SQLite + PostgreSQL)
├── news_fetcher.py         # Fetch da News API
├── google_news_fetcher.py  # Fetch da Google News
├── reddit_fetcher.py       # Fetch da Reddit
├── content_scraper.py      # Scraping testo completo
├── content_filter.py       # Filtri intelligenti
└── DEPLOY_RENDER.md        # Questa guida
```

---

## ✅ Checklist Post-Deploy

- [ ] Database PostgreSQL creato
- [ ] Web Service deployed e accessibile
- [ ] Cron Job configurato
- [ ] `NEWS_API_KEY` configurata su entrambi i servizi
- [ ] `DATABASE_URL` configurata su entrambi i servizi
- [ ] Database inizializzato con `python init_db.py`
- [ ] Primo cron eseguito (manualmente o schedulato)
- [ ] Web viewer mostra articoli
- [ ] Log controllati per errori

---

## 🎉 Completato!

Il tuo sistema OncoNews è ora online e funzionante su Render!

- 🌐 **Web Viewer**: Visualizza articoli 24/7
- 🤖 **Cron Job**: Raccoglie notizie automaticamente ogni giorno
- 💾 **Database**: PostgreSQL gestito con backup

### Prossimi Passi

1. Monitora i log per i primi giorni
2. Verifica che le notizie vengano raccolte correttamente
3. Ottimizza keywords in `config.yaml` se necessario
4. Dopo 90 giorni, considera migrazione a database gratuito esterno

---

## 📞 Supporto

**Render.com**:
- Docs: https://render.com/docs
- Community: https://community.render.com

**News API**:
- Docs: https://newsapi.org/docs

**Problemi con il codice**:
- Controlla i log
- Testa localmente prima
- Verifica configurazione variabili d'ambiente
